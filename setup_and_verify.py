#!/usr/bin/env python3
"""
Script d'installation et de vérification du système BOM
Vérifie les dépendances, installe les packages manquants, et teste le système
"""

import sys
import subprocess
import importlib
import os
from datetime import datetime

def print_banner():
    """Affiche la bannière du script"""
    print("=" * 60)
    print("🔧 INSTALLATION ET VÉRIFICATION SYSTÈME BOM")
    print("=" * 60)
    print(f"Python: {sys.version}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

def check_python_version():
    """Vérifie la version de Python"""
    print("\n🐍 Vérification de la version Python...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ requis")
        print(f"Version actuelle: {sys.version}")
        return False
    else:
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        return True

def install_package(package_name):
    """
    Installe un package Python
    
    Args:
        package_name (str): Nom du package à installer
        
    Returns:
        bool: True si installation réussie
    """
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        return False

def check_and_install_dependencies():
    """Vérifie et installe les dépendances"""
    print("\n📦 Vérification des dépendances...")
    
    # Liste des packages requis avec leurs noms d'import
    required_packages = {
        'pandas': 'pandas>=2.0.0',
        'openpyxl': 'openpyxl>=3.1.0',
        'numpy': 'numpy>=1.24.0',
        'streamlit': 'streamlit>=1.28.0'
    }
    
    missing_packages = []
    
    for import_name, package_spec in required_packages.items():
        try:
            importlib.import_module(import_name)
            print(f"✅ {import_name}")
        except ImportError:
            print(f"❌ {import_name} - manquant")
            missing_packages.append(package_spec)
    
    # Installer les packages manquants
    if missing_packages:
        print(f"\n🔄 Installation de {len(missing_packages)} package(s) manquant(s)...")
        
        for package in missing_packages:
            print(f"Installation de {package}...")
            if install_package(package):
                print(f"✅ {package} installé")
            else:
                print(f"❌ Échec installation {package}")
                return False
    
    print("✅ Toutes les dépendances sont installées")
    return True

def check_project_structure():
    """Vérifie la structure du projet"""
    print("\n📁 Vérification de la structure du projet...")
    
    required_files = [
        'src/__init__.py',
        'src/bom_status_updater.py',
        'src/bom_comparator.py',
        'src/master_bom_processor.py',
        'config/bom_config.py',
        'bom_update_main.py',
        'example_usage.py',
        'requirements.txt'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - manquant")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️ {len(missing_files)} fichier(s) manquant(s)")
        return False
    
    print("✅ Structure du projet correcte")
    return True

def test_imports():
    """Teste les imports des modules principaux"""
    print("\n🔍 Test des imports...")
    
    modules_to_test = [
        'src.bom_status_updater',
        'src.bom_comparator',
        'src.master_bom_processor',
        'config.bom_config'
    ]
    
    for module_name in modules_to_test:
        try:
            importlib.import_module(module_name)
            print(f"✅ {module_name}")
        except ImportError as e:
            print(f"❌ {module_name} - {str(e)}")
            return False
    
    print("✅ Tous les imports réussis")
    return True

def test_basic_functionality():
    """Teste les fonctionnalités de base"""
    print("\n⚙️ Test des fonctionnalités de base...")
    
    try:
        from src.bom_status_updater import BOMStatusUpdater
        from config.bom_config import get_config
        
        # Test d'initialisation
        updater = BOMStatusUpdater()
        print("✅ Initialisation BOMStatusUpdater")
        
        # Test de configuration
        config = get_config('columns')
        if config and 'part_number' in config:
            print("✅ Configuration chargée")
        else:
            print("❌ Problème de configuration")
            return False
        
        # Test des méthodes utilitaires
        import pandas as pd
        test_df = pd.DataFrame({'Part Number': ['PN001'], 'Projet': ['TEST']})
        
        pn_col = updater._find_column(test_df, updater.possible_pn_names)
        if pn_col == 'Part Number':
            print("✅ Détection de colonnes")
        else:
            print("❌ Problème détection colonnes")
            return False
        
        print("✅ Fonctionnalités de base opérationnelles")
        return True
        
    except Exception as e:
        print(f"❌ Erreur test fonctionnalités: {str(e)}")
        return False

def run_example_test():
    """Exécute un test d'exemple simple"""
    print("\n🧪 Test d'exemple...")
    
    try:
        # Importer et exécuter le test rapide
        import test_bom_system
        
        if test_bom_system.run_quick_test():
            print("✅ Test d'exemple réussi")
            return True
        else:
            print("❌ Test d'exemple échoué")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test d'exemple: {str(e)}")
        return False

def create_sample_config():
    """Crée un fichier de configuration d'exemple"""
    print("\n📝 Création de la configuration d'exemple...")
    
    config_content = """# Configuration personnalisée pour votre environnement
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
"""
    
    try:
        os.makedirs('config', exist_ok=True)
        with open('config/user_config_example.py', 'w', encoding='utf-8') as f:
            f.write(config_content)
        print("✅ Configuration d'exemple créée: config/user_config_example.py")
        return True
    except Exception as e:
        print(f"❌ Erreur création config: {str(e)}")
        return False

def display_usage_instructions():
    """Affiche les instructions d'utilisation"""
    print("\n" + "="*60)
    print("📋 INSTRUCTIONS D'UTILISATION")
    print("="*60)
    
    instructions = """
🚀 DÉMARRAGE RAPIDE:

1. Mode interactif (recommandé pour débuter):
   python bom_update_main.py

2. Mode ligne de commande:
   python bom_update_main.py --cleaned-file "fichier.xlsx" --master-bom "master.xlsx"

3. Interface web Streamlit:
   streamlit run app.py

4. Exécuter les exemples:
   python example_usage.py

5. Tests complets:
   python test_bom_system.py

📁 FICHIERS REQUIS:
   - Fichier Excel nettoyé (avec colonnes PN et Projet)
   - Master BOM (avec colonnes PN, Projet, Statut)

🎯 RÉSULTATS:
   - Update_[date].xlsx : Fichier mis à jour
   - Rapport_[date].xlsx : Rapport détaillé
   - Master BOM mis à jour automatiquement

💡 AIDE:
   python bom_update_main.py --help-detailed
"""
    
    print(instructions)

def main():
    """Fonction principale"""
    print_banner()
    
    success = True
    
    # Vérifications et installations
    checks = [
        ("Version Python", check_python_version),
        ("Dépendances", check_and_install_dependencies),
        ("Structure projet", check_project_structure),
        ("Imports modules", test_imports),
        ("Fonctionnalités base", test_basic_functionality),
        ("Test exemple", run_example_test),
        ("Configuration exemple", create_sample_config)
    ]
    
    for check_name, check_func in checks:
        if not check_func():
            print(f"\n❌ Échec: {check_name}")
            success = False
            break
    
    # Résultat final
    print("\n" + "="*60)
    if success:
        print("🎉 INSTALLATION ET VÉRIFICATION RÉUSSIES!")
        print("✅ Le système BOM est prêt à être utilisé")
        display_usage_instructions()
    else:
        print("💥 ÉCHEC DE L'INSTALLATION/VÉRIFICATION")
        print("❌ Veuillez corriger les erreurs avant de continuer")
    print("="*60)

if __name__ == "__main__":
    main()
