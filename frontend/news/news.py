import streamlit as st
from streamlit_elements import mui, html, elements
from pymongo import MongoClient
from datetime import datetime
from pymongo import MongoClient
import random
import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from bloc_2.SearchWorkflow import SearchWorkflow
from bloc_2.SmartLinkAnalysisWorkflow import SmartLinkAnalysisWorkflow,StructuredResponse

from bloc_2.AgentsResearchTeam import (
    academic_paper_researcher_,
    engine_search_agent_,
    Video_agent_,
    social_media_researcher,    
)

# Inject CSS once
card_css = """
<style>
.card {
    background-color: white;
    border-radius: 10px;
    padding: 0px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    width: 340px;
    height: 500px;
    font-family: 'Segoe UI', sans-serif;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    
}
.card img {
    width: 100%;
    height: 180px;
    object-fit: cover;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
}
.card .content {
    padding: 15px;
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    width: 100%;
    
}
.date-badge {
    background-color: #f44336;
    color: white;
    font-size: 12px;
    border-radius: 20px;
    padding: 10px;
    position: absolute;
    right: 15px;
    top: 15px;
    width: 100px;
    height: 30px;
    text-align: center;
    line-height: 10px;
}
.title {
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 5px;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 3; /* limite à 2 lignes */
    -webkit-box-orient: vertical;
}
.subtitle {
    color: #e74c3c;
    font-size: 14px;
    margin-bottom: 10px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.description {
    font-size: 13px;
    color: #555;
    height: 70px;
    overflow: hidden;
    text-overflow: ellipsis;
    width: 100%;
    height: 50%; 
    display: -webkit-box;
    -webkit-line-clamp: 3; /* limite à 2 lignes */
    -webkit-box-orient: vertical;
}
.meta {
    font-size: 12px;
    color: gray;
    margin-top: 10px;
}
.actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 10px;
}
    a.visit-link {
    text-decoration: none;
    font-size: 13px;
    color: #2c7be5;
}
</style>
"""
st.markdown(card_css, unsafe_allow_html=True)
RANDOM_IMAGES = [
    "https://images.unsplash.com/photo-1549924231-f129b911e442?fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1532094349884-543bc11b234d?fit=crop&w=600&q=80",
]
# Function to render a card
def render_card(title, source, summary, Publication_date, image_url, link, meta="🕒 Just now • 💬 0 comments"):
    return f"""
    <div class="card">
        <div style="position: relative;">
            <img src="{image_url}">
            <div class="date-badge">{Publication_date}</div>
        </div>
        <div class="content">
            <div class="title">{title}</div>
            <div class="subtitle">{source}</div>
            <div class="description">{summary}</div>
            <!--<div class="meta">{meta}</div>-->
            <div class="actions">
                <div>❤️ &nbsp; 💾</div>
                <a class="visit-link" href="{link}" target="_blank">Visit Source ↗</a>
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

    Returns:
        A list of dicts with the following fields:
        - title, source, summary, Publication_date, image_url, link
    """
    client = MongoClient("mongodb://localhost:27017/")
    db = client['newsfeed_db']
    collection = db['feednews']

    # Flatten all results inside each document's "results" list
    final_results = []

    cursor = collection.find().sort("created_at", -1).limit(limit)

    for doc in cursor:
        for result in doc.get("results", []):
            pub_date = result.get("publication_date", datetime.utcnow())
            if isinstance(pub_date, datetime):
                formatted_date = format_publication_date(pub_date)
            else:
                try:
                    formatted_date = format_publication_date(datetime.strptime(str(pub_date), "%Y-%m-%d"))
                except:
                    formatted_date = "N/A"

            final_results.append({
                "title": result.get("title", ""),
                "source": result.get("source", ""),
                "summary": result.get("summary", ""),
                "Publication_date": formatted_date,
                "image_url": random.choice(RANDOM_IMAGES),  # or extract if you ever store them
                "link": result.get("link", "")
            })

    return final_results


