import pandas as pd
import streamlit as st
from .excel_cleaner import ExcelCleaner

def process_uploaded_file(uploaded_file):
    """Traite le fichier uploadé et retourne les résultats"""
    try:
        # Lire le fichier Excel en préservant les formats
        df = pd.read_excel(uploaded_file)
        st.success(f"Fichier chargé: {len(df)} lignes")
        
        # Bouton pour nettoyer
        if st.button("🧽 Nettoyer le fichier"):
            cleaner = ExcelCleaner()
            cleaned_df = cleaner.clean_dataframe(df.copy())
            
            if cleaned_df is not None:
                st.success(f"Nettoyage terminé: {len(cleaned_df)} lignes restantes")
                return {
                    'original_df': df,
                    'cleaned_df': cleaned_df,
                    'original_count': len(df),
                    'cleaned_count': len(cleaned_df)
                }
        
        return None
        
    except Exception as e:
        st.error(f"Erreur lors du traitement: {str(e)}")
        return None

