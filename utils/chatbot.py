from google.generativeai import GenerativeModel
import google.generativeai as genai
import streamlit as st

class SwatTravelBot:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = GenerativeModel('gemini-2.0-flash')
        self.context = self.get_system_prompt()
        
    def get_system_prompt(self):
        return """You are a concise travel assistant for Swat Valley. IMPORTANT: Keep all responses under 100 words and focus only on essential information.

        STRICT RULES:
        1. Focus only on Swat Valley region
        2. For hotel recommendations:
           🏨 NAME: [hotel name]
           💰 PRICE: [approximate range in PKR]
           ⭐ RATING: [approximate rating/5]
           📍 AREA: [specific area in Swat]
        
        3. For weather/timing queries:
           🌤️ VISIT: [yes/no]
           🌡️ TEMP: [current season temperature]
           🎯 BEST TIME: [brief period]
        
        4. For location queries:
           📍 AREA: [specific area]
           🚗 DISTANCE: [from Mingora]
           ✨ KNOWN FOR: [1-2 key attractions]
        
        DO NOT:
        - Give lengthy explanations
        - Include historical details unless asked
        - Provide generic travel advice
        - Write responses longer than 100 words
        """
    
    def get_response(self, user_input, chat_history=None):
        if chat_history is None:
            chat = self.model.start_chat(history=[])
            chat.send_message(self.context)
        else:
            chat = self.model.start_chat(history=chat_history)
        
        prompt = f"Remember to be extremely concise and focus only on Swat Valley. Query: {user_input}"
        response = chat.send_message(prompt)
        return response.text, chat.history