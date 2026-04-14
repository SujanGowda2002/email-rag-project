from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain_core.documents import Document
from langchain_classic.chains import RetrievalQA
import shutil
import os


class EmailRAG:
    def __init__(self, user_id="SSG"):
        self.user_id = user_id

        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )

        if os.path.exists("./chroma_db"):
            shutil.rmtree("./chroma_db")
            print("--- Database Reset: Previous session data cleared ---")

        self.vector_db = Chroma(
            persist_directory="./chroma_db",
            embedding_function=self.embeddings,
            collection_name="user_emails"
        )

    def ingest_emails(self, email_list):
        """
        Convert raw emails into LangChain Document objects and store them
        in the vector database.
        """
        docs = []

        for em in email_list:
            metadata = {
                "user_id": self.user_id,
                "subject": em.get("subject", "No Subject"),
                "from": em.get("from", "Unknown Sender"),
                "date": em.get("date", "Unknown Date"),
                "id": em.get("id", "Unknown ID"),
            }

            page_content = (
                f"From: {em.get('from', 'Unknown Sender')}\n"
                f"Date: {em.get('date', 'Unknown Date')}\n"
                f"Subject: {em.get('subject', 'No Subject')}\n"
                f"Content: {em.get('content', '')}"
            )

            doc = Document(
                page_content=page_content,
                metadata=metadata
            )

            docs.append(doc)

        if docs:
            self.vector_db.add_documents(docs)
            print(f"Successfully indexed {len(docs)} emails for {self.user_id}")

    def ask(self, question):
        """
        Ask a question over the indexed emails using retrieval-augmented generation.
        """
        llm = Ollama(model="mistral")

        retriever = self.vector_db.as_retriever(
            search_kwargs={
                "filter": {"user_id": self.user_id},
                "k": 5
            }
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True
        )

        response = qa_chain.invoke({"query": question})
        return response