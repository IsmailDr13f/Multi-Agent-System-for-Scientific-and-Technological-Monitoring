import streamlit as st
from datetime import date
import threading
import time
import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from bloc_2.SearchWorkflow import SearchWorkflow

from bloc_2.AgentsResearchTeam import (
    academic_paper_researcher_,
    engine_search_agent_,
    Video_agent_,
    social_media_researcher,    
)

# Variables globales pour gérer l'état
if 'last_refresh_date' not in st.session_state:
    st.session_state.last_refresh_date = {}
if 'refresh_in_progress' not in st.session_state:
    st.session_state.refresh_in_progress = False
if 'new_preferences' not in st.session_state:
    st.session_state.new_preferences = set()

def mark_preference_as_new(preference):
    """Marque une préférence comme nouvelle"""
    if 'new_preferences' not in st.session_state:
        st.session_state.new_preferences = set()
    st.session_state.new_preferences.add(preference)

def get_preferences_to_refresh(preferences):
    """Détermine quelles préférences doivent être rafraîchies"""
    today = date.today()
    preferences_to_refresh = []
    
    # Vérifier les nouvelles préférences
    if hasattr(st.session_state, 'new_preferences') and st.session_state.new_preferences:
        for new_pref in st.session_state.new_preferences:
            if new_pref in preferences:
                preferences_to_refresh.append(new_pref)
        # Nettoyer les nouvelles préférences après traitement
        st.session_state.new_preferences.clear()
        return preferences_to_refresh, "new_preferences"
    
    # Vérifier les préférences qui n'ont pas été rafraîchies aujourd'hui
    for pref in preferences:
        last_refresh = st.session_state.last_refresh_date.get(pref)
        if last_refresh != today:
            preferences_to_refresh.append(pref)
    
    if not preferences_to_refresh:
        return [], "up_to_date"
    
    return preferences_to_refresh, "daily_refresh"

def show_progress_status(preferences_to_refresh, refresh_type):
    """Display progress status with enhanced workflow tracking"""
    if refresh_type == "new_preferences":
        st.info(f"📋 Processing new preferences: {', '.join(preferences_to_refresh)}")
    else:
        st.info(f"📋 Daily refresh for: {', '.join(preferences_to_refresh)}")
    
    # Create progress tracking containers
    overall_progress = st.progress(0)
    current_topic_text = st.empty()
    
    # Container for detailed progress messages
    progress_container = st.container()
    with progress_container:
        st.markdown("**Detailed Progress:**")
        progress_messages = st.empty()
    
    # Initialize progress tracking
    total_prefs = len(preferences_to_refresh)
    all_messages = []
    
    # Create workflow
    workflow = SearchWorkflow(
        name="SmartSearchWorkflow",
        agents=[
            academic_paper_researcher_,
            engine_search_agent_,
            Video_agent_,
            social_media_researcher,
        ],
    )
    
    results = []
    
    for i, pref in enumerate(preferences_to_refresh):
        current_topic_text.markdown(f"**Currently processing:** `{pref}` ({i+1}/{total_prefs})")
        
        # Create a progress callback for this topic
        def progress_callback(message):
            all_messages.append(f"• {message}")
            # Keep only last 8 messages to avoid overwhelming the display
            display_messages = all_messages[-8:]
            progress_messages.text("\n".join(display_messages))
        
        try:
            # Run workflow with progress callback
            result = workflow.run_with_progress(topic=pref, progress_callback=progress_callback)
            results.append((pref, result))
            
            # Mark as refreshed today
            st.session_state.last_refresh_date[pref] = date.today()
            
            # Add completion message
            completion_msg = f"✅ Topic '{pref}' completed successfully!"
            all_messages.append(f"• {completion_msg}")
            progress_messages.text("\n".join(all_messages[-8:]))
            
        except Exception as e:
            error_msg = f"❌ Error processing {pref}: {str(e)}"
            all_messages.append(f"• {error_msg}")
            progress_messages.text("\n".join(all_messages[-8:]))
            results.append((pref, f"Error: {e}"))
        
        # Update overall progress
        overall_progress.progress((i + 1) / total_prefs)
    
    # Final status
    current_topic_text.markdown("**✅ All topics completed!**")
    overall_progress.progress(1.0)
    
    # Success summary
    successful_topics = [pref for pref, result in results if not str(result).startswith("Error:")]
    failed_topics = [pref for pref, result in results if str(result).startswith("Error:")]
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("✅ Successful", len(successful_topics))
    with col2:
        st.metric("❌ Failed", len(failed_topics))
    
    if successful_topics:
        st.success(f"Successfully processed: {', '.join(successful_topics)}")
    if failed_topics:
        st.error(f"Failed to process: {', '.join(failed_topics)}")
    
    return results

