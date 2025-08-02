#!/usr/bin/env python3
"""
Script de test pour vérifier le bon fonctionnement du système BOM
Crée des données de test et vérifie toutes les fonctionnalités
"""

import os
import pandas as pd
import tempfile
import shutil
from datetime import datetime
from src.bom_status_updater import BOMStatusUpdater

def create_test_master_bom():
    """
    Crée un Master BOM de test avec différents statuts
    """
    data = {
        'Part Number': [
            'PN001', 'PN002', 'PN003', 'PN004', 'PN005', 
            'PN006', 'PN007', 'PN008', 'PN009', 'PN010'
        ],
        'Projet': [
            'PROJ_A', 'PROJ_A', 'PROJ_B', 'PROJ_B', 'PROJ_C',
            'PROJ_C', 'PROJ_D', 'PROJ_D', 'PROJ_E', 'PROJ_E'
        ],
        'Statut': [
            'D', 'X', 'D', '0', 'X',
            'D', 'X', 'D', '0', 'D'
        ],
        'Description': [
            'Résistance 10K', 'Condensateur 100nF', 'LED Rouge', 'Connecteur USB', 'Microcontrôleur',
            'Écran LCD', 'Capteur Temp', 'Alimentation', 'Boîtier', 'Câble'
        ],
        'Fournisseur': [
            'Fournisseur A', 'Fournisseur B', 'Fournisseur A', 'Fournisseur C', 'Fournisseur D',
            'Fournisseur B', 'Fournisseur A', 'Fournisseur C', 'Fournisseur D', 'Fournisseur A'
        ],
        'Prix': [0.10, 0.05, 0.25, 2.50, 15.00, 25.00, 8.50, 12.00, 5.00, 3.50]
    }
    
    df = pd.DataFrame(data)
    return df

def create_test_cleaned_file():
    """
    Crée un fichier nettoyé de test avec différents cas
    """
    data = {
        'Part Number': [
            'PN001',    # Statut D - aucune action
            'PN002',    # Statut X - mise à jour
            'PN011',    # NaN - PN introuvable
            'PN004',    # Statut 0 - doublon
            'PN005',    # Statut X - mise à jour
            '',         # NaN - erreur format
            'PN012',    # NaN - PN introuvable
            'PN006',    # Statut D - aucune action
            'PN013'     # NaN - PN introuvable
        ],
        'Projet': [
            'PROJ_A', 'PROJ_A', 'PROJ_F', 'PROJ_B', 'PROJ_C',
            'PROJ_G', 'PROJ_H', 'PROJ_C', 'PROJ_I'
        ],
        'Quantité': [10, 5, 2, 8, 3, 1, 4, 6, 2],
        'Notes': [''] * 9
    }
    
    df = pd.DataFrame(data)
    return df

