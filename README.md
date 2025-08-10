# VST — Scientific & Technical Monitoring Platform

This project is an **innovative AI-powered platform** for scientific and technical monitoring.  
It collects, analyzes, and summarizes the latest research, technological advancements, and industry trends, giving users timely and relevant insights.  

## 🏗 Main Architecture

Below is the main **AI Agents Architecture** used in the platform:

<img width="1918" height="966" alt="architecture complete" src="https://github.com/user-attachments/assets/1a48b22a-65af-42ff-81fa-65ae595cbfe9" />


**Description:**  
The architecture is based on a **multi-agent AI system** built with Agno AI, where each agent specializes in a specific task.

- **Research & Synthesis Agents** collect news from various sources (academic papers, web search, videos, and social media) and aggregate them into structured insights.  
- **Context & Preferences Agent** personalizes the results based on the user’s profile and stored preferences.  
- **Source/Link Search Agent** allows searching directly from a given URL.  
- **Analyzer Agent** enables interactive discussions and deeper analysis of selected news.  
- All processed data is stored in **MongoDB**, displayed through a **Streamlit UI**, and continuously updated for the user.  

---

## 🎥 Demo Video

1️⃣ **News Auto Search (Agentic AI-based approach)**  


https://github.com/user-attachments/assets/ab405ad2-a66d-4225-922c-4535449b1ac4



2️⃣ **Search News via Link (URL)**  



Uploading Media1.mp4…


3️⃣ **Discuss News with Analyzer Agent**  
 


https://github.com/user-attachments/assets/1b200aeb-0aca-45a8-8414-fe8f59000f4a


## 🛠 Stack Used
- **Python** 3.11.8  
- **Package management**: [uv](https://github.com/astral-sh/uv)  
- **Frameworks & Libraries**: [Agno AI](https://pypi.org/project/agno/), [Streamlit](https://streamlit.io/), [MongoDB](https://www.mongodb.com/), [Google Gemini 2 API](https://deepmind.google/technologies/gemini/)  
- **Development environment**: Windows 11 + VS Code  

---

## 📦 Installation & Setup

### 1. Download the project
```bash
# Clone or download the repository
git clone https://github.com/IsmailDr13f/Multi-Agent-System-for-Scientific-and-Technological-Monitoring.git
cd Multi-Agent-System-for-Scientific-and-Technological-Monitoring
```

### 2. Create a virtual environment
```bash
python3 -m venv .venv
```

### 3. Activate the virtual environment  
- **Windows (PowerShell)**:
```bash
.venv\Scripts\activate
```
- **Linux/macOS**:
```bash
source .venv/bin/activate
```

### 4. Install `uv`
```bash
pip install uv
```

### 5. Install dependencies
```bash
uv pip install -r requirements.txt
```

### 6. Setup MongoDB
This project requires a **MongoDB server**. You can:
- Install it locally: [MongoDB Community Server Download](https://www.mongodb.com/try/download/community)
- Or use a cloud service: [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)

Make sure to update your **MongoDB URI** in the `.env` file.

### 7. Run the frontend
```bash
cd frontend
streamlit run main.py
```

---

## 🔑 Usage
1. Create an account via the app interface.
<img width="1910" height="911" alt="image" src="https://github.com/user-attachments/assets/e6d6b156-48b6-437d-88c6-7c40efe9bb9b" />
2. Complete the login information.
<img width="1913" height="908" alt="image" src="https://github.com/user-attachments/assets/b09a8849-71f8-4787-8409-f4bc0e2d9e6e" />
3. Access the **main news page** to start monitoring scientific & technical updates.  
<img width="1917" height="912" alt="ui_news" src="https://github.com/user-attachments/assets/0f228967-f4dc-420c-9687-3eaefb1832c7" />

---

## 📄 Dependencies
Main dependencies from `requirements.txt`:
```
agno==1.7.9
streamlit==1.45.0
google-genai==1.29.0
pymongo==4.14.0
exa-py==1.14.20
streamlit-elements==0.1.0
```
> See `requirements.txt` for the full list.

---

## ⚠️ Disclaimer
> This project integrates **third-party services** (Gemini 2 API, MongoDB hosting, etc.).  
> Some services **may require paid subscriptions** to fully unlock all features.  
> Please review the pricing of each service before production deployment.  