def refresh_news_workflow(preferences_to_refresh, progress_callback=None):
    """Execute workflow for given preferences with optional progress callback"""
    workflow = SearchWorkflow(
        name="SmartSearchWorkflow",
        agents=[
            academic_paper_researcher_,
            engine_search_agent_,
            Video_agent_,
            social_media_researcher,
        ],
    )
    
    results = []
    for pref in preferences_to_refresh:
        if progress_callback:
            progress_callback(f"_____Running workflow for topic: {pref}_____")
        else:
            print(f"_____Running workflow for topic: {pref}_____")
        
        try:
            if progress_callback:
                result = workflow.run_with_progress(topic=pref, progress_callback=progress_callback)
            else:
                result = workflow.run(topic=pref)
            results.append((pref, result))
            
            if progress_callback:
                progress_callback(f"✅ Completed workflow for topic: {pref}")
            else:
                print(result)
            
            # Mark as refreshed today
            st.session_state.last_refresh_date[pref] = date.today()
            
        except Exception as e:
            error_msg = f"Error processing {pref}: {e}"
            if progress_callback:
                progress_callback(f"❌ {error_msg}")
            else:
                print(error_msg)
            results.append((pref, f"Error: {e}"))
    
    return results

def refresh_news(preferences):
    """
    Main news refresh function with dialog progress display
    
    Args:
        preferences (list): List of user preferences
    """
    # Initialize session state variables if they don't exist
    if 'last_refresh_date' not in st.session_state:
        st.session_state.last_refresh_date = {}
    if 'refresh_in_progress' not in st.session_state:
        st.session_state.refresh_in_progress = False
    if 'new_preferences' not in st.session_state:
        st.session_state.new_preferences = set()
    
    # Check if refresh is already in progress
    if st.session_state.refresh_in_progress:
        st.warning("⏳ A refresh is already in progress. Please wait...")
        return
    
    # Determine which preferences to refresh
    preferences_to_refresh, refresh_type = get_preferences_to_refresh(preferences)
    
    # Check if everything is up to date
    if refresh_type == "up_to_date":
        st.success("✅ All your news is up to date!")
        st.info("💡 News is refreshed once per day.")
        return
    
    # Mark refresh as in progress
    st.session_state.refresh_in_progress = True
    
    try:
        # Show progress status and execute workflow
        results = show_progress_status(preferences_to_refresh, refresh_type)
        
        # Display final results summary in main interface
        if refresh_type == "new_preferences":
            st.success(f"✅ New preferences processed: {', '.join(preferences_to_refresh)}")
        else:
            st.success(f"✅ Daily refresh completed for: {', '.join(preferences_to_refresh)}")
        
        # Optional: show results summary
        with st.expander("📊 Refresh Details", expanded=False):
            for pref, result in results:
                if str(result).startswith("Error:"):
                    st.error(f"**{pref}:** {result}")
                else:
                    st.success(f"**{pref}:** Successfully retrieved and processed data")
    
    except Exception as e:
        st.error(f"❌ Error during refresh: {e}")
    
    finally:
        # Mark refresh as completed
        st.session_state.refresh_in_progress = False

