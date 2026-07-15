import os
from database import initialiser_bdd, offre_existe_deja, sauvegarder_offre, obtenir_utilisateurs_premium
from scrapers import CollecteurCanada, filtrer_et_noter
from twilio.rest import Client

def envoyer_sms_twilio(telephone, titre, score, lien):
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID', 'VOTRE_SID_PROD')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN', 'VOTRE_TOKEN_PROD')
    numero_twilio = os.environ.get('TWILIO_NUMBER', '+12345678901')
    
    if 'VOTRE_' in account_sid: 
        return False # Mode déconnecté pour les tests locaux
        
    client = Client(account_sid, auth_token)
    try:
        client.messages.create(
            body=f"🚨 [GovProcure AI] Match Exceptionnel ({score}/100) !\nContrat: {titre[:40]}...\nLien: {lien}",
            from_=numero_twilio, to=telephone
        )
        return True
    except Exception:
        return False

def executer_routine_quotidienne():
    initialiser_bdd()
    collecteur = CollecteurCanada(pays="Canada", region="Ontario")
    
    # Récupération des opportunités
    offres_brutes = collecteur.collecter_federal(mot_cle="informatique")
    premiums = obtenir_utilisateurs_premium()
    
    for offre in offres_brutes:
        if offre_existe_deja(offre['ID']):
            continue
            
        score = filtrer_et_noter(offre)
        if score is None: 
            continue # Offre exclue par secteur
            
        statut_sms = "NON_ÉLIGIBLE"
        # Alerte SMS immédiate uniquement si Score élevé ET utilisateur Premium disponible
        if score >= 75:
            statut_sms = "ÉCHEC_ENVOI"
            for tel in premiums:
                if envoyer_sms_twilio(tel, offre['Titre'], score, offre['Lien']):
                    statut_sms = "ENVOYÉ"
                    
        sauvegarder_offre(offre, score, statut_sms)

if __name__ == "__main__":
    print("🚀 Démarrage du scan quotidien des marchés publics...")
    executer_routine_quotidienne()
    print("✅ Traitement et sauvegardes SQLite terminés avec succès.")
