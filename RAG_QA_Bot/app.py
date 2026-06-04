import os
import streamlit as st
from dotenv import load_dotenv
from src.ingestion import load_directory, chunk_documents
from src.embedding import DocumentEmbedder
from src.vector_store import QdrantVectorStore
from src.generator import LLMGenerator

# Load environment variables
load_dotenv(override=True)

# Cache the Qdrant connection to avoid database folder lock conflicts
@st.cache_resource
def get_vector_store():
    return QdrantVectorStore(collection_name="documents", path="./qdrant_db")

# Set Page Config
st.set_page_config(
    page_title="InsightRAG - Document Q&A Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR SLEEK DARK THEME & GLASSMORPHISM ---
st.markdown("""
<style>
    /* Google Font Import */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
    
    /* Font override */
    html, body, [class*="css"], .stMarkdown {
        font-family: 'Outfit', 'Segoe UI', sans-serif;
    }
    
    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
    }

    /* Background and containers */
    .stApp {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
        color: #c9d1d9;
    }
    
    /* Sleek gradient title */
    .gradient-title {
        background: linear-gradient(135deg, #6366f1 0%, #3b82f6 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem !important;
        font-weight: 800;
        margin-bottom: 5px;
        text-align: left;
    }
    
    .gradient-subtitle {
        color: #8b949e;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }

    /* Glassmorphic card design */
    .glass-card {
        background: rgba(22, 27, 34, 0.6);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    /* Metric boxes */
    .metric-container {
        display: flex;
        justify-content: space-between;
        gap: 15px;
        margin-bottom: 25px;
    }
    
    .metric-card {
        flex: 1;
        background: rgba(33, 38, 45, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #58a6ff;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Document badges */
    .source-badge {
        background-color: #21262d;
        color: #58a6ff;
        border: 1px solid #30363d;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 5px;
    }
    
    .location-badge {
        background-color: #1f2937;
        color: #10b981;
        border: 1px solid #111827;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 5px;
    }

    .score-badge {
        background-color: #2e1a47;
        color: #d3adf7;
        border: 1px solid #49227a;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }

    /* Custom expanders */
    .streamlit-expanderHeader {
        background-color: rgba(22, 27, 34, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 8px !important;
        margin-bottom: 5px;
    }
    
    /* Sidebar styling */
    .css-163gpadd {
        background-color: #0d1117 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR INTERACTIVE PARAMETERS ---
st.sidebar.image("https://img.icons8.com/nolan/96/artificial-intelligence.png", width=80)
st.sidebar.markdown("<h2 style='margin-top: 0;'>InsightRAG Config</h2>", unsafe_allow_html=True)

st.sidebar.subheader("🔑 API Key Setup")

# Input for Groq Key
env_groq_key = os.environ.get("GROQ_API_KEY", "")
# Clean prefix if existing
if "gsk_" in env_groq_key:
    env_groq_key = env_groq_key[env_groq_key.index("gsk_"):]
    
groq_api_key = st.sidebar.text_input(
    "Groq API Key",
    value=env_groq_key,
    type="password",
    help="Enter your Groq API Key starting with gsk_"
)

# Input for Gemini Key
env_gemini_key = os.environ.get("GEMINI_API_KEY", "")
gemini_api_key = st.sidebar.text_input(
    "Gemini API Key",
    value=env_gemini_key,
    type="password",
    help="Enter your Gemini API Key"
)

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Retrieval Parameters")

top_k = st.sidebar.slider("Top-K context chunks", min_value=1, max_value=6, value=3)
llm_temperature = st.sidebar.slider("LLM Temperature", min_value=0.0, max_value=1.0, value=0.0, step=0.1)

st.sidebar.markdown("---")
st.sidebar.subheader("🧠 Models Selection")

provider_choice = st.sidebar.selectbox("LLM Provider", ["Groq", "Gemini"])
if provider_choice == "Groq":
    llm_model = st.sidebar.selectbox(
        "Groq Model",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "llama3-8b-8192"]
    )
else:
    llm_model = st.sidebar.selectbox(
        "Gemini Model",
        ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.5-flash"]
    )

st.sidebar.markdown("---")
st.sidebar.subheader("🗄️ Ingest & Index Database")

# Function to run the indexer within streamlit
def run_indexing():
    with st.spinner("Step 1: Reading data files..."):
        docs = load_directory("data")
        if not docs:
            st.error("No documents found in the '/data' folder.")
            return False
            
    with st.spinner("Step 2: Splitting text into overlapping chunks..."):
        chunks = chunk_documents(docs, chunk_size=1000, chunk_overlap=150)
        
    with st.spinner("Step 3: Loading Local Sentence-Transformer model & generating embeddings..."):
        embedder = DocumentEmbedder(provider="local", model_name="all-MiniLM-L6-v2")
        texts = [chunk["text"] for chunk in chunks]
        embeddings = embedder.embed_documents(texts)
        vector_size = len(embeddings[0])
        
    with st.spinner("Step 4: Writing to Qdrant vector store..."):
        vector_store = get_vector_store()
        vector_store.create_collection(vector_size=vector_size, force_recreate=True)
        vector_store.add_documents(chunks, embeddings)
        
    st.success(f"Successfully indexed {len(docs)} documents ({len(chunks)} chunks)!")
    return True

if st.sidebar.button("🔨 Re-Index Documents"):
    success = run_indexing()
    if success:
        # Clear cache to reflect updates
        st.cache_data.clear()

# --- MAIN APP LAYOUT ---
st.markdown("<h1 class='gradient-title'>InsightRAG</h1>", unsafe_allow_html=True)
st.markdown("<div class='gradient-subtitle'>Grounded Document Q&A Bot using Local Vectors & Cited LLM Generation</div>", unsafe_allow_html=True)

# Helper to read Qdrant point count
def get_db_stats():
    qdrant_path = "./qdrant_db"
    if not os.path.exists(qdrant_path):
        return 0, 0
    try:
        vector_store = get_vector_store()
        client = vector_store.client
        collections = client.get_collections().collections
        exists = any(c.name == "documents" for c in collections)
        if exists:
            count = client.get_collection("documents").points_count
            # Count unique file sources in data folder
            files_count = len(os.listdir("data")) if os.path.exists("data") else 0
            return files_count, count
    except Exception as e:
        print(f"Error getting db stats: {e}")
        pass
    return 0, 0

doc_count, chunk_count = get_db_stats()

# Metrics Grid
st.markdown(f"""
<div class='metric-container'>
    <div class='metric-card'>
        <div class='metric-value'>{doc_count}</div>
        <div class='metric-label'>Source Documents</div>
    </div>
    <div class='metric-card'>
        <div class='metric-value'>{chunk_count}</div>
        <div class='metric-label'>Indexed Vector Chunks</div>
    </div>
    <div class='metric-card'>
        <div class='metric-value'>{"Persistent (Qdrant)" if chunk_count > 0 else "Empty"}</div>
        <div class='metric-label'>Database Status</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Check if Qdrant database folder is configured
if chunk_count == 0:
    st.warning("⚠️ The database is currently empty. Please place 4-5 files in your `/data` folder and click the **🔨 Re-Index Documents** button in the sidebar to build the database.")

# --- QUERY & RESPONSE DASHBOARD ---
tab1, tab2 = st.tabs(["💬 Ask Questions", "📂 Inspect Database Documents"])

with tab1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    query_input = st.text_input("Ask a question about the ingested documents:", placeholder="e.g. What are the severity levels of AI security incidents?")
    st.markdown("</div>", unsafe_allow_html=True)
    
    if query_input:
        # 1. Validation of keys
        active_key = groq_api_key if provider_choice == "Groq" else gemini_api_key
        if not active_key:
            st.error(f"Error: Please configure the {provider_choice} API Key in the sidebar to generate answers.")
        elif chunk_count == 0:
            st.error("Error: The vector store has no documents indexed. Please click 'Re-Index Documents' first.")
        else:
            with st.spinner("Processing RAG pipeline (Retrieval + Generation)..."):
                try:
                    # Initialize embedder (using local all-MiniLM-L6-v2)
                    embedder = DocumentEmbedder(provider="local", model_name="all-MiniLM-L6-v2")
                    query_vector = embedder.embed_query(query_input)
                    
                    # Connect to vector store
                    vector_store = get_vector_store()
                    results = vector_store.search(query_vector, top_k=top_k)
                    
                    if not results:
                        st.warning("No matching context was found in the database.")
                    else:
                        # Initialize LLM
                        generator = LLMGenerator(
                            provider=provider_choice.lower(),
                            model_name=llm_model,
                            api_key=active_key
                        )
                        
                        # Generate grounded answer
                        answer = generator.generate_answer(query_input, results)
                        
                        # Display Answer
                        st.markdown("### 🤖 Answer")
                        st.markdown(f"<div class='glass-card' style='background: rgba(33, 150, 243, 0.08); border-left: 4px solid #1e88e5;'>\n\n{answer}\n\n</div>", unsafe_allow_html=True)
                        
                        # Display Source Chunks
                        st.markdown("### 📚 Retrieved Context (Sources)")
                        for idx, hit in enumerate(results):
                            meta = hit["metadata"]
                            source = meta.get("source", "Unknown file")
                            location = f"Page {meta['page']}" if "page" in meta else f"Section: {meta['section']}"
                            score = hit["score"]
                            
                            with st.expander(f"Context Chunk #{idx+1} - {source} ({location})"):
                                st.markdown(f"""
                                <span class='source-badge'>{source}</span>
                                <span class='location-badge'>{location}</span>
                                <span class='score-badge'>Similarity: {score:.4f}</span>
                                <div style='margin-top:10px; background:rgba(0,0,0,0.2); padding:10px; border-radius:5px; font-size:0.9rem; line-height:1.4;'>
                                {hit['text']}
                                </div>
                                """, unsafe_allow_html=True)
                                
                except Exception as e:
                    st.error(f"An error occurred: {e}")

with tab2:
    st.markdown("### 📄 Currently Available Source Documents in `/data`")
    data_dir = "data"
    if os.path.exists(data_dir):
        files = os.listdir(data_dir)
        if files:
            for f in files:
                ext = os.path.splitext(f)[1].upper()
                filepath = os.path.join(data_dir, f)
                size_kb = os.path.getsize(filepath) / 1024
                st.markdown(f"📁 **{f}** | Type: `{ext}` | Size: `{size_kb:.2f} KB`")
        else:
            st.info("The `/data` folder is empty.")
    else:
        st.info("The `/data` folder does not exist.")
