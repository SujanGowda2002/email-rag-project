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
        # Local Embedding Model
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2") 
        
        # --- THE FIX: RESET FOR DEMO ---
        # If you want to start fresh every time you run the script:
        if os.path.exists("./chroma_db"):
            shutil.rmtree("./chroma_db")
            print("--- Database Reset: Previous session data cleared ---")

        # Local Vector DB 
        self.vector_db = Chroma( 
            persist_directory="./chroma_db", 
            embedding_function=self.embeddings, 
            collection_name="user_emails" 
        ) 
        
    def ingest_emails(self, email_list): 
        docs = [] 
        for em in email_list: 
            # Metadata filtering for Multi-User Support 
            metadata = {
                "user_id": self.user_id, 
                "subject": em['subject'], 
                "id": em['id']
            } 
            doc = Document(
                page_content=f"Subject: {em['subject']}\nContent: {em['content']}", 
                metadata=metadata
            ) 
            docs.append(doc) 
        
        # --- PERFORMANCE FIX ---
        # Move this OUTSIDE the loop. 
        # Before, you were re-adding the entire 'docs' list for every single email!
        if docs:
            self.vector_db.add_documents(docs) 
            print(f"Successfully indexed {len(docs)} emails for {self.user_id}") 
            
    def ask(self, question): 
        # Local LLM via Ollama 
        llm = Ollama(model="mistral") 
        
        # Retrieval with Metadata filtering
        # Increased 'k' to 5 so it sees more context if you have multiple related emails
        retriever = self.vector_db.as_retriever( 
            search_kwargs={'filter': {'user_id': self.user_id}, 'k': 5} 
        ) 
        
        qa_chain = RetrievalQA.from_chain_type( 
            llm=llm, 
            chain_type="stuff", 
            retriever=retriever, 
            return_source_documents=True 
        ) 
        
        response = qa_chain.invoke({"query": question}) 
        return response