from textwrap import dedent
from agno.agent import Agent
from agno.tools.exa import ExaTools
from agno.models.google import Gemini
from dotenv import load_dotenv
import os
load_dotenv()
from datetime import date

sources = [
    "journals.plos.org",
    "nature.com",
    "frontiersin.org",
    "mdpi.com",
    "ieeexplore.ieee.org",
    "jmlr.org",
    "ncbi.nlm.nih.gov",
    #"arxiv.org",
    "doaj.org",
    "semanticscholar.org",
    "scholar.google.com",
    "thinkchecksubmit.org"
]


def generate_academic_prompt(topic: str, today: date) -> str:
    year = today.year
    academic_paper_prompt_ = f"""
You are a highly skilled academic research assistant specializing in scientific papers, peer-reviewed articles, and scholarly discussions.
You MUST use the provided academic search tool (Exa) to find relevant papers. Do not generate results without querying the tool.


Research Topic: {topic}  
Your Responsibilities:
- Search for the most recent and most relevant scholarly articles, preprints, and academic discussions on the topic.
- Pay special attention to publication dates to ensure temporal relevance and highlight the state of the art.
- Prioritize peer-reviewed publications, high-impact journals, and recognized preprint servers (e.g., ArXiv, IEEE,...).
- For each article, provide:
  1. Title of the paper
  2. Authors and publication year
  3. Date of publication or preprint submission
  4. A concise summary (3–5 sentences) covering the research objective, methodology, and key results
  5. Link to the full text or citation
- Indicate whether the article contributes to the state of the art and in what way (e.g., introducing a novel method, improving performance, synthesizing trends).
- Identify emerging themes, new subfields, or open research questions based on the literature.

Output Format:
- Use Markdown structured lists
- Group articles by thematic relevance where appropriate
- Highlight state-of-the-art contributions explicitly
- Ensure all links are active and citations are properly formatted

Your Final Output Should Serve As:
A clear, concise, and insightful research digest that a scientist, PhD student, or technical expert could use as a launching pad for deeper investigation or as context for their own research.

Example Output Format:
{{ 
  "academic_papers": [
  {{- Title: ...  
  - Authors : ...  
  - Publication_date: ...  
  - Abstract: ...  
  - key_findings: ...  
  - link: ...}},
  {{}},...
  ],
}}

7. Do NOT include any explanation, summary, or text outside this JSON output.

Additional Instructions for Academic Paper Researcher:  
- Search the listed trusted academic sources only.  
- Focus on papers published/submitted in this year only **{year}**.  
"""
    return academic_paper_prompt_



def get_academic_papers(topic: str) -> str:
    today = date.today()
    prompt = generate_academic_prompt(topic=topic, today=today)
    RP_Agent = Agent(
    model=Gemini("gemini-2.0-flash", api_key=os.getenv("GEMINI_API_KEY")),
    tools=[ExaTools(
        include_domains=sources,
        category="article",
        text_length_limit=1000,
    )],
    instructions=dedent(prompt),
    show_tool_calls=True,
    debug_mode=True,
)
    return RP_Agent.run(topic).content


#print(get_academic_papers("Agentic AI"))

agent = Agent(
    model=Gemini("gemini-2.0-flash", api_key=os.getenv("GEMINI_API_KEY")),
    tools=[ExaTools(
        include_domains=sources,#["cnbc.com", "reuters.com", "bloomberg.com"],
        category="article",
        text_length_limit=1000,
    )],
    show_tool_calls=True,
    debug_mode=True,
    instructions="""Get the response in this format:
        {- Title: ...  
        - Authors : ...  
        - Publication_date: ...  
        - Abstract: ...  
        - key_findings: ...  
        - link: ...
        }
        """,
)
agent.print_response("Agentic AI in 31/05/2025 papers", markdown=True)


