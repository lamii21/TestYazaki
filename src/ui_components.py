import streamlit as st
import pandas as pd
import io
from .master_bom_manager import MasterBOMManager

def render_upload_section():
    """Affiche la section d'upload de fichier"""
    return st.file_uploader(
        "Choisissez un fichier Excel", 
        type=['xlsx'],
        help="Formats supportés: .xlsx"
    )

def render_results_section(result):
    """Affiche les résultats du nettoyage"""
    cleaned_df = result['cleaned_df']
    
    # Statistiques
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Lignes originales", result['original_count'])
    with col2:
        st.metric("Lignes nettoyées", result['cleaned_count'])
    with col3:
        reduction = result['original_count'] - result['cleaned_count']
        st.metric("Lignes supprimées", reduction)
    
    # Aperçu avec formatage des dates
    st.subheader("📋 Aperçu du fichier nettoyé (5 premières lignes)")
    
    # Formater les colonnes de dates pour l'affichage
    display_df = cleaned_df.head().copy()
    for col in display_df.columns:
        if display_df[col].dtype == 'datetime64[ns]':
            display_df[col] = display_df[col].dt.strftime('%-m/%-d/%Y')
    
    st.dataframe(display_df, use_container_width=True)
    
    # Bouton de téléchargement
    download_data = _create_excel_download(cleaned_df)
    st.download_button(
        label="📥 Télécharger le fichier nettoyé",
        data=download_data,
        file_name="fichier_nettoye.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    # Section comparaison Master BOM
    render_master_bom_section(cleaned_df)

def render_master_bom_section(cleaned_df):
    """Affiche la section de comparaison avec Master BOM"""
    st.divider()
    st.subheader("🔍 Comparaison avec Master BOM")
    
    master_manager = MasterBOMManager()
    
    if st.button("📊 Comparer avec Master BOM"):
        if master_manager.load_master_bom():
            st.success("Master BOM chargée avec succès")
            
            # Effectuer la comparaison
            comparison_results = master_manager.compare_with_master(cleaned_df)
            
            if comparison_results is not None:
                st.subheader("📋 Résultats de la comparaison")
                st.dataframe(comparison_results, use_container_width=True)
                
                # Statistiques de comparaison
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    count_d = len(comparison_results[comparison_results['Statut trouvé'] == 'D'])
                    st.metric("Deleted (D)", count_d)
                with col2:
                    count_x = len(comparison_results[comparison_results['Statut trouvé'] == 'X'])
                    st.metric("Obsolète (X)", count_x)
                with col3:
                    count_0 = len(comparison_results[comparison_results['Statut trouvé'] == '0'])
                    st.metric("Doublon (0)", count_0)
                with col4:
                    count_nan = len(comparison_results[comparison_results['Statut trouvé'] == 'NaN'])
                    st.metric("Inconnu (NaN)", count_nan)
                
                # Boutons d'action
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🔄 Mettre à jour la Master BOM"):
                        updated_master = master_manager.update_master_bom(cleaned_df)
                        if updated_master is not None:
                            st.success("Master BOM mise à jour avec succès")
                            st.session_state['updated_master'] = updated_master
                
                with col2:
                    if 'updated_master' in st.session_state:
                        download_data = _create_excel_download(st.session_state['updated_master'])
                        st.download_button(
                            label="📥 Télécharger la nouvelle Master BOM",
                            data=download_data,
                            file_name="master_bom_updated.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

def _create_excel_download(df):
    """Crée le fichier Excel pour téléchargement"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()


