import os
import google.generativeai as genai

class RAGFactory:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            print("WARNING: GOOGLE_API_KEY not found. Chatbot will not work.")
            self.model = None
            return

        try:
            genai.configure(api_key=self.api_key)
            # Use Gemini 1.5 Flash for speed and large context window
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.chat_session = None
            self.context_text = ""
            self.init_error = None
            print("RAG System: Initialized with Google Gemini SDK (Native).")
        except Exception as e:
            self.init_error = f"Initialization Failed: {str(e)}"
            self.model = None
            print(f"CRITICAL ERROR in RAG init: {e}")

    def ingest_data(self, texts: list[str]):
        """
        Ingests text by concatenating it into a single context string.
        Gemini 1.5 Flash has a 1M token context window, so we can pass the whole README.
        """
        print(f"DEBUG: ingest_data called with {len(texts)} texts.")
        if not texts:
            return
        
        try:
            # Combine all texts into one large context block
            self.context_text = "\n\n".join(texts)
            
            # Initialize a chat session with the system instruction (context)
            # We treat the context as a "system prompt" or initial user message for grounding
            history = [
                {
                    "role": "user",
                    "parts": [f"System Context:\n{self.context_text}\n\nYou are a helpful assistant for the Network Security project described above. Answer questions based only on this context."]
                },
                {
                    "role": "model",
                    "parts": ["Understood. I will answer questions based on the provided Network Security project context."]
                }
            ]
            
            self.chat_session = self.model.start_chat(history=history)
            print("DEBUG: Chat session started with context.")
            
        except Exception as e:
            print(f"Error in ingest_data: {e}")
            self.init_error = str(e)

    def get_response(self, question: str) -> str:
        if self.init_error:
            return f"System Unavailable: {self.init_error}"
        if not self.model:
            return "System is initializing... please wait."
            
        try:
            if not self.chat_session:
                # Fallback if no data was ingested yet, just start a blank chat
                self.chat_session = self.model.start_chat(history=[])
                
            response = self.chat_session.send_message(question)
            return response.text
        except Exception as e:
            return f"Error generating response: {e}"

# Global singleton
rag_system = RAGFactory()
