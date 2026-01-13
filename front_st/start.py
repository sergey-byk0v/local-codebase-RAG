import streamlit as st

home_page = st.Page("pages/home_page.py", title="Home")
page_main_app = st.Page("pages/main_chat.py", title="General chat")
page_pytorch = st.Page("pages/pytorch_docs.py", title="Pytorch docs RAG")

pgs = st.navigation([home_page, page_main_app, page_pytorch])

pgs.run()