# Configuration personnalisée pour votre environnement
# Copiez ce fichier vers config/user_config.py et modifiez selon vos besoins

# Chemins par défaut
DEFAULT_MASTER_BOM = "master_bom_cleaned.xlsx"
DEFAULT_OUTPUT_DIR = "output"

# Noms de colonnes spécifiques à votre organisation
CUSTOM_COLUMN_NAMES = {
    'part_number': ['Part Number', 'PN', 'Votre_Nom_PN'],
    'project': ['Projet', 'Project', 'Votre_Nom_Projet'],
    'status': ['Statut', 'Status', 'Votre_Nom_Statut']
}

# Couleurs personnalisées
CUSTOM_COLORS = {
    'error': 'FF9999',    # Rouge plus vif
    'warning': 'FFCC99',  # Orange plus vif
    'success': 'CCFF99'   # Vert plus vif
}
