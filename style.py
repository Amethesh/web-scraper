import os
import json
import logging
import requests
import asyncio
import streamlit as st

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores.chroma import Chroma

from services.search_service import search_service
from services.ai_service import ai_chat_service
from config.settings import settings

# ----------------------------
# Setup Logging and Environment
# ----------------------------
logger = logging.getLogger(__name__)
os.environ['OPENAI_API_KEY'] = settings.OPENAI_API_KEY
os.environ['USER_AGENT'] = 'LangChain/1.0 (web scraping project)'

# ----------------------------
# Helper Functions
# ----------------------------
def load_documents(sources):
    """Load documents from a list of sources (PDFs or web URLs)."""
    documents = []
    for source in sources:
        try:
            if source.endswith('.pdf'):
                loader = PyPDFLoader(source)
                documents.extend(loader.load())
            else:
                loader = WebBaseLoader(source, verify_ssl=False)
                documents.extend(loader.load())
        except ValueError as e:
            logger.warning(f"Skipping {source} due to error: {e}")
        except requests.exceptions.SSLError as e:
            logger.warning(f"SSL error for {source}: {e}")
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Connection error for {source}: {e}")
        except Exception as e:
            logger.warning(f"Skipping {source} due to unexpected error: {e}")
    return documents

def setup_qa_system(sources):
    """Set up the QA system (RAG chain) based on the provided sources."""
    # Load documents
    with st.spinner("Loading documents from sources..."):
        documents = load_documents(sources)

    # Create embeddings and vector store
    with st.spinner("Creating embeddings and building the vector store..."):
        embeddings = OpenAIEmbeddings()
        vectorstore = Chroma.from_documents(
            documents,
            embeddings,
            persist_directory="./chroma_db"
            )
        vectorstore.persist() 

    # Initialize GPT-4 model
    llm = ChatOpenAI(
        model="gpt-4o", 
        temperature=0
    )

    # Create the retriever from the vector store
    retriever = vectorstore.as_retriever()

    # Create prompt template
    prompt = ChatPromptTemplate.from_template("""
    Answer the following question based on the provided context:
    
    Context: {context}
    Question: {question}
    
    Answer:
    """)

    # Build the document chain
    document_chain = create_stuff_documents_chain(llm, prompt)

    # Create the RAG (Retrieval Augmented Generation) chain
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | document_chain
        | StrOutputParser()
    )

    return rag_chain, vectorstore

# ----------------------------
# Streamlit UI Setup
# ----------------------------
st.set_page_config(page_title="Advanced Search & QA System", layout="wide")

# Optionally, inject some custom CSS for a modern look.
st.markdown(
    """
    <style>
    .reportview-container {
        background: #f5f5f5;
    }
    .sidebar .sidebar-content {
        background: #e0e0e0;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🔍 Advanced Search & QA System")
st.markdown("""
This application uses LangChain, GPT-4, and vector search to answer questions based on a curated set of documents.
Use the sidebar to start the process.
""")

# ----------------------------
# Sidebar: Initial Setup Form
# ----------------------------
with st.sidebar:
    st.header("Initial Setup")
    initial_question = st.text_area(
        "Enter your initial question", 
        height=100, 
        help="This question will be compressed and used to search for relevant documents."
    )
    input_url = st.text_input(
        "Enter a URL", 
        help="Provide a URL relevant to your query (e.g., an article or a PDF link)."
    )
    start_process = st.button("Start Search & Setup QA System")

# ----------------------------
# Process: Compress, Search, and Setup QA
# ----------------------------
if start_process:
    if not initial_question or not input_url:
        st.error("Please provide both a question and a URL to proceed.")
    else:
        try:
            # Compress the query using the AI chat service (async function)
            with st.spinner("Compressing your query..."):
                compressed_query = asyncio.run(
                    ai_chat_service.compress_user_query(initial_question, name=input_url)
                )
                search_query = json.loads(compressed_query)
                query_text = search_query.get("response", "").strip('"\'')

            st.success("Query compressed!")
            st.markdown(f"**Compressed Query:** `{query_text}`")

            # Perform an advanced search with the compressed query
            with st.spinner("Performing advanced search..."):
                search_result = search_service.advanced_search(query_text, max_results=5)
            st.success("Search completed!")

            st.markdown("#### Search Results:")
            st.json(search_result)

            # Extract source URLs from search results
            sources = [result['url'] for result in search_result.get('results', [])]
            if sources:
                st.markdown("**Extracted Sources:**")
                for src in sources:
                    st.markdown(f"- {src}")
            else:
                st.warning("No sources were found from the search.")

            # Set up the QA system using the extracted sources
            with st.spinner("Setting up the QA system..."):
                qa_system, vectorstore = setup_qa_system(sources)
                st.session_state['qa_system'] = qa_system
                st.session_state['vectorstore'] = vectorstore
            st.success("QA system is ready!")

            # Store the QA system and vectorstore in session state for later use.

        except Exception as e:
            st.error(f"An error occurred during setup: {e}")
            logger.exception("Error in initial setup:")

# ----------------------------
# Main Area: Ask Questions to the QA System
# ----------------------------
if 'qa_system' in st.session_state and 'vectorstore' in st.session_state:
    st.header("Ask a Question")
    user_query = st.text_input("Enter your question for the QA system", key="qa_input")
    if st.button("Get Answer"):
        if not user_query:
            st.error("Please enter a question.")
        else:
            try:
                with st.spinner("Processing your question..."):
                    # Invoke the QA system (RAG chain)
                    response = st.session_state['qa_system'].invoke(user_query)
                st.markdown("### Answer:")
                st.write(response)

                # Retrieve and display source documents for transparency
                relevant_docs = st.session_state['vectorstore'].similarity_search(user_query)
                st.markdown("### Sources:")
                if relevant_docs:
                    for doc in relevant_docs:
                        source_info = doc.metadata.get("source", "Unknown")
                        st.markdown(f"- {source_info}")
                else:
                    st.info("No source documents were found.")

            except Exception as e:
                st.error(f"Error during query processing: {e}")
                logger.exception("Error processing QA query:")
