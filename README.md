# 🔧 Système de Mise à Jour BOM avec Gestion des Statuts

Un système Python complet pour comparer et mettre à jour des fichiers Excel BOM (Bill of Materials) avec gestion intelligente des statuts.

## 🎯 Fonctionnalités Principales

### 🔄 Logique de Traitement par Statut

Le système traite chaque ligne selon le statut trouvé via XLOOKUP dans le Master BOM :

- **Statut D** : Aucune action (ligne ignorée)
- **Statut X** : Mise à jour vers D + commentaire + surlignage jaune
- **Statut 0** : Nouvelle ligne pour doublon + surlignage rouge
- **Statut NaN** : Nouvelle ligne selon le type d'erreur + surlignage orange

### 📊 Fonctionnalités Avancées

- ✅ Recherche XLOOKUP basée sur Part Number + Projet
- ✅ Mise à jour automatique du Master BOM
- ✅ Formatage Excel avec couleurs selon les statuts
- ✅ Génération de rapports détaillés (CSV/Excel)
- ✅ Gestion des erreurs et validation des données
- ✅ Interface en ligne de commande et mode interactif
- ✅ Configuration personnalisable
- ✅ Logging complet des opérations

## 📁 Structure du Projet

```
Test/
├── src/
│   ├── bom_status_updater.py      # Classe principale
│   ├── bom_comparator.py          # Comparateur existant
│   ├── master_bom_processor.py    # Processeur Master BOM
│   ├── new_bom_processor.py       # Processeur nouvelles BOM
│   ├── excel_cleaner.py           # Nettoyeur Excel
│   ├── file_processor.py          # Traitement fichiers
│   ├── ui_components.py           # Composants UI
│   └── master_bom_manager.py      # Gestionnaire Master BOM
├── config/
│   ├── bom_config.py              # Configuration système
│   └── settings.py                # Paramètres généraux
├── bom_update_main.py             # Script principal
├── example_usage.py               # Exemples d'utilisation
├── app.py                         # Interface Streamlit
├── requirements.txt               # Dépendances
└── README.md                      # Documentation
```

## 🚀 Installation

1. **Cloner le projet** :
```bash
git clone <repository-url>
cd Test
```

2. **Installer les dépendances** :
```bash
pip install -r requirements.txt
```

3. **Vérifier l'installation** :
```bash
python bom_update_main.py --help-detailed
```

## 💻 Utilisation

### Mode Interactif (Recommandé)

```bash
python bom_update_main.py
```

Le script vous guidera pour :
- Sélectionner le fichier Excel nettoyé
- Choisir le Master BOM
- Définir le répertoire de sortie

### Mode Ligne de Commande

```bash
python bom_update_main.py --cleaned-file "fichier_nettoye.xlsx" --master-bom "master_bom.xlsx" --output-dir "output/"
```

### Interface Web Streamlit

```bash
streamlit run app.py
```

### Utilisation Programmatique

```python
from src.bom_status_updater import BOMStatusUpdater

# Initialiser l'updater
updater = BOMStatusUpdater("master_bom.xlsx")

# Exécuter le processus complet
results = updater.run_complete_process("fichier_nettoye.xlsx")

if results['success']:
    print(f"Fichier mis à jour: {results['updated_file']}")
    print(f"Rapport: {results['report_file']}")
```

## 📋 Format des Fichiers

### Fichier Excel Nettoyé (Entrée)

Colonnes requises :
- **Part Number** (ou PN, Réf Composant, etc.)
- **Projet** (optionnel mais recommandé)

Colonnes optionnelles :
- Quantité, Description, Fournisseur, Prix, etc.

### Master BOM (Référence)

Colonnes requises :
- **Part Number**
- **Statut** (D, X, 0, ou autre)
- **Projet** (optionnel)

## 🎨 Fichiers Générés

### 1. Fichier Mis à Jour (`Update_YYYYMMDD_HHMMSS.xlsx`)

- Fichier original avec modifications appliquées
- Formatage couleur selon les statuts
- Commentaires dans la colonne Notes
- Nouvelles lignes ajoutées à la fin

### 2. Master BOM Mis à Jour

- Statuts X changés en D
- Sauvegardé automatiquement

### 3. Rapport de Modifications (`Rapport_Modifications_YYYYMMDD_HHMMSS.xlsx`)

Contient :
- **Feuille Modifications** : Détail de chaque action
- **Feuille Statistiques** : Résumé par statut
- **Feuille Résumé** : Vue d'ensemble

## ⚙️ Configuration

Le fichier `config/bom_config.py` permet de personnaliser :

```python
# Noms de colonnes possibles
COLUMN_NAMES = {
    'part_number': ['Part Number', 'PN', 'Réf Composant'],
    'project': ['Projet', 'Project', 'Programme'],
    # ...
}

# Couleurs Excel
EXCEL_COLORS = {
    'red': 'FFCCCC',      # Doublons
    'orange': 'FFE6CC',   # Erreurs
    'yellow': 'FFFFCC',   # Mises à jour
}
```

## 📊 Exemples d'Utilisation

Exécuter les exemples :

```bash
python example_usage.py
```

Cela génère :
- Fichiers d'exemple
- Démonstrations des différents modes
- Tests de toutes les fonctionnalités

## 🔍 Détail de la Logique de Traitement

### Processus XLOOKUP

1. **Recherche par Part Number** dans le Master BOM
2. **Affinage par Projet** si disponible
3. **Récupération du Statut** correspondant
4. **Application de l'action** selon le statut

### Actions par Statut

| Statut | Action | Résultat |
|--------|--------|----------|
| D | Aucune | Ligne ignorée |
| X | Mise à jour Master BOM | Statut → D, commentaire ajouté |
| 0 | Nouvelle ligne | Copie PN+Projet, champs vides |
| NaN | Analyse erreur | Ligne selon type d'erreur |

## 🛠️ Développement

### Structure des Classes

- **BOMStatusUpdater** : Classe principale
- **BOMComparator** : Comparaison existante
- **MasterBOMProcessor** : Traitement Master BOM
- **NewBOMProcessor** : Traitement nouvelles BOM

### Tests

```bash
python -m pytest tests/
```

### Contribution

1. Fork le projet
2. Créer une branche feature
3. Commiter les changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## 📝 Changelog

### Version 1.0.0
- ✅ Implémentation complète du système de statuts
- ✅ Interface ligne de commande
- ✅ Génération de rapports
- ✅ Configuration personnalisable
- ✅ Formatage Excel avancé

## 🤝 Support

Pour toute question ou problème :
1. Consulter la documentation
2. Exécuter les exemples
3. Vérifier les logs
4. Ouvrir une issue

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