cards= get_formatted_feednews(limit=50)
#print(f"Number of cards fetched: {len(cards)}")
#print(cards[0])  # Print the first card for debugging

def refresh_news(preferences):
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
        result = workflow.run(topic=pref)
        print(result)

preferences = st.session_state.preferences

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
#print(f"Number of valid cards after cleaning: {len(cards_sorted)}")

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Configuration MongoDB
@st.cache_resource
def get_mongodb_connection():
    """Initialise la connexion MongoDB"""
    try:
        # Configuration de MongoDB (ajustez selon vos paramètres)
        MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        client = MongoClient(MONGODB_URI)
        db = client.get_database("link_analysis")  # Nom de votre base de données
        return db
    except Exception as e:
        st.error(f"Erreur de connexion MongoDB: {e}")
        return None

def save_to_mongodb(link, analysis_result):
    """Sauvegarde les résultats dans MongoDB"""
    try:
        db = get_mongodb_connection()
        if db is None:
            return False
            
        collection = db.searched_links
        
        # Préparation du document
        document = {
            "link": link,
            "analyzed_at": datetime.now(),
            "analysis_result": {}
        }
        
        # Extraction des données selon le type de résultat
        if isinstance(analysis_result.content, StructuredResponse):
            content = analysis_result.content
            document["analysis_result"] = {
                "title": content.Title,
                "source": content.Source,
                "upload_date": content.Upload_Date,
                "summary_captions": content.Summary_captions,
                "original_link": content.Link
            }
        else:
            document["analysis_result"] = {
                "raw_content": str(analysis_result.content)
            }
        
        # Insertion dans la collection
        result = collection.insert_one(document)
        return result.inserted_id is not None
        
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde: {e}")
        return False

# Initialisation des états de session
if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled = False

if "open_dialog" not in st.session_state:
    st.session_state.open_dialog = False

if "workflow_result" not in st.session_state:
    st.session_state.workflow_result = None

if "current_link" not in st.session_state:
    st.session_state.current_link = ""

# Initialisation du workflow
@st.cache_resource
def initialize_workflow():
    """Initialise le workflow une seule fois"""
    return SmartLinkAnalysisWorkflow(name="URL Intelligence Workflow")

def run_workflow_analysis(url):
    """Exécute l'analyse du workflow sur l'URL donnée"""
    try:
        workflow = initialize_workflow()
        with st.spinner("🔍 Analyzing your link... This may take a few moments."):
            result = workflow.run_workflow(url)
            return result, None
    except Exception as e:
        error_msg = f"Error analyzing link: {str(e)}"
        st.error(error_msg)
        return None, error_msg

