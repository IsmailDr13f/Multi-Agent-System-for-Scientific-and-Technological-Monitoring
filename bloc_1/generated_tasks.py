from typing import List
import asyncio
from agno.agent import Agent
from agno.team.team import Team
from agno.models.google import Gemini
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv  
load_dotenv()
# Load API keys from environment variables
api_key = os.getenv("GEMINI_API_KEY")

# --- Define the Pydantic models for Jira output ---

class Issue(BaseModel):
    id: str = Field(..., description="Unique identifier of the Jira issue")
    key: str = Field(..., description="Jira issue key, e.g. PROJ-123")
    summary: str = Field(..., description="Short summary or title of the issue")
    status: str = Field(..., description="Current status of the issue, e.g. Open, In Progress, Done")
    assignee: str = Field(..., description="User assigned to the issue")
    created_at: str = Field(..., description="Creation timestamp in ISO 8601 format")
    updated_at: str = Field(..., description="Last update timestamp in ISO 8601 format")
    url: str = Field(..., description="Direct link to the issue in Jira")

class JiraData(BaseModel):
    user: str = Field(..., description="Username or email of the user whose Jira data is fetched")
    total_issues: int = Field(..., description="Total number of issues assigned to the user")
    issues: List[Issue] = Field(..., description="List of issues with detailed information")

# --- Define the Pydantic models for Confluence output ---

class Page(BaseModel):
    id: str = Field(..., description="Unique identifier of the Confluence page")
    title: str = Field(..., description="Title of the Confluence page")
    space: str = Field(..., description="Space key or name where the page resides")
    url: str = Field(..., description="Direct link to the Confluence page")
    last_updated: str = Field(..., description="Last update timestamp in ISO 8601 format")
    author: str = Field(..., description="User who last updated the page")
    summary: str = Field(..., description="A brief summary or excerpt of the page content")

class ConfluenceData(BaseModel):
    user: str = Field(..., description="Username or email of the user whose Confluence data is fetched")
    total_pages: int = Field(..., description="Total number of pages edited or created by the user")
    pages: List[Page] = Field(..., description="List of pages with detailed information")

# --- Instantiate the agents ---

jira_agent = Agent(
    model=Gemini(id="gemini-2.0-flash-exp",api_key=api_key),
    description=(
        "You are an expert in Jira. Given a username or email, fetch all issues "
        "assigned to that user and return structured data as per the JiraData model."
    ),
    response_model=JiraData,
)

confluence_agent = Agent(
    model=Gemini(id="gemini-2.0-flash-exp",api_key=api_key),    
    description=(
        "You are an expert in Confluence. Given a username or email, fetch all pages "
        "edited or created by that user and return structured data as per the ConfluenceData model."
    ),
    response_model=ConfluenceData,
)
user_data_generator = Team(
    name="User Data Fetcher",
    mode="collaborate",
    model=Gemini(id="gemini-2.0-flash",api_key=api_key),
    members=[jira_agent, confluence_agent],
    instructions=[
        "You are a team of agents specialized in fetching user data from Jira and Confluence.",
        "Given a username or email, fetch all issues assigned to that user in Jira and all pages edited or created by that user in Confluence.",
        "Return the data in structured format as per the defined models."
    ],
    enable_agentic_context=True,
    show_tool_calls=True,
    markdown=True,
    show_members_responses=True,
    debug_mode=True,
)

# Example usage
if __name__ == "__main__":
    asyncio.run(
        user_data_generator.print_response(
            message="make tasks for a datascientist who is working on a project about LLMs and AI agents",
            stream=True,
            stream_intermediate_steps=True,
        )
    )