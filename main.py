import streamlit as st
from config import init_session
from database import init_db
from components import sidebar
from pages import page_map

def main():
    init_db()
    init_session()
    sidebar()
    current = st.session_state.page
    if current in page_map:
        page_map[current]()

if __name__ == "__main__":
    main()