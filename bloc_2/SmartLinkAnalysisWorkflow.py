from agno.agent import Agent
from agno.workflow import Workflow
from agno.run.response import RunResponse
from agno.models.google import Gemini
from pydantic import BaseModel, Field
from typing import List, Optional
from textwrap import dedent
from datetime import datetime
import os
import re
from dotenv import load_dotenv

# Import des agents spécifiques
from AgentsResearchTeam import (
    link_search_agent
)

load_dotenv()

# === Step 1: Define the unified response schema ===
class StructuredResponse(BaseModel):
    Title: str = Field(..., description="The title of the response.")
    Source: str = Field(..., description="The source of the information.")
    Type: str = Field(..., description="Type of the response (e.g., paper, video, social media, blog).")
    Publication_Date: float = Field(..., description="Publication date of the response.")
    Summary: str = Field(..., description="Summary of the response.")
    Link: str = Field(..., description="Link to the source.")
    Key_words: Optional[List[str]] = Field(..., description="List of key words associated with the response.")
    Image_link: str = Field(..., description="Link to the image associated with the response.")

# === Step 2: Define the workflow ===
class SmartLinkAnalysisWorkflow(Workflow):
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, **kwargs)
        
        
        # Agent de structuration
        self.structuring_agent = Agent(
            model=Gemini(id="gemini-2.0-flash", api_key=os.getenv("GEMINI_API_KEY")),
            response_model=StructuredResponse,
        )
    
    def run_workflow(self, url: str) -> RunResponse:
        raw_response = link_search_agent.run(url)
        raw_content = str(raw_response.content)
        
        # === Step 5: Structurer la réponse ===
        structured_response = self.structuring_agent.run(raw_content)
        
        if isinstance(structured_response.content, StructuredResponse):
            return RunResponse(content=structured_response.content)
        else:
            raise ValueError("Failed to structure the output properly.")

if __name__ == "__main__":
    workflow = SmartLinkAnalysisWorkflow(name="URL Intelligence Workflow")
    url = "https://arxiv.org/abs/2409.17093"
    
    result = workflow.run_workflow(url)  # Changé de run() à run_workflow()
    print(result)