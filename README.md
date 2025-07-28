# 🧹 Nettoyeur de fichiers BOM Excel

Interface web simple pour nettoyer les fichiers Excel BOM en supprimant les caractères spéciaux des Part Numbers.

## 🚀 Installation

```bash
pip install -r requirements.txt
```

## 📁 Structure du projet

```
├── app.py                 # Point d'entrée principal
├── src/
│   ├── __init__.py
│   ├── file_processor.py  # Traitement des fichiers
│   ├── excel_cleaner.py   # Logique de nettoyage
│   └── ui_components.py   # Composants interface
├── config/
│   └── settings.py        # Configuration
├── requirements.txt
└── README.md
```

## 🎯 Fonctionnalités

- Upload de fichiers Excel (.xlsx)
- Détection automatique de la colonne Part Number
- Nettoyage des caractères spéciaux
- Suppression des doublons et lignes vides
- Aperçu et téléchargement du fichier nettoyé

## 🏃‍♂️ Lancement

```bash
streamlit run app.py
```