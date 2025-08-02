#!/usr/bin/env python3
"""
Exemple d'utilisation de la classe BOMStatusUpdater
Démontre les différentes façons d'utiliser le système
"""

import pandas as pd
from datetime import datetime
from src.bom_status_updater import BOMStatusUpdater

def create_sample_data():
    """
    Crée des données d'exemple pour tester le système
    """
    print("🔧 Création des fichiers d'exemple...")
    
    # Créer un Master BOM d'exemple
    master_data = {
        'Part Number': ['PN001', 'PN002', 'PN003', 'PN004', 'PN005', 'PN006'],
        'Projet': ['PROJ_A', 'PROJ_A', 'PROJ_B', 'PROJ_B', 'PROJ_C', 'PROJ_C'],
        'Statut': ['D', 'X', 'D', '0', 'X', 'D'],
        'Description': ['Résistance 10K', 'Condensateur 100nF', 'LED Rouge', 'Connecteur USB', 'Microcontrôleur', 'Écran LCD'],
        'Fournisseur': ['Fournisseur A', 'Fournisseur B', 'Fournisseur A', 'Fournisseur C', 'Fournisseur D', 'Fournisseur B'],
        'Prix': [0.10, 0.05, 0.25, 2.50, 15.00, 25.00]
    }
    
    master_df = pd.DataFrame(master_data)
    master_df.to_excel('master_bom_example.xlsx', index=False)
    print("✅ Master BOM d'exemple créé: master_bom_example.xlsx")
    
    # Créer un fichier nettoyé d'exemple
    cleaned_data = {
        'Part Number': ['PN001', 'PN002', 'PN007', 'PN003', 'PN008', '', 'PN004'],
        'Projet': ['PROJ_A', 'PROJ_A', 'PROJ_D', 'PROJ_B', 'PROJ_E', 'PROJ_F', 'PROJ_B'],
        'Quantité': [10, 5, 2, 8, 3, 1, 4],
        'Notes': ['', '', '', '', '', '', '']
    }
    
    cleaned_df = pd.DataFrame(cleaned_data)
    cleaned_df.to_excel('fichier_nettoye_example.xlsx', index=False)
    print("✅ Fichier nettoyé d'exemple créé: fichier_nettoye_example.xlsx")
    
    return 'fichier_nettoye_example.xlsx', 'master_bom_example.xlsx'

def example_basic_usage():
    """
    Exemple d'utilisation basique
    """
    print("\n" + "="*50)
    print("📋 EXEMPLE 1: UTILISATION BASIQUE")
    print("="*50)
    
    # Créer les fichiers d'exemple
    cleaned_file, master_file = create_sample_data()
    
    # Initialiser l'updater
    updater = BOMStatusUpdater(master_file)
    
    # Exécuter le processus complet
    results = updater.run_complete_process(cleaned_file)
    
    if results['success']:
        print("\n✅ Traitement réussi!")
        print(f"📄 Fichier mis à jour: {results['updated_file']}")
        print(f"📊 Rapport: {results['report_file']}")
        print(f"📈 Lignes traitées: {results['total_processed']}")
        print(f"🔧 Modifications: {results['total_modified']}")
        
        # Afficher statistiques
        print("\n📊 Statistiques par statut:")
        for status, count in results['stats'].items():
            print(f"  {status}: {count}")
    else:
        print(f"❌ Erreur: {results['error']}")

