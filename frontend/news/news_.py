import streamlit as st
from streamlit_elements import mui, html, elements
from pymongo import MongoClient
from datetime import datetime
from pymongo import MongoClient
import random
import sys
import os
import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from bloc_2.SearchWorkflow import SearchWorkflow
from bloc_2.SmartLinkAnalysisWorkflow import SmartLinkAnalysisWorkflow,StructuredResponse

from bloc_2.AgentsResearchTeam import (
    academic_paper_researcher_,
    engine_search_agent_,
    Video_agent_,
    social_media_researcher, 
    chat_agent   
)
from news.refresh import refresh_news_

# --- Page functions ---
# --- MongoDB connection ---
client = MongoClient("mongodb://localhost:27017")  # ou votre URI
db = client["vst_db"]
users_col = db["Users"]

# --- User email (à définir dynamiquement selon ton auth) ---
email = st.session_state.email
#print(f"User email: {email}")
# --- Load preferences from DB ---
def load_preferences():
    user = users_col.find_one({"email": st.session_state.email})
    if user and "preferences" in user:
        return user["preferences"]
    return []

# --- Update preferences in DB ---
def save_preferences_to_db(prefs):
    users_col.update_one(
        {"email": st.session_state.email},
        {"$set": {"preferences": prefs}},
        upsert=True
    )

# --- Dialogues avec @st.dialog ---
@st.dialog("➕ Add a new preference")
def add_preference():
    new_pref = st.text_input("Enter new preference:")
    if st.button("Add"):
        if new_pref and new_pref not in st.session_state.preferences:
            st.session_state.preferences.append(new_pref)
            save_preferences_to_db(st.session_state.preferences)
            st.success(f"'{new_pref}' added.")
            refresh_news_([new_pref])
            st.rerun()
        elif new_pref in st.session_state.preferences:
            st.warning("Preference already exists.")
        else:
            st.error("Please enter a valid preference.")

@st.dialog("❌ Delete preferences")
def delete_preferences():
    to_delete = st.multiselect("Select preferences to delete:", st.session_state.preferences)
    if st.button("Delete Selected"):
        for item in to_delete:
            st.session_state.preferences.remove(item)
        save_preferences_to_db(st.session_state.preferences)
        st.success("Selected preferences removed.")
        st.rerun()
# --- page Content ---

st.markdown("---")
# --- Row 1: Multiselect + Manual Add + Refresh ---
preferences_display = [":material/add:", "All Preferences", *st.session_state.preferences, ":material/delete:"]
selection = st.pills("Search Preferences", preferences_display, selection_mode="single", default="All Preferences", label_visibility='collapsed')

# --- Actions selon la sélection ---
if selection == ":material/add:":
    add_preference()
elif selection == ":material/delete:":
    delete_preferences()



from news.style import card_css

st.markdown(card_css, unsafe_allow_html=True)

RANDOM_IMAGES = [
    "https://images.unsplash.com/photo-1549924231-f129b911e442?fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1532094349884-543bc11b234d?fit=crop&w=600&q=80",
    "https://images.pexels.com/photos/373543/pexels-photo-373543.jpeg",
    "https://images.pexels.com/photos/3861969/pexels-photo-3861969.jpeg",
    "https://images.pexels.com/photos/3861968/pexels-photo-3861968.jpeg",
    
]


# Configuration MongoDB
@st.cache_resource
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

def save_news_to_mongodb(user_email, news_item):
    db = get_mongodb_connection()
    if db is None:
        return False

    news_col = db.news
    users_col = db.client["vst_db"].Users

    # Vérifie si la news est déjà en base
    existing_news = news_col.find_one({"link": news_item["link"]})
    if not existing_news:
        news_item["saved_at"] = datetime.now()
        news_id = news_col.insert_one(news_item).inserted_id
    else:
        news_id = existing_news["_id"]

    # Associer cette news à l'utilisateur
    users_col.update_one(
        {"email": user_email},
        {"$addToSet": {"saved_news": news_id}}
    )

    return True


def unsave_news_from_mongodb(user_email, link):
    """Supprime un article des favoris de l'utilisateur"""
    try:
        db = get_mongodb_connection()
        if db is None:
            return False
        
        news_col = db.news
        users_col = db.client["vst_db"].Users
        
        # Trouver l'article dans la collection news
        news_item = news_col.find_one({"link": link})
        if not news_item:
            return False
        
        news_id = news_item["_id"]
        
        # Retirer cet article des favoris de l'utilisateur
        result = users_col.update_one(
            {"email": user_email},
            {"$pull": {"saved_news": news_id}}
        )
        
        return result.modified_count > 0
        
    except Exception as e:
        st.error(f"Erreur lors de la suppression: {e}")
        return False


