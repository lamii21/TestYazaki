import pandas as pd
import streamlit as st
import re

class NewBOMProcessor:
    """Processeur pour nettoyer les nouvelles BOM"""
    
    def __init__(self):
        self.possible_pn_names = [
            'Part Number', 'PN', 'Réf Composant', 'Reference', 
            'Ref', 'Part_Number', 'Référence'
        ]
    
    def clean_new_bom(self, uploaded_file):
        """Nettoie une nouvelle BOM"""
        try:
            # Lire le fichier
            df = pd.read_excel(uploaded_file)
            original_count = len(df)
            
            # Nettoyer
            cleaned_df = self._clean_dataframe(df)
            
            if cleaned_df is not None:
                return {
                    'cleaned_df': cleaned_df,
                    'original_count': original_count,
                    'cleaned_count': len(cleaned_df),
                    'preview': self._format_preview(cleaned_df.head(5))
                }
            
            return None
            
        except Exception as e:
            st.error(f"Erreur lors du nettoyage: {str(e)}")
            return None
    
    def _clean_dataframe(self, df):
        """Nettoie le DataFrame"""
        # Identifier la colonne Part Number
        pn_col = self._find_part_number_column(df)
        if not pn_col:
            st.error("Colonne Part Number non trouvée")
            return None
        
        # Identifier les colonnes de dates
        date_columns = []
        for col in df.columns:
            if df[col].dtype == 'datetime64[ns]' or 'date' in col.lower():
                date_columns.append(col)
        
        # Nettoyer les espaces (sauf dates)
        for col in df.columns:
            if col not in date_columns:
                df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
        
        # Nettoyer les Part Numbers
        df[pn_col] = df[pn_col].apply(self._clean_part_number)
        
        # Supprimer lignes vides
        df = df[df[pn_col] != ""]
        
        # Réorganiser colonnes
        df = self._reorder_columns(df, pn_col)
        
        return df
    
    def _find_part_number_column(self, df):
        """Trouve la colonne Part Number"""
        for col in df.columns:
            if any(name.lower() in col.lower() for name in self.possible_pn_names):
                return col
        return None
    
    def _clean_part_number(self, pn):
        """Nettoie un Part Number"""
        if pd.isna(pn):
            return ""
        return re.sub(r'[^A-Za-z0-9]', '', str(pn))
    
    def _reorder_columns(self, df, pn_col):
        """Réorganise les colonnes"""
        desired_cols = [pn_col, "Projet", "Quantité", "Désignation"]
        available_cols = [col for col in desired_cols if col in df.columns]
        other_cols = [col for col in df.columns if col not in available_cols]
        return df[available_cols + other_cols]
    
    def _format_preview(self, df):
        """Formate l'aperçu pour l'affichage"""
        display_df = df.copy()
        for col in display_df.columns:
            if display_df[col].dtype == 'datetime64[ns]':
                display_df[col] = display_df[col].dt.strftime('%-m/%-d/%Y')
        return display_df