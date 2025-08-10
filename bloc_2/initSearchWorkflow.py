from agno.agent import Agent
from agno.run.response import RunResponse
from agno.workflow import Workflow
from typing import List, Optional, Callable
from pydantic import BaseModel, Field
import os
import time
import functools
import asyncio
import inspect
from dotenv import load_dotenv
from textwrap import dedent
from agno.models.google import Gemini
from api_quota_management.quota_mecanisme import GeminiKeyRotator
from AgentsResearchTeam import (
    academic_paper_researcher_,
    engine_search_agent_,
    Video_agent_,
    make_gemini_model,
)
from bloc_1.context_agent import Context_Agent
from pymongo import MongoClient
from datetime import datetime, timezone
import re
import asyncio
import time
from dateutil import parser as date_parser

# === Imports ===
today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# === Load environment ===
load_dotenv()

# === Timing decorators ===
def timed(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        # Get the progress callback from kwargs if available
        progress_callback = kwargs.get('progress_callback')
        if progress_callback:
            progress_callback(f"⏱ Function '{func.__name__}' took {elapsed:.2f}s")
        else:
            print(f"⏱ Function '{func.__name__}' took {elapsed:.2f}s")
        return result
    return wrapper


def async_timed(func):
    if inspect.iscoroutinefunction(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            # Get the progress callback from kwargs if available
            progress_callback = kwargs.get('progress_callback')
            if progress_callback:
                progress_callback(f"⏱️ Async function '{func.__name__}' took {elapsed_time:.2f} seconds")
            else:
                print(f"⏱️ Async function '{func.__name__}' took {elapsed_time:.2f} seconds")
            return result
        return wrapper
    else:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            # Get the progress callback from kwargs if available
            progress_callback = kwargs.get('progress_callback')
            if progress_callback:
                progress_callback(f"⏱️ Sync function '{func.__name__}' took {elapsed_time:.2f} seconds")
            else:
                print(f"⏱️ Sync function '{func.__name__}' took {elapsed_time:.2f} seconds")
            return result
        return wrapper


# === Models ===
class UnifiedResponse(BaseModel):
    Title: str = Field(..., description="The title of the response.")
    Source: str = Field(..., description="The source of the information.")
    Type: str = Field(..., description="Type of the response (e.g., paper, video, social media, blog).")
    Publication_Date: float = Field(..., description="Publication date of the response.")
    Summary: str = Field(..., description="Summary of the response.")
    Link: str = Field(..., description="Link to the source.")
    Key_words: Optional[List[str]] = Field(..., description="List of key words associated with the response.")
    Image_link: str = Field(..., description="Link to the image associated with the response.")

class SearchResponse(BaseModel):
    results: List[UnifiedResponse] = Field(..., description="List of search results.")

class UserContext(BaseModel):
    User_identity: str = Field(..., description="User's professional identity and role")
    User_email: str = Field(..., description="User's email address")
    News_Interests: str = Field(..., description="User's specific interests and areas of focus")
    Usage_Timing: str = Field(..., description="User's availability and preferred usage periods")
    Special_notes: str = Field(..., description="Any special requirements or notes about the user")
    Search_Context: str = Field(..., description="Comprehensive context for tailoring the search")


# === Workflow ===
class initSearchWorkflow(Workflow):
    class Config:
        arbitrary_types_allowed = True

    def __init__(self, name: str, agents: List[Agent], **kwargs):
        super().__init__(name=name, **kwargs)
        self.agents = agents
        self.storage = kwargs.get("storage")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.rotator = GeminiKeyRotator()
        self.progress_callback: Optional[Callable[[str], None]] = None
        self.context_agent = Context_Agent  # Add context agent

        self.result_structurer = Agent(
            model=make_gemini_model(),
            description=dedent(f"""
                You are tasked with unifying and structuring the outputs from multiple search agents.
                Your responsibilities include:
                
                - Parsing raw search results from various sources, including academic papers, web pages and videos
                - Formatting ALL extracted data according to the UnifiedResponse schema
                - For dates: if you cannot parse a date properly, use a reasonable default (e.g., current year)
                - DO NOT filter out results unless they are clearly invalid or duplicated
                - Preserve ALL unique and valid results from the input
                - If you encounter any parsing issues, include the result with best-effort parsing rather than excluding it

                IMPORTANT: Your goal is to preserve and structure ALL results, not to filter them.
                Today's date for reference: {today}
                """),
            response_model=SearchResponse,
        )

    def set_progress_callback(self, callback: Callable[[str], None]):
        """Set a callback function to receive progress updates"""
        self.progress_callback = callback

    def _log_progress(self, message: str):
        """Log progress message using callback or print"""
        if self.progress_callback:
            self.progress_callback(message)
        else:
            print(message)

    def get_user_profile_from_db(self, user_email: str) -> dict:
        """Retrieve user profile from MongoDB"""
        self._log_progress(f"👤 Retrieving user profile for: {user_email}")
        
        client = MongoClient("mongodb://localhost:27017/")
        db = client["newsfeed_db"]
        # Assuming you have a users collection - adjust collection name as needed
        users_collection = db["users"]  
        
        try:
            user_profile = users_collection.find_one({"email": user_email})
            if user_profile:
                self._log_progress(f"✅ User profile found for: {user_email}")
                return user_profile
            else:
                self._log_progress(f"⚠️ No user profile found for: {user_email}")
                # Return a default profile structure
                return {
                    "name": "Unknown User",
                    "email": user_email,
                    "role": "General User",
                    "laboratory": "N/A",
                    "preferences": ["General Technology", "AI", "Machine Learning"],
                    "availability": "Part-time",
                    "preferred_usage_periods": ["🕐 Any time"],
                    "comment": "General user with interest in technology updates."
                }
        except Exception as e:
            self._log_progress(f"❌ Error retrieving user profile: {e}")
            # Return a minimal default profile
            return {
                "name": "Unknown User",
                "email": user_email,
                "role": "General User",
                "laboratory": "N/A",
                "preferences": ["Technology"],
                "availability": "Part-time",
                "preferred_usage_periods": ["🕐 Any time"],
                "comment": "Default user profile."
            }

    @async_timed
    async def extract_user_context(self, user_email: str) -> UserContext:
        """Extract user context using the Context Agent"""
        self._log_progress("🧠 Extracting user context...")
        
        # Get user profile from database
        user_profile = self.get_user_profile_from_db(user_email)
        
        # Convert user profile to string format for Context Agent
        user_profile_str = str(user_profile)
        
        try:
            # Run context agent
            context_start = time.time()
            context_response = await asyncio.to_thread(
                self.context_agent.run, user_profile_str
            )
            elapsed = time.time() - context_start
            self._log_progress(f"🧠 Context extraction completed in {elapsed:.2f}s")
            
            if context_response and context_response.content:
                # Parse the context response content
                context_content = str(context_response.content)
                self._log_progress(f"📄 Raw context: {context_content[:200]}...")
                
                # Extract structured information from the context response
                # The context agent returns a formatted string, we need to parse it
                user_context = self._parse_context_response(context_content, user_email)
                
                self._log_progress(f"✅ User context extracted successfully")
                return user_context
            else:
                self._log_progress("⚠️ Context agent returned no content, using default context")
                return self._create_default_context(user_profile)
                
        except Exception as e:
            self._log_progress(f"❌ Error extracting user context: {e}")
            return self._create_default_context(user_profile)

    def _parse_context_response(self, context_content: str, user_email: str) -> UserContext:
        """Parse the context agent response into structured UserContext"""
        # The context agent returns structured information, extract it
        try:
            # Initialize default values
            user_identity = "General User"
            news_interests = "Technology, AI"
            usage_timing = "Flexible"
            special_notes = "No specific requirements"
            search_context = f"General technology updates for {user_email}"
            
            # Parse the context content (assuming it follows the format shown in your example)
            lines = context_content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith("User_identity="):
                    user_identity = line.split("=", 1)[1].strip("'\"")
                elif line.startswith("News_Interests="):
                    news_interests = line.split("=", 1)[1].strip("'\"")
                elif line.startswith("Usage_Timing="):
                    usage_timing = line.split("=", 1)[1].strip("'\"")
                elif line.startswith("Special_notes="):
                    special_notes = line.split("=", 1)[1].strip("'\"")
                elif line.startswith("Search_Context="):
                    search_context = line.split("=", 1)[1].strip("'\"")
            
            return UserContext(
                User_identity=user_identity,
                User_email=user_email,
                News_Interests=news_interests,
                Usage_Timing=usage_timing,
                Special_notes=special_notes,
                Search_Context=search_context
            )
            
        except Exception as e:
            self._log_progress(f"⚠️ Error parsing context response: {e}")
            return self._create_default_context({"email": user_email})

    def _create_default_context(self, user_profile: dict) -> UserContext:
        """Create a default user context from user profile"""
        return UserContext(
            User_identity=f"{user_profile.get('role', 'General User')} at {user_profile.get('laboratory', 'N/A')}",
            User_email=user_profile.get('email', ''),
            News_Interests=', '.join(user_profile.get('preferences', ['Technology', 'AI'])),
            Usage_Timing=user_profile.get('availability', 'Flexible'),
            Special_notes=user_profile.get('comment', 'General interest in technology updates'),
            Search_Context=f"User seeks relevant updates in their areas of interest: {', '.join(user_profile.get('preferences', ['Technology']))}"
        )

    def _enhance_topic_with_context(self, topic: str, user_context: UserContext) -> str:
        """Enhance the search topic with user context"""
        enhanced_topic = f"""
        Original Topic: {topic}
        
        User Context:
        - Identity: {user_context.User_identity}
        - Interests: {user_context.News_Interests}
        - Usage: {user_context.Usage_Timing}
        - Special Notes: {user_context.Special_notes}
        
        Search Context: {user_context.Search_Context}
        
        Please focus on finding content that is relevant to this user's specific interests and professional context.
        """
        return enhanced_topic.strip()

    from datetime import datetime, timezone
    from dateutil import parser as date_parser

    def float_to_date(self, float_date) -> datetime | None:
        self._log_progress(f"🔄 Processing date: {float_date}")
        # Si c'est un nombre (float ou int), on le convertit en string
        if isinstance(float_date, (int, float)):
            s = str(int(float_date))
        elif isinstance(float_date, str):
            s = float_date.strip()
        else:
            return None

        # Cas des timestamps en millisecondes
        if re.fullmatch(r"\d{13}", s):
            try:
                return datetime.fromtimestamp(int(s) / 1000, tz=timezone.utc)
            except Exception:
                return None

        # Cas des timestamps en secondes
        elif re.fullmatch(r"\d{10}", s):
            try:
                return datetime.fromtimestamp(int(s), tz=timezone.utc)
            except Exception:
                return None

        # Tentative de parsing ISO 8601 comme "2025-06-22T00:00:00.000Z"
        iso_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$"
        if re.fullmatch(iso_pattern, s):
            try:
                print(f"🔄 Parsing ISO 8601 date: {s}")  # Debugging output
                return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            except ValueError:
                try:
                    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                except Exception:
                    return None

        # Nettoyage pour les formats compacts
        s_clean = re.sub(r"[^\d]", "", s)
        try:
            if len(s_clean) == 8:
                return datetime.strptime(s_clean, "%Y%m%d")
            elif len(s_clean) == 6:
                return datetime.strptime(s_clean, "%Y%m").replace(day=1)
            elif len(s_clean) == 4:
                return datetime.strptime(s_clean, "%Y").replace(month=1, day=1)
        except Exception:
            pass

        # Fallback avec dateutil pour gérer d'autres cas
        try:
            return date_parser.parse(s)
        except Exception:
            return None

    def save_run_response_to_mongodb(self, run_response, topic: str, user_email: str, user_context: UserContext):
        """Sauvegarde les résultats en base de données avec l'email de l'utilisateur et le contexte"""
        self._log_progress("💾 Saving results to MongoDB...")
        
        client = MongoClient("mongodb://localhost:27017/")
        db = client["newsfeed_db"]
        collection = db["feednews"]

        created_at_dt = datetime.fromtimestamp(run_response.created_at)

        doc = {
            "run_id": run_response.run_id,
            "user_email": user_email,  
            "topic": topic,
            "user_context": {
                "identity": user_context.User_identity,
                "interests": user_context.News_Interests,
                "usage_timing": user_context.Usage_Timing,
                "special_notes": user_context.Special_notes,
                "search_context": user_context.Search_Context
            },
            "created_at": created_at_dt,
            "results": [],
        }

        for item in run_response.content.results:
            print(f"🔄 Processing item: {item.Publication_Date}")  # Debugging output
            print(f"type de date: {type(item.Publication_Date)}")  # Debugging output
            doc["results"].append({
                "title": item.Title,
                "source": item.Source,
                "publication_date": self.float_to_date(item.Publication_Date),
                "summary": item.Summary,
                "link": item.Link,
                "image_link": item.Image_link,
                "key_words": item.Key_words,
            })

        try:
            collection.insert_one(doc)
            self._log_progress(f"✅ Results saved to MongoDB successfully for user: {user_email}")
            self._log_progress(f"📊 Saved {len(doc['results'])} results with user context")
        except Exception as e:
            self._log_progress(f"❌ Error saving to MongoDB: {e}")

    # Méthode run() avec user_email
    def run(self, topic: str, user_email: str) -> RunResponse:
        """Execute the workflow with user identification"""
        return asyncio.run(self._async_run(topic, user_email))
    
    # Méthode run_with_progress()
    def run_with_progress(self, topic: str, user_email: str, progress_callback: Callable[[str], None]) -> RunResponse:
        """Execute the workflow with progress tracking and user identification"""
        self.set_progress_callback(progress_callback)
        return asyncio.run(self._async_run(topic, user_email))
    
    # _async_run() avec user_email comme paramètre obligatoire et intégration du Context Agent
    async def _async_run(self, topic: str, user_email: str) -> RunResponse:
        self._log_progress(f"🚀 Starting enhanced search workflow for topic: {topic} (User: {user_email})")
        
        # Step 1: Extract user context
        user_context = await self.extract_user_context(user_email)
        self._log_progress(f"👤 User context: {user_context.User_identity}")
        self._log_progress(f"🎯 Interests: {user_context.News_Interests}")
        
        # Step 2: Enhance topic with user context
        enhanced_topic = self._enhance_topic_with_context(topic, user_context)
        self._log_progress(f"📈 Enhanced topic with user context")
        
        # Step 3: Run search agents with enhanced topic
        all_contents = []

        async def run_agent(agent: Agent, agent_name: str):
            self._log_progress(f"🔍 Running {agent_name} agent with personalized context...")
            result = await asyncio.to_thread(agent.run, enhanced_topic)
            self._log_progress(f"✅ {agent_name} agent completed")
            return result

        # Get agent names for better progress tracking
        agent_names = ["Academic Paper Researcher", "Search Engine Agent", "Video Agent", "Social Media Researcher"]
        available_agents = self.agents[:len(agent_names)]
        
        # Time agents in parallel
        agent_start = time.time()
        self._log_progress(f"⚙️ Running {len(available_agents)} agents in parallel with personalized context...")
        
        # Create tasks with agent names
        tasks = [run_agent(agent, agent_names[i]) for i, agent in enumerate(available_agents)]
        responses = await asyncio.gather(*tasks)
        
        elapsed = time.time() - agent_start
        self._log_progress(f"⚙️ All agents finished in {elapsed:.2f}s")

        # Process responses with detailed logging
        valid_responses = 0
        total_raw_results = 0
        
        for i, response in enumerate(responses):
            if response and response.content:
                print(response.content)  # Debugging output
                all_contents.append(response.content)
                valid_responses += 1
                
                # Try to count results in raw content (debugging)
                content_str = str(response.content)
                # This is a rough estimate - you might need to adjust based on your agent's output format
                estimated_results = content_str.count('\n\n') + content_str.count('Title:') + content_str.count('"title"')
                total_raw_results += estimated_results
                self._log_progress(f"📊 {agent_names[i]} provided ~{estimated_results} results")
            else:
                self._log_progress(f"⚠️ {agent_names[i]} returned no content")
        
        self._log_progress(f"📊 Collected {valid_responses} valid responses from {len(responses)} agents")
        self._log_progress(f"📊 Estimated total raw results: {total_raw_results}")

        combined_input = "\n\n".join(str(c) for c in all_contents)
        
        # Add user context to the structuring input
        contextualized_input = f"""
        USER CONTEXT:
        {user_context.Search_Context}
        
        SEARCH RESULTS:
        {combined_input}
        """
        
        # Log input size for debugging
        input_size = len(contextualized_input)
        self._log_progress(f"📏 Combined input size: {input_size} characters")
        
        # If input is too large, consider chunking
        if input_size > 50000:  # Adjust threshold as needed
            self._log_progress("⚠️ Input size is large - this might cause issues with the structurer")

        # Structure results
        structure_start = time.time()
        self._log_progress("📦 Structuring and validating results with user context...")
        
        try:
            structuring_response: RunResponse = await asyncio.to_thread(
                self.result_structurer.run, contextualized_input
            )
        except Exception as e:
            self._log_progress(f"❌ Error during structuring: {e}")
            raise
        
        elapsed = time.time() - structure_start
        self._log_progress(f"📦 Structuring completed in {elapsed:.2f}s")

        if structuring_response and isinstance(structuring_response.content, SearchResponse):
            result_count = len(structuring_response.content.results)
            self._log_progress(f"✨ Successfully structured {result_count} personalized results")
            
            # Log the ratio for debugging
            if total_raw_results > 0:
                ratio = result_count / total_raw_results
                self._log_progress(f"📊 Result preservation ratio: {ratio:.2%} ({result_count}/{total_raw_results})")
            
            rr = RunResponse(content=structuring_response.content)
            self.save_run_response_to_mongodb(rr, topic, user_email, user_context)
            
            self._log_progress("🎉 Enhanced workflow completed successfully!")
            return rr
        else:
            error_msg = "❌ Failed to structure the search results properly"
            self._log_progress(error_msg)
            
            # Additional debugging info
            if structuring_response:
                self._log_progress(f"🔍 Structuring response type: {type(structuring_response.content)}")
                self._log_progress(f"🔍 Structuring response content: {str(structuring_response.content)[:500]}...")
            
            raise ValueError(error_msg)

    # MÉTHODES UTILITAIRES SUPPLÉMENTAIRES
    def get_user_searches(self, user_email: str, limit: int = 10) -> List[dict]:
        """Récupère les recherches précédentes d'un utilisateur"""
        client = MongoClient("mongodb://localhost:27017/")
        db = client["newsfeed_db"]
        collection = db["feednews"]
        
        try:
            searches = list(collection.find(
                {"user_email": user_email},
                {"topic": 1, "created_at": 1, "run_id": 1, "user_context": 1, "_id": 0}
            ).sort("created_at", -1).limit(limit))
            
            return searches
        except Exception as e:
            self._log_progress(f"❌ Error retrieving user searches: {e}")
            return []

    def get_search_results(self, user_email: str, run_id: str) -> dict:
        """Récupère les résultats d'une recherche spécifique"""
        client = MongoClient("mongodb://localhost:27017/")
        db = client["newsfeed_db"]
        collection = db["feednews"]
        
        try:
            result = collection.find_one({
                "user_email": user_email,
                "run_id": run_id
            })
            return result
        except Exception as e:
            self._log_progress(f"❌ Error retrieving search results: {e}")
            return {}

    def get_user_context_history(self, user_email: str) -> List[dict]:
        """Récupère l'historique des contextes utilisateur pour analyse des préférences"""
        client = MongoClient("mongodb://localhost:27017/")
        db = client["newsfeed_db"]
        collection = db["feednews"]
        
        try:
            contexts = list(collection.find(
                {"user_email": user_email, "user_context": {"$exists": True}},
                {"user_context": 1, "created_at": 1, "topic": 1, "_id": 0}
            ).sort("created_at", -1).limit(20))
            
            return contexts
        except Exception as e:
            self._log_progress(f"❌ Error retrieving user context history: {e}")
            return []


# === Main execution ===
if __name__ == "__main__":
    workflow = initSearchWorkflow(
        name="SmartSearchWorkflow",
        agents=[
            academic_paper_researcher_,
            engine_search_agent_,
            Video_agent_,
        ],
    )

    # Appel avec user_email et contexte personnalisé
    user_email = "driefismail722@gmail.com"  # À remplacer par l'email réel de l'utilisateur
    result = workflow.run(topic="AI and workflows", user_email=user_email)
    print(f"Enhanced search completed for user: {user_email}")
    print(f"Results count: {len(result.content.results)}")
    
    # Exemple d'utilisation des méthodes utilitaires améliorées
    print("\n--- User's previous searches with context ---")
    previous_searches = workflow.get_user_searches(user_email)
    for search in previous_searches:
        print(f"- {search['topic']} (Run ID: {search['run_id']}, Date: {search['created_at']})")
        if 'user_context' in search:
            print(f"  Context: {search['user_context']['identity']}")
            print(f"  Interests: {search['user_context']['interests']}")
    
    print("\n--- User's context evolution ---")
    context_history = workflow.get_user_context_history(user_email)
    for ctx in context_history[:3]:  # Show last 3 contexts
        print(f"- {ctx['topic']} ({ctx['created_at']})")
        print(f"  Identity: {ctx['user_context']['identity']}")
        print(f"  Interests: {ctx['user_context']['interests']}")