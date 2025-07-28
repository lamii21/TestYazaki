"""Configuration de l'application"""

# Configuration Streamlit
STREAMLIT_CONFIG = {
    "page_title": "Nettoyeur BOM Excel",
    "page_icon": "🧹",
    "layout": "wide"
}

# Configuration du nettoyage
CLEANING_CONFIG = {
    "part_number_patterns": [
        'Part Number', 'PN', 'Réf Composant', 'Reference', 
        'Ref', 'Part_Number', 'Référence'
    ],
    "desired_columns": ["Projet", "Quantité", "Désignation"],
    "regex_pattern": r'[^A-Za-z0-9]'
}

# Configuration des fichiers
FILE_CONFIG = {
    "supported_formats": ['xlsx'],
    "max_file_size": "200MB",
    "output_filename": "fichier_nettoye.xlsx"
}