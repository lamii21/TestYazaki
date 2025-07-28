import pandas as pd
import streamlit as st
from .master_bom_processor import MasterBOMProcessor

class BOMComparator:
    """Comparateur entre Master BOM et nouvelle BOM"""
    
    def __init__(self):
        self.master_processor = MasterBOMProcessor()
    
    def compare_boms(self, new_bom_df):
        """Compare la nouvelle BOM avec le Master BOM"""
        # Charger Master BOM
        master_df = self.master_processor.load_master_bom()
        
        if master_df is None:
            st.error("❌ Aucun Master BOM trouvé. Veuillez d'abord définir un Master BOM.")
            st.info("💡 Allez dans la section 1 pour uploader et définir votre Master BOM")
            return None
        
        st.success(f"✅ Master BOM chargé avec succès ({len(master_df)} lignes)")
        
        # Identifier les colonnes
        new_pn_col = self._find_part_number_column(new_bom_df)
        new_project_col = self._find_project_column(new_bom_df)
        
        if not new_pn_col:
            st.error("Colonne Part Number non trouvée dans la nouvelle BOM")
            return None
        
        # Effectuer la comparaison
        results = []
        
        for idx, row in new_bom_df.iterrows():
            part_number = row[new_pn_col]
            project = row[new_project_col] if new_project_col else ""
            
            # Recherche dans Master BOM
            status = self._lookup_status(master_df, part_number, project)
            action = self._determine_action(status)
            
            results.append({
                'Part Number': part_number,
                'Projet': project,
                'Statut': status,
                'Action requise': action
            })
        
        comparison_df = pd.DataFrame(results)
        
        # Calculer statistiques
        stats = {
            'D': len(comparison_df[comparison_df['Statut'] == 'D']),
            'X': len(comparison_df[comparison_df['Statut'] == 'X']),
            '0': len(comparison_df[comparison_df['Statut'] == '0']),
            'NaN': len(comparison_df[comparison_df['Statut'] == 'NaN'])
        }
        
        return {
            'comparison_df': comparison_df,
            'stats': stats,
            'master_df': master_df
        }
    
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
    
    def _find_status_column(self, df):
        """Trouve la colonne de statut"""
        possible_names = ['Statut', 'Status', 'État', 'State']
        for col in df.columns:
            if any(name.lower() in col.lower() for name in possible_names):
                return col
        return None
    
    def _lookup_status(self, master_df, part_number, project=""):
        """Recherche le statut dans Master BOM (XLOOKUP)"""
        master_pn_col = self._find_part_number_column(master_df)
        master_project_col = self._find_project_column(master_df)
        
        if not master_pn_col:
            return "NaN"
        
        # Recherche par Part Number
        mask = master_df[master_pn_col] == part_number
        
        # Affiner par projet si disponible
        if master_project_col and project:
            mask = mask & (master_df[master_project_col] == project)
        
        matches = master_df[mask]
        
        if matches.empty:
            return "NaN"
        elif len(matches) > 1:
            return "0"  # Doublon
        else:
            # Chercher colonne statut
            status_col = self._find_status_column(master_df)
            if status_col and status_col in matches.columns:
                status = matches[status_col].iloc[0]
                return status if pd.notna(status) else "NaN"
            else:
                return "NaN"
    
    def _determine_action(self, status):
        """Détermine l'action selon le statut"""
        if status == "D":
            return "✅ Aucune action"
        elif status == "X":
            return "🔄 Changer statut en D"
        elif status == "0":
            return "➕ Ajouter nouvelle ligne"
        elif status == "NaN" or pd.isna(status):
            return "➕ Ajouter nouvelle ligne"
        else:
            return "⚠️ Vérifier manuellement"
    
    def update_master_bom(self, comparison_result, new_bom_df):
        """Met à jour le Master BOM"""
        try:
            master_df = comparison_result['master_df'].copy()
            comparison_df = comparison_result['comparison_df']
            
            master_pn_col = self._find_part_number_column(master_df)
            status_col = self._find_status_column(master_df)
            
            # 1. Changer X en D
            for idx, row in comparison_df.iterrows():
                if row['Action requise'] == "🔄 Changer statut en D":
                    part_number = row['Part Number']
                    mask = master_df[master_pn_col] == part_number
                    if status_col and mask.any():
                        master_df.loc[mask, status_col] = "D"
            
            # 2. Ajouter nouvelles lignes
            new_rows = []
            new_pn_col = self._find_part_number_column(new_bom_df)
            
            for idx, row in comparison_df.iterrows():
                if row['Action requise'] == "➕ Ajouter nouvelle ligne":
                    # Trouver ligne correspondante dans new_bom_df
                    new_mask = new_bom_df[new_pn_col] == row['Part Number']
                    if new_mask.any():
                        new_bom_row = new_bom_df[new_mask].iloc[0]
                        
                        # Créer nouvelle ligne
                        new_row = {}
                        if master_pn_col:
                            new_row[master_pn_col] = row['Part Number']
                        if status_col:
                            new_row[status_col] = "A"  # Actif
                        
                        # Copier autres colonnes
                        for col in new_bom_df.columns:
                            if col in master_df.columns and col != master_pn_col:
                                new_row[col] = new_bom_row[col]
                        
                        new_rows.append(new_row)
            
            # Ajouter nouvelles lignes
            if new_rows:
                new_df = pd.DataFrame(new_rows)
                master_df = pd.concat([master_df, new_df], ignore_index=True)
            
            # Sauvegarder
            self.master_processor.master_bom_path = "master_bom_cleaned.xlsx"
            master_df.to_excel(self.master_processor.master_bom_path, index=False)
            
            return master_df
            
        except Exception as e:
            st.error(f"Erreur lors de la mise à jour: {str(e)}")
            return None
