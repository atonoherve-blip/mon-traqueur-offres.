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
        offres = []
        try:
            reception = requests.get(url, params=params, timeout=10)
            if reception.status_code == 200:
                for id_avis, infos in reception.json().get("results", {}).items():
                    offres.append({
                        "ID": id_avis, "Paye": self.paye, "Region": self.region,
                        "Source": "Approvisionnement Canada (SPAC)",
                        "Titre": infos.get("tenderTitle_fr", "Sans titre"),
                        "Description": infos.get("description", ""),
                        "DateCloture": infos.get("closingDate", "Inconnue"),
                        "Lien": f"https://canada.ca{id_avis}",
                        "Budget": 0, "JoursRestants": 14, "NombreAmendements": 0
                    })
        except Exception as e:
            print(f"Erreur d'accès à l'API Fédérale : {e}")
        return offres


# --- MOTEUR D'INTELLIGENCE & FILTRAGE ---

MOTS_EXCLUS = ["déneigement", "gardiennage", "asphaltage", "restauration", "nettoyage"]

def filtrer_et_noter(offre):
    """Analyse l'offre, applique les exclusions et calcule le score de match de 0 à 100."""
    texte_complet = f"{offre['Titre']} {offre['Description']}".lower()
    
    # 1. Vérification des exclusions sectorielles
    if any(mot in texte_complet for mot in MOTS_EXCLUS):
        return None # Élimination automatique
        
    score_pme = 0
    score_urgence = 0
    score_concurrence = 0
    
    # Évaluation PME / Budget faible
    if offre['Budget'] > 0 and offre['Budget'] <= 100000:
        score_pme = 40
    elif "faible valeur" in texte_complet or "simplifié" in texte_complet:
        score_pme = 30
        
    # Évaluation Urgence
    if offre['JoursRestants'] <= 7 or any(u in texte_complet for u in ["urgent", "immédiat", "critical"]):
        score_urgence = 30
        
    # Évaluation Faible Concurrence (offres prolongées ou amendées)
    if offre['NombreAmendements'] >= 2 or "prolongation" in texte_complet or "extension" in texte_complet:
        score_concurrence = 30
        
    return min(score_pme + score_urgence + score_concurrence, 100)
