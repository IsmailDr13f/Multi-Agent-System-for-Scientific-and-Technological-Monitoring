import streamlit as st
from pymongo import MongoClient

def sidebar_nav(user_info):
    # Sidebar navigation
    st.sidebar.title("👤 Profil connecté")
    st.sidebar.markdown(f"""
    **Nom** : {user_info.name if hasattr(user_info, "name") else "Non fourni"}  
    **Email** : {user_info.email if hasattr(user_info, "email") else "Non fourni"}  
    """)
    st.sidebar.button("Logout", on_click=st.logout)

    # --- section news ----
    news = st.Page("news/news.py", title="news & notification", icon=":material/dashboard:", default=True)

    # --- section saved & liked news ----
    saved_news = st.Page("saved_liked/saved.py", title="Saved news", icon=":material/bug_report:")
    liked_news = st.Page("saved_liked/liked.py", title="Liked news", icon=":material/thumb_up:")

    # --- discussion history ----
    discussed_news = st.Page("chat/agents_ui.py", title="System alerts", icon=":material/notification_important:")

    # --- section profile ----
    profile = st.Page("settings/profile.py", title="Profile", icon=":material/account_circle:")
    system_settings = st.Page("settings/system_settings.py", title="System settings", icon=":material/settings:")

    pg = st.navigation(
        {
            "Newsfeed": [news],
            "Saved & Liked News": [saved_news, liked_news],
            "Discussed news History": [discussed_news],
            "Settings": [profile, system_settings],
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

def save_profile_to_mongodb(profile):
    collection = connect_to_mongodb_users()
    # Insert the profile into the collection
    result = collection.insert_one(profile)
    # Output inserted ID
    print("Inserted profile ID:", result.inserted_id)


# Fonction pour afficher la page principale avec le formulaire
def load_forms(user_info):
    # Construction du profil à partir de st.user
    profil = {
        "name": user_info.name if hasattr(user_info, "name") else "",
        "email": user_info.email if hasattr(user_info, "email") else "",
        "role": "",  
        "laboratory": "",
        "preferences": [
            "GenAI", "AI Agents", "Predictive Modeling", "Time Series Analysis",
            "Data Wrangling", "Big Data Analytics", "Business Intelligence",
            "Causal Inference", "LLMs", "Clustering Techniques", "Hypothesis Testing",
            "Data Storytelling", "Data Visualization", "Data Quality Management",
            "Feature Selection", "A/B Testing", "Statistical Modeling", 
            "Natural Language Processing (NLP)", "Reinforcement Learning", 
            "Deep Learning", "Machine Learning"
        ],
        "availability": "Full-time"
    }

    # ---- SIDEBAR ----
    st.sidebar.title("👤 Profil connecté")
    st.sidebar.markdown(f"""
    **Nom** : {profil['name'] or "Non fourni"}  
    **Email** : {profil['email'] or "Non fourni"}  
    """)
    st.sidebar.button("Logout", on_click=st.logout)

    # ---- PAGE PRINCIPALE ----
    st.title("🧾 Formulaire d'information")

    with st.form("formulaire_principal"):
        st.header("📌 Informations générales")

        name = st.text_input("Nom complet", value=profil["name"])
        email = st.text_input("Email", value=profil["email"])
        role = st.text_input("Rôle", value=profil["role"])
        lab = st.text_input("Laboratoire", value=profil["laboratory"])

        st.header("🎯 Préférences et intérêts")
        preferences = st.multiselect(
            "Sélectionnez vos thématiques favorites :",
            options=profil["preferences"],
            default=["Machine Learning", "Deep Learning"]
        )

        st.header("📆 Disponibilité & implication")
        availability = st.radio(
            "Disponibilité actuelle :",
            options=["Full-time", "Part-time"],
            index=0 if profil["availability"] == "Full-time" else 1
        )

        st.header("🕒 Temps souhaité d'utilisation de la plateforme")

        usage_periods = st.multiselect(
            "Quand préférez-vous utiliser la plateforme VST DICE ?",
            options=[
                "🕗 Matin (08h00 - 12h00)",
                "🌞 Midi (12h00 - 14h00)",
                "🕓 Après-midi (14h00 - 18h00)",
            ],
            default=["🕗 Matin (08h00 - 12h00)"]
        )

        st.header("💬 Commentaire (optionnel)")
        comment = st.text_area("Vos remarques ou suggestions")

        profile = {
            "name": name,
            "email": email,
            "role": role,
            "laboratory": lab,
            "preferences": preferences,
            "availability": availability,
            "preferred_usage_periods": usage_periods,
            "comment": comment
        }

        submitted = st.form_submit_button("✅ Soumettre", on_click=save_profile_to_mongodb, args=(profile,))

    if submitted:
        st.success("✅ Merci ! Vos réponses ont été enregistrées.")
        #st.subheader("📦 Données soumises :")
        #st.json(profile)

# Fonction de login si l'utilisateur n'est pas connecté
def login_screen():
    st.header("🔐 VST DICE")
    st.subheader("Veuillez vous connecter avec votre compte Microsoft.")
    st.button("Log in with Microsoft", on_click=st.login)

# Logique principale
if not st.user.is_logged_in:
    login_screen()
else:
    st.header(f"👋 Bienvenue, {st.user.name or 'Utilisateur'} !")

    # Connexion à la base MongoDB
    collection_ = connect_to_mongodb_users()

    # Filtre de recherche par email
    user_email = st.user.email
    existing_user = collection_.find_one({"email": user_email})

    if existing_user is None:
        # Si l'utilisateur n'existe pas, afficher le formulaire
        load_forms(st.user)
    else:
        st.session_state.lab = existing_user.get("laboratory", "")
        print(st.user)
        sidebar_nav(st.user)
        # L'utilisateur existe déjà
        #st.success("✅ Vous êtes déjà enregistré, Vos informations ont déjà été soumises.")
        

