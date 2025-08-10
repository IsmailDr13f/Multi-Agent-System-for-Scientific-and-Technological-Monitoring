
from agno.playground import Playground, serve_playground_app
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))
from bloc_2.AgentsResearchTeam import chat_agent

playground = Playground(
    agents=[
        chat_agent,
    ],
    
)
app = playground.get_app()

if __name__ == "__main__":
    #playground.serve(app="basic:app", reload=True)
    serve_playground_app("test_chatagent:app", reload=True, port=7777)