"""
Configuration pour le système de mise à jour BOM
Permet de personnaliser les noms de colonnes, couleurs, et comportements
"""

# Configuration des noms de colonnes possibles
COLUMN_NAMES = {
    'part_number': [
        'Part Number', 'PN', 'Réf Composant', 'Reference', 
        'Ref', 'Part_Number', 'Référence', 'Part_Num',
        'Numéro_Pièce', 'Code_Article', 'Article'
    ],
    
    'project': [
        'Projet', 'Project', 'Prj', 'Programme', 'Program',
        'Nom_Projet', 'Code_Projet', 'Project_Name'
    ],
    
    'status': [
        'Statut', 'Status', 'État', 'State', 'Etat',
        'État_Pièce', 'Statut_Article', 'Component_Status'
    ],
    
    'description': [
        'Description', 'Désignation', 'Desc', 'Libellé',
        'Component_Description', 'Part_Description'
    ],
    
    'supplier': [
        'Fournisseur', 'Supplier', 'Vendor', 'Fabricant',
        'Manufacturer', 'Supplier_Name'
    ],
    
    'price': [
        'Prix', 'Price', 'Coût', 'Cost', 'Unit_Price',
        'Prix_Unitaire', 'Tarif'
    ],
    
    'quantity': [
        'Quantité', 'Quantity', 'Qty', 'Qté', 'Amount'
    ]
}

# Configuration des statuts et leurs actions
STATUS_CONFIG = {
    'D': {
        'name': 'Désactivé',
        'action': 'no_action',
        'description': 'Aucune action requise',
        'color': None
    },
    
    'X': {
        'name': 'À remplacer',
        'action': 'update_to_d',
        'description': 'Mettre à jour le statut vers D',
        'color': 'yellow',
        'comment': 'Statut X remplacé par D'
    },
    
    '0': {
        'name': 'Doublon/Ambigu',
        'action': 'add_new_line',
        'description': 'Ajouter nouvelle ligne pour vérification',
        'color': 'red',
        'comment': 'Doublon ou incertain - Vérification manuelle requise'
    },
    
    'NaN': {
        'name': 'Introuvable/Erreur',
        'action': 'add_new_line_error',
        'description': 'Ajouter ligne selon le type d\'erreur',
        'color': 'orange',
        'comment_format_error': 'Erreur de format – à corriger manuellement',
        'comment_not_found': 'PN inconnu – insertion possible'
    }
}

# Configuration des couleurs Excel
EXCEL_COLORS = {
    'red': 'FFCCCC',      # Rouge clair pour doublons
    'orange': 'FFE6CC',   # Orange clair pour erreurs
    'yellow': 'FFFFCC',   # Jaune clair pour mises à jour
    'green': 'CCFFCC',    # Vert clair pour succès
    'blue': 'CCE6FF'      # Bleu clair pour informations
}

# Configuration des fichiers
FILE_CONFIG = {
    'master_bom_default': 'master_bom_cleaned.xlsx',
    'output_prefix': 'Update_',
    'report_prefix': 'Rapport_Modifications_',
    'date_format': '%Y%m%d_%H%M%S',
    'backup_enabled': True,
    'backup_suffix': '_backup'
}

# Configuration de validation
VALIDATION_CONFIG = {
    'min_part_number_length': 2,
    'max_part_number_length': 50,
    'allowed_part_number_chars': 'alphanumeric_dash_underscore',
    'require_project': False,
    'case_sensitive_lookup': False
}

# Configuration des rapports
REPORT_CONFIG = {
    'include_statistics': True,
    'include_timestamp': True,
    'include_summary': True,
    'default_format': 'xlsx',  # 'csv' ou 'xlsx'
    'separate_sheets': {
        'modifications': 'Modifications',
        'statistics': 'Statistiques',
        'summary': 'Résumé'
    }
}

# Configuration du logging
LOGGING_CONFIG = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file_enabled': True,
    'file_name': 'bom_updater.log',
    'console_enabled': True
}

# Messages personnalisables
MESSAGES = {
    'success': {
        'file_loaded': '✅ Fichier chargé avec succès',
        'process_complete': '✅ Mise à jour terminée avec succès',
        'file_saved': '✅ Fichier sauvegardé',
        'report_generated': '✅ Rapport généré'
    },
    
    'error': {
        'file_not_found': '❌ Fichier non trouvé',
        'column_not_found': '❌ Colonne requise non trouvée',
        'process_failed': '❌ Erreur lors du traitement',
        'save_failed': '❌ Erreur lors de la sauvegarde'
    },
    
    'warning': {
        'duplicate_found': '⚠️ Doublon détecté',
        'format_error': '⚠️ Erreur de format',
        'missing_data': '⚠️ Données manquantes'
    },
    
    'info': {
        'processing': '🔄 Traitement en cours...',
        'analyzing': '🔍 Analyse des données...',
        'updating': '📝 Mise à jour...',
        'saving': '💾 Sauvegarde...'
    }
}

# Configuration avancée
ADVANCED_CONFIG = {
    'enable_backup': True,
    'max_backup_files': 10,
    'enable_audit_trail': True,
    'enable_data_validation': True,
    'enable_auto_formatting': True,
    'enable_progress_tracking': True,
    'batch_size': 1000,  # Pour traitement par lots si nécessaire
    'memory_optimization': False
}

def get_config(section=None):
    """
    Récupère la configuration
    
    Args:
        section (str): Section spécifique à récupérer
        
    Returns:
        dict: Configuration demandée
    """
    config_map = {
        'columns': COLUMN_NAMES,
        'status': STATUS_CONFIG,
        'colors': EXCEL_COLORS,
        'files': FILE_CONFIG,
        'validation': VALIDATION_CONFIG,
        'reports': REPORT_CONFIG,
        'logging': LOGGING_CONFIG,
        'messages': MESSAGES,
        'advanced': ADVANCED_CONFIG
    }
    
    if section:
        return config_map.get(section, {})
    
    return {
        'columns': COLUMN_NAMES,
        'status': STATUS_CONFIG,
        'colors': EXCEL_COLORS,
        'files': FILE_CONFIG,
        'validation': VALIDATION_CONFIG,
        'reports': REPORT_CONFIG,
        'logging': LOGGING_CONFIG,
        'messages': MESSAGES,
        'advanced': ADVANCED_CONFIG
    }

def update_config(section, key, value):
    """
    Met à jour une valeur de configuration
    
    Args:
        section (str): Section de configuration
        key (str): Clé à mettre à jour
        value: Nouvelle valeur
    """
    config_map = {
        'columns': COLUMN_NAMES,
        'status': STATUS_CONFIG,
        'colors': EXCEL_COLORS,
        'files': FILE_CONFIG,
        'validation': VALIDATION_CONFIG,
        'reports': REPORT_CONFIG,
        'logging': LOGGING_CONFIG,
        'messages': MESSAGES,
        'advanced': ADVANCED_CONFIG
    }
    
    if section in config_map and key in config_map[section]:
        config_map[section][key] = value
        return True
    
    return False
