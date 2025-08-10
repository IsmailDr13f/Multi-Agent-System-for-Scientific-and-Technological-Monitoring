import streamlit as st
from streamlit_elements import mui, html, elements
from pymongo import MongoClient
from datetime import datetime
from pymongo import MongoClient
import sys
import os
from bson import ObjectId
from datetime import datetime
import pandas as pd


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def get_saved_news_for_user(user_email, mongo_uri="mongodb://localhost:27017/"):
    """
    Récupère les actualités sauvegardées pour un utilisateur donné
    """
    try:
        # Connexion à MongoDB
        client = MongoClient(mongo_uri)
        
        # Base de données utilisateurs
        users_db = client.get_database("vst_db")  # Remplacez par le nom de votre DB utilisateurs
        users_collection = users_db.get_collection("Users")
        
        # Base de données des actualités
        newsfeed_db = client.get_database("newsfeed_db")
        news_collection = newsfeed_db.get_collection("news")
        
        # Récupérer l'utilisateur
        user = users_collection.find_one({"email": user_email})
        
        if not user or "saved_news" not in user:
            return []
        
        # Récupérer les IDs des actualités sauvegardées
        saved_news_ids = [ObjectId(news_id["$oid"]) if isinstance(news_id, dict) else ObjectId(news_id) 
                         for news_id in user["saved_news"]]
        
        # Récupérer les actualités correspondantes
        saved_news = list(news_collection.find({"_id": {"$in": saved_news_ids}}))
        
        client.close()
        return saved_news
        
    except Exception as e:
        st.error(f"Erreur lors de la récupération des actualités : {str(e)}")
        return []


def remove_from_saved_news(user_email, news_id, mongo_uri="mongodb://localhost:27017/"):
    """
    Supprime une actualité des favoris d'un utilisateur
    """
    try:
        client = MongoClient(mongo_uri)
        users_db = client.get_database("vst_db")
        users_collection = users_db.get_collection("Users")

        # Retirer l'ID de la liste saved_news
        result = users_collection.update_one(
            {"email": user_email},
            {"$pull": {"saved_news": ObjectId(news_id)}}
        )
        
        client.close()
        return result.modified_count > 0
        
    except Exception as e:
        st.error(f"Erreur lors de la suppression : {str(e)}")
        return False



def create_news_card(news_item, user_email):
    """
    Crée une carte d'actualité avec st.form
    """
    with st.form(key=f"news_card_{news_item['_id']}"):
        # Conteneur principal avec colonnes
        col_content, col_image = st.columns([3, 1])
        
        with col_content:
            # Titre
            st.markdown(f"### {news_item.get('title', 'Titre non disponible')}")
            
            # Description/Summary
            description = news_item.get('summary', news_item.get('description', 'Aucune description disponible'))
            if len(description) > 400:
                description = description[:400] + "..."
            st.write(description)
            print(news_item)    
            # Informations supplémentaires
            info_col1, info_col2 = st.columns(2)
            
            with info_col1:
                if 'source' in news_item:
                    st.caption(f"📰 **Source:** {news_item['source']}")
                if 'topic' in news_item:
                    st.caption(f"✍️ **Topic:** {news_item['topic']}")

            with info_col2:
                if 'Publication_date' in news_item:
                    date_str = news_item['Publication_date']
                    if isinstance(date_str, datetime):
                        formatted_date = date_str.strftime("%d/%m/%Y")
                    else:
                        formatted_date = str(date_str)
                    st.caption(f"📅 **Date:** {formatted_date}")
                
                if 'link' in news_item:
                    #st.caption(f"🏷️ **Catégorie:** {news_item['category']}")
                    st.caption(f"🔗 **Link:** {news_item['link']}")

        with col_image:
            # Image de l'actualité
            if 'image_url' in news_item and news_item['image_url']:
                try:
                    st.image(news_item['image_url'], use_container_width=True, caption="")
                except:
                    st.image("https://via.placeholder.com/150x100/cccccc/666666?text=Image", use_container_width=True)
            else:
                # Image placeholder si pas d'image
                st.image("https://via.placeholder.com/150x100/cccccc/666666?text=No+Image", use_container_width=True)
        
        # Boutons en bas de la carte
        st.markdown("---")
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            unsave_btn = st.form_submit_button("🗑️ Unsave", type="secondary", use_container_width=True)
        
        with btn_col2:
            chat_btn = st.form_submit_button("💬 Chat", type="primary", use_container_width=True, disabled=False, help="Discuss this content")
        
        # Gestion des actions
        if unsave_btn:
            if remove_from_saved_news(user_email, news_item['_id']):
                st.success("✅ Actualité supprimée des favoris!")
                st.rerun()
            else:
                st.error("❌ Erreur lors de la suppression")
        
        if chat_btn:
            # Vider d'abord l'ancien contenu
            if 'card_content' in st.session_state:
                del st.session_state.card_content
            
            # Puis définir le nouveau contenu
            st.session_state.card_content = news_item
            #st.rerun()  # Force la réexécution avant le switch
            st.switch_page("chat/agents_ui.py")
            

def get_mongodb_connection():
    """Initialise la connexion MongoDB"""
    try:
        MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        client = MongoClient(MONGODB_URI)
        db = client.get_database("newsfeed_db")
        return db
    except Exception as e:
        st.error(f"Erreur de connexion MongoDB: {e}")
        return None


