"""just a test file to check the agents and their functionality
and accessibility
"""
# Test the agents accecibility and functionality
from bloc_2 import (academic_paper_researcher_
    , engine_search_agent_, Video_agent_, linkedin_researcher, task_type_agent)
from agno.models.google import Gemini
from agno.team.team import Team
import os
from dotenv import load_dotenv
from bloc_2.prompt import team_manager_prompt
from agno.playground import Playground, serve_playground_app
from agno.storage.sqlite import SqliteStorage
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory


load_dotenv()

# Load API keys from environment variables
gemini_key = os.getenv("GEMINI_API_KEY")

# Create memory storage
memory_db = SqliteMemoryDb(
    table_name="memories",
    db_file="tmp/memory.db"
)
memory = Memory(db=memory_db)

# Create agent storage
agent_storage = SqliteStorage(
    table_name="agent_sessions",
    db_file="tmp/agent_storage.db"
)



# Team Manager to manage the agents and their interactions
# using OpenRouter model with API key
manager_team_ = Team(
    name="Large Research Team",
    mode="collaborate",
    model=Gemini(id="gemini-2.0-flash",api_key=gemini_key), 
    members=[
        engine_search_agent_,
        academic_paper_researcher_,
        linkedin_researcher,
        Video_agent_,
    ],
    instructions=[team_manager_prompt],
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
    storage=agent_storage,
    enable_user_memories=True,
    monitoring=True,
)


# example usage
# Run the team manager to manage the agents and their interactions
# print(manager_team_.run(user_query))

app = Playground(teams=[manager_team_]).get_app()

if __name__ == "__main__":
    serve_playground_app("playground:app", reload=True)

#from Architecture_1.prompt import acadimic_paper_prompt, engine_search_prompt, Video_agent_prompt, linkedin_research_prompt, task_type_prompt, team_manager_prompt
#print(academic_paper_researcher_.run("What are the latest advancements in gen-AI?").content)
#print(engine_search_agent_.run("What are the latest advancements in AI?").content)
#print(Video_agent_.run("What are the latest advancements in AI?").content)
#print(linkedin_researcher.run("What are the latest advancements in AI?").content)
# All the agents are working and accessible