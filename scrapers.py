import requests
from bs4 import BeautifulSoup

class CollecteurMarches:
    def __init__(self, paye, region):
        self.paye = paye
        self.region = region

class CollecteurCanada(CollecteurMarches):
    def collecter_federal(self, mot_cle=""):
        # Utilisation du flux Atom officiel d'AchatsCanada (Garantit l'absence de blocage)
        url = "https://canada.ca"
        params = {"keywords": mot_cle} if mot_cle else {}
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        
        offres = []
        try:
            reception = requests.get(url, params=params, headers=headers, timeout=15)
            if reception.status_code == 200:
                soup = BeautifulSoup(reception.content, "xml")
                entries = soup.find_all("entry")
                
                for entry in entries:
                    id_avis = entry.find("id").text.split("/")[-1] if entry.find("id") else "inconnu"
                    titre = entry.find("title").text if entry.find("title") else "Sans titre"
                    description = entry.find("summary").text if entry.find("summary") else ""
                    lien = entry.find("link")["href"] if entry.find("link") else f"https://canada.ca{id_avis}"
                    
                    offres.append({
                        "ID": id_avis, "Paye": self.paye, "Region": self.region,
                        "Source": "Approvisionnement Canada (SPAC)",
                        "Titre": titre,
                        "Description": description,
                        "DateCloture": "Voir sur le site",
                        "Lien": lien,
                        "Budget": 0, "JoursRestants": 14, "NombreAmendements": 0
                    })
        except Exception as e:
            print(f"Erreur lors du scan du flux : {e}")
        return offres

# --- MOTEUR D'INTELLIGENCE & FILTRAGE ---

MOTS_EXCLUS = ["Déneigement", "Gardiennage", "Asphaltage", "Restauration", "Nettoyage"]

def filtrer_et_noter(offre):
    texte_complet = f"{offre['Titre']} {offre['Description']}".lower()
    if any(mot.lower() in texte_complet for mot in MOTS_EXCLUS):
        return None
    return 50  # Score par défaut pour les tests
