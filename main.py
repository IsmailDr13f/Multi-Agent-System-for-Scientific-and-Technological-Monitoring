"""just a test file to check the agents and their functionality
and accessibility
"""
# Test the agents accecibility and functionality
from bloc_2 import (academic_paper_researcher_, engine_search_agent_, Video_agent_, social_media_researcher)
from agno.models.google import Gemini
from agno.team.team import Team
import os
from dotenv import load_dotenv
from bloc_2.prompt import team_manager_prompt,team_manager_prompt_
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from api_quota_management.quota_mecanisme import GeminiKeyRotator


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
rotator = GeminiKeyRotator()
gemini_key = os.getenv("GEMINI_API_KEY")

# Create memory storage
memory_db = SqliteMemoryDb(
    table_name="memories",
    db_file="tmp/memory.db"
)
memory = Memory(db=memory_db)



# Team Manager to manage the agents and their interactions
# using OpenRouter model with API key
agent_orchestrateur = Team(
    name="Large Research Team",
    mode="collaborate",
    model=Gemini(id="gemini-2.0-flash",api_key=rotator.get_current_key()), 
    members=[
        engine_search_agent_,
        academic_paper_researcher_,
        social_media_researcher,
        Video_agent_,
    ],
    instructions=[team_manager_prompt],
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

agent_orchestrateur.print_response(
    """Image Classification, Object Detection, Image Segmentation, Video Analysis, 3D Reconstruction""")

