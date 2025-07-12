"""
Validierungsfunktionen für SEOlyzer
"""

import re
from urllib.parse import urlparse
from typing import Tuple, Optional

def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validiert eine URL
    
    Args:
        url: Die zu validierende URL
        
    Returns:
        Tuple mit (is_valid, error_message)
    """
    if not url:
        return False, "URL darf nicht leer sein"
    
    # Füge http:// hinzu, falls kein Protokoll angegeben ist
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return False, "Ungültige URL-Struktur"
        
        # Überprüfe auf gültige Domain
        if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$', result.netloc):
            return False, "Ungültige Domain"
        
        return True, None
        
    except Exception as e:
        return False, f"Fehler bei der URL-Validierung: {str(e)}"

def validate_depth(depth: int) -> Tuple[bool, Optional[str]]:
    """
    Validiert die Crawling-Tiefe
    
    Args:
        depth: Die zu validierende Tiefe
        
    Returns:
        Tuple mit (is_valid, error_message)
    """
    if not isinstance(depth, int):
        return False, "Tiefe muss eine ganze Zahl sein"
    
    if depth < 1:
        return False, "Tiefe muss mindestens 1 sein"
    
    if depth > 10:
        return False, "Tiefe darf maximal 10 sein"
    
    return True, None

def validate_output_path(path: str) -> Tuple[bool, Optional[str]]:
    """
    Validiert einen Ausgabepfad
    
    Args:
        path: Der zu validierende Pfad
        
    Returns:
        Tuple mit (is_valid, error_message)
    """
    if not path:
        return False, "Ausgabepfad darf nicht leer sein"
    
    # Überprüfe auf gültige Dateiendung
    if not path.endswith('.json'):
        return False, "Ausgabedatei muss die Endung .json haben"
    
    # Überprüfe auf gültige Zeichen im Pfad
    if not re.match(r'^[a-zA-Z0-9_\-./]+$', path):
        return False, "Ungültige Zeichen im Ausgabepfad"
    
    return True, None 