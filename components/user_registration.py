import streamlit as st
from utils.user_manager import UserManager

def user_registration():
    st.title("🧑‍💼 User Registration")
    
    # Create tabs for login and registration
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    user_manager = UserManager()
    
    with tab1:
        st.header("Login")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", key="login_button"):
            if login_username and login_password:
                success, result = user_manager.authenticate_user(login_username, login_password)
                if success:
                    st.session_state.user = result
                    st.session_state.logged_in = True
                    st.success(f"Welcome back, {result['username']}!")
                    st.rerun()
                else:
                    st.error(result)
            else:
                st.warning("Please enter both username and password")
    
    with tab2:
        st.header("Register")
        reg_username = st.text_input("Username", key="reg_username")
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_password")
        
        if st.button("Register", key="register_button"):
            if reg_username and reg_email and reg_password:
                if reg_password != reg_confirm_password:
                    st.error("Passwords do not match")
                else:
                    success, message = user_manager.create_user(reg_username, reg_email, reg_password)
                    if success:
                        st.success(message)
                        # Automatically log in the user
                        success, result = user_manager.authenticate_user(reg_username, reg_password)
                        if success:
                            st.session_state.user = result
                            st.session_state.logged_in = True
                            st.rerun()
                    else:
                        st.error(message)
            else:
                st.warning("Please fill in all fields") 