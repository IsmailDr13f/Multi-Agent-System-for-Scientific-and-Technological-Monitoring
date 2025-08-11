import streamlit as st
st.set_page_config(layout="wide")
from pymongo import MongoClient
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','bloc_2')))
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
#from bloc_1.context_agent import Context_Agent
from bloc_2.AgentsResearchTeam import Context_Agent, academic_paper_researcher_, engine_search_agent_, Video_agent_
from bloc_2.SearchWorkflow import SearchWorkflow
import streamlit as st
from datetime import datetime, timedelta
import time
from searchbar import search_agent, apply_search_styles
import logging
import warnings
warnings.filterwarnings("ignore")
logging.getLogger('streamlit.runtime.scriptrunner').setLevel(logging.ERROR)
st.logo("images/logo_dice_and_um6p.png")
from PIL import Image


def get_Search_Context(user_profile):
    # Generate the search context
    search_context = Context_Agent.run(str(user_profile))

    # Return the generated search context
    return search_context.content

@st.dialog("Détails de l'article",width="large")
def show_article_dialog(article_data):
    print(article_data)
    
    # Layout horizontal principal : informations à gauche, image à droite
    col_info, col_image = st.columns([3, 1])
    
    with col_info:
        # Titre
        if hasattr(article_data, 'Title'):
            st.markdown(f"### {article_data.Title}")
        
        # Informations principales en deux colonnes
        info_col1, info_col2 = st.columns(2)
        
        with info_col1:
            if hasattr(article_data, 'Source'):
                st.markdown(f"**Source:** {article_data.Source}")
            if hasattr(article_data, 'Publication_date'):
                st.markdown(f"**Date de publication:** {article_data.Publication_Date}")
        
        with info_col2:
            if hasattr(article_data, 'Type'):
                st.markdown(f"**Type:** {article_data.Type}")
            # Lien
            if hasattr(article_data, 'Link') and article_data.Link:
                st.markdown(f"**Link:** [Read more]({article_data.Link})")
        
        # Résumé
        if hasattr(article_data, 'Summary'):
            st.markdown("**Summary:**")
            st.markdown(article_data.Summary)
        
        # Keywords
        if hasattr(article_data, 'Key_words') and article_data.Key_words:
            st.markdown("**Keywords:**")
            keywords = article_data.Key_words.split(",") if isinstance(article_data.Key_words, str) else article_data.Key_words
            keywords = [keyword.strip() for keyword in keywords]
            st.markdown(", ".join(keywords))
    
    with col_image:
        # Image à droite
        if hasattr(article_data, 'Image_link') and article_data.Image_link:
            try:
                st.image(article_data.Image_link, use_container_width=True)
            except:
                st.info("Image non disponible")
        else:
            # Placeholder si pas d'image
            st.markdown("---")
            st.markdown("🖼️")
            st.markdown("*Pas d'image*")
    
    st.divider()
    
    # Boutons en bas, centrés
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        st.button(
            "💾 Save", 
            disabled=False,
            help="Click to save this content",
            use_container_width=True
        )
    
    with col3:
        st.button(
            "💬 Save & Chat", 
            disabled=False,
            help="Click to discuss and save this content",
            use_container_width=True
        )

