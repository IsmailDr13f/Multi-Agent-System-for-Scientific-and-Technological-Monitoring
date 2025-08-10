import streamlit as st
from bloc_2.AgentsResearchTeam import chat_agent   


# Check if card content exists
if 'card_content' not in st.session_state:
    st.error("No article selected. Please go back and select an article to chat about.")
    if st.button("← Back to Articles"):
        st.switch_page("news/news_.py")  # Adjust path as needed
    st.stop()

# Get the card content
card = st.session_state.card_content

# Custom CSS for the horizontal card
st.markdown("""
<style>
.article-card {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 12px;
    padding: 25px;
    margin-bottom: 50px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    color: #333;
}

.card-content {
    display: flex;
    align-items: flex-start;
    gap: 30px;
}

.card-info {
    flex: 1;
}

.card-title {
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 15px;
    line-height: 1.3;
    color: #2c3e50;
}

.card-meta {
    display: flex;
    gap: 15px;
    margin-bottom: 20px;
    font-size: 14px;
}

.card-source {
    background: #e3f2fd;
    color: #1976d2;
    padding: 6px 14px;
    border-radius: 20px;
    font-weight: 500;
}

.card-date {
    background: #f3e5f5;
    color: #7b1fa2;
    padding: 6px 14px;
    border-radius: 20px;
    font-weight: 500;
}

.card-topic {
    background: #e8f5e8;
    color: #388e3c;
    padding: 6px 14px;
    border-radius: 20px;
    font-weight: 600;
}

.card-summary {
    font-size: 16px;
    line-height: 1.6;
    margin-bottom: 20px;
    color: #555;
}

.card-image {
    width: 300px;
    height: 220px;
    border-radius: 12px;
    object-fit: cover;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-link-button {
    display: inline-block;
    background: #007bff;
    color: white;
    text-decoration: none;
    padding: 12px 24px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 14px;
    transition: all 0.3s ease;
    border: none;
    cursor: pointer;
}

.card-link-button:hover {
    background: #0056b3;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
    text-decoration: none;
    color: white;
}

.chat-container {
    background: #ffffff;
    border-radius: 10px;
    padding: 20px;
    margin-top: 30px;
}

.user-message {
    background: #007bff;
    color: white;
    padding: 12px 16px;
    border-radius: 18px 18px 4px 18px;
    margin: 8px 0;
    margin-left: 20%;
    word-wrap: break-word;
}

.assistant-message {
    background: #f8f9fa;
    color: #333;
    padding: 12px 16px;
    border-radius: 18px 18px 18px 4px;
    margin: 8px 0;
    margin-right: 20%;
    word-wrap: break-word;
    border: 1px solid #e9ecef;
}

@media (max-width: 768px) {
    .card-content {
        flex-direction: column;
    }
    .card-image {
        width: 100%;
        height: 250px;
    }
    .user-message, .assistant-message {
        margin-left: 0;
        margin-right: 0;
    }
}
</style>
""", unsafe_allow_html=True)

# Display the article card
st.markdown(f"""
<div class="article-card">
    <div class="card-content">
        <div class="card-info">
            <div class="card-title">{card['title']}</div>
            <div class="card-meta">
                <span class="card-source">{card['source']}</span>
                <span class="card-date">{card['Publication_date']}</span>
                <span class="card-topic">{card['topic']}</span>
            </div>
            <div class="card-summary">{card['summary']}</div>
            <a href="{card['link']}" target="_blank" class="card-link"> Read Full Content</a>
        </div>
        <div>
            <img src="{card['image_url']}" alt="Article Image" class="card-image">
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize chat history and agent
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
    # Add a welcome message
    welcome_msg = f"Hello! I'm here to help you discuss and analyze the content: **{card['title']}**. What would you like to know or discuss about it?"
    st.session_state.chat_messages.append({"role": "assistant", "content": welcome_msg})

# Initialize the chat agent if not already done
if "agent" not in st.session_state:
    try:
        st.session_state.agent = chat_agent(
            title=card['title'],
            summary=card['summary'],
            date=card['Publication_date'],
            url=card['link'],
            source=card['source'],
            user_name=st.session_state.name,
            user_interests=str(st.session_state.preferences),
            user_role=st.session_state.role
        )
    except Exception as e:
        st.error(f"Failed to initialize chat agent: {str(e)}")
        print(e)
        st.stop()

# Display chat messages
chat_container = st.container()
with chat_container:
    for message in st.session_state.chat_messages:
        if message["role"] == "user":
            st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="assistant-message">{message["content"]}</div>', unsafe_allow_html=True)

# Chat input
user_input = st.chat_input(placeholder="Ask me anything about this Content!")

# Handle user input
if user_input:
    # Add user message to chat history
    st.session_state.chat_messages.append({"role": "user", "content": user_input})
    
    # Display loading message
    with chat_container:
        st.markdown('<div class="loading-message">🤔 Thinking...</div>', unsafe_allow_html=True)
    
    try:
        # Generate response using the chat agent
        response = st.session_state.agent.run(user_input)
        
        # Extract the response content (adjust based on your agent's response format)
        if hasattr(response, 'content'):
            agent_response = response.content
        elif isinstance(response, str):
            agent_response = response
        else:
            agent_response = str(response)
        
        # Add assistant response to chat history
        st.session_state.chat_messages.append({"role": "assistant", "content": agent_response})
        
    except Exception as e:
        error_response = f"I apologize, but I encountered an error while processing your question: {str(e)}"
        st.session_state.chat_messages.append({"role": "assistant", "content": error_response})
    
    # Rerun to update the chat display
    st.rerun()