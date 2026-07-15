import streamlit as st
import sqlite3
import pandas as pd
from database import DB_NAME, initialiser_bdd
from cron_worker import executer_routine_quotidienne

st.set_page_config(page_title="GovProcure AI Tracker", layout="wide")
initialiser_bdd()

# --- ESPACE ABONNEMENT USER ---
st.sidebar.title("👤 Mon Compte SaaS")
statut_user = st.sidebar.radio("Niveau d'accès :", ["Gratuit", "Premium (Alerte SMS active)"])

st.title("🇨🇦 GovProcure AI Tracker - Ottawa & International")
st.caption("Analyse en temps réel des marchés à faible concurrence et budgets optimisés.")

# --- EN-TÊTE PUBLICITAIRE (Monétisation Compte Gratuit) ---
if statut_user == "Gratuit":
    st.markdown("""
    <div style="background-color:#fff3cd;padding:10px;border-radius:5px;border-left:5px solid #ffc107;margin-bottom:20px;">
        <strong>📢 Publicité :</strong> Vous cherchez un partenaire de cautionnement pour vos soumissions ? 
        Contactez <a href='#'>OttawaBonds Inc.</a> | <em>Passez au forfait Premium pour supprimer les publicités.</em>
    </div>
    """)

# --- BOUTON DE RECHARGE MANUELLE ---
if st.button("🔄 Forcer la mise à jour (Scan en direct des portails publics)"):
    with st.spinner("Analyse de CanadaBuys et MERX en cours..."):
        executer_routine_quotidienne()
    st.success("Base de données synchronisée !")

# --- FILTRES DE VISUALISATION ---
st.markdown("### 📊 Opportunités Détectées")
conn = sqlite3.connect(DB_NAME)
df = pd.read_sql_query("SELECT * FROM appels_offres ORDER BY score DESC", conn)
conn.close()

if df.empty:
    st.info("Aucun contrat en base de données. Cliquez sur le bouton de mise à jour ci-dessus.")
else:
    col1, col2 = st.columns(2)
    with col1:
        score_min = st.slider("Score de Match minimum", 0, 100, 30)
    with col2:
        source_filter = st.multiselect("Filtrer par guichet :", df['source'].unique(), default=df['source'].unique())
        
    df_filtre = df[(df['score'] >= score_min) & (df['source'].isin(source_filter))]
    
    # Affichage personnalisé selon l'abonnement
    if statut_user == "Gratuit":
        # Masquer les colonnes à forte valeur ajoutée aux utilisateurs non payants
        df_visuel = df_filtre.drop(columns=['id', 'statut_sms', 'description'])
        st.dataframe(df_visuel, use_container_width=True)
        st.warning("🔒 Les descriptions complètes et l'accès aux liens directs de soumission sont réservés aux membres Premium.")
    else:
        st.dataframe(df_filtre, use_container_width=True)

# --- BAS DE PAGE PUBLICITAIRE ---
if statut_user == "Gratuit":
    st.markdown("<br><hr><center><small>Espace Publicitaire de Google AdSense disponible pour affichage de bannières</small></center>", unsafe_url_allowed=True)