def sidebar_nav(user_info):
    # Sidebar navigation
    if "visibility" not in st.session_state:
        st.session_state.visibility = "visible"
        st.session_state.disabled = False
        st.session_state.placeholder = "Enter URL for searching"
    
    # Appliquer les styles
    apply_search_styles()
    st.sidebar.title("🔍 Search Your Links")
    
    # Conteneur pour organiser l'input et le bouton
    with st.sidebar.container():
        text_input = st.text_input(
            "Search",
            label_visibility="collapsed",
            disabled=st.session_state.disabled,
            placeholder=st.session_state.placeholder,
            key="search_input"
        )
        
        search_button = st.button(
            "🔍 Search",
            type="primary",
            use_container_width=True,
            key="search_button"
        )
    
    # Déclencher la recherche uniquement via le bouton
    if search_button:
        if text_input and text_input.strip():
            st.toast("Please wait...", icon="⏳")
            with st.spinner("Searching..."):
                try:
                    search_response = search_agent(text_input)
                    st.session_state.search_results = search_response.content
                    print(f"Search results: {st.session_state.search_results}")
                    show_article_dialog(st.session_state.search_results)
                    
                except Exception as e:
                    st.sidebar.error(f"Search failed: {str(e)}")
        else:
            st.sidebar.warning("Please enter a search query")

    st.sidebar.markdown("---")
    if st.sidebar.button("Logout", use_container_width=True):
        # Clear session state and logout
        st.session_state.clear()
        st.rerun()

    # --- section news ----
    news = st.Page("news/news.py", title="news & notification", icon=":material/dashboard:")
    news_ = st.Page("news/news_.py", title="News", icon=":material/dashboard:", default=True)

    # --- section saved & liked news ----
    saved_liked_news = st.Page("saved_liked/saved.py", title="Saved & Discussed News", icon=":material/save:")

    # --- discussion history ----
    discussed_news = st.Page("chat/agents_ui.py", title="Discussion history", icon=":material/chat:")

    # --- section profile ----
    profile = st.Page("settings/profile.py", title="Profile", icon=":material/account_circle:")
    system_settings = st.Page("settings/system_settings.py", title="System settings", icon=":material/settings:")
    
    pg = st.navigation(
        {
            "Newsfeed": [news_],
            "Settings": [profile, saved_liked_news, system_settings],
            "Discussed news History": [discussed_news],
        }
    )

    pg.run()


def connect_to_mongodb_users():
    # Connect to MongoDB (change the URI if you're using MongoDB Atlas)
    client = MongoClient("mongodb://localhost:27017/")  
    
    # Create or use a database
    db = client["vst_db"]

    # Create or use a collection
    collection = db["Users"]
    return collection

def check_email_in_database(email):
    """
    Check if email exists in the MongoDB users collection
    """
    try:
        collection = connect_to_mongodb_users()
        # Search for user by email
        user = collection.find_one({"email": email})
        return user is not None
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return False

def save_profile_to_mongodb(profile):
    collection = connect_to_mongodb_users()
    # Insert the profile into the collection
    collection.insert_one(profile)
    st.session_state.new_user = True
    return True

def search_content_4_new_user():
    """
    Function to handle search content for new users.
    This function is called when a new user is created and needs to search content.
    """
    workflow = SearchWorkflow(
        name="SmartSearchWorkflow",
        agents=[
            academic_paper_researcher_,
            engine_search_agent_,
            Video_agent_,
        ],
    )

    
