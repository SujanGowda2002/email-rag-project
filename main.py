# main.py
from gmail_lib import fetch_emails  # <- switch to the mock function
from processor import EmailRAG
import os

#import warning exemptions
import warnings
warnings.filterwarnings("ignore")


def run_demo():
    print("--- Initializing Local Email RAG ---")
    
    # 1. Fetch mock emails
    raw_emails = fetch_emails(max_results=10)
    
    # 2. Setup RAG for a specific user
    user_a_rag = EmailRAG(user_id="user_123")
    user_a_rag.ingest_emails(raw_emails)
    
    # 3. Query
    query = "Who sent me the most recent email and what was it about?."
    print(f"\nUser Query: {query}")
    
    result = user_a_rag.ask(query)
    
    print("\n--- LLM Response ---")
    print(result["result"])
    
    print("\n--- Sources Used ---")
    for doc in result["source_documents"]:
        print(f"- {doc.metadata['subject']}")

if __name__ == "__main__":
    run_demo()
