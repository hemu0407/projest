import streamlit as st
import mysql.connector
import hashlib
import requests
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Database Configuration
db_config = {
    'user': 'root',
    'password': 'your_db_password',
    'host': 'localhost',
    'database': 'stock_app_db',
    'raise_on_warnings': True
}

# Initialize Database Connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        st.error(f"Database connection error: {err}")
        return None

# Initialize Database Tables
def init_db():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()

# Initialize the database
init_db()

# Password Hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Custom CSS for Auth Pages
st.markdown("""
    <style>
    .auth-container {
        max-width: 400px;
        padding: 2rem;
        margin: 0 auto;
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .auth-title {
        text-align: center;
        color: #2c3e50;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Authentication Page
def auth_page():
    st.title("📈 Stock Market Analytics Platform")
    
    # Centered Container
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.markdown('<h2 class="auth-title">🔒 User Authentication</h2>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])

        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login")
                
                if submitted:
                    conn = get_db_connection()
                    if conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
                        result = cursor.fetchone()
                        
                        if result and hash_password(password) == result[0]:
                            st.session_state.authenticated = True
                            st.session_state.current_user = username
                            st.success("Login successful! Redirecting...")
                            st.experimental_rerun()
                        else:
                            st.error("Invalid username or password")
                        cursor.close()
                        conn.close()

        with tab2:
            with st.form("signup_form"):
                new_username = st.text_input("Choose Username")
                new_password = st.text_input("Choose Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                submitted = st.form_submit_button("Create Account")
                
                if submitted:
                    if new_password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        conn = get_db_connection()
                        if conn:
                            try:
                                cursor = conn.cursor()
                                cursor.execute(
                                    "INSERT INTO users (username, password) VALUES (%s, %s)",
                                    (new_username, hash_password(new_password))
                                )
                                conn.commit()
                                st.success("Account created successfully! Please login.")
                            except mysql.connector.IntegrityError:
                                st.error("Username already exists")
                            finally:
                                cursor.close()
                                conn.close()

        st.markdown('</div>', unsafe_allow_html=True)

# ... [Keep the rest of your existing code for main_app and other functions] ...

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# App Flow
if not st.session_state.authenticated:
    auth_page()
else:
    main_app()
    # Add logout button in sidebar
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.session_state.current_user = None
        st.experimental_rerun()