# Function to display the main page with the form
def load_forms(user_info):
    
    # Déterminer le type de user_info et extraire les informations
    if isinstance(user_info, dict):
        # user_info est un dictionnaire - utiliser les clés directement
        user_name = user_info.get("name", "")
        user_email = user_info.get("email", "")
    else:
        # user_info est un objet - utiliser hasattr et les attributs
        user_name = user_info.name if hasattr(user_info, "name") else ""
        user_email = user_info.email if hasattr(user_info, "email") else ""
    
    # Check if user exists in database
    collection = connect_to_mongodb_users()
    existing_user = collection.find_one({"email": user_email})

    if not existing_user:
        # New user - show welcome message
        st.info("🎉 Welcome! Please fill out your profile.")

    # Pre-fill profile with existing user data from MongoDB or defaults
    profil = {
        "name": existing_user.get("name", user_name) if existing_user else user_name,
        "email": existing_user.get("email", user_email) if existing_user else user_email,
        "role": existing_user.get("role", "") if existing_user else "",
        "laboratory": existing_user.get("laboratory", "") if existing_user else "",
        "preferences": existing_user.get("preferences", []) if existing_user else [],
        "availability": existing_user.get("availability", "Full-time") if existing_user else "Full-time"
    }

    # ---- SIDEBAR ----
    st.sidebar.markdown(f"""
    **Name** : {profil['name'] or "Not provided"}  
    **Email** : {profil['email'] or "Not provided"}  
    """)
    
    if st.sidebar.button("Logout", use_container_width=True):
        # Clear session state
        st.session_state.clear()
        st.rerun()

    # ---- MAIN PAGE ----
    st.title("🧾 Information Form")

    with st.form("main_form"):
        #st.header("📌 General Information")

        name = st.text_input("Full Name", value=profil["name"])
        email = st.text_input("Email", value=profil["email"])
        role = st.text_input("Role", value=profil["role"])
        role_description = st.text_area("Role Description", placeholder="Describe your responsibilities, focus areas, etc.")

        # Dropdown selection for laboratory
        lab = st.selectbox(
            "Select your Laboratory",
            options=["DATA", "CODE", "TECH", "SPECTRUM", "FACTORY", "FAB"],
            index=0 if not profil["laboratory"] else 
                  ["DATA", "CODE", "TECH", "SPECTRUM", "FACTORY", "FAB"].index(profil["laboratory"])
        )

        #st.header("🎯 Preferences and Interests")
        preferences = st.multiselect(
            "Select your favorite topics:",
            options=[
                "GenAI", "AI Agents", "Predictive Modeling", "Time Series Analysis",
                "Data Wrangling", "Big Data Analytics", "Business Intelligence",
                "Causal Inference", "LLMs", "Clustering Techniques", "Hypothesis Testing",
                "Data Storytelling", "Data Visualization", "Data Quality Management",
                "Feature Selection", "A/B Testing", "Statistical Modeling", 
                "Natural Language Processing (NLP)", "Reinforcement Learning", 
                "Deep Learning", "Machine Learning"
            ],
            default=profil["preferences"] if profil["preferences"] else ["Machine Learning", "Deep Learning"]
        )

        #st.header("📆 Availability & Commitment")
        availability = st.radio(
            "Current availability:",
            options=["Full-time", "Part-time"],
            index=0 if profil["availability"] == "Full-time" else 1
        )

        #st.header("🕒 Preferred Platform Usage Time")
        usage_periods = st.multiselect(
            "When do you prefer to use the VST DICE platform?",
            options=[
                "🕗 Morning (08:00 - 12:00)",
                "🌞 Noon (12:00 - 14:00)",
                "🕓 Afternoon (14:00 - 18:00)",
            ],
            default=["🕗 Morning (08:00 - 12:00)"]
        )

        profile = {
            "name": name,
            "email": email,
            "role": role,
            "role_description": role_description,
            "laboratory": lab,
            "preferences": preferences,
            "availability": availability,
            "preferred_usage_periods": usage_periods,
        }

        btn_1, space_2, btn_3 = st.columns([1, 2, 1])
        with btn_1:
            submitted = st.form_submit_button("✅ Create Account", on_click=save_profile_to_mongodb, args=(profile,))
        

    if submitted:
        # Inform the user
        st.toast('Please wait while we prepare the context and securely save the information to the database…', icon="ℹ️")
        
        # Connect to MongoDB
        collection = connect_to_mongodb_users()
        
        # Check if profile exists by email
        existing_profile = collection.find_one({"email": profile["email"]})
        
        # Also handle the _id field if it exists in the existing profile
        if existing_profile:
            # Update existing profile with new data
            updated_profile = existing_profile.copy()
            updated_profile.update(profile)  # Merge new profile data with existing
            profile = updated_profile
            # Remove _id from the profile to avoid conflicts during update
            profile_to_save = {k: v for k, v in profile.items() if k != '_id'}
        else:
            profile_to_save = profile
        
        # Create user context using the complete profile
        user_context = Context_Agent.run(str(profile)).content
        
        # Convert user_context to dictionary if it's a custom object
        if hasattr(user_context, '__dict__'):
            user_context_dict = user_context.__dict__
        else:
            user_context_dict = user_context
        print(f"User context: {user_context_dict}")
        # Add user_context to the profile as a serializable dictionary
        profile["user_context"] = user_context_dict['Search_Context']

        # Save or update profile in MongoDB (upsert by email)
        collection.update_one(
            {"email": profile["email"]},   # Match by email
            {"$set": profile_to_save},     # Update all profile fields excluding _id
        )

        # Store in session state
        st.session_state.user_context = user_context
        st.session_state.profile = profile  # Also store the complete profile
        st.session_state.new_user_search_context = user_context_dict['Search_Context']

        # Confirm to the user
        st.success("✅ Thank you! Your responses have been recorded along with your personalized context.")
        with btn_3:
            search_content=st.form_submit_button("➡️ Next",on_click=search_content_4_new_user, use_container_width=True,type="primary")


