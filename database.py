import sqlite3
import os
from datetime import datetime

DB_NAME = "gov_procure.db"

def initialiser_bdd():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Table des appels d'offres
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appels_offres (
            id TEXT PRIMARY KEY,
            pays TEXT,
            region TEXT,
            source TEXT,
            titre TEXT,
            description TEXT,
            date_cloture TEXT,
            lien TEXT,
            score INTEGER,
            statut_sms TEXT,
            date_decouverte TEXT
        )
    ''')
    
    # Table des utilisateurs et abonnements
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS utilisateurs (
            telephone TEXT PRIMARY KEY,
            nom TEXT,
            type_abonnement TEXT, -- 'Gratuit' ou 'Premium'
            date_inscription TEXT
        )
    ''')
    
    # Insertion d'un utilisateur de test Premium
    try:
        cursor.execute("INSERT INTO utilisateurs VALUES (?, ?, ?, ?)", 
                       ("+16135550123", "Demo User", "Premium", datetime.now().strftime("%Y-%m-%d")))
    except sqlite3.IntegrityError:
        pass
        
    conn.commit()
    conn.close()

def offre_existe_deja(id_offre):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM appels_offres WHERE id = ?", (id_offre,))
    existe = cursor.fetchone() is not None
    conn.close()
    return existe

def sauvegarder_offre(offre, score, statut_sms):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO appels_offres VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            offre['ID'], offre.get('Pays', 'Canada'), offre.get('Region', 'Ontario'),
            offre['Source'], offre['Titre'], offre.get('Description', ''),
            offre['DateCloture'], offre['Lien'], score, statut_sms, 
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()

def obtenir_utilisateurs_premium():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT telephone FROM utilisateurs WHERE type_abonnement = 'Premium'")
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users