def is_news_saved(user_email, link):
    """Vérifie si un article est dans les favoris de l'utilisateur"""
    try:
        db = get_mongodb_connection()
        if db is None:
            return False
        
        news_col = db.news
        users_col = db.client["vst_db"].Users
        
        # Trouver l'article dans la collection news
        news_item = news_col.find_one({"link": link})
        if not news_item:
            return False
        
        news_id = news_item["_id"]
        
        # Vérifier si cet article est dans les favoris de l'utilisateur
        user = users_col.find_one({
            "email": user_email,
            "saved_news": news_id
        })
        
        return user is not None
        
    except Exception as e:
        return False


def save_relevant_news(news_item):
    """Sauvegarde un article marqué comme pertinent"""
    try:
        db = get_mongodb_connection()
        if db is None:
            return False
        
        collection = db.relevant_news

        print(collection)
        
        # Vérifier si l'article existe déjà
        existing = collection.find_one({"link": news_item["link"]})
        if existing:
            return True  # Déjà marqué comme pertinent
        
        # Ajouter la date de marquage
        news_item["marked_relevant_at"] = datetime.now()
        
        # Insertion dans la collection
        result = collection.insert_one(news_item)
        return result.inserted_id is not None
        
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde de pertinence: {e}")
        return False

def remove_from_feed(link):
    """Marque un article comme non pertinent et le cache du feed"""
    try:
        db = get_mongodb_connection()
        if db is None:
            return False
        
        collection = db.hidden_news
        
        # Vérifier si l'article existe déjà dans les cachés
        existing = collection.find_one({"link": link})
        if existing:
            return True  # Déjà caché
        
        # Ajouter à la collection des articles cachés
        hidden_item = {
            "link": link,
            "hidden_at": datetime.now(),
            "reason": "not_relevant"
        }
        
        result = collection.insert_one(hidden_item)
        return result.inserted_id is not None
        
    except Exception as e:
        st.error(f"Erreur lors du masquage: {e}")
        return False

def is_news_hidden(link):
    """Vérifie si un article est caché"""
    try:
        db = get_mongodb_connection()
        if db is None:
            return False
        
        collection = db.hidden_news
        return collection.find_one({"link": link}) is not None
        
    except Exception as e:
        return False

def truncate_text(text, max_length=150):
    """Tronque le texte si trop long et ajoute '...'"""
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(' ', 1)[0] + "...    "

# Function to render a card
def render_card(title, source, summary, Publication_date, image_url, link, topic="General", key_words=["keyword_1", "keyword_2"], card_id=""):
    # Tronquer le résumé
    truncated_summary = truncate_text(summary, 280)
    return f"""
    <div class="card" id="card_{card_id}">
        <div style="position: relative;">
            <img src="{image_url}">
            <div class="date-badge">{Publication_date}</div>
        </div>
        <div class="content">
            <div class="title">{title}</div>
            <div class="subtitle">{source}</div>
            <div class="description">{truncated_summary}</div>
            <div class="meta-info">
                <a class="visit-link" href="{link}" target="_blank">Visit Source ↗</a>
                <div class="topic">📂 {topic}</div>
            </div>
            <div class="keywords">
                {''.join(f'<span class="keyword">{kw}</span>' for kw in key_words[0:4])}
            </div>
        </div>
    </div>
    """

def format_publication_date(dt: datetime) -> str:
    """Format a datetime object to 'DD MMM YYYY' format, e.g., '03 MAY 2025'."""
    return dt.strftime("%d %b %Y").upper()

