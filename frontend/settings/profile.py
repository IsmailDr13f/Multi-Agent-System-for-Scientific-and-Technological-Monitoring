import streamlit as st

st.markdown(f"""
    **Nom** : {st.session_state.user_info.name if hasattr(st.session_state.user_info, "name") else st.session_state.name}  
    **Email** : {st.session_state.user_info.email if hasattr(st.session_state.user_info, "email") else st.session_state.email}  
    **LAB** : {st.session_state.lab if hasattr(st.session_state, "lab") else st.session_state.lab}   
    **Role** : {st.session_state.role if hasattr(st.session_state, "role") else st.session_state.role}    
    """)
    