from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.youtube import YouTubeTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.arxiv import ArxivTools
from agno.tools.pubmed import PubmedTools
from dotenv import load_dotenv
from agno.tools.serpapi import SerpApiTools
from agno.tools.jina import JinaReaderTools
from agno.tools.newspaper4k import Newspaper4kTools
from agno.tools.newspaper import NewspaperTools
from agno.tools.website import WebsiteTools
import os 

load_dotenv()

# Agent to search for Videos content
Video_Search_Agent = Agent(
    name="Video agent",
    model=Gemini(id="gemini-2.0-flash",
                     api_key=os.getenv("GEMINI_API_KEY")),
    role="YouTube agent",
    tools=[YouTubeTools(cache_results=True)],
    instructions=["""You are a YouTube agent. Obtain the captions of a YouTube video from the given URL.
                  follow this output format:
                  {
                    Title: <title of the video>
                    Source: <source of the video>
                    Upload_Date: <upload date of the video>
                    Summary_captions: <summary of the video>
                    Link: <link to the video>
                  }
                  """],
    #response_model=VideoResponse,
    show_tool_calls=True,
)

#print(Video_Search_Agent.run("https://youtu.be/nVyD6THcvDQ?si=hOgZ80CHu34xj_N9").content)

Links_Search_Agent = Agent(
    name="Links agent",
    model=Gemini(id="gemini-2.0-flash",
                     api_key=os.getenv("GEMINI_API_KEY")),
    role="Search agent",
    tools=[GoogleSearchTools(cache_results=True)],
    instructions=["""You are a Search agent. Obtain the given URL ,analyse and extract the following information.
                  follow this output format:
                  {
                    Title: <title of the content>
                    Source: <source of the content>
                    Upload_Date: <upload date of the content>
                    Summary_captions: <summary of the content>
                    Link: <link to the content>
                  }
                  """],
    #response_model=VideoResponse,
    show_tool_calls=True,
)

#print(Links_Search_Agent.run("http://medium.com/data-science-collective/agentic-ai-comparing-new-open-source-frameworks-21ec676732df").content)


Articles_Search_Agent = Agent(
    name="Articles agent",
    model=Gemini(id="gemini-2.0-flash",
                     api_key=os.getenv("GEMINI_API_KEY")),
    role="Articles agent",
    tools=[JinaReaderTools(cache_results=True),Newspaper4kTools(cache_results=True)],
    instructions=["""You are an Articles agent. The user provides a **URL** pointing to a scientific article. However, Follow these steps carefully:

1. Pass the URL to **Newspaper4kTools** to extract and analyze the article content.
2. Retrieve and return the article information in the following strict format:
{
  Title: <title of the content>,
  Source: <source of the content>,
  Upload_Date: <upload date of the content>,
  Summary_captions: <summary of the content>,
  Link: <link to the content>
}
# additional instructions:
- Ensure the URL is a valid webpage URL.
- If the URL is not valid or the content cannot be retrieved (Time out errors), use Newspaper4kTools().
 """],
    show_tool_calls=True,
    #debug_mode=True,
)

# remarques:
# -also chatgpt and gemini 2.5 can't access to ieeexplore.ieee.org and nature resources
#print(Articles_Search_Agent.run("https://ieeexplore.ieee.org/document/10578990").content)
#print(Articles_Search_Agent.run("https://www.nature.com/articles/s44287-025-00169-3").content)
#print(Articles_Search_Agent.run("https://arxiv.org/abs/2409.17093").content)
#print(Articles_Search_Agent.run("https://www.nature.com/articles/s44287-025-00169-3").content)

Agent_chooser = Agent(
    name="Agent Chooser",
    model=Gemini(id="gemini-2.0-flash",
                     api_key=os.getenv("GEMINI_API_KEY")),
    role="Agent Chooser",
    instructions=["""You are an Agent Chooser. The user provides a **URL** pointing to a scientific article or a video. 
                  You will choose the appropriate agent based on the URL type and return the agent's name.
                  If the URL is a video, use Video_Search_Agent.
                  If the URL is an article, use Articles_Search_Agent.
                  If the URL is a link, use Links_Search_Agent.
                  If the URL is not valid or the content cannot be retrieved, return 'Invalid URL'.
                  **In the output just return the agent name.**
                  """],
    #show_tool_calls=True,
    #debug_mode=True,
)

print(Agent_chooser.run("https://youtu.be/nVyD6THcvDQ?si=hOgZ80CHu34xj_N9").content)
print(Agent_chooser.run("https://arxiv.org/abs/2409.17093").content)