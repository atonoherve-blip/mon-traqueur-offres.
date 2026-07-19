import requests
from bs4 import BeautifulSoup
import re

class RobotScraperBase:
    """Classe mère pour encadrer le développement de futurs pays."""
    def __init__(self, code_pays):
        self.code_pays = code_pays

class RobotCanada(RobotScraperBase):
    """Moteur d'extraction pour le gouvernement du Canada (AchatsCanada)."""
    def extraire_opportunites(self):
        # Utilisation du flux Atom officiel pour garantir l'absence de blocage pare-feu
        url = "https://canada.ca"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        
        liste_offres = []
        try:
            reponse = requests.get(url, headers=headers, timeout=15)
            if reponse.status_code == 200:
                soup = BeautifulSoup(reponse.content, "xml")
                articles = soup.find_all("entry")
                
                for article in articles:
                    id_offre = article.find("id").text.split("/")[-1] if article.find("id") else "inconnu"
                    titre = article.find("title").text if article.find("title") else "Sans titre"
                    description = article.find("summary").text if article.find("summary") else ""
                    lien = article.find("link")["href"] if article.find("link") else f"https://canada.ca{id_offre}"
                    date_pub = article.find("published").text[:10] if article.find("published") else "Inconnue"
                    
                    liste_offres.append({
                        "id_unique": id_offre,
                        "pays": "CA",
                        "titre": titre,
                        "description": description,
                        "lien": lien,
                        "date_publication": date_pub
                    })
        except Exception as e:
            print(f"Erreur d'extraction Canada : {e}")
        return liste_offres

def analyser_et_qualifier_pme(offre):
    """
    Moteur IA d'analyse de texte. Classe l'offre selon les critères demandés
    et extrait le secteur, produit, région, contraintes et montants.
    """
    texte_analyse = f"{offre['titre']} {offre['description']}".lower()
    
    # 1. Détermination du type d'opportunité PME
    type_opp = "Marché Général"
    if any(m in texte_analyse for m in ["faible valeur", "simplifié", "proforma", "direct"]):
        type_opp = "Faible valeur / Simplifié"
    elif any(m in texte_analyse for m in ["innovation", "subvention", "recherche", "développer", "tester", "idéation"]):
        type_opp = "Innovation / Subvention"
    elif any(m in texte_analyse for m in ["diversité", "autochtone", "minorité", "inclusion", "féminin"]):
        type_opp = "Diversité / Inclusion"
    elif any(m in texte_analyse for m in ["sous-traitance", "partenaire", "fournisseur secondaire"]):
        type_opp = "Sous-traitance"
    elif any(m in texte_analyse for m in ["urgent", "immédiat", "urgence", "critique", "sinistre"]):
        type_opp = "Contrat Urgent"
    else:
        # Si aucun mot clé critique n'est trouvé, on l'oriente en faible valeur par sécurité pour les PME
        type_opp = "Faible valeur / Simplifié"

    # 2. Extraction du Secteur d'activité
    secteur = "Services professionnels"
    if any(m in texte_analyse for m in ["logiciel", "informatique", "ordinateur", "cloud", "serveur", "développement"]):
        secteur = "Technologies (TI)"
    elif any(m in texte_analyse for m in ["construction", "bâtiment", "rénovation", "pont", "route", "travaux"]):
        secteur = "Construction / Infrastructures"
    elif any(m in texte_analyse for m in ["médical", "santé", "hôpital", "clinique", "médicament"]):
        secteur = "Santé / Médical"

    # 3. Extraction du type de produit à livrer
    produit = "Livrable de service ou matériel"
    match_produit = re.search(r"(pour la fourniture de|achat de|prestation de)\s+([^,.]+)", texte_analyse)
    if match_produit:
        produit = match_produit.group(2).strip()[:50]
    else:
        produit = offre['titre'][:50] + "..."

    # 4. Estimation du montant
    montant = "Non spécifié (À valider sur le portail)"
    if "faible valeur" in texte_analyse:
        montant = "< 40 000 $ CAD"
    elif "accord de libre-échange" in texte_analyse:
        montant = "> 100 000 $ CAD"

    # 5. Extraction de la Région
    region = "Canada (National)"
    regions_canada = ["Québec", "Ontario", "Alberta", "Colombie-Britannique", "Manitoba", "Nouvelle-Écosse", "Montréal", "Ottawa", "Toronto"]
    for r in regions_canada:
        if r.lower() in texte_analyse:
            region = r
            break

    # 6. Extraction des défis et contraintes
    defis = "Délais de soumission standards"
    if "sécurité" in texte_analyse:
        defis = "🔒 Cote de sécurité requise"
    elif "urgence" in texte_analyse:
        defis = "⚠️ Délai d'exécution très court"
    elif "certification" in texte_analyse:
        defis = "📜 Certifications techniques obligatoires"

    return {
        "id_unique": offre["id_unique"],
        "pays": offre["pays"],
        "type_opportunite": type_opp,
        "secteur": secteur,
        "produit": produit,
        "montant": montant,
        "region": region,
        "date_publication": offre["date_publication"],
        "date_limite": "Voir lien officiel",
        "defis_contraintes": defis,
        "lien": offre["lien"]
    }
