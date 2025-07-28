import streamlit as st
from src.master_bom_processor import MasterBOMProcessor
from src.new_bom_processor import NewBOMProcessor
from src.bom_comparator import BOMComparator

def main():
    st.set_page_config(
        page_title="Nettoyeur BOM Excel",
        page_icon="🧹",
        layout="wide"
    )
    
    st.title("🧹 Nettoyeur de fichiers BOM Excel")
    st.write("Gérez votre Master BOM et comparez avec de nouvelles BOM")
    
    # Section 1: Master BOM
    st.header("🗂️ 1. Définition du Master BOM (fichier de référence)")
    render_master_bom_section()
    
    st.divider()
    
    # Section 2: Nouvelle BOM
    st.header("🔄 2. Comparaison avec Nouvelle BOM")
    render_new_bom_section()

def render_master_bom_section():
    """Section pour gérer le Master BOM"""
    master_processor = MasterBOMProcessor()
    
    # Vérifier si Master BOM existe déjà
    if 'master_bom_df' in st.session_state:
        st.success("✅ Master BOM déjà défini")
        if st.button("📋 Voir aperçu Master BOM", key="show_master"):
            st.dataframe(st.session_state['master_bom_df'].head(10), use_container_width=True)
    
    # Upload Master BOM
    master_file = st.file_uploader(
        "📁 Choisissez votre fichier Master BOM", 
        type=['xlsx'],
        key="master_upload",
        help="Ce fichier servira de référence pour toutes les comparaisons"
    )
    
    if master_file:
        if st.button("🔧 Définir comme Master BOM", key="define_master"):
            result = master_processor.process_master_bom(master_file)
            
            if result:
                st.success(f"✅ Master BOM définie avec succès ! ({result['cleaned_count']} lignes)")
                
                # Afficher aperçu
                st.subheader("📋 Aperçu Master BOM (10 premières lignes)")
                st.dataframe(result['preview'], use_container_width=True)
                
                # Statistiques
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Lignes originales", result['original_count'])
                with col2:
                    st.metric("Lignes nettoyées", result['cleaned_count'])
                with col3:
                    st.metric("Lignes supprimées", result['original_count'] - result['cleaned_count'])

def render_new_bom_section():
    """Section pour traiter et comparer une nouvelle BOM"""
    new_processor = NewBOMProcessor()
    comparator = BOMComparator()
    
    # Upload nouvelle BOM
    new_file = st.file_uploader(
        "📁 Choisissez votre nouvelle BOM à comparer", 
        type=['xlsx'],
        key="new_upload",
        help="Cette BOM sera comparée avec votre Master BOM"
    )
    
    if new_file:
        # Nettoyer la nouvelle BOM
        if st.button("🧽 Nettoyer la nouvelle BOM", key="clean_new"):
            cleaned_result = new_processor.clean_new_bom(new_file)
            
            if cleaned_result:
                st.success(f"✅ Nouvelle BOM nettoyée ! ({cleaned_result['cleaned_count']} lignes)")
                st.session_state['cleaned_new_bom'] = cleaned_result
                
                # Aperçu
                st.subheader("📋 Aperçu nouvelle BOM nettoyée (5 premières lignes)")
                st.dataframe(cleaned_result['preview'], use_container_width=True)
        
        # Comparaison avec Master BOM
        if 'cleaned_new_bom' in st.session_state:
            st.divider()
            
            if st.button("🔍 Comparer avec Master BOM", key="compare_boms"):
                comparison_result = comparator.compare_boms(st.session_state['cleaned_new_bom']['cleaned_df'])
                
                if comparison_result:
                    st.session_state['comparison_result'] = comparison_result
                    
                    st.subheader("📊 Résultats de la comparaison")
                    st.dataframe(comparison_result['comparison_df'], use_container_width=True)
                    
                    # Statistiques
                    stats = comparison_result['stats']
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("🟢 Deleted (D)", stats['D'], help="Aucune action requise")
                    with col2:
                        st.metric("🟡 Obsolète (X)", stats['X'], help="À changer en D")
                    with col3:
                        st.metric("🔵 Doublon (0)", stats['0'], help="À ajouter")
                    with col4:
                        st.metric("🔴 Inconnu (NaN)", stats['NaN'], help="À ajouter")
            
            # Actions sur Master BOM
            if 'comparison_result' in st.session_state:
                st.divider()
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🔄 Mettre à jour la Master BOM", key="update_master"):
                        updated_master = comparator.update_master_bom(
                            st.session_state['comparison_result'],
                            st.session_state['cleaned_new_bom']['cleaned_df']
                        )
                        
                        if updated_master is not None:
                            st.success("✅ Master BOM mise à jour avec succès !")
                            st.session_state['updated_master'] = updated_master
                
                with col2:
                    if 'updated_master' in st.session_state:
                        # Créer le fichier de téléchargement
                        import io
                        import pandas as pd
                        
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            st.session_state['updated_master'].to_excel(writer, index=False)
                        
                        st.download_button(
                            label="📥 Télécharger la nouvelle Master BOM",
                            data=output.getvalue(),
                            file_name="master_bom_updated.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="download_master"
                        )

if __name__ == "__main__":
    main()

