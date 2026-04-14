from gmail_lib import fetch_emails
from processor import EmailRAG
import warnings

# Suppress warnings to keep terminal output cleaner during demo runs.
warnings.filterwarnings("ignore")


def run_demo():
    """
    Run the full Email RAG demo:
    1. Fetch emails from Gmail
    2. Index them into Chroma
    3. Ask a question over them
    4. Print the answer and the source emails used
    """
    print("--- Initializing Local Email RAG ---")

    # Step 1: Fetch recent emails from Gmail
    raw_emails = fetch_emails(max_results=10)

    # Step 2: Create a RAG instance for a specific user
    # user_id helps keep one user's emails separate from another user's.
    user_a_rag = EmailRAG(user_id="SSG")

    # Step 3: Ingest the fetched emails into the vector database
    user_a_rag.ingest_emails(raw_emails)

    # Step 4: Ask a question about the emails
    query = "What was the subject of the recent email sent from Linkedin to me?"
    print(f"\nUser Query: {query}")

    result = user_a_rag.ask(query)

    # Step 5: Print the generated answer
    print("\n--- LLM Response ---")
    print(result["result"])

    # Step 6: Print the source documents used for answering
    print("\n--- Sources Used ---")
    for doc in result["source_documents"]:
        print(
                f"- From: {doc.metadata.get('from', 'Unknown Sender')} | "
                f"Subject: {doc.metadata.get('subject', 'No Subject')}"
        )


if __name__ == "__main__":
    run_demo()