def example_step_by_step():
    """
    Exemple d'utilisation étape par étape
    """
    print("\n" + "="*50)
    print("📋 EXEMPLE 2: UTILISATION ÉTAPE PAR ÉTAPE")
    print("="*50)
    
    # Créer les fichiers d'exemple
    cleaned_file, master_file = create_sample_data()
    
    # Initialiser l'updater
    updater = BOMStatusUpdater(master_file)
    
    # Étape 1: Charger les fichiers
    print("\n🔄 Étape 1: Chargement des fichiers")
    if updater.load_master_bom():
        print("✅ Master BOM chargé")
    else:
        print("❌ Erreur chargement Master BOM")
        return
    
    if updater.load_cleaned_file(cleaned_file):
        print("✅ Fichier nettoyé chargé")
    else:
        print("❌ Erreur chargement fichier nettoyé")
        return
    
    # Étape 2: Traiter le fichier
    print("\n🔄 Étape 2: Traitement des données")
    results = updater.process_file()
    
    if results:
        print("✅ Traitement terminé")
        print(f"📊 Statistiques: {results['stats']}")
    else:
        print("❌ Erreur lors du traitement")
        return
    
    # Étape 3: Sauvegarder
    print("\n🔄 Étape 3: Sauvegarde")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Sauvegarder fichier mis à jour
    updated_file = updater.save_updated_file(results['updated_df'], f'update_step_by_step_{timestamp}.xlsx')
    if updated_file:
        print(f"✅ Fichier mis à jour sauvegardé: {updated_file}")
    
    # Sauvegarder Master BOM
    master_saved = updater.save_master_bom()
    if master_saved:
        print(f"✅ Master BOM sauvegardé: {master_saved}")
    
    # Générer rapport
    report_file = updater.generate_report('xlsx', f'rapport_step_by_step_{timestamp}.xlsx')
    if report_file:
        print(f"✅ Rapport généré: {report_file}")

def example_custom_configuration():
    """
    Exemple avec configuration personnalisée
    """
    print("\n" + "="*50)
    print("📋 EXEMPLE 3: CONFIGURATION PERSONNALISÉE")
    print("="*50)
    
    # Créer un updater avec configuration personnalisée
    updater = BOMStatusUpdater()
    
    # Personnaliser les noms de colonnes possibles
    updater.possible_pn_names.extend(['Numéro_Pièce', 'Code_Article'])
    updater.possible_project_names.extend(['Nom_Projet', 'Code_Projet'])
    updater.possible_status_names.extend(['État_Pièce', 'Statut_Article'])
    
    print("✅ Configuration personnalisée appliquée")
    print(f"📋 Noms PN possibles: {updater.possible_pn_names}")
    print(f"📋 Noms Projet possibles: {updater.possible_project_names}")
    print(f"📋 Noms Statut possibles: {updater.possible_status_names}")

def demonstrate_status_logic():
    """
    Démontre la logique de traitement des statuts
    """
    print("\n" + "="*50)
    print("📋 DÉMONSTRATION DE LA LOGIQUE DES STATUTS")
    print("="*50)
    
    print("""
🔄 LOGIQUE DE TRAITEMENT:

📌 Statut D (Désactivé):
   ➤ Action: Aucune action
   ➤ Résultat: Ligne ignorée

📌 Statut X (À remplacer):
   ➤ Action: Mettre à jour le statut vers D dans Master BOM
   ➤ Résultat: Commentaire ajouté + ligne surlignée en jaune

📌 Statut 0 (Doublon/Ambigu):
   ➤ Action: Ajouter nouvelle ligne à la fin
   ➤ Résultat: Ligne avec PN et Projet, champs vides + commentaire + surlignage rouge

📌 Statut NaN (Introuvable/Erreur):
   ➤ Si erreur de format: Ligne vide + commentaire d'erreur + surlignage orange
   ➤ Si PN introuvable: Ligne avec PN et Projet + commentaire + surlignage orange

📤 FICHIERS GÉNÉRÉS:
   ✅ Update_[date].xlsx: Fichier principal mis à jour avec formatage
   ✅ Master BOM mis à jour avec nouveaux statuts
   ✅ Rapport_Modifications_[date].xlsx: Rapport détaillé des actions
""")

def main():
    """
    Fonction principale des exemples
    """
    print("🚀 EXEMPLES D'UTILISATION DU SYSTÈME BOM STATUS UPDATER")
    print("=" * 60)
    
    try:
        # Démonstration de la logique
        demonstrate_status_logic()
        
        # Exemple basique
        example_basic_usage()
        
        # Exemple étape par étape
        example_step_by_step()
        
        # Exemple configuration personnalisée
        example_custom_configuration()
        
        print("\n" + "="*60)
        print("✅ TOUS LES EXEMPLES TERMINÉS AVEC SUCCÈS!")
        print("📁 Vérifiez les fichiers générés dans le répertoire courant")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'exécution des exemples: {str(e)}")

if __name__ == "__main__":
    main()
