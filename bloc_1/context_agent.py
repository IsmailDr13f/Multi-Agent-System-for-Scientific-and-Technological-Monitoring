from typing import List
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.google import Gemini
import os
from dotenv import load_dotenv
from pymongo import MongoClient

context_prompt="""
You are a smart assistant tasked with generating a clear and concise search context to assist a research team specializing in recent news and developments. The team needs a high-level yet focused understanding of the user’s interests and usage habits to conduct precise, up-to-date information retrieval.

Your task is to analyze the following user profile (in JSON format) and produce a short, structured summary describing:
1. Who the user is (role, lab, background).
2. What kind of news they care about (preferences).
3. When they are most likely to use or read the findings (availability and preferred usage periods).
4. Any specific comments or expectations (custom needs, motivations, or remarks).

Format:
- User Identity: A short description of the user's background.
- News Interests: Summarize the key themes or domains the user wants updates on.
- Usage Timing: When the user expects to engage with the news.
- Special Notes: Any relevant extra context or custom requests from the user.

Input:
```json
{user_profile}
```
Output:
```json
{
    "User_identity": "",
    "User_email": "",
    "News_Interests": "",
    "Usage_Timing": "",
    "Special_notes": "",
    "Search_Context": ""
}
"""

# Connect to MongoDB (change the URI if you're using MongoDB Atlas)
client = MongoClient("mongodb://localhost:27017/")
# Use a database
db = client["vst_db"]

# Use a collection
collection = db["Users"]



# Load environment variables from .env file
load_dotenv()
gemini_key = os.getenv("GEMINI_API_KEY")

class SearxContext(BaseModel):
    User_identity: str = Field(..., description="Informations about user.")
    User_email: str = Field(..., description="Email of the user.")
    News_Interests: str = Field(..., description="search context.")
    Usage_Timing: str = Field(..., description="Actual Context date.")
    Special_notes: str = Field(..., description="Any special notes.")
    Search_Context: str = Field(..., description="Search context for the user.")

Context_Agent = Agent(
    model=Gemini(id="gemini-2.0-flash", api_key=gemini_key),
    response_model=SearxContext,
    instructions=context_prompt ,
    markdown=True,
)

#Context_Agent.print_response("""
#print(Context_Agent.run(
#""""
#{
#'_id': ObjectId('682b36c2d63d1ad2f99006b1'), 
#'name': 'Ismail Drief', 
#'email': 'driefismail722@gmail.com', 
#'role': 'Data-scientist', 
#'laboratory': 'DATA-LAB', 
#'preferences': ['AI Agents', 'LLMs', 'Natural Language Processing (NLP)', 'Reinforcement Learning', 'Deep Learning'], 
#'availability': 'Full-time', 
#'preferred_usage_periods': ['🕗 Matin (08h00 - 12h00)'],
#'comment': "Looking for practical updates I can use in my research and side projects."
#}
#"""
#).content)