def get_formatted_feednews(limit=20) -> list[dict]:
    """
    Fetches and formats documents from MongoDB for news feed presentation.
    Exclut les articles marqués comme cachés.
    """
    client = MongoClient("mongodb://localhost:27017/")
    db = client['newsfeed_db']
    collection = db['feednews']

    # Obtenir la liste des liens cachés
    hidden_collection = db['hidden_news']
    hidden_links = {doc['link'] for doc in hidden_collection.find({}, {'link': 1})}

    # Flatten all results inside each document's "results" list
    final_results = []

    cursor = collection.find().sort("created_at", -1).limit(limit * 2)  # Récupérer plus pour compenser les cachés

    for doc in cursor:
        for result in doc.get("results", []):
            # Ignorer les articles cachés
            if result.get("link", "") in hidden_links:
                continue
                
            pub_date = result.get("publication_date", datetime.utcnow())
            if isinstance(pub_date, datetime):
                formatted_date = format_publication_date(pub_date)
            else:
                try:
                    formatted_date = format_publication_date(datetime.strptime(str(pub_date), "%Y-%m-%d"))
                except:
                    formatted_date = "N/A"

            source = result.get("source", "")
            if re.search(r"\barxiv\b", source, re.IGNORECASE):
                result["image_link"] = "https://info.arxiv.org/brand/images/brand-logo-primary.jpg"
            final_results.append({
                "title": result.get("title", ""),
                "source": result.get("source", ""),
                "summary": result.get("summary", ""),
                "Publication_date": formatted_date,
                "image_url": result.get("image_link", random.choice(RANDOM_IMAGES)),
                "link": result.get("link", ""),
                "topic": doc.get("topic", "General"),
                "key_words": result.get("key_words", "topic"),
            })
            
            if len(final_results) >= limit:
                break
        
        if len(final_results) >= limit:
            break

    return final_results[:limit]

def re_fresh_news(preferences):
    workflow = SearchWorkflow(
        name="SmartSearchWorkflow",
        agents=[
            academic_paper_researcher_,
            engine_search_agent_,
            Video_agent_,
            social_media_researcher,
        ],
    )
    for pref in preferences:
        print(f"_____Running workflow for topic: {pref}_____")
        result = workflow.run(topic=pref,user_email=st.session_state.email)
        print(result)

#from news.style import js_code

# JavaScript pour gérer les interactions
js_code = """
<script>
function toggleSave(link, cardId) {
    const saveBtn = document.getElementById('save_btn_' + cardId);
    const currentIcon = saveBtn.innerText;
    
    if (currentIcon === '💾') {
        // Sauvegarder
        saveBtn.innerText = '❌';
        // Ici vous pourriez faire un appel AJAX pour sauvegarder
        console.log('Saving:', link);
    } else {
        // Désauvegarder
        saveBtn.innerText = '💾';
        // Ici vous pourriez faire un appel AJAX pour désauvegarder
        console.log('Unsaving:', link);
    }
}

function markRelevant(link, cardId) {
    console.log('Marking as relevant:', link);
    // Vous pourriez faire un appel AJAX ici
    alert('Marked as relevant!');
}

function markNotRelevant(link, cardId) {
    const card = document.getElementById('card_' + cardId);
    if (confirm('Remove this article from your feed?')) {
        card.style.transition = 'opacity 0.5s';
        card.style.opacity = '0.5';
        console.log('Marking as not relevant:', link);
        // Vous pourriez faire un appel AJAX ici
        setTimeout(() => {
            card.style.display = 'none';
        }, 500);
    }
}
</script>
"""


st.markdown(js_code, unsafe_allow_html=True)

# Initialisation des états de session
if 'preferences' not in st.session_state:
    st.session_state.preferences = ["AI", "Technology", "Science"]  # Valeurs par défaut

preferences = st.session_state.preferences

# Récupération et nettoyage des cartes
cards = get_formatted_feednews(limit=400)

# Nettoyer la liste des cartes : ne garder que celles avec une date valide
def is_valid_date(card):
    try:
        datetime.strptime(card['Publication_date'], '%d %b %Y')
        return True
    except (ValueError, TypeError):
        return False

# Filtrer les cartes valides
cards_cleaned = [card for card in cards if is_valid_date(card)]

# Trier les cartes nettoyées par date décroissante
cards_sorted = sorted(
    cards_cleaned,
    key=lambda c: datetime.strptime(c['Publication_date'], '%d %b %Y'),
    reverse=True
)
st.markdown("---")
# Bouton de rafraîchissement
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.write(f"Showing {len(cards_sorted)} News")

