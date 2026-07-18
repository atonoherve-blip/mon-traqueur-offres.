import os
from database import initialiser_bdd, offre_existe_deja, sauvegarder_offre, obtenir_utilisateurs_premium
from scrapers import CollecteurCanada, filtrer_et_noter
from twilio.rest import Client

def envoyer_sms_twilio(telephone, titre, partition, privilege):
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "VOTRE_SID_PROD")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "VOTRE_TOKEN_PROD")
    numero_twilio = os.environ.get("TWILIO_NUMBER", "+12345678901")
    
    if "VOTRE_" in account_sid:
        return False  # Mode déconnecté pour les tests locaux
        
    client = Client(account_sid, auth_token)
    try:
        client.messages.create(
            body=f"[GovProcure AI] Match Exceptionnel ({partition}/100) \nContrat : {titre[:40]}...",
            from_=numero_twilio,
            to=telephone
        )
        return True
    except Exception:
        return False

def executer_routine_quotidienne():
    initialiser_bdd()
    collecteur = CollecteurCanada(paye="Canada", region="Ontario")
    
    # Récupération des opportunités
    offres_brutes = collecteur.collecter_federal(mot_cle="informatique")
    primes = obtenir_utilisateurs_premium()
    
    for offre in offres_brutes:
        if offre_existe_deja(offre['ID']):
            continue
            
        partition = filtrer_et_noter(offre)
        if partition is None:
            continue  # offre exclue par secteur
            
        # Sauvegarde en base de données
        sauveg_ok = sauvegarder_offre(
            offre['ID'], offre['Titre'], offre['Description'],
            offre['DateCloture'], offre['Lien'], partition,
            offre['Budget'], offre['JoursRestants'], offre['NombreAmendements'],
            offre['Source'], offre['Paye'], offre['Region']
        )
        
        # Envoi d'alertes SMS si score élevé
        if sauveg_ok and partition >= 70:
            for u in primes:
                envoyer_sms_twilio(u['telephone'], offre['Titre'], partition, u['privilege'])