def get_saved_news_for_user(user_email):
    """
    Récupère toutes les actualités sauvegardées d'un utilisateur
    triées par date de sauvegarde (plus récent en premier)
    """
    try:
        db = get_mongodb_connection()
        if db is None:
            return []
        
        news_col = db.news
        users_col = db.client["vst_db"].Users
        
        # Récupérer l'utilisateur et ses news sauvegardées
        user = users_col.find_one({"email": user_email})
        if not user or "saved_news" not in user:
            return []
        
        saved_news_ids = user["saved_news"]
        if not saved_news_ids:
            return []
        
        # Récupérer les actualités avec tri par date de sauvegarde (décroissant)
        saved_news = list(news_col.find(
            {"_id": {"$in": saved_news_ids}}
        ).sort("saved_at", -1))  # -1 pour ordre décroissant (plus récent en premier)
        
        return saved_news
        
    except Exception as e:
        st.error(f"Erreur lors de la récupération des actualités sauvegardées: {e}")
        return []


def display_saved_news_cards(user_email):
    """
    Affiche toutes les cartes d'actualités sauvegardées
    triées par date de sauvegarde (plus récent en premier)
    """
    
    # Récupérer les actualités sauvegardées (déjà triées)
    saved_news = get_saved_news_for_user(user_email)
    
    if not saved_news:
        st.info("🔖 No saved news for the moment")
        st.write("""Explore news and save the ones you're interested in!""")
        return
    
    # Afficher le nombre total
    st.success(f"📊 {len(saved_news)} saved New(s)")
    
    # Afficher la date de la dernière sauvegarde
    if saved_news:
        latest_save_date = saved_news[0].get("saved_at")
        if latest_save_date:
            formatted_date = latest_save_date.strftime("%d/%m/%Y à %H:%M")
            st.caption(f"📅 Dernière sauvegarde: {formatted_date}")
    
    # Espacement
    st.markdown("---")
    
    # Créer une carte pour chaque actualité
    for i, news_item in enumerate(saved_news):
        # Conteneur pour chaque carte avec bordure
        with st.container():
            # Afficher la date de sauvegarde pour chaque carte (optionnel)
            save_date = news_item.get("saved_at")
            if save_date:
                formatted_save_date = save_date.strftime("%d/%m/%Y à %H:%M")
                st.caption(f"💾 Sauvegardé le: {formatted_save_date}")
            
            create_news_card(news_item, user_email)
            
            # Espacement entre les cartes
            if i < len(saved_news) - 1:
                st.markdown("<br>", unsafe_allow_html=True)

# Version alternative avec style CSS personnalisé
def display_saved_news_cards_styled(user_email):
    """
    Version avec style CSS personnalisé pour de meilleures cartes
    """
    # CSS pour styliser les cartes
    st.markdown("""
    <style>
    .news-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        background-color: #fafafa;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .news-title {
        color: #2c3e50;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .news-meta {
        color: #7f8c8d;
        font-size: 12px;
        margin: 5px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.subheader("📰 Actualités Sauvegardées")
    
    saved_news = get_saved_news_for_user(user_email)
    
    if not saved_news:
        st.info("🔖 Aucune actualité sauvegardée pour le moment.")
        return
    
    st.success(f"📊 {len(saved_news)} actualité(s) sauvegardée(s)")
    st.markdown("---")
    
    for news_item in saved_news:
        with st.container():
            st.markdown('<div class="news-card">', unsafe_allow_html=True)
            create_news_card(news_item, user_email)
            st.markdown('</div>', unsafe_allow_html=True)

# --- Page functions ---
# --- MongoDB connection ---
client = MongoClient("mongodb://localhost:27017")  # ou votre URI
db = client["vst_db"]
users_col = db["Users"]

# --- User email (à définir dynamiquement selon ton auth) ---
email = st.session_state.email


instr = 'Search for news, research papers, Videos and more !.'
# --- Row 2: Input and Search Button ---
with st.form('search_form',border=False):
    # Create two columns; adjust the ratio to your liking
    col1, col2 = st.columns([3,1]) 

    # Use the first column for text input
    with col1:
        search_input=st.text_input(
            instr,
            value=instr,
            placeholder=instr,
            label_visibility='collapsed')
    with col2:
        if st.form_submit_button("Search"):
            print("Search button clicked")
            #st.success(f"Searched for: {search_input}")

# --- Row 3: Three Select Boxes ---
with st.expander("Filter Content"):
    with st.form('filter_form',border=True):
        col3, col4, col5 = st.columns(3)
        with col3:
            poste = st.selectbox("Times", ["All Times","Today Posts", "Last week Posts", "last month Posts"])
        with col4:
            category = st.selectbox("Categories", ["All Categories","Research Papers", "Blogs", "Videos"])
        with col5:
            popular_post = st.selectbox("Popularity", ["All Posts","High Cited Articles", "Most viewed Videos", "Most shared Blogs"])
        if st.form_submit_button("Apply Filters"):
            #st.success(f"Filters applied: {poste}, {category}, {popular_post}")
            print(f"Filters applied: {poste}, {category}, {popular_post}")

st.markdown("---")

import numpy as np

tab1, tab2 = st.tabs(["Saved News", "Discussed News"])



tab1.subheader("Saved News")
with tab1:
        # Utiliser la fonction pour afficher les cartes
        display_saved_news_cards(st.session_state.email)


tab2.subheader("Discussed News")
tab2.write("No discussed news articles and research papers yet.")

