from textwrap import dedent
from agno.agent import Agent
#from agno.tools.youtube import YouTubeTools
from agno.models.google import Gemini
#from agno.tools.newspaper4k import Newspaper4kTools
#from agno.tools.reasoning import ReasoningTools
#from agno.tools.baidusearch import BaiduSearchTools
#from agno.models.openrouter import OpenRouter
#from agno.team.team import Team
#from agno.tools.arxiv import ArxivTools
#from agno.tools.duckduckgo import DuckDuckGoTools
#from agno.tools.googlesearch import GoogleSearchTools
from dotenv import load_dotenv
from agno.tools.exa import ExaTools
from pydantic import BaseModel, Field
import os
from datetime import datetime
from api_quota_management.quota_mecanisme import GeminiKeyRotator
#from api_quota_management.key_rotator_utils import with_key_rotation
from prompt import (
    Academic_Paper_prompt,
    Engine_Search_prompt,
    Video_Research_prompt,
    Social_Media_Research_prompt,
    context_prompt
)
#from agno.memory.agent import AgentMemory
#from agno.memory.db.mongodb import MongoMemoryDb
#from agno.storage.mongodb import MongoDbStorage
from datetime import datetime, timedelta
from my_exa import ExaTools_


end_date = datetime.today().date()
start_date = end_date - timedelta(days=2)
# Format the dates as strings in 'YYYY-MM-DD'
start_published_date = start_date.strftime('%Y-%m-%d')
end_published_date = end_date.strftime('%Y-%m-%d')
# Load variables from .env file
load_dotenv()

# Access them with os.getenv()
rotator = GeminiKeyRotator()
gemini_key = os.getenv("GEMINI_API_KEY")

def make_gemini_model():
    key = rotator.get_current_key()
    rotator.rotate_key_if_needed()  # Rotate on each use
    return Gemini(id="gemini-2.5-flash-lite", api_key=key)


#sources_articles = [
    #"journals.plos.org",
    #"nature.com",
    #"frontiersin.org",
    #"mdpi.com",
    #"ieeexplore.ieee.org",
    #"jmlr.org",
    #"ncbi.nlm.nih.gov",
    #"arxiv.org",
    #"doaj.org",
    #"semanticscholar.org",
    #"scholar.google.com",
    #"thinkchecksubmit.org"
#]
# Agent to search for academic papers and scholarly content

academic_paper_researcher_ = Agent(
    name="Paper Researcher Agent",
    model=make_gemini_model(),
    role="Research academic papers and scholarly content",
    tools=[ExaTools_(
        include_domains=["arxiv.org"],
        category="research paper",
        type='hybrid',
        num_results=5,
        start_published_date=start_published_date,
        end_published_date=end_published_date ,
        show_results=True,
    
    )],
    add_name_to_instructions=True,
    debug_mode=True,
    show_tool_calls=True,
    instructions=dedent(Academic_Paper_prompt(datetime.now())),
)

# example usage
#print(academic_paper_researcher_.run("AI Agents").content)

#test_agent = Agent(
#    name="test video agent",
#    model=make_gemini_model(),
#    role="test video scientific content",
#    tools=[ExaTools_(
#        #include_domains=sources_articles,
#        include_domains=["youtube.com", "youtu.be"],
#        category="video",
#        type='hybrid',
#        num_results=5,
#        start_published_date=start_published_date,
#        end_published_date=end_published_date ,
#        show_results=True,
    
#    )],
#    add_name_to_instructions=True,
#    debug_mode=True,
#    show_tool_calls=True,
#    instructions=[Video_Research_prompt(datetime.now())]
#)
# example usage
#print(test_agent.run("AI Agents").content)

#sources_blog= [
#    "artificialintelligence-news.com",
#    "medium.com",
#    "towardsdatascience.com",
#    "coursera.org",
#]
# Agent to search for information using Baidu
# using OpenRouter model with API key
engine_search_agent_ = Agent(
    name="Blog Search Agent",
    model=make_gemini_model(),
    role="Research blog articles and content",
    tools=[ExaTools_(
        #include_domains=sources_articles,
        category="news article",
        type='hybrid',
        num_results=5,
        start_published_date=start_published_date,
        end_published_date=end_published_date ,
        show_results=True,
    
    )],
    add_name_to_instructions=True,
    debug_mode=True,
    show_tool_calls=True,
    instructions=[Engine_Search_prompt(datetime.now())],
)
# example usage
# Run the agent to search for academic papers and scholarly content
#print(engine_search_agent_.run("Google").content)

# Agent to summarize viodeo content using YouTubeTools
# using OpenRouter model with API key
Video_agent_ = Agent(
    name="test video agent",
    model=make_gemini_model(),
    role="test video scientific content",
    tools=[ExaTools_(
        #include_domains=sources_articles,
        include_domains=["youtube.com", "youtu.be"],
        category="video",
        type='hybrid',
        num_results=5,
        start_published_date=start_published_date,
        end_published_date=end_published_date ,
        show_results=True,
    
    )],
    add_name_to_instructions=True,
    debug_mode=True,
    show_tool_calls=True,
    instructions=[Video_Research_prompt(datetime.now())]
)
#Video_agent_.instructions = dedent(Video_agent_.instructions[0])  # Ensure instructions are in string format
# example usage
#print(Video_agent_.run("https://youtu.be/FwOTs4UxQS4?si=4sOzf3XF_kANZPch").content)
#print(Video_agent_.run("gen-AI").content)

# Agent to search for trending discussions and real-time updates on social media
# using Gemini model with API key
social_media_researcher = Agent(
    name="Social Media Researcher",
    model=make_gemini_model(),#Gemini(id="gemini-2.5-flash-preview-05-20",api_key=rotator.get_current_key()),
    role="Research trending discussions and real-time updates agent",
    tools=[ExaTools_(
        include_domains=["x.com", "reddit.com", "linkedin.com"],
        category="social_media",
        num_results=5,
    )],
    add_name_to_instructions=True,
    instructions=dedent(Social_Media_Research_prompt(datetime.now())),
    show_tool_calls=True,
    #debug_mode=True,
    monitoring=True,
)


def prompt_chat(title: str, summary: str,  date: str, url: str, source: str,user_name: str, user_interests: str, user_role: str) -> str:
    return f"""
You are a focused AI agent designed to discuss a specific piece of news content (an article, video, blog, or paper) with a user.
You must stay on-topic and tailor your analysis to the user's interests and goals.

Inputs:
- Title: {title}
- Summary: {summary}
- Date: {date}
- URL: {url}
- Source: {source}

User Profile:
- Name: {user_name}
- Interests: {user_interests}
- Role: {user_role}

### Instructions:


1. **Key Insight Extraction**
   Identify and restate one or more core insights or claims from the content. Prioritize those aligned with the user's interests.
   
2. **Relevance & Novelty Analysis**
   For each insight:
   a. Ask: *Would this insight be useful to someone focused on {user_role}?*  
   b. Is it a new perspective or widely known?  
   c. Could it influence how the user approaches their work or learning?

3. **Source-Type Awareness**
   Adapt your discussion based on the content type:
   - **Video**: Highlight tone, style, visual examples, or speaker expertise.
   - **ArXiv paper**: Be technical, focus on methods, novelty, and limitations.
   - **Blog**: Focus on author opinion, anecdotes, or industry perspective.
   - **News article**: Focus on factual claims and external impact.

4. **Discussion Hooks**
   Suggest 1–2 engaging questions or critiques for the user:
   - “How would this apply in your context?”
   - “Do you find this convincing or biased?”
   - “Would you adopt this method/tool/idea?”

5. **Stay On-Topic**
   If the user drifts off-topic, **gently** remind them: 
   Exemple:  
   *“Please {user_name} remember to stay focused on this item for now: {title}.”*
"""

# Load environment variables from .env file
load_dotenv()


db_url = "mongodb://localhost:27017/"


def chat_agent(title: str, summary: str, date: str, url: str, source: str, user_name: str, user_interests: str, user_role: str) -> Agent:
    return Agent(
    model=make_gemini_model(),
    instructions=prompt_chat(
        title=title,
        summary=summary,
        date=date,
        url=url,
        source=source,
        user_name=user_name,
        user_interests=user_interests,
        user_role=user_role
    ),
    name="News Discussion Agent",
    tools=[ExaTools()],
    #memory=AgentMemory(

    #    db=MongoMemoryDb(
    #        collection_name="agent_memory",
    #        db_url=db_url,
    #    ),
    #    create_user_memories=True,
    #    update_user_memories_after_run=True,
    #    create_session_summary=True,
    #    update_session_summary_after_run=True,
    #),
    #storage=MongoDbStorage(
    #    collection_name="agent_sessions", db_url=db_url,
    #),
    #add_history_to_messages=True,
    #num_history_responses=3,
    #add_datetime_to_instructions=True,
    markdown=True,
)


link_search_agent = Agent(
    model=make_gemini_model(),
    instructions=dedent("""
    You are an advanced content analysis agent specializing in extracting structured information from web links. 
    Your primary goal is to browse the provided URL, understand its content, categorize it, summarize it, and return all information in a strict JSON format. 
    You must use `EXATool_()` to assist in browsing and extracting content from the provided URL.

    **Strict Output Format:**
    You *must* return your response as a JSON object with the following schema. If a field cannot be determined, set its value to `null` or "N/A" as appropriate, but do not omit the field.

    Your Final Output Should Serve As:
    A clear, concise, and insightful research digest that a scientist, PhD student, or technical expert could use as a launching pad for deeper investigation or as context for their own research.
    Example Output Format:
  
  - Title: ...  
  - Source: ...
  - Type: Conference Paper/Article/Preprint
  - Publication_date: ... 
  - Summary: ...  
  - Link: ...
  - Authors : ... 
  - key_words: ...
  - image_link: ..."""
    ),
    tools=[ExaTools_()],
    debug_mode=True,
    show_tool_calls=True,
    name="Link Search Agent",
    )

#print(link_search_agent.run("https://arxiv.org/html/2503.12687v1").content)

class SearxContext(BaseModel):
    User_identity: str = Field(..., description="Informations about user.")
    User_email: str = Field(..., description="Email of the user.")
    News_Interests: str = Field(..., description="search context.")
    Usage_Timing: str = Field(..., description="Actual Context date.")
    Special_notes: str = Field(..., description="Any special notes.")
    Search_Context: str = Field(..., description="Search context for the user.")

Context_Agent = Agent(
    model=make_gemini_model(),
    response_model=SearxContext,
    instructions=context_prompt ,
    markdown=True,
)