def login_screen():
    # Simplified CSS for the login design
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(0deg, #ffffff 85%, #D64A2B 100%);
    }
    
    
    .login-header {
        text-align: center;
        margin-bottom: 40px;
    }
    
    .login-title {
        font-size: 28px;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 10px;
        letter-spacing: -0.5px;
    }
    
    .login-subtitle {
        font-size: 16px;
        color: #7f8c8d;
        margin: 20px 0;
    }
    
    .logo-section {
        text-align: center;
        margin-bottom: 30px;
    }
    
    .stTextInput > div > div > input {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 15px 20px;
        font-size: 14px;
        transition: all 0.3s ease;
        width: 100%;
        box-sizing: border-box;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        background: white;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stTextInput > label {
        font-weight: 500;
        color: #2c3e50;
        margin-bottom: 8px;
        font-size: 14px;
    }
    
    .stButton > button {
        background: #00A4EF !important; 
        color: white !important;
        border: none !important;
        padding: 15px 30px !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        width: 100% !important;
        height: 50px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(0, 164, 239, 0.3) !important;
        background: #0078d4 !important;     
    }
    
    .stAlert {
        margin-top: 15px;
        border-radius: 10px;
    }
    
    .form-container {
        max-width: 400px;
        margin: 0 auto;
    }
    
    .signup-form {
        margin-top: 20px;
    }
    
    .contact-info {
        text-align: center; 
        margin-top: 30px; 
        color: #7f8c8d; 
        font-size: 12px;
    }
    
    .contact-info a {
        color: #667eea; 
        text-decoration: none;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create the main layout
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Logo section
        import base64

        # Function to encode image to base64
        def get_base64_image(image_path):
            try:
                with open(image_path, "rb") as img_file:
                    return base64.b64encode(img_file.read()).decode()
            except FileNotFoundError:
                return None

        # Get encoded image
        logo_base64 = get_base64_image("images/LOGO DICE and um6p.png")

        if logo_base64:
            st.markdown(f"""
            <div class="logo-section">
                <img src="data:image/png;base64,{logo_base64}" alt="VST DICE" style="width: 300px; height: auto;">
                <div class="login-subtitle">Welcome to VST DICE Platform</div>
            </div>
            """, unsafe_allow_html=True)
        
        
        # Tab buttons
        tab_login, tab_signup = st.tabs(["Login", "Sign Up"])
        
        # Login Tab
        with tab_login:
            with st.form("email_login", clear_on_submit=False):
                email = st.text_input(
                    "Email",
                    placeholder="Enter your email",
                    key="email_input",
                    help="Please enter your email to verify your account."
                )
                st.warning(""" **Important Notice:**
                For the test period, we have simplified the login process to make access quicker and easier.
                Please note that this change is temporary and intended solely to streamline your experience during testing.
                Thank you for your understanding and cooperation.""", icon="⚠️")
                login_submitted = st.form_submit_button("LOGIN", type="primary", use_container_width=True)

            # Process login AFTER the form (not inside)
            if login_submitted:
                if not email:
                    st.error("❌ Please enter your email.")
                elif check_email_in_database(email):
                    st.success("✅ Email found in database. Welcome back!")
                    st.session_state.verified_email = email
                    if st.session_state.get("new_user_email") == email:
                        st.session_state.new_user = True
                    st.rerun()  
                else:
                    st.error("❌ Email not found in database. Please sign up first.")

        # Signup Tab
        with tab_signup:
            st.markdown('<div class="signup-form">', unsafe_allow_html=True)
            
            with st.form("email_signup", clear_on_submit=False):
                st.markdown("### Create Account")
                
                signup_email = st.text_input(
                    "Email",
                    placeholder="Enter your email address",
                    key="signup_email_input",
                    help="This will be your login email"
                )
                
                full_name = st.text_input(
                    "Full Name",
                    placeholder="Enter your full name",
                    key="signup_name_input"
                )
                
                # Work fields
                st.markdown("**Work Information:**")
                
                lab = st.selectbox(
                    "Laboratory",
                    ["DATA", "CODE", "TECH", "SPECTRUM", "FACTORY", "FAB"],
                    key="signup_department"
                )
                
                role = st.selectbox(
                    "Role",
                    ["", "PhD Student", "Engineer", "Researcher", "Other"],
                    key="signup_role"
                )
                
                profile = {
                    "name": full_name,
                    "email": signup_email,
                    "role": role,
                    "role_description": "",
                    "laboratory": lab,
                    "preferences": "",
                    "availability": "",
                    "preferred_usage_periods": "",
                }

                # Signup button
                signup_submitted = st.form_submit_button("CREATE ACCOUNT", type="primary", use_container_width=True)
                
            if signup_submitted:
                if not signup_email or not full_name:
                    st.error("❌ Please fill in all required fields (Email and Full Name)")
                elif not is_valid_email(signup_email):
                    st.error("❌ Please enter a valid email address")
                elif check_email_in_database(signup_email):
                    st.error("❌ An account with this email already exists")
                else:
                    # Create new user account
                    if save_profile_to_mongodb(profile):
                        st.success("✅ Account created successfully! You can now login.")
                        time.sleep(2)  # Optional delay before redirecting
                        st.rerun()
                    else:
                        st.error("❌ Failed to create account. Please try again.")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Contact info
        st.markdown("""
        <div class="contact-info">
            Do you have a problem? Please contact your administrator<br>
            <a href="mailto:Ismail.DRIEF-EXT@um6p.ma">Ismail.DRIEF-EXT@um6p.ma</a>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)


def is_valid_email(email):
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


# Main authentication logic
if "verified_email" not in st.session_state:
    login_screen()
else:
    # Get user info from verified email
    user_email = st.session_state.verified_email
    collection_temp = connect_to_mongodb_users()
    user_info = collection_temp.find_one({"email": user_email})
    user_name = user_info.get("name", "User") if user_info else "User"

    if not user_email:
        st.error("Error: Unable to retrieve user email")
        st.stop()
    
    st.header(f"👋 Welcome back, {user_name}!")
    
    # Connect to MongoDB once
    collection_ = connect_to_mongodb_users()
    existing_user = collection_.find_one({"email": user_email})
    
    # Handle new vs existing users
    if existing_user is None:
        # New user - show registration form
        st.session_state.new_user = True
        load_forms(user_info)
    elif st.session_state.get("new_user", False):
        # Existing user but forced to redo form
        load_forms(user_info)
        st.session_state.new_user = False
    else:
        # Check if profile fields are empty
        required_fields = {
            "name": existing_user.get("name", ""),
            "email": existing_user.get("email", ""),
            "role": existing_user.get("role", ""),
            "role_description": existing_user.get("role_description", ""),
            "laboratory": existing_user.get("laboratory", ""),
            "preferences": existing_user.get("preferences", []),
            "availability": existing_user.get("availability", ""),
            "preferred_usage_periods": existing_user.get("preferred_usage_periods", [])
        }
        
        # Check if any required fields are empty
        has_empty_fields = (
            not required_fields["name"] or
            not required_fields["email"] or
            not required_fields["role"] or
            not required_fields["role_description"] or
            not required_fields["laboratory"] or
            not required_fields["preferences"] or
            not required_fields["availability"] or
            not required_fields["preferred_usage_periods"]
        )
        
        if has_empty_fields:
            # Show form to complete profile
            load_forms(user_info)
        else:
            # Existing user with complete profile - load their data
            # Load info into session
            st.session_state.user_info = user_info
            st.session_state.lab = existing_user.get("laboratory", "")
            st.session_state.role = existing_user.get("role", "")
            st.session_state.preferences = existing_user.get("preferences", [])
            st.session_state.email = existing_user.get("email", "")
            st.session_state.name = existing_user.get("name", "")
            st.session_state.preferred_usage_periods = existing_user.get("preferred_usage_periods", [])
            
            # Show navigation
            sidebar_nav(user_info)