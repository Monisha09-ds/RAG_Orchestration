import streamlit as st

# Import from the new modular package
from graph_rag.neo4j_connector import seed_graph_data, verify_connection
from graph_rag.controller import ingest_url, handle_question

# -----------------------
# Streamlit UI
# -----------------------
st.set_page_config(page_title="Portfolio Knowledge Bot", layout="centered")

# Check Connection Logic
if not verify_connection():
    st.error("❌ Failed to connect to Knowledge Graph (Neo4j). Please check your configuration.")
    st.stop()
else:
    st.toast("✅ Graph Connection Established", icon="🟢")

st.title("🧠 Knowledge-Aware Portfolio Chatbot")
st.caption("Powered by Neo4j + Groq (Llama-3)")

# Sidebar for Ingestion
with st.sidebar:
    st.header("📥 Ingest Portfolio")
    
    if st.button("Load Dummy Data"):
        seed_graph_data()
        st.success("Dummy data loaded!")
        
    st.divider()
    
    url_input = st.text_input("Portfolio URL", placeholder="https://my-portfolio.com")
    if st.button("Analyze & Ingest URL"):
        if url_input:
            with st.spinner("Scraping & Analyzing..."):
                result = ingest_url(url_input)
                if result["success"]:
                    st.success(result["message"])
                else:
                    st.error(result["message"])
        else:
            st.warning("Please enter a URL")

# Main Chat Interface
question = st.text_input(
    "Ask:",
    placeholder="Ask strictly about the portfolio..."
)

if question:
    with st.spinner("Consulting Knowledge Graph..."):
        # Delegate to Controller
        answer = handle_question(question)

    st.markdown("### 🤖 Answer")
    st.write(answer)