# Gestion des actions utilisateur
if 'action' in st.session_state:
    action = st.session_state.action
    
    if action['type'] == 'save':
        # Trouver l'article correspondant
        article = next((card for card in cards_sorted if card['link'] == action['link']), None)
        if article:
            success = save_news_to_mongodb(st.session_state.email, article)
            if success:
                st.success("Article saved!")
            else:
                st.info("Article already saved or error occurred")
    
    elif action['type'] == 'unsave':
        success = unsave_news_from_mongodb(action['link'])
        if success:
            st.success("News removed from saved!")

    elif action['type'] == 'relevant':
        article = next((card for card in cards_sorted if card['link'] == action['link']), None)
        if article:
            success = save_relevant_news(article)
            if success:
                st.success("Article marked as relevant!")
    
    elif action['type'] == 'not_relevant':
        success = remove_from_feed(action['link'])
        if success:
            st.success("Article removed from feed!")
            # Rafraîchir la page pour masquer l'article
            st.rerun()
    
    # Nettoyer l'action
    del st.session_state.action




# Filtrage des cartes par topic selon la sélection
if 'selection' in locals() and selection:
    if selection == "All Preferences" or selection == ":material/add:" or selection == ":material/remove:":
        filtered_cards = cards_sorted
    else:
        filtered_cards = [card for card in cards_sorted if card.get('topic') == selection]
else:
    filtered_cards = cards_sorted
#print(filtered_cards[0])
# Affichage du feed de news - 3 cartes par ligne
#st.markdown("---")
card_counter = 0
for i in range(0, len(filtered_cards), 3):
    cols = st.columns(3)
    for col, card in zip(cols, filtered_cards[i:i+3]):
        with col:
            card_counter += 1
            card_id = f"{card_counter}_{abs(hash(card['link']))}"
            #print(card)
            
            # Afficher la carte
            html = render_card(card_id=card_id, **card)
            
            with st.form(card_id):
                st.markdown(html, unsafe_allow_html=True)
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                
                # Vérifier les états actuels (maintenant avec l'email utilisateur)
                is_saved = is_news_saved(st.session_state.email, card['link'])
                is_hidden = is_news_hidden(card['link'])
                
                # Créer trois colonnes pour les boutons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # BOUTON SAVE/UNSAVE
                    if is_saved:
                        save_button_text = "Unsave"
                        save_button_icon = ":material/bookmark_remove:"
                        save_button_type = "secondary"
                    else:
                        save_button_text = "Save"
                        save_button_icon = ":material/bookmark_border:"
                        save_button_type = "tertiary"
                    
                    if st.form_submit_button(
                        save_button_text, 
                        icon=save_button_icon, 
                        type=save_button_type,
                        use_container_width=True
                    ):
                        if is_saved:
                            print(card)
                            # Désauvegarder (maintenant avec l'email utilisateur)
                            if unsave_news_from_mongodb(st.session_state.email, card['link']):
                                st.success("Article retiré des favoris!")
                                st.rerun()
                            else:
                                st.error("Erreur lors de la suppression")
                        else:
                            # Sauvegarder
                            news_item = {
                                "title": card['title'],
                                "source": card['source'],
                                "summary": card['summary'],
                                "Publication_date": card['Publication_date'],
                                "image_url": card['image_url'],
                                "link": card['link'],
                                "topic": card['topic']
                            }

                            result = save_news_to_mongodb(st.session_state.email, news_item)
                            if result:
                                st.success("Article sauvegardé!")
                                st.rerun()
                            else:
                                st.info("Article déjà sauvegardé")
                
                with col2:
                    # BOUTON SHOW LESS/SHOW MORE
                    if is_hidden:
                        hide_button_text = "Show More"
                        hide_button_icon = ":material/visibility:"
                        hide_button_type = "secondary"
                    else:
                        hide_button_text = "Hide"
                        hide_button_icon = ":material/visibility_off:"
                        hide_button_type = "tertiary"
                    
                    if st.form_submit_button(
                        hide_button_text, 
                        icon=hide_button_icon, 
                        type=hide_button_type,
                        use_container_width=True
                    ):
                        # Cacher du feed
                        if remove_from_feed(card['link']):
                            st.success("New masked!")
                            st.rerun()
                        else:
                            st.error("masking failed")

                with col3:
                    # Store card data with a unique key first
                    card_key = f"card_data_{card_id}"
                    st.session_state[card_key] = card
                    
                    if st.form_submit_button(
                        "Chat", 
                        icon=":material/chat:", 
                        type="tertiary",
                        use_container_width=True
                    ):
                        # Get the specific card data and set it as active
                        st.session_state.card_content = st.session_state[card_key]
                        #print("Card content set:", st.session_state.card_content)
                        st.switch_page("chat/agents_ui.py")

    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)