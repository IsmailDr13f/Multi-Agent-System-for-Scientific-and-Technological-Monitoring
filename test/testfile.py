"""🎨 Blog Post Generator - Your AI Content Creation Studio!

This advanced example demonstrates how to build a sophisticated blog post generator that combines
web research capabilities with professional writing expertise. The workflow uses a multi-stage
approach:
1. Intelligent web research and source gathering
2. Content extraction and processing
3. Professional blog post writing with proper citations

Key capabilities:
- Advanced web research and source evaluation
- Content scraping and processing
- Professional writing with SEO optimization
- Automatic content caching for efficiency
- Source attribution and fact verification

Example blog topics to try:
- "The Rise of Artificial General Intelligence: Latest Breakthroughs"
- "How Quantum Computing is Revolutionizing Cybersecurity"
- "Sustainable Living in 2024: Practical Tips for Reducing Carbon Footprint"
- "The Future of Work: AI and Human Collaboration"
- "Space Tourism: From Science Fiction to Reality"
- "Mindfulness and Mental Health in the Digital Age"
- "The Evolution of Electric Vehicles: Current State and Future Trends"

Run `pip install openai duckduckgo-search newspaper4k lxml_html_clean sqlalchemy agno` to install dependencies.
"""

import json
from textwrap import dedent
from typing import Dict, Iterator, Optional

from agno.agent import Agent
from agno.models.google import Gemini
from agno.storage.sqlite import SqliteStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools
from agno.utils.log import logger
from agno.utils.pprint import pprint_run_response
from agno.workflow import RunEvent, RunResponse, Workflow
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv

load_dotenv()
gemini_key = os.getenv("GEMINI_API_KEY")
print(f"Gemini Key: {gemini_key}")

from agno.agent import Agent
from agno.tools.searxng import Searxng

# Initialize Searxng with your Searxng instance URL
searxng_ = Searxng(
    host="http://localhost:53153",
    engines=['google', 'bing', 'duckduckgo'],
    fixed_max_results=5,
    news=True,
    science=True
)

# Create an agent with Searxng
agent = Agent(model=Gemini(id="gemini-2.0-flash", api_key=gemini_key), tools=[searxng_],add_name_to_instructions=True,
    debug_mode=True,
    show_tool_calls=True)

# Example: Ask the agent to search using Searxng
agent.print_response("""
Please search for information about artificial intelligence
and summarize the key points from the top results
""")