import streamlit as st
from bloc_2.SmartLinkAnalysisWorkflow import SmartLinkAnalysisWorkflow
import time
import re

def is_valid_url(url):
    """Valide si l'URL est correcte"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None

def search_agent(url):
    """Agent de recherche utilisant SmartLinkAnalysisWorkflow"""
    try:
        workflow = SmartLinkAnalysisWorkflow(name="URL Intelligence Workflow")
        results = workflow.run_workflow(url)
        print (results)
        return results
    except Exception as e:
        st.error(f"Erreur lors de l'analyse: {str(e)}")
        return []

@st.dialog("Modifier le résultat")
def edit_result_dialog():
    """Dialog pour modifier les résultats de recherche"""
    if st.session_state.get('selected_result'):
        result = st.session_state.selected_result
        
        st.write("### Modifier le résultat")
        
        # Champs éditables
        edited_title = st.text_input("Titre:", value=result.get("title", ""))
        edited_url = st.text_input("URL:", value=result.get("url", ""))
        edited_description = st.text_area("Description:", value=result.get("description", ""), height=100)
        edited_content = st.text_area("Contenu:", value=result.get("content", ""), height=200)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Sauvegarder", type="primary"):
                # Mettre à jour le résultat dans session state
                for i, res in enumerate(st.session_state.search_results):
                    if res == result:
                        st.session_state.search_results[i] = {
                            "title": edited_title,
                            "url": edited_url,
                            "description": edited_description,
                            "content": edited_content
                        }
                        break
                st.success("Modifications sauvegardées!")
                time.sleep(1)
                st.rerun()
        
        with col2:
            if st.button("❌ Annuler"):
                st.session_state.show_dialog = False
                st.rerun()
        
        with col3:
            if st.button("🗑️ Supprimer", type="secondary"):
                # Supprimer le résultat
                st.session_state.search_results = [
                    res for res in st.session_state.search_results if res != result
                ]
                st.success("Résultat supprimé!")
                time.sleep(1)
                st.rerun()

def init_search_session_state():
    """Initialise les variables de session state pour la recherche"""
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []
    if 'selected_result' not in st.session_state:
        st.session_state.selected_result = None
    if 'show_dialog' not in st.session_state:
        st.session_state.show_dialog = False

def render_search_component():
    """
    Composant de recherche compact pour sidebar
    Retourne True si une recherche a été effectuée
    """
    # Initialiser session state
    init_search_session_state()
    
    st.write("🔍 **Analyse de lien**")
    
    # Input pour URL avec validation en temps réel
    url_input = st.text_input(
        "URL à analyser:",
        placeholder="https://example.com",
        key="url_search_input",
        label_visibility="collapsed"
    )
    
    # Validation URL en temps réel
    url_valid = True
    if url_input and not is_valid_url(url_input):
        st.error("⚠️ URL invalide")
        url_valid = False
    
    # Bouton de recherche avec icône
    search_clicked = st.button(
        "🔍 Analyser", 
        type="primary", 
        use_container_width=True,
        disabled=not (url_input and url_valid)
    )
    
    # Effectuer la recherche
    if search_clicked and url_input and url_valid:
        with st.spinner("Analyse en cours..."):
            results = search_agent(url_input.strip())
            if results:
                st.session_state.search_results = results if isinstance(results, list) else [results]
                st.success(f"✅ Analyse terminée!")
                return True
            else:
                st.warning("Aucun résultat trouvé")
    
    return False

def render_search_results():
    """
    Affiche les résultats de recherche de manière compacte
    """
    if not st.session_state.get('search_results'):
        return
    
    st.write("📋 **Résultats**")
    
    for i, result in enumerate(st.session_state.search_results):
        with st.container():
            # Titre tronqué
            title = result.get('title', 'Sans titre')
            display_title = title[:30] + "..." if len(title) > 30 else title
            st.write(f"**{display_title}**")
            
            # URL tronquée
            url = result.get('url', '')
            display_url = url[:35] + "..." if len(url) > 35 else url
            st.caption(f"🔗 {display_url}")
            
            # Bouton d'édition compact
            if st.button(f"✏️", key=f"edit_btn_{i}", help="Modifier ce résultat"):
                st.session_state.selected_result = result
                edit_result_dialog()
            
            if i < len(st.session_state.search_results) - 1:
                st.divider()

def render_full_search_component():
    """
    Composant complet incluant la barre de recherche et les résultats
    """
    render_search_component()
    
    if st.session_state.get('search_results'):
        st.divider()
        render_search_results()

def get_search_results():
    """
    Retourne les résultats de recherche actuels
    """
    return st.session_state.get('search_results', [])

def clear_search_results():
    """
    Efface les résultats de recherche
    """
    st.session_state.search_results = []
    st.session_state.selected_result = None

# Styles CSS pour le composant
def apply_search_styles():
    """Applique les styles CSS pour le composant de recherche"""
    st.markdown("""
    <style>
    .search-component {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    
    .search-result-item {
        padding: 8px;
        border-left: 3px solid #007bff;
        margin-bottom: 8px;
        background-color: #ffffff;
    }
    
    div[data-testid="stButton"] > button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)