import streamlit as st

def home_page():
    # Page configuration
    st.set_page_config(
        page_title="RAG",
        page_icon="🤖",
        layout="wide"
    )
    
    # Header
    st.title("🤖 Welcome")
    st.markdown("---")
    
    # Introduction section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("About This Application")
        st.write("""
        Welcome to your local RAG chat!
        
        This application provides two chat modes:
        - **General Chat** - Code-trained LLM for general programming questions
        - **PyTorch RAG Chat** - Retrieval-Augmented Generation using PyTorch docstrings
        """)

        
        st.subheader("🔧 How PyTorch RAG Works")
        st.write("""
        1. Your query is used to search parsed PyTorch docstrings
        2. Relevant documentation is retrieved
        3. Query + found docs are sent to the LLM
        4. Get accurate, context-aware responses about PyTorch
        """)
    
    with col2:
        st.info("🚀 **Getting Started**\n\nChoose your chat mode:\n- General Chat for coding questions\n- PyTorch RAG for PyTorch-specific help")
        
        st.success("🔐 **All processing happens locally on your machine.**")


if __name__ == "__main__":
    home_page()