import io
import sys
from contextlib import redirect_stdout
def refresh_news_(preferences):
    """
    Refresh news for a list of preferences with live print display.
    """
    if 'last_refresh_date' not in st.session_state:
        st.session_state.last_refresh_date = {}
    if 'refresh_in_progress' not in st.session_state:
        st.session_state.refresh_in_progress = False
    if 'new_preferences' not in st.session_state:
        st.session_state.new_preferences = set()

    if st.session_state.refresh_in_progress:
        st.warning("⏳ A refresh is already in progress. Please wait...")
        return

    preferences_to_refresh, refresh_type = get_preferences_to_refresh(preferences)

    if refresh_type == "up_to_date":
        st.success("✅ All your news is up to date!")
        st.info("💡 News is refreshed once per day.")
        return

    st.session_state.refresh_in_progress = True

    with st.status("🔄 Refreshing news...", expanded=True) as status:
        for pref in preferences_to_refresh:
            st.write(f"🔍 **Running search for:** `{pref}`")
            # Create in-memory buffer to capture prints
            buffer = io.StringIO()

            # Instantiate the workflow
            workflow = SearchWorkflow(
                name="SmartSearchWorkflow",
                agents=[academic_paper_researcher_, engine_search_agent_, Video_agent_],
            )

            try:
                with redirect_stdout(buffer):
                    workflow.run(topic=pref,user_email=st.session_state.email)
            except Exception as e:
                st.error(f"❌ Error while refreshing `{pref}`: {e}")
                continue

            # Display captured logs
            logs = buffer.getvalue()
            for line in logs.strip().split('\n'):
                st.write(line)

            # Mark refresh complete for this preference
            from datetime import datetime, timezone
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            st.session_state.last_refresh_date[pref] = today

        status.update(label="✅ Refresh complete", state="complete")

    st.session_state.refresh_in_progress = False


def refresh_news_silent(preferences):
    """
    Silent news refresh function without dialog (for background operations)
    
    Args:
        preferences (list): List of user preferences
    """
    # Initialize session state variables if they don't exist
    if 'last_refresh_date' not in st.session_state:
        st.session_state.last_refresh_date = {}
    if 'refresh_in_progress' not in st.session_state:
        st.session_state.refresh_in_progress = False
    if 'new_preferences' not in st.session_state:
        st.session_state.new_preferences = set()
    
    # Check if refresh is already in progress
    if st.session_state.refresh_in_progress:
        return "refresh_in_progress"
    
    # Determine which preferences to refresh
    preferences_to_refresh, refresh_type = get_preferences_to_refresh(preferences)
    
    # Check if everything is up to date
    if refresh_type == "up_to_date":
        return "up_to_date"
    
    # Mark refresh as in progress
    st.session_state.refresh_in_progress = True
    
    try:
        # Execute workflow silently
        results = refresh_news_workflow(preferences_to_refresh)
        
        # Mark refresh as completed
        st.session_state.refresh_in_progress = False
        
        return {
            "status": "completed",
            "preferences_processed": preferences_to_refresh,
            "results": results,
            "refresh_type": refresh_type
        }
    
    except Exception as e: 
        st.session_state.refresh_in_progress = False
        return {
            "status": "error",
            "error": str(e),
            "preferences_processed": preferences_to_refresh,
            "refresh_type": refresh_type
        }

# Utility function to add a new preference
def add_new_preference(preference):
    """
    Add a new preference and mark it for refresh
    
    Args:
        preference (str): The new preference to add
    """
    # Add preference to your storage system
    # ... your preference addition logic ...
    
    # Mark as new preference
    mark_preference_as_new(preference)
    
    st.success(f"✅ Preference '{preference}' added! It will be processed on next refresh.")

# Function to check refresh status
def get_refresh_status(preferences):
    """Return refresh status for each preference"""
    # Initialize session state if not exists
    if 'last_refresh_date' not in st.session_state:
        st.session_state.last_refresh_date = {}
    
    today = date.today()
    status = {}
    
    for pref in preferences:
        last_refresh = st.session_state.last_refresh_date.get(pref)
        if last_refresh == today:
            status[pref] = "✅ Up to date"
        elif last_refresh:
            days_ago = (today - last_refresh).days
            status[pref] = f"⏰ {days_ago} day(s) ago"
        else:
            status[pref] = "❌ Never refreshed"
    
    return status