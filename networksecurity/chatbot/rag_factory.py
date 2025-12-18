import os
import faiss
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document

class RAGFactory:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            print("WARNING: GOOGLE_API_KEY not found. RAG will not work.")
            self.rag_chain = None
            return

        # 1. Initialize Embeddings (Zero-Bloat Cloud Embeddings)
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

        # 2. Initialize Vector Store (FAISS - In-Memory/Local)
        # We start with an empty index and populate it via ingest()
        index = faiss.IndexFlatL2(768) # 768 is dim for embedding-001
        self.vector_store = FAISS(
            embedding_function=self.embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={}
        )

        # 3. Initialize LLM (Gemini Flash - Fast & Cheap)
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

        # 4. Define Prompt
        self.template = """Answer the question based only on the following context:
        {context}

        Question: {question}
        """
        self.prompt = ChatPromptTemplate.from_template(self.template)
        
        # 5. Initialize Cache
        self.cache = {}
        self.MAX_CACHE_SIZE = 100
        
        self.rag_chain = None
    
    def ingest_data(self, texts: list[str]):
        """
        Ingests a list of text strings into the vector store.
        """
        print(f"DEBUG: ingest_data called with {len(texts)} texts.")
        if not texts:
            return
        
        try:
            docs = [Document(page_content=t) for t in texts]
            print("DEBUG: Documents created.")
            
            # This step calls the Embedding API
            self.vector_store.add_documents(docs)
            print("DEBUG: Documents added to Vector Store.")
            
            # Re-build chain after ingestion
            retriever = self.vector_store.as_retriever()
            self.rag_chain = (
                {"context": retriever | self._format_docs, "question": RunnablePassthrough()}
                | self.prompt
                | self.llm
                | StrOutputParser()
            )
            print(f"RAG System: Ingested {len(texts)} documents. Chain Ready.")
            self.init_error = None
        except Exception as e:
            error_msg = str(e)
            if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
                self.init_error = "Google API Quota Limit. Please try again in a few minutes."
            else:
                self.init_error = f"Initialization Failed: {error_msg}"
            print(f"CRITICAL ERROR in ingest_data: {e}")

    def _format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def get_response(self, question: str) -> str:
        if self.init_error:
            return f"System Unavailable: {self.init_error}"
        if not self.rag_chain:
            return "System is initializing... please wait."
            
        # Check Cache
        if question in self.cache:
            print(f"RAG Cache HIT: {question}")
            return self.cache[question]
            
        try:
             response = self.rag_chain.invoke(question)
             
             # Update Cache
             if len(self.cache) >= self.MAX_CACHE_SIZE:
                 # Remove oldest item (Python 3.7+ dicts preserve insertion order)
                 self.cache.pop(next(iter(self.cache)))
             
             self.cache[question] = response
             return response
        except Exception as e:
            return f"Error generating response: {e}"

# Global singleton
rag_system = RAGFactory()
