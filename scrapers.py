import requests
import re
from bs4 import BeautifulSoup

class CollecteurMarches:
    """Classe parente configurable pour l'international."""
    def __init__(self, paye, region):
        self.paye = paye
        self.region = region

class CollecteurCanada(CollecteurMarches):
    """Collecteur officiel pour Approvisionnement Canada (SPAC)."""
    def collecter_federal(self, mot_cle=""):
        url = "https://canada.ca"
        params = {"keywords": mot_cle} if mot_cle else {}
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }
        
        offres = []
        try:
            reception = requests.get(url, params=params, headers=headers, timeout=10)
            if reception.status_code == 200:
                donnees = reception.json()
                liste_avis = donnees.get("results", [])
                
                # Si les résultats sont sous forme de dictionnaire au lieu de liste
                if isinstance(liste_avis, dict):
                    liste_avis = liste_avis.values()
                    
                for infos in liste_avis:
                    id_avis = infos.get("tenderId", "inconnu")
                    offres.append({
                        "ID": id_avis, "Paye": self.paye, "Region": self.region,
                        "Source": "Approvisionnement Canada (SPAC)",
                        "Titre": infos.get("tenderTitle_fr", infos.get("tenderTitle_en", "Sans titre")),
                        "Description": infos.get("description", ""),
                        "DateCloture": infos.get("closingDate", "Inconnue"),
                        "Lien": f"https://canada.ca{id_avis}",
                        "Budget": 0, "JoursRestants": 14, "NombreAmendements": 0
                    })
        except Exception as e:
            print(f"Erreur d'accès à l'API Fédérale : {e}")
        return offres

# --- MOTEUR D'INTELLIGENCE & FILTRAGE ---

MOTS_EXCLUS = ["Déneigement", "Gardiennage", "Asphaltage", "Restauration", "Nettoyage"]

def filtrer_et_noter(offre):
    """Analyse l'offre, applique les exclusions et calcule le score de match de 0 à 100."""
    texte_complet = f"{offre['Titre']} {offre['Description']}".lower()
    
    if any(mot.lower() in texte_complet for mot in MOTS_EXCLUS):
        return None
        
    score_pme = 0
    score_urgence = 0
    score_concurrence = 0
    
    if 0 < offre['Budget'] <= 100000:
        score_pme = 40
    elif "faible valeur" in texte_complet or "simplifié" in texte_complet:
        score_pme = 30
        
    if offre['JoursRestants'] <= 7 or any(u in texte_complet for u in ["urgent", "immédiat", "critique"]):
        score_urgence = 30
        
    if offre['NombreAmendements'] >= 2 or "prolongation" in texte_complet or "extension" in texte_complet:
        score_concurrence = 30
        
    return score_pme + score_urgence + score_concurrence
