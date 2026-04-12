import streamlit as st
from pages import page_map

def main():
    current = st.sidebar.radio("导航", list(page_map.keys()))
    page_map

if __name__ == "__main__":
    main()