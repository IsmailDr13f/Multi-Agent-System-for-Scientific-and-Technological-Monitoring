from textwrap import dedent
from agno.agent import Agent
from agno.tools.youtube import YouTubeTools
from agno.models.google import Gemini
from agno.tools.newspaper4k import Newspaper4kTools
from agno.tools.reasoning import ReasoningTools
from agno.tools.baidusearch import BaiduSearchTools
from agno.models.openrouter import OpenRouter
from agno.team.team import Team
from agno.tools.arxiv import ArxivTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.googlesearch import GoogleSearchTools
from dotenv import load_dotenv
from agno.tools.searxng import Searxng
import os
from api_quota_management.quota_mecanisme import GeminiKeyRotator
#from agno.tools.x import XTools
from .prompt import (acadimic_paper_prompt_, 
                     engine_search_prompt, Video_agent_prompt, 
                     social_media_researcher_prompt, team_manager_prompt
)

from .structured_outputs import (
    AcademicResearchResponse,
    SearchResponse,
    VideoResponse,
    SocialMediaResearchResponse
)

# Load variables from .env file
load_dotenv()

# Access them with os.getenv()
rotator = GeminiKeyRotator()
gemini_key = os.getenv("GEMINI_API_KEY")
#hf_key = os.getenv("HF_API_KEY")

#print(f"GEMINI Key: {gemini_key}")


# Agent to search for academic papers and scholarly content
# using OpenRouter model with API key
academic_paper_researcher_ = Agent(
    name="Academic Paper Researcher",
    model=Gemini(id="gemini-2.0-flash",
                     api_key=rotator.get_current_key()),
    role="Research academic papers and scholarly content",
    #response_model=AcademicResearchResponse,
    tools=[DuckDuckGoTools(cache_results=True), ArxivTools(cache_results=True)],
    add_name_to_instructions=True,
    debug_mode=True,
    show_tool_calls=True,
    instructions=dedent(acadimic_paper_prompt_),
)
# example usage
#print(academic_paper_researcher_.run("What are the latest advancements in gen-AI?").content)


# Agent to search for information using Baidu
# using OpenRouter model with API key
engine_search_agent_ = Agent(
    name="Search engine agent",
    model=Gemini(id="gemini-2.0-flash",
                     api_key=rotator.get_current_key()), #OpenAIChat("gpt-4o"),
    role="Research academic papers and scholarly content",
   #response_model=SearchResponse,
    tools=[BaiduSearchTools(cache_results=True),DuckDuckGoTools(cache_results=True), GoogleSearchTools(cache_results=True)],
    description="You are a search agent that helps users find the most relevant information using Baidu.",
    debug_mode=True,
    show_tool_calls=True,
    instructions=[engine_search_prompt],
   
)
# example usage
# Run the agent to search for academic papers and scholarly content
#print(engine_search_agent_.run("What are the latest advancements in AI?").content)

# Agent to summarize viodeo content using YouTubeTools
# using OpenRouter model with API key
Video_agent_ = Agent(
    name="Video agent",
    model=Gemini(id="gemini-2.0-flash",
                     api_key=rotator.get_current_key()), #OpenAIChat("gpt-4o"),
    role="YouTube agent",
    tools=[GoogleSearchTools(cache_results=True),YouTubeTools(cache_results=True)],
    #response_model=VideoResponse,
    show_tool_calls=True,
    debug_mode=True,
    description="You are a YouTube agent. Obtain the captions of a YouTube video and answer questions.",
    instructions=[Video_agent_prompt],
)
# example usage
#print(Video_agent_.run("Summarize this video https://www.youtube.com/watch?v=Iv9dewmcFbs&t").content)
#print(Video_agent_.run("learn machine and deep learning").content)

# Agent to search for trending discussions and real-time updates on social media
# using Gemini model with API key
social_media_researcher = Agent(
    name="Social Media Researcher",
    model=Gemini(id="gemini-2.0-flash",
                     api_key=rotator.get_current_key()),
    role="Research trending discussions and real-time updates",
    #response_model=SocialMediaResearchResponse,
    tools=[DuckDuckGoTools(cache_results=True)],
    add_name_to_instructions=True,
    instructions=dedent(social_media_researcher_prompt),
    show_tool_calls=True,
    debug_mode=True,
    monitoring=True,
)
#print(social_media_researcher.run("What are the latest advancements in gen-AI?").content)

