import streamlit as st
from streamlit_elements import mui, html, elements
import streamlit as st

# Set page config
#st.set_page_config(page_title="City Card", layout="centered")
#imageeee=st.image("./images/cover.jpeg", caption="Sunrise by the mountains")

st.header("news page")
#st.write(f"You are logged in lab {st.session_state.lab}.")

# Card style
card_css = """
<style>
.card {
    background-color: white;
    border-radius: 10px;
    padding: 0;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    width: 300px;
    font-family: 'Segoe UI', sans-serif;
}
.card img {
    width: 100%;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
}
.card .content {
    padding: 15px;
}
.label {
    background-color: #ff4b4b;
    color: white;
    padding: 4px 8px;
    font-size: 12px;
    border-radius: 4px;
    display: inline-block;
    margin-top: -30px;
    margin-left: 15px;
    position: absolute;
}
.date-badge {
    background-color: #f44336;
    color: white;
    font-size: 12px;
    border-radius: 50%;
    padding: 10px;
    position: absolute;
    right: 15px;
    top: 15px;
    width: 30px;
}
.title {
    font-size: 18px;
    font-weight: bold;
}
.subtitle {
    color: #e74c3c;
    font-size: 14px;
    margin-bottom: 10px;
}
.description {
    font-size: 13px;
    color: #555;
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
.icon {
    font-size: 18px;
    cursor: pointer;
}
a.visit-link {
    text-decoration: none;
    font-size: 13px;
    color: #2c7be5;
}
</style>
"""

# Card HTML
card_html = """
<div class="card">
    <div style="position: relative;">
        <img src="https://images.unsplash.com/photo-1549924231-f129b911e442?fit=crop&w=600&q=80">
        <!--<div class="label">PHOTOS</div>-->
        <div class="date-badge">27 MAR</div>
    </div>
    <div class="content">
        <div class="title">City Lights in New York</div>
        <div class="subtitle">The city that never sleeps.</div>
        <div class="description">
            New York, the largest city in the U.S., is an architectural marvel with plenty of historic monuments, magnificent buildings, and countless dazzling skyscrapers.
        </div>
        <div class="meta">🕒 6 mins ago &nbsp; • &nbsp; 💬 39 comments</div>
        <div class="actions">
            <div>
                ❤️ &nbsp; 💾
            </div>
            <a class="visit-link" href="https://example.com" target="_blank">Visit Source ↗</a>
        </div>
    </div>
</div>
"""

# Render
st.markdown(card_css, unsafe_allow_html=True)
st.markdown(card_html, unsafe_allow_html=True)
