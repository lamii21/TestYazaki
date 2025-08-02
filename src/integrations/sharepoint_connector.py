"""
Connecteur SharePoint pour le système BOM
Permet de lire/écrire des fichiers directement depuis SharePoint
"""

import os
from typing import Optional, List, Dict
import pandas as pd
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
import io

class SharePointConnector:
    """
    Connecteur pour intégrer SharePoint avec le système BOM
    """
    
    def __init__(self, site_url: str, username: str = None, password: str = None):
        """
        Initialise le connecteur SharePoint
        
        Args:
            site_url (str): URL du site SharePoint
            username (str): Nom d'utilisateur (optionnel si auth intégrée)
            password (str): Mot de passe (optionnel si auth intégrée)
        """
        self.site_url = site_url
        self.username = username
        self.password = password
        self.ctx = None
        self._authenticate()
    
    def _authenticate(self):
        """Authentification SharePoint"""
        try:
            if self.username and self.password:
                # Authentification par nom d'utilisateur/mot de passe
                auth_ctx = AuthenticationContext(self.site_url)
                auth_ctx.acquire_token_for_user(self.username, self.password)
                self.ctx = ClientContext(self.site_url, auth_ctx)
            else:
                # Authentification intégrée Windows
                self.ctx = ClientContext(self.site_url)
            
            # Test de connexion
            web = self.ctx.web
            self.ctx.load(web)
            self.ctx.execute_query()
            
        except Exception as e:
            raise ConnectionError(f"Échec authentification SharePoint: {str(e)}")
    
    def list_files(self, folder_path: str, file_extension: str = ".xlsx") -> List[Dict]:
        """
        Liste les fichiers dans un dossier SharePoint
        
        Args:
            folder_path (str): Chemin du dossier
            file_extension (str): Extension des fichiers à lister
            
        Returns:
            List[Dict]: Liste des fichiers avec métadonnées
        """
        try:
            folder = self.ctx.web.get_folder_by_server_relative_url(folder_path)
            files = folder.files
            self.ctx.load(files)
            self.ctx.execute_query()
            
            file_list = []
            for file in files:
                if file.name.endswith(file_extension):
                    file_list.append({
                        'name': file.name,
                        'url': file.server_relative_url,
                        'size': file.length,
                        'modified': file.time_last_modified,
                        'created': file.time_created
                    })
            
            return file_list
            
        except Exception as e:
            raise FileNotFoundError(f"Erreur listage fichiers: {str(e)}")
    
    def download_file(self, file_url: str) -> pd.DataFrame:
        """
        Télécharge un fichier Excel depuis SharePoint
        
        Args:
            file_url (str): URL du fichier SharePoint
            
        Returns:
            pd.DataFrame: Contenu du fichier Excel
        """
        try:
            file_obj = File.open_binary(self.ctx, file_url)
            
            # Lire le contenu en mémoire
            file_content = io.BytesIO(file_obj.content)
            
            # Convertir en DataFrame
            df = pd.read_excel(file_content)
            
            return df
            
        except Exception as e:
            raise FileNotFoundError(f"Erreur téléchargement fichier: {str(e)}")
    
    def upload_file(self, local_file_path: str, sharepoint_folder: str, 
                   filename: str = None) -> str:
        """
        Upload un fichier vers SharePoint
        
        Args:
            local_file_path (str): Chemin du fichier local
            sharepoint_folder (str): Dossier de destination SharePoint
            filename (str): Nom du fichier (optionnel)
            
        Returns:
            str: URL du fichier uploadé
        """
        try:
            if not filename:
                filename = os.path.basename(local_file_path)
            
            with open(local_file_path, 'rb') as file_content:
                target_folder = self.ctx.web.get_folder_by_server_relative_url(sharepoint_folder)
                uploaded_file = target_folder.upload_file(filename, file_content.read())
                self.ctx.execute_query()
                
                return uploaded_file.serverRelativeUrl
                
        except Exception as e:
            raise ConnectionError(f"Erreur upload fichier: {str(e)}")
    
    def upload_dataframe(self, df: pd.DataFrame, sharepoint_folder: str, 
                        filename: str) -> str:
        """
        Upload un DataFrame directement vers SharePoint
        
        Args:
            df (pd.DataFrame): DataFrame à uploader
            sharepoint_folder (str): Dossier de destination
            filename (str): Nom du fichier
            
        Returns:
            str: URL du fichier uploadé
        """
        try:
            # Convertir DataFrame en Excel en mémoire
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            buffer.seek(0)
            
            # Upload vers SharePoint
            target_folder = self.ctx.web.get_folder_by_server_relative_url(sharepoint_folder)
            uploaded_file = target_folder.upload_file(filename, buffer.getvalue())
            self.ctx.execute_query()
            
            return uploaded_file.serverRelativeUrl
            
        except Exception as e:
            raise ConnectionError(f"Erreur upload DataFrame: {str(e)}")
    
    def create_folder(self, folder_path: str) -> bool:
        """
        Crée un dossier dans SharePoint
        
        Args:
            folder_path (str): Chemin du dossier à créer
            
        Returns:
            bool: True si création réussie
        """
        try:
            parent_folder = os.path.dirname(folder_path)
            folder_name = os.path.basename(folder_path)
            
            parent = self.ctx.web.get_folder_by_server_relative_url(parent_folder)
            new_folder = parent.folders.add(folder_name)
            self.ctx.execute_query()
            
            return True
            
        except Exception as e:
            print(f"Erreur création dossier: {str(e)}")
            return False
    
    def file_exists(self, file_url: str) -> bool:
        """
        Vérifie si un fichier existe dans SharePoint
        
        Args:
            file_url (str): URL du fichier
            
        Returns:
            bool: True si le fichier existe
        """
        try:
            file_obj = self.ctx.web.get_file_by_server_relative_url(file_url)
            self.ctx.load(file_obj)
            self.ctx.execute_query()
            return True
        except:
            return False
    
    def get_file_metadata(self, file_url: str) -> Dict:
        """
        Récupère les métadonnées d'un fichier
        
        Args:
            file_url (str): URL du fichier
            
        Returns:
            Dict: Métadonnées du fichier
        """
        try:
            file_obj = self.ctx.web.get_file_by_server_relative_url(file_url)
            self.ctx.load(file_obj)
            self.ctx.execute_query()
            
            return {
                'name': file_obj.name,
                'size': file_obj.length,
                'modified': file_obj.time_last_modified,
                'created': file_obj.time_created,
                'url': file_obj.server_relative_url,
                'version': file_obj.major_version
            }
            
        except Exception as e:
            raise FileNotFoundError(f"Erreur métadonnées: {str(e)}")

# Exemple d'utilisation
def example_sharepoint_integration():
    """
    Exemple d'intégration SharePoint avec le système BOM
    """
    # Configuration
    site_url = "https://votre-tenant.sharepoint.com/sites/votre-site"
    folder_path = "/sites/votre-site/Shared Documents/BOM"
    
    try:
        # Connexion
        sp = SharePointConnector(site_url)
        
        # Lister les fichiers BOM
        files = sp.list_files(folder_path, ".xlsx")
        print(f"Fichiers trouvés: {len(files)}")
        
        # Télécharger le Master BOM
        if files:
            master_bom_url = files[0]['url']  # Premier fichier
            master_df = sp.download_file(master_bom_url)
            print(f"Master BOM chargé: {len(master_df)} lignes")
            
            # Traitement avec le système BOM...
            # processed_df = process_bom(master_df)
            
            # Upload du fichier traité
            # result_url = sp.upload_dataframe(
            #     processed_df, 
            #     folder_path, 
            #     f"BOM_Updated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            # )
            # print(f"Fichier uploadé: {result_url}")
        
    except Exception as e:
        print(f"Erreur: {str(e)}")

if __name__ == "__main__":
    example_sharepoint_integration()
