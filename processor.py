from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_community.vectorstores import Chroma 
from langchain_community.llms import Ollama 
from langchain_core.documents import Document 
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
import shutil
import os

class EmailRAG: 
    def __init__(self, user_id="SSG"): 
        self.user_id = user_id 
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2") 
        
        if os.path.exists("./chroma_db"):
            shutil.rmtree("./chroma_db")
            print("--- Database Reset: Previous session data cleared ---")

        self.vector_db = Chroma( 
            persist_directory="./chroma_db", 
            embedding_function=self.embeddings, 
            collection_name="user_emails" 
        ) 
        
    def ingest_emails(self, email_list): 
        docs = [] 
        for em in email_list: 
            metadata = {
                "user_id": self.user_id, 
                "subject": em['subject'], 
                "id": em['id'],
                "date": em.get('date', 'Unknown') # Store date in metadata
            } 
            # --- THE FIX: Include Date in the actual text ---
            doc = Document(
                page_content=f"Date: {metadata['date']}\nSubject: {em['subject']}\nContent: {em['content']}", 
                metadata=metadata
            ) 
            docs.append(doc) 
        
        if docs:
            self.vector_db.add_documents(docs) 
            print(f"Successfully indexed {len(docs)} emails for {self.user_id}") 
            
    def ask(self, question): 
        llm = Ollama(model="mistral") 
        
        # Custom Prompt to force the LLM to look at the Dates
        template = """You are a personal assistant. Use the following emails to answer the user's question. 
        The emails include dates; if there are conflicting updates, prioritize the information in the most recent email.
        
        Context: {context}
        Question: {question}
        
        Answer:"""
        
        PROMPT = PromptTemplate(
            template=template, input_variables=["context", "question"]
        )

        retriever = self.vector_db.as_retriever( 
            search_kwargs={'filter': {'user_id': self.user_id}, 'k': 5} 
        ) 
        
        qa_chain = RetrievalQA.from_chain_type( 
            llm=llm, 
            chain_type="stuff", 
            retriever=retriever, 
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT} # Pass the custom prompt here
        ) 
        
        response = qa_chain.invoke({"query": question}) 
        return response