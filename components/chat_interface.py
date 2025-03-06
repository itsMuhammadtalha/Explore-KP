import streamlit as st
from utils.chatbot import SwatTravelBot

def chat_interface():
    st.title("🤖 AI Travel Assistant")
    st.markdown("---")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about Swat Valley..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get bot response
        bot = SwatTravelBot("AIzaSyBDi_ROaSCUnqCzhaUWe43pPmU34Rmli6E")
        response, _ = bot.get_response(prompt)
        
        # Add assistant message
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun() 