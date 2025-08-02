"""
Exceptions personnalisées pour le système BOM
"""

class BOMException(Exception):
    """Exception de base pour le système BOM"""
    pass

class FileProcessingError(BOMException):
    """Erreur lors du traitement de fichier"""
    pass

class ValidationError(BOMException):
    """Erreur de validation des données"""
    pass

class ConfigurationError(BOMException):
    """Erreur de configuration"""
    pass

class MasterBOMError(BOMException):
    """Erreur liée au Master BOM"""
    pass

class StatusUpdateError(BOMException):
    """Erreur lors de la mise à jour des statuts"""
    pass
