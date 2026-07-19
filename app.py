import streamlit as st
import pandas as pd
import sqlite3
from cron_worker import executer_routine_quotidienne

# Configuration de la page
st.set_page_config(page_title="GovProcure PME Tracker", layout="wide")

st.title("🎯 GovProcure PME Tracker")
st.subheader("Détecteur intelligent de marchés publics pour les petites et moyennes entreprises")

# 1. BARRE DE SÉLECTION DU PAYS (Évolutive)
pays_disponibles = {
    "Canada 🇨🇦": {"code": "CA", "source": "AchatsCanada (Fédéral)"},
    "France 🇫🇷 (Bientôt disponible)": {"code": "FR", "source": "BOAMP"},
    "États-Unis 🇺🇸 (Bientôt disponible)": {"code": "US", "source": "SAM.gov"}
}

choix_pays = st.selectbox("🌐 Sélectionnez le pays cible :", list(pays_disponibles.keys()))
infos_pays = pays_disponibles[choix_pays]

# Bouton de synchronisation en direct
if st.button("🔄 Synchroniser et scanner les derniers appels d'offres en direct"):
    with st.spinner(f"Connexion au serveur de {choix_pays} et analyse IA des critères PME..."):
        try:
            nb_offres = executer_routine_quotidienne(infos_pays["code"])
            st.success(f"Analyse terminée ! {nb_offres} nouvelles opportunités qualifiées trouvées pour les PME.")
        except Exception as e:
            st.error(f"Erreur lors de la synchronisation : {e}")

# 2. FILTRES SPÉCIFIQUES POUR PME
st.markdown("### 🔍 Filtrer par type d'opportunité PME")
col1, col2, col3, col4, col5 = st.columns(5)

with col1: opt_faible = st.checkbox("📉 Faible valeur / Simplifié")
with col2: opt_tech = st.checkbox("🚀 Innovation / Subvention")
with col3: opt_div = st.checkbox("🤝 Diversité / Inclusion")
with col4: opt_sous = st.checkbox("🏗️ Sous-traitance")
with col5: opt_urgent = st.checkbox("⚡ Contrats Urgents")

# Connexion à la base de données pour afficher le tableau
conn = sqlite3.connect("opportunites_pme.db")

try:
    # Lecture des données correspondant au pays sélectionné
    query = "SELECT * FROM offres WHERE pays = ?"
    df = pd.read_sql_query(query, conn, params=(infos_pays["code"],))
    
    if not df.empty:
        # Application des filtres cochés par l'utilisateur
        conditions = []
        if opt_faible: conditions.append(df['type_opportunite'] == "Faible valeur / Simplifié")
        if opt_tech: conditions.append(df['type_opportunite'] == "Innovation / Subvention")
        if opt_div: conditions.append(df['type_opportunite'] == "Diversité / Inclusion")
        if opt_sous: conditions.append(df['type_opportunite'] == "Sous-traitance")
        if opt_urgent: conditions.append(df['type_opportunite'] == "Contrat Urgent")
        
        if conditions:
            df_filtre = df[pd.concat(conditions, axis=1).any(axis=1)]
        else:
            df_filtre = df # Si rien n'est coché, on montre tout
            
        if not df_filtre.empty:
            # Nettoyage de l'affichage pour l'utilisateur
            df_affichage = df_filtre[[
                "type_opportunite", "secteur", "produit", "montant", 
                "region", "date_publication", "date_limite", "defis_contraintes", "lien"
            ]].copy()
            
            df_affichage.columns = [
                "Type d'opportunité", "Secteur d'activité", "Produit à livrer", 
                "Montant estimé", "Région", "Date Publication", "Date Limite", "Défis & Contraintes", "Lien officiel"
            ]
            
            # Affichage du tableau interactif
            st.dataframe(df_affichage, use_container_width=True, hide_index=True)
        else:
            st.info("Aucun contrat ne correspond à cette combinaison de filtres pour le moment.")
    else:
        st.info(f"La base de données pour {choix_pays} est vide. Cliquez sur le bouton de synchronisation ci-dessus pour lancer le premier scan.")
except Exception:
    st.info("Base de données en attente d'initialisation. Cliquez sur le bouton de synchronisation ci-dessus.")

conn.close()
