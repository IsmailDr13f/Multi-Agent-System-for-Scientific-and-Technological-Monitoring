# Test the agents accecibility and functionality

from AgentsResearchTeam import (academic_paper_researcher_, engine_search_agent_, Video_agent_, social_media_researcher)
from agno.models.google import Gemini
from agno.team.team import Team
import os
from dotenv import load_dotenv
from prompt_ import team_manager_prompt,team_manager_prompt_,Video_agent_prompt
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
#import os
#import sys
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api_quota_management.quota_mecanisme import GeminiKeyRotator
from textwrap import dedent
from agno.storage.mongodb import MongoDbStorage

db_url = "mongodb://localhost:27017/"

# Create a storage backend using the Mongo database
storage = MongoDbStorage(
    # store sessions in the agent_sessions collection
    collection_name="agents_output",
    db_url=db_url,
)

load_dotenv()

# Load API keys from environment variables
#rotator = GeminiKeyRotator()
gemini_key = os.getenv("GEMINI_API_KEY")

# Create memory storage
memory_db = SqliteMemoryDb(
    table_name="memories",
    db_file="tmp/memory.db"
)
memory = Memory(db=memory_db)


Video_agent_.instructions = dedent(Video_agent_prompt)
# Team Manager to manage the agents and their interactions
# using OpenRouter model with API key
Orchestrateur_Agent = Team(
    name="Newsfeed Orchestrator",
    mode="route",
    model=Gemini(id="gemini-2.0-flash",api_key=gemini_key), 
    members=[
        engine_search_agent_,
        academic_paper_researcher_,
        social_media_researcher,
        Video_agent_,
    ],
    #instructions=[team_manager_prompt_],
    storage=storage,
    enable_agentic_context=True,
    show_tool_calls=True,
    markdown=True,
    show_members_responses=True,
    debug_mode=True,
    success_criteria="The team has reached a consensus on the topic",
    add_datetime_to_instructions=True,
    enable_team_history=True,
    num_of_interactions_from_history=5,
    memory=memory,
    enable_agentic_memory=True,
    enable_user_memories=True,
    monitoring=True,
)
#print(Video_agent_.instructions[0])
#Orchestrateur_Agent.print_response(
#    """https://youtu.be/FwOTs4UxQS4?si=4sOzf3XF_kANZPch""")