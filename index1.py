import os
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores.chroma import Chroma
from services.search_service import search_service
import json
import logging
import requests
from services.ai_service import ai_chat_service
from config.settings import settings

logger = logging.getLogger(__name__)

os.environ['OPENAI_API_KEY'] = settings.OPENAI_API_KEY
os.environ['USER_AGENT'] = 'LangChain/1.0 (web scraping project)'

def load_documents(sources):
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
    # Load documents
    documents = load_documents(sources)

    # Create embeddings and vector store
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(documents, embeddings)

    # Initialize GPT-4 model
    llm = ChatOpenAI(
        model="gpt-4", 
        temperature=0
    )

    # Create the retriever
    retriever = vectorstore.as_retriever()

    # Create prompt template
    prompt = ChatPromptTemplate.from_template("""
    Answer the following question based on the provided context:
    
    Context: {context}
    Question: {question}
    
    Answer:
    """)

    # Create the chain
    document_chain = create_stuff_documents_chain(llm, prompt)

    # Create the RAG chain
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | document_chain
        | StrOutputParser()
    )

    return rag_chain, vectorstore

async def main():
    question = input("Enter your question: ")
    url = input("Enter the URL: ")

    search_query = await ai_chat_service.compress_user_query(question, name=url)
    search_query = json.loads(search_query)
    query_text = search_query["response"]
    query_text = query_text.strip('"\'')

    print(query_text)
    search_result = search_service.advanced_search(query_text, max_results=5)
    logger.info(search_result)
    print(search_result)

    sources = [result['url'] for result in search_result['results']]
    print(sources)
    
    # Set up the QA system
    qa_system, vectorstore = setup_qa_system(sources)

    # Interact with the QA system
    while True:
        query = input("Enter your question (or 'exit' to quit): ")
        if query.lower() == 'exit':
            break

        try:
            # Invoke the RAG chain
            response = qa_system.invoke(query)
            print("\nAnswer:", response)
            
            # Get source documents
            relevant_docs = vectorstore.similarity_search(query)
            print("\nSources:")
            for doc in relevant_docs:
                print("-", doc.metadata.get("source", "Unknown"))
                
        except Exception as e:
            print(f"Error during query: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())