def run_comprehensive_test():
    """
    Exécute un test complet du système
    """
    print("🧪 DÉMARRAGE DES TESTS COMPLETS")
    print("=" * 50)
    
    # Créer un répertoire temporaire pour les tests
    test_dir = tempfile.mkdtemp(prefix="bom_test_")
    print(f"📁 Répertoire de test: {test_dir}")
    
    try:
        # 1. Créer les fichiers de test
        print("\n🔧 Création des fichiers de test...")
        
        master_df = create_test_master_bom()
        master_path = os.path.join(test_dir, "master_bom_test.xlsx")
        master_df.to_excel(master_path, index=False)
        print(f"✅ Master BOM créé: {master_path}")
        
        cleaned_df = create_test_cleaned_file()
        cleaned_path = os.path.join(test_dir, "cleaned_file_test.xlsx")
        cleaned_df.to_excel(cleaned_path, index=False)
        print(f"✅ Fichier nettoyé créé: {cleaned_path}")
        
        # 2. Initialiser l'updater
        print("\n🔄 Initialisation du système...")
        updater = BOMStatusUpdater(master_path)
        
        # 3. Test de chargement
        print("\n📂 Test de chargement des fichiers...")
        if updater.load_master_bom():
            print("✅ Master BOM chargé avec succès")
        else:
            print("❌ Échec chargement Master BOM")
            return False
        
        if updater.load_cleaned_file(cleaned_path):
            print("✅ Fichier nettoyé chargé avec succès")
        else:
            print("❌ Échec chargement fichier nettoyé")
            return False
        
        # 4. Test de traitement
        print("\n⚙️ Test de traitement...")
        results = updater.process_file()
        
        if results:
            print("✅ Traitement terminé avec succès")
            print(f"📊 Statistiques: {results['stats']}")
            
            # Vérifier les statistiques attendues
            expected_stats = {'D': 2, 'X': 2, '0': 1, 'NaN': 4}
            actual_stats = results['stats']
            
            print("\n🔍 Vérification des statistiques...")
            for status, expected_count in expected_stats.items():
                actual_count = actual_stats.get(status, 0)
                if actual_count == expected_count:
                    print(f"✅ Statut {status}: {actual_count} (attendu: {expected_count})")
                else:
                    print(f"❌ Statut {status}: {actual_count} (attendu: {expected_count})")
        else:
            print("❌ Échec du traitement")
            return False
        
        # 5. Test de sauvegarde
        print("\n💾 Test de sauvegarde...")
        
        # Sauvegarder fichier mis à jour
        updated_path = os.path.join(test_dir, "updated_test.xlsx")
        saved_file = updater.save_updated_file(results['updated_df'], updated_path)
        
        if saved_file and os.path.exists(saved_file):
            print(f"✅ Fichier mis à jour sauvegardé: {saved_file}")
        else:
            print("❌ Échec sauvegarde fichier mis à jour")
            return False
        
        # Sauvegarder Master BOM
        master_saved = updater.save_master_bom()
        if master_saved:
            print(f"✅ Master BOM sauvegardé: {master_saved}")
        else:
            print("❌ Échec sauvegarde Master BOM")
            return False
        
        # 6. Test de génération de rapport
        print("\n📊 Test de génération de rapport...")
        report_path = os.path.join(test_dir, "rapport_test.xlsx")
        report_file = updater.generate_report('xlsx', report_path)
        
        if report_file and os.path.exists(report_file):
            print(f"✅ Rapport généré: {report_file}")
        else:
            print("❌ Échec génération rapport")
            return False
        
        # 7. Test du processus complet
        print("\n🚀 Test du processus complet...")
        complete_results = updater.run_complete_process(cleaned_path, test_dir)
        
        if complete_results['success']:
            print("✅ Processus complet réussi")
            print(f"📄 Fichier final: {complete_results['updated_file']}")
            print(f"📊 Rapport final: {complete_results['report_file']}")
            print(f"📈 Total traité: {complete_results['total_processed']}")
            print(f"🔧 Total modifié: {complete_results['total_modified']}")
        else:
            print(f"❌ Échec processus complet: {complete_results['error']}")
            return False
        
        # 8. Vérification des fichiers générés
        print("\n🔍 Vérification des fichiers générés...")
        
        files_to_check = [
            complete_results['updated_file'],
            complete_results['report_file']
        ]
        
        for file_path in files_to_check:
            if file_path and os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"✅ {os.path.basename(file_path)}: {file_size} bytes")
            else:
                print(f"❌ Fichier manquant: {file_path}")
                return False
        
        print("\n" + "="*50)
        print("🎉 TOUS LES TESTS RÉUSSIS!")
        print("="*50)
        print(f"📁 Fichiers de test disponibles dans: {test_dir}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR LORS DES TESTS: {str(e)}")
        return False
    
    finally:
        # Nettoyer le répertoire de test (optionnel)
        # shutil.rmtree(test_dir)
        pass

def run_quick_test():
    """
    Exécute un test rapide des fonctionnalités de base
    """
    print("⚡ TEST RAPIDE")
    print("-" * 20)
    
    try:
        # Test d'importation
        from src.bom_status_updater import BOMStatusUpdater
        print("✅ Import BOMStatusUpdater réussi")
        
        # Test d'initialisation
        updater = BOMStatusUpdater()
        print("✅ Initialisation réussie")
        
        # Test des méthodes utilitaires
        test_columns = ['Part Number', 'PN', 'Référence']
        found_col = updater._find_column(pd.DataFrame(columns=test_columns), updater.possible_pn_names)
        if found_col:
            print(f"✅ Détection colonne: {found_col}")
        else:
            print("❌ Échec détection colonne")
            return False
        
        print("✅ Test rapide réussi")
        return True
        
    except Exception as e:
        print(f"❌ Erreur test rapide: {str(e)}")
        return False

def main():
    """
    Fonction principale des tests
    """
    print("🧪 SYSTÈME DE TESTS BOM STATUS UPDATER")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test rapide
    if not run_quick_test():
        print("\n❌ Test rapide échoué - arrêt des tests")
        return
    
    print("\n")
    
    # Test complet
    if run_comprehensive_test():
        print("\n🎯 RÉSULTAT FINAL: TOUS LES TESTS RÉUSSIS")
    else:
        print("\n💥 RÉSULTAT FINAL: ÉCHEC DES TESTS")

if __name__ == "__main__":
    main()
