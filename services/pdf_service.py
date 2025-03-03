import os
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from search_service import search_service
import json
import logging
from ai_service import ai_chat_service
logger = logging.getLogger(__name__)

os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")

# Set a User-Agent to identify requests
os.environ['USER_AGENT'] = 'LangChain/1.0 (web scraping project)'

# Function to load documents from websites and PDFs
def load_documents(sources):
    documents = []
    for source in sources:
        if source.endswith('.pdf'):
            loader = PyPDFLoader(source)
            documents.extend(loader.load())
        else:
            loader = WebBaseLoader(source)
            documents.extend(loader.load())
    return documents

# Initialize LangChain components
def setup_qa_system(sources):
    # Load documents
    documents = load_documents(sources)

    # Create an index using OpenAI embeddings and Chroma vector store
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(documents, embeddings)

    # Set up the retrieval-based QA chain
    retriever = vectorstore.as_retriever()
    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(temperature=0),
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
    )
    return qa_chain

async def main():
    question = input("Enter your question: ")
    url = input("Enter the URL: ")

    search_query = await ai_chat_service.compress_user_query(question, name=url)
    search_query = json.loads(search_query)
    query_text = search_query["response"]
    query_text = query_text.strip('"\'')  # Remove both single and double quotes

    print(query_text)
    search_result = search_service.advanced_search(query_text, max_results=5)
    logger.info(search_result)
    print(search_result)
    # Set up the QA system
    sources = [result['url'] for result in search_result['results']]
    print(sources)
    qa_system = setup_qa_system(sources)

    # Interact with the QA system
    while True:
        query = input("Enter your question (or 'exit' to quit): ")
        if query.lower() == 'exit':
            break

        # Call the QA chain directly with the query as input
        try:
            response = qa_system.invoke({"query": query})
            print("\nAnswer:", response["result"])
            print("\nSources:")
            for doc in response["source_documents"]:
                print("-", doc.metadata.get("source", "Unknown"))
        except Exception as e:
            print(f"Error during query: {e}")

import asyncio
asyncio.run(main())
