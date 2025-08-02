#!/usr/bin/env python3
"""
Script principal pour la mise à jour des BOM avec gestion des statuts
Utilise la classe BOMStatusUpdater pour traiter les fichiers Excel
"""

import os
import sys
import argparse
from datetime import datetime
from src.bom_status_updater import BOMStatusUpdater

def print_banner():
    """Affiche la bannière du programme"""
    print("=" * 60)
    print("🔧 SYSTÈME DE MISE À JOUR BOM AVEC GESTION DES STATUTS")
    print("=" * 60)
    print("Traite les fichiers Excel selon les statuts D, X, 0, NaN")
    print("Auteur: Assistant IA")
    print("Date:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 60)

def print_help():
    """Affiche l'aide détaillée"""
    help_text = """
📋 UTILISATION:

1. Mode interactif (recommandé):
   python bom_update_main.py

2. Mode ligne de commande:
   python bom_update_main.py --cleaned-file "fichier_nettoye.xlsx" --master-bom "master_bom.xlsx"

📂 FICHIERS REQUIS:
   - Fichier Excel nettoyé (contenant PN et Projet)
   - Master BOM (fichier de référence avec statuts)

🔄 LOGIQUE DE TRAITEMENT:
   - Statut D: Aucune action
   - Statut X: Mise à jour vers D + commentaire
   - Statut 0: Nouvelle ligne pour doublon
   - Statut NaN: Nouvelle ligne selon le type d'erreur

📤 FICHIERS GÉNÉRÉS:
   - Update_[date].xlsx: Fichier mis à jour avec formatage
   - Master BOM mis à jour
   - Rapport_Modifications_[date].xlsx: Rapport détaillé
"""
    print(help_text)

def get_user_input():
    """Récupère les chemins des fichiers via interface interactive"""
    print("\n📁 SÉLECTION DES FICHIERS")
    print("-" * 30)
    
    # Fichier nettoyé
    while True:
        cleaned_file = input("Chemin vers le fichier Excel nettoyé: ").strip()
        if os.path.exists(cleaned_file):
            break
        print("❌ Fichier non trouvé. Veuillez réessayer.")
    
    # Master BOM
    while True:
        master_bom = input("Chemin vers le Master BOM (ou ENTER pour 'master_bom_cleaned.xlsx'): ").strip()
        if not master_bom:
            master_bom = "master_bom_cleaned.xlsx"
        
        if os.path.exists(master_bom):
            break
        print("❌ Fichier non trouvé. Veuillez réessayer.")
    
    # Répertoire de sortie
    output_dir = input("Répertoire de sortie (ou ENTER pour le répertoire courant): ").strip()
    if not output_dir:
        output_dir = "."
    
    return cleaned_file, master_bom, output_dir

def display_stats(stats):
    """Affiche les statistiques de traitement"""
    print("\n📊 STATISTIQUES DE TRAITEMENT")
    print("-" * 35)
    print(f"Statut D (aucune action):     {stats.get('D', 0):>3}")
    print(f"Statut X (mis à jour):        {stats.get('X', 0):>3}")
    print(f"Statut 0 (doublon):          {stats.get('0', 0):>3}")
    print(f"Statut NaN (erreur/inconnu): {stats.get('NaN', 0):>3}")
    print("-" * 35)
    print(f"TOTAL TRAITÉ:                {sum(stats.values()):>3}")

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Mise à jour BOM avec gestion des statuts")
    parser.add_argument("--cleaned-file", help="Chemin vers le fichier Excel nettoyé")
    parser.add_argument("--master-bom", help="Chemin vers le Master BOM")
    parser.add_argument("--output-dir", help="Répertoire de sortie")
    parser.add_argument("--help-detailed", action="store_true", help="Affiche l'aide détaillée")
    
    args = parser.parse_args()
    
    # Afficher bannière
    print_banner()
    
    # Aide détaillée
    if args.help_detailed:
        print_help()
        return
    
    try:
        # Récupérer les paramètres
        if args.cleaned_file and args.master_bom:
            # Mode ligne de commande
            cleaned_file = args.cleaned_file
            master_bom = args.master_bom
            output_dir = args.output_dir or "."
        else:
            # Mode interactif
            cleaned_file, master_bom, output_dir = get_user_input()
        
        print(f"\n🔄 TRAITEMENT EN COURS...")
        print(f"Fichier nettoyé: {cleaned_file}")
        print(f"Master BOM: {master_bom}")
        print(f"Sortie: {output_dir}")
        
        # Créer l'updater
        updater = BOMStatusUpdater(master_bom)
        
        # Exécuter le processus complet
        results = updater.run_complete_process(cleaned_file, output_dir)
        
        if results['success']:
            print("\n✅ MISE À JOUR TERMINÉE AVEC SUCCÈS!")
            print("-" * 40)
            print(f"📄 Fichier mis à jour: {results['updated_file']}")
            print(f"📋 Master BOM: {results['master_bom_updated']}")
            print(f"📊 Rapport: {results['report_file']}")
            
            # Afficher statistiques
            display_stats(results['stats'])
            
            print(f"\n📈 RÉSUMÉ:")
            print(f"Total lignes traitées: {results['total_processed']}")
            print(f"Total modifications: {results['total_modified']}")
            
        else:
            print(f"\n❌ ERREUR: {results['error']}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Traitement interrompu par l'utilisateur")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ ERREUR INATTENDUE: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