# Fonction de la boîte de dialogue améliorée
@st.dialog("🔎 Link Analysis Results", width="large")
def show_link_dialog():
    st.markdown("### 📊 Analysis Results")
    
    # Affichage du lien analysé
    st.markdown(f"**🔗 Analyzed Link:** `{st.session_state.current_link}`")
    st.divider()
    
    if st.session_state.workflow_result:
        try:
            # Récupération des données structurées
            content = st.session_state.workflow_result.content
            
            if isinstance(content, StructuredResponse):
                # Affichage des informations structurées
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("#### 📝 General Information")
                    st.markdown(f"**Title:** {content.Title}")
                    st.markdown(f"**Source:** {content.Source}")
                    st.markdown(f"**Upload Date:** {content.Upload_Date}")
                
                with col2:
                    st.markdown("#### 🔗 Link")
                    st.markdown(f"**Original Link:** [{content.Link}]({content.Link})")
                
                st.markdown("#### 📄 Summary")
                st.markdown(content.Summary_captions)
                
            else:
                # Affichage du contenu brut si la structure n'est pas reconnue
                st.markdown("#### 📋 Raw Content")
                st.text(str(content))
                
        except Exception as e:
            st.error(f"Error displaying results: {str(e)}")
            st.markdown("#### 🔍 Raw Analysis Result")
            st.text(str(st.session_state.workflow_result))
    else:
        st.error("❌ No analysis results available")
    
    # Boutons d'action
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔄 Analyze Again", use_container_width=True):
            st.session_state.workflow_result = None
            st.rerun()
    
    with col2:
        if st.button("📋 Discuss Content", use_container_width=True):
            if st.session_state.workflow_result:
                st.write("This functionality requires additional Development.")
    
    with col3:
        if st.button("💾 Save & Close", use_container_width=True):
            if st.session_state.workflow_result and st.session_state.current_link:
                with st.spinner("💾 Saving to database..."):
                    success = save_to_mongodb(
                        st.session_state.current_link, 
                        st.session_state.workflow_result
                    )
                    
                if success:
                    st.success("✅ Results saved successfully!")
                    st.session_state.open_dialog = False
                    st.session_state.workflow_result = None
                    time.sleep(1)  
                    st.rerun()
                else:
                    st.error("❌ Failed to save results to database")
            else:
                st.warning("⚠️ No results to save")
                st.session_state.open_dialog = False
                st.session_state.workflow_result = None
                st.rerun()

# Interface principale
st.markdown("Enter any link to get detailed analysis including title, summary, source information, and more!")

# Champ de texte pour l'URL
text_input = st.text_input(
    "Search for your own Articles, Blogs or Videos and more 👇",
    label_visibility="collapsed",#st.session_state.visibility,
    disabled=st.session_state.disabled,
    placeholder="Please enter your search link here...: https://www.example.com",
    help="Enter any valid URL (YouTube videos, articles, blogs, research papers, etc.)"
)

# Validation simple de l'URL
def is_valid_url(url):
    """Validation basique de l'URL"""
    return url.startswith(('http://', 'https://')) and '.' in url

# Boutons d'action
col1, col2 = st.columns([2, 1])

with col1:
    if st.button("🔍 Analyze Link", use_container_width=True, type="primary"):
        if text_input:
            if is_valid_url(text_input):
                st.session_state.current_link = text_input
                
                # Exécution de l'analyse
                result, error = run_workflow_analysis(text_input)
                
                if result:
                    st.session_state.workflow_result = result
                    st.session_state.open_dialog = True
                    st.success("✅ Analysis completed! Opening results...")
                    st.rerun()
                else:
                    st.error(f"❌ Analysis failed: {error}")
            else:
                st.warning("⚠️ Please enter a valid URL starting with http:// or https://")
        else:
            st.warning("⚠️ Please enter a link before analyzing.")

#with col2:
#    if st.button("🧹 Clear", use_container_width=True):
#        st.session_state.workflow_result = None
#        st.rerun()

# Ouverture automatique de la boîte de dialogue si nécessaire
if st.session_state.open_dialog and st.session_state.workflow_result:
    show_link_dialog()

# Section d'aide
with st.expander("ℹ️ How to use this tool"):
    st.markdown("""
    **Supported Link Types:**
    - 📹 YouTube videos
    - 📰 News articles  
    - 📝 Blog posts
    - 📚 Research papers (ArXiv, etc.)
    - 🌐 General web pages
    
    **What you'll get:**
    - Title and source information
    - Upload/publication date
    - Content summary
    - Direct link access
    
    **Tips:**
    - Make sure your link is complete and valid
    - The analysis may take a few moments depending on the content type
    - Results will be displayed in a detailed dialog box
    """)

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////




# Display the news feed
st.button("Refresh", on_click=refresh_news, args=(preferences,))
# Display 3 cards per row
for i in range(0, len(cards_sorted), 3):
    cols = st.columns(3)
    for col, card in zip(cols, cards_sorted[i:i+3]):
        with col:
            html = render_card(**card)
            st.markdown(html, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

