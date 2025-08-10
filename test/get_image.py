from agno.agent import Agent
from agno.models.google import Gemini
import os
from dotenv import load_dotenv
from agno.tools.website import WebsiteTools

# Load environment variables from .env file
load_dotenv()

agent = Agent(
    model=Gemini(
        id="gemini-2.0-flash",
        api_key=os.getenv("GEMINI_API_KEY"),
    ),
    tools=[WebsiteTools()],
    description="You are a link image search agent that return a image's link from a given website link.",
    instructions=[
        "Given a link by the user, respond with 1 latest image link about that link.",
        "Respond with the image link only, without any additional text.",
    ],
    show_tool_calls=True,
    debug_mode=True,
)

agent.print_response("https://medium.com/not-perfect/want-to-just-start-writing-join-the-write-with-medium-june-micro-challenge-d8a50f0e384a", markdown=True)