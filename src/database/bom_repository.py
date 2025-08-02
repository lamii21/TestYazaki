"""
Repository pour la gestion des données BOM en base de données
Support SQLite, PostgreSQL, SQL Server
"""

import sqlite3
import pandas as pd
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from contextlib import contextmanager

class BOMRepository:
    """
    Repository pour gérer les données BOM en base de données
    """
    
    def __init__(self, connection_string: str = None, db_type: str = "sqlite"):
        """
        Initialise le repository
        
        Args:
            connection_string (str): Chaîne de connexion à la DB
            db_type (str): Type de base de données (sqlite, postgresql, sqlserver)
        """
        self.connection_string = connection_string or "bom_database.db"
        self.db_type = db_type
        self.logger = logging.getLogger(__name__)
        
        # Initialiser la base de données
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialise les tables de la base de données"""
        create_tables_sql = """
        -- Table Master BOM
        CREATE TABLE IF NOT EXISTS master_bom (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            part_number VARCHAR(100) NOT NULL,
            project VARCHAR(100),
            status VARCHAR(10) NOT NULL,
            description TEXT,
            supplier VARCHAR(200),
            price DECIMAL(10,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(part_number, project)
        );
        
        -- Table historique des modifications
        CREATE TABLE IF NOT EXISTS bom_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            part_number VARCHAR(100) NOT NULL,
            project VARCHAR(100),
            old_status VARCHAR(10),
            new_status VARCHAR(10),
            action VARCHAR(50),
            user_name VARCHAR(100),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            details TEXT
        );
        
        -- Table des traitements
        CREATE TABLE IF NOT EXISTS processing_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename VARCHAR(500),
            total_rows INTEGER,
            processed_rows INTEGER,
            errors_count INTEGER,
            status VARCHAR(50),
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            details TEXT
        );
        
        -- Index pour performance
        CREATE INDEX IF NOT EXISTS idx_master_bom_pn ON master_bom(part_number);
        CREATE INDEX IF NOT EXISTS idx_master_bom_project ON master_bom(project);
        CREATE INDEX IF NOT EXISTS idx_master_bom_status ON master_bom(status);
        CREATE INDEX IF NOT EXISTS idx_history_pn ON bom_history(part_number);
        CREATE INDEX IF NOT EXISTS idx_history_timestamp ON bom_history(timestamp);
        """
        
        try:
            with self._get_connection() as conn:
                conn.executescript(create_tables_sql)
                conn.commit()
            self.logger.info("Base de données initialisée avec succès")
        except Exception as e:
            self.logger.error(f"Erreur initialisation DB: {str(e)}")
            raise
    
    @contextmanager
    def _get_connection(self):
        """Context manager pour les connexions DB"""
        if self.db_type == "sqlite":
            conn = sqlite3.connect(self.connection_string)
            conn.row_factory = sqlite3.Row  # Pour accès par nom de colonne
        else:
            # TODO: Ajouter support PostgreSQL/SQL Server
            raise NotImplementedError(f"DB type {self.db_type} non supporté")
        
        try:
            yield conn
        finally:
            conn.close()
    
    def load_master_bom(self, project: str = None) -> pd.DataFrame:
        """
        Charge le Master BOM depuis la base de données
        
        Args:
            project (str): Filtrer par projet (optionnel)
            
        Returns:
            pd.DataFrame: Master BOM
        """
        try:
            query = """
            SELECT part_number, project, status, description, supplier, price, updated_at
            FROM master_bom
            WHERE 1=1
            """
            params = []
            
            if project:
                query += " AND project = ?"
                params.append(project)
            
            query += " ORDER BY part_number, project"
            
            with self._get_connection() as conn:
                df = pd.read_sql_query(query, conn, params=params)
            
            self.logger.info(f"Master BOM chargé: {len(df)} lignes")
            return df
            
        except Exception as e:
            self.logger.error(f"Erreur chargement Master BOM: {str(e)}")
            raise
    
    def save_master_bom(self, df: pd.DataFrame, replace: bool = False) -> int:
        """
        Sauvegarde le Master BOM en base
        
        Args:
            df (pd.DataFrame): DataFrame à sauvegarder
            replace (bool): Remplacer les données existantes
            
        Returns:
            int: Nombre de lignes sauvegardées
        """
        try:
            required_columns = ['part_number', 'status']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Colonnes manquantes: {missing_columns}")
            
            # Préparer les données
            df_clean = df.copy()
            df_clean['updated_at'] = datetime.now()
            
            # Colonnes optionnelles
            optional_columns = ['project', 'description', 'supplier', 'price']
            for col in optional_columns:
                if col not in df_clean.columns:
                    df_clean[col] = None
            
            with self._get_connection() as conn:
                if replace:
                    # Supprimer les données existantes
                    conn.execute("DELETE FROM master_bom")
                
                # Insérer les nouvelles données
                df_clean.to_sql('master_bom', conn, if_exists='append', index=False)
                conn.commit()
                
                rows_affected = len(df_clean)
            
            self.logger.info(f"Master BOM sauvegardé: {rows_affected} lignes")
            return rows_affected
            
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde Master BOM: {str(e)}")
            raise
    
    def update_status(self, part_number: str, project: str, new_status: str, 
                     user_name: str = "system") -> bool:
        """
        Met à jour le statut d'une pièce
        
        Args:
            part_number (str): Numéro de pièce
            project (str): Projet
            new_status (str): Nouveau statut
            user_name (str): Utilisateur effectuant la modification
            
        Returns:
            bool: True si mise à jour réussie
        """
        try:
            with self._get_connection() as conn:
                # Récupérer l'ancien statut
                old_status_query = """
                SELECT status FROM master_bom 
                WHERE part_number = ? AND project = ?
                """
                cursor = conn.execute(old_status_query, (part_number, project))
                result = cursor.fetchone()
                old_status = result['status'] if result else None
                
                if old_status is None:
                    self.logger.warning(f"Pièce non trouvée: {part_number} - {project}")
                    return False
                
                # Mettre à jour le statut
                update_query = """
                UPDATE master_bom 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE part_number = ? AND project = ?
                """
                conn.execute(update_query, (new_status, part_number, project))
                
                # Enregistrer dans l'historique
                history_query = """
                INSERT INTO bom_history 
                (part_number, project, old_status, new_status, action, user_name, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                conn.execute(history_query, (
                    part_number, project, old_status, new_status, 
                    'status_update', user_name, f'Statut changé de {old_status} vers {new_status}'
                ))
                
                conn.commit()
            
            self.logger.info(f"Statut mis à jour: {part_number} {old_status} -> {new_status}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur mise à jour statut: {str(e)}")
            return False
    
    def get_processing_history(self, limit: int = 100) -> pd.DataFrame:
        """
        Récupère l'historique des traitements
        
        Args:
            limit (int): Nombre maximum de résultats
            
        Returns:
            pd.DataFrame: Historique des traitements
        """
        try:
            query = """
            SELECT * FROM processing_logs 
            ORDER BY start_time DESC 
            LIMIT ?
            """
            
            with self._get_connection() as conn:
                df = pd.read_sql_query(query, conn, params=[limit])
            
            return df
            
        except Exception as e:
            self.logger.error(f"Erreur récupération historique: {str(e)}")
            return pd.DataFrame()
    
    def log_processing(self, filename: str, total_rows: int, processed_rows: int, 
                      errors_count: int, status: str, details: str = None) -> int:
        """
        Enregistre un traitement dans les logs
        
        Args:
            filename (str): Nom du fichier traité
            total_rows (int): Nombre total de lignes
            processed_rows (int): Lignes traitées avec succès
            errors_count (int): Nombre d'erreurs
            status (str): Statut du traitement
            details (str): Détails additionnels
            
        Returns:
            int: ID du log créé
        """
        try:
            query = """
            INSERT INTO processing_logs 
            (filename, total_rows, processed_rows, errors_count, status, start_time, end_time, details)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?)
            """
            
            with self._get_connection() as conn:
                cursor = conn.execute(query, (
                    filename, total_rows, processed_rows, errors_count, status, details
                ))
                log_id = cursor.lastrowid
                conn.commit()
            
            return log_id
            
        except Exception as e:
            self.logger.error(f"Erreur enregistrement log: {str(e)}")
            return -1
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Récupère les statistiques de la base de données
        
        Returns:
            Dict: Statistiques diverses
        """
        try:
            stats = {}
            
            with self._get_connection() as conn:
                # Statistiques Master BOM
                cursor = conn.execute("SELECT COUNT(*) as total FROM master_bom")
                stats['total_parts'] = cursor.fetchone()['total']
                
                # Statistiques par statut
                cursor = conn.execute("""
                    SELECT status, COUNT(*) as count 
                    FROM master_bom 
                    GROUP BY status
                """)
                stats['by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}
                
                # Statistiques par projet
                cursor = conn.execute("""
                    SELECT project, COUNT(*) as count 
                    FROM master_bom 
                    WHERE project IS NOT NULL
                    GROUP BY project
                    ORDER BY count DESC
                    LIMIT 10
                """)
                stats['by_project'] = {row['project']: row['count'] for row in cursor.fetchall()}
                
                # Dernières modifications
                cursor = conn.execute("""
                    SELECT COUNT(*) as count 
                    FROM bom_history 
                    WHERE timestamp > datetime('now', '-7 days')
                """)
                stats['recent_changes'] = cursor.fetchone()['count']
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Erreur récupération statistiques: {str(e)}")
            return {}

# Exemple d'utilisation
def example_database_usage():
    """
    Exemple d'utilisation du repository BOM
    """
    # Initialiser le repository
    repo = BOMRepository("bom_example.db")
    
    # Créer des données d'exemple
    sample_data = pd.DataFrame({
        'part_number': ['PN001', 'PN002', 'PN003'],
        'project': ['PROJ_A', 'PROJ_A', 'PROJ_B'],
        'status': ['D', 'X', 'D'],
        'description': ['Résistance', 'Condensateur', 'LED'],
        'supplier': ['Fournisseur A', 'Fournisseur B', 'Fournisseur A'],
        'price': [0.10, 0.05, 0.25]
    })
    
    # Sauvegarder en base
    repo.save_master_bom(sample_data, replace=True)
    
    # Charger depuis la base
    loaded_data = repo.load_master_bom()
    print(f"Données chargées: {len(loaded_data)} lignes")
    
    # Mettre à jour un statut
    repo.update_status('PN002', 'PROJ_A', 'D', 'user_test')
    
    # Récupérer les statistiques
    stats = repo.get_statistics()
    print(f"Statistiques: {stats}")

if __name__ == "__main__":
    example_database_usage()
