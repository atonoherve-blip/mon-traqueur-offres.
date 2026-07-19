import sqlite3
import scrapers

def initialiser_base_donnees():
    """Crée la table SQL si elle n'existe pas encore sur la machine."""
    conn = sqlite3.connect("opportunites_pme.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS offres (
            id_unique TEXT PRIMARY KEY,
            pays TEXT,
            type_opportunite TEXT,
            secteur TEXT,
            produit TEXT,
            montant TEXT,
            region TEXT,
            date_publication TEXT,
            date_limite TEXT,
            defis_contraintes TEXT,
            lien TEXT
        )
    """)
    conn.commit()
    conn.close()

def executer_routine_quotidienne(code_pays):
    """Démarre le bon scraper selon le pays choisi et enregistre les offres qualifiées."""
    initialiser_base_donnees()
    
    # Sélection automatique du robot selon le choix de l'utilisateur
    if code_pays == "CA":
        robot = scrapers.RobotCanada("CA")
    else:
        return 0 # Pays non géré pour le moment
        
    # 1. Extraction des offres brutes
    offres_brutes = robot.extraire_opportunites()
    
    conn = sqlite3.connect("opportunites_pme.db")
    cursor = conn.cursor()
    
    compteur_nouvelles_offres = 0
    
    # 2. Analyse et sauvegarde de chaque offre
    for offre in offres_brutes:
        # Éviter les doublons en vérifiant si l'ID existe déjà
        cursor.execute("SELECT 1 FROM offres WHERE id_unique = ?", (offre["id_unique"],))
        if cursor.fetchone():
            continue
            
        # Qualification automatique par l'intelligence des mots-clés
        offre_qualifiee = scrapers.analyser_et_qualifier_pme(offre)
        
        # Insertion finale dans la base de données
        cursor.execute("""
            INSERT INTO offres VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            offre_qualifiee["id_unique"], offre_qualifiee["pays"], offre_qualifiee["type_opportunite"],
            offre_qualifiee["secteur"], offre_qualifiee["produit"], offre_qualifiee["montant"],
            offre_qualifiee["region"], offre_qualifiee["date_publication"], offre_qualifiee["date_limite"],
            offre_qualifiee["defis_contraintes"], offre_qualifiee["lien"]
        ))
        compteur_nouvelles_offres += 1
        
    conn.commit()
    conn.close()
    return compteur_nouvelles_offres
