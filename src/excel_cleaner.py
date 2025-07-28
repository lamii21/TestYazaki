import pandas as pd
import re
import streamlit as st

class ExcelCleaner:
    """Classe pour nettoyer les fichiers Excel BOM"""
    
    def __init__(self):
        self.possible_pn_names = [
            'Part Number', 'PN', 'Réf Composant', 'Reference', 
            'Ref', 'Part_Number', 'Référence'
        ]
        self.desired_columns = ["Projet", "Quantité", "Désignation"]
    
    def find_part_number_column(self, df):
        """Identifie automatiquement la colonne Part Number"""
        for col in df.columns:
            if any(name.lower() in col.lower() for name in self.possible_pn_names):
                return col
        return None
    
    def clean_part_number(self, pn):
        """Nettoie un Part Number en gardant seulement lettres et chiffres"""
        if pd.isna(pn):
            return ""
        return re.sub(r'[^A-Za-z0-9]', '', str(pn))
    
    def clean_dataframe(self, df):
        """Nettoie le DataFrame selon les règles définies"""
        # Identifier la colonne Part Number
        pn_col = self.find_part_number_column(df)
        if not pn_col:
            st.error("Colonne Part Number non trouvée")
            return None
        
        # Identifier les colonnes de dates pour préserver leur format
        date_columns = []
        for col in df.columns:
            if df[col].dtype == 'datetime64[ns]' or 'date' in col.lower():
                date_columns.append(col)
        
        # Nettoyer les espaces dans toutes les cellules (sauf dates)
        for col in df.columns:
            if col not in date_columns:
                df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
        
        # Nettoyer la colonne Part Number
        df[pn_col] = df[pn_col].apply(self.clean_part_number)
        
        # Supprimer les lignes avec Part Number vide
        df = df[df[pn_col] != ""]
        
        # Réorganiser les colonnes
        df = self._reorder_columns(df, pn_col)
        
        return df
    
    def _reorder_columns(self, df, pn_col):
        """Réorganise les colonnes avec Part Number en premier"""
        desired_cols = [pn_col] + self.desired_columns
        available_cols = [col for col in desired_cols if col in df.columns]
        other_cols = [col for col in df.columns if col not in available_cols]
        return df[available_cols + other_cols]

