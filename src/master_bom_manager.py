import pandas as pd
import streamlit as st
import os
from pathlib import Path

class MasterBOMManager:
    """Gestionnaire pour la comparaison et mise à jour de la Master BOM"""
    
    def __init__(self):
        self.master_bom_path = "master_bom.xlsx"
        self.master_df = None
        self.comparison_results = None
    
    def load_master_bom(self):
        """Charge le fichier Master BOM s'il existe"""
        if os.path.exists(self.master_bom_path):
            try:
                self.master_df = pd.read_excel(self.master_bom_path)
                return True
            except Exception as e:
                st.error(f"Erreur lors du chargement de la Master BOM: {str(e)}")
                return False
        else:
            st.warning("Fichier master_bom.xlsx non trouvé dans le dossier du projet")
            return False
    
    def compare_with_master(self, new_bom_df):
        """Compare la nouvelle BOM avec la Master BOM"""
        if self.master_df is None:
            st.error("Master BOM non chargée")
            return None
        
        # Identifier les colonnes nécessaires
        pn_col = self._find_part_number_column(new_bom_df)
        project_col = self._find_project_column(new_bom_df)
        
        if not pn_col:
            st.error("Colonne Part Number non trouvée dans la nouvelle BOM")
            return None
        
        # Préparer les résultats de comparaison
        results = []
        
        for idx, row in new_bom_df.iterrows():
            part_number = row[pn_col]
            project = row[project_col] if project_col else ""
            
            # Recherche dans Master BOM
            status = self._lookup_status(part_number, project)
            action = self._determine_action(status)
            
            results.append({
                'Part Number': part_number,
                'Projet': project,
                'Statut trouvé': status,
                'Action requise': action
            })
        
        self.comparison_results = pd.DataFrame(results)
        return self.comparison_results
    
    def _find_part_number_column(self, df):
        """Trouve la colonne Part Number"""
        possible_names = ['Part Number', 'PN', 'Réf Composant', 'Reference', 'Ref', 'Part_Number', 'Référence']
        for col in df.columns:
            if any(name.lower() in col.lower() for name in possible_names):
                return col
        return None
    
    def _find_project_column(self, df):
        """Trouve la colonne Projet"""
        possible_names = ['Projet', 'Project', 'Nom du Projet', 'Project Name']
        for col in df.columns:
            if any(name.lower() in col.lower() for name in possible_names):
                return col
        return None
    
    def _lookup_status(self, part_number, project=""):
        """Recherche le statut dans la Master BOM (équivalent XLOOKUP)"""
        master_pn_col = self._find_part_number_column(self.master_df)
        master_project_col = self._find_project_column(self.master_df)
        
        if not master_pn_col:
            return "NaN"
        
        # Recherche par Part Number
        mask = self.master_df[master_pn_col] == part_number
        
        # Si colonne projet existe, affiner la recherche
        if master_project_col and project:
            mask = mask & (self.master_df[master_project_col] == project)
        
        matches = self.master_df[mask]
        
        if matches.empty:
            return "NaN"
        elif len(matches) > 1:
            return "0"  # Doublon
        else:
            # Chercher colonne statut
            status_col = self._find_status_column(self.master_df)
            if status_col:
                return matches[status_col].iloc[0]
            else:
                return "NaN"
    
    def _find_status_column(self, df):
        """Trouve la colonne de statut"""
        possible_names = ['Statut', 'Status', 'État', 'State']
        for col in df.columns:
            if any(name.lower() in col.lower() for name in possible_names):
                return col
        return None
    
    def _determine_action(self, status):
        """Détermine l'action à effectuer selon le statut"""
        if status == "D":
            return "Aucune action"
        elif status == "X":
            return "Changer statut en D"
        elif status == "0":
            return "Ajouter nouvelle ligne"
        elif status == "NaN" or pd.isna(status):
            return "Ajouter nouvelle ligne"
        else:
            return "Vérifier manuellement"
    
    def update_master_bom(self, new_bom_df):
        """Met à jour la Master BOM selon les résultats de comparaison"""
        if self.comparison_results is None:
            st.error("Aucune comparaison effectuée")
            return None
        
        updated_master = self.master_df.copy()
        master_pn_col = self._find_part_number_column(updated_master)
        status_col = self._find_status_column(updated_master)
        
        # 1. Changer les statuts X en D
        for idx, row in self.comparison_results.iterrows():
            if row['Action requise'] == "Changer statut en D":
                part_number = row['Part Number']
                mask = updated_master[master_pn_col] == part_number
                if status_col:
                    updated_master.loc[mask, status_col] = "D"
        
        # 2. Ajouter les nouvelles lignes
        new_rows = []
        for idx, row in self.comparison_results.iterrows():
            if row['Action requise'] == "Ajouter nouvelle ligne":
                # Trouver la ligne correspondante dans new_bom_df
                new_bom_row = new_bom_df[new_bom_df.iloc[:, 0] == row['Part Number']].iloc[0]
                
                # Créer nouvelle ligne pour Master BOM
                new_row = {}
                if master_pn_col:
                    new_row[master_pn_col] = row['Part Number']
                if status_col:
                    new_row[status_col] = "A"  # Actif par défaut
                
                # Copier autres colonnes si elles existent
                for col in new_bom_df.columns:
                    if col in updated_master.columns:
                        new_row[col] = new_bom_row[col]
                
                new_rows.append(new_row)
        
        # Ajouter les nouvelles lignes
        if new_rows:
            new_df = pd.DataFrame(new_rows)
            updated_master = pd.concat([updated_master, new_df], ignore_index=True)
        
        return updated_master