import os
import glob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from llm import get_groq_client, MODEL_NAME

# Simplified RAG bot - returns static responses for now
# Uses TF-IDF for retrieval and Groq for generation

class RAGBot:
    def __init__(self):
        self.documents = []
        self.vectorizer = None
        self.tfidf_matrix = None
        self.load_documents()

    def load_documents(self):
        """Loads all text files from data/rag_docs/"""
        # Adjusted path to match project structure (root/data/rag_docs)
        # Using .. to go up from backend/ to root
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'rag_docs', '*.txt')
        files = glob.glob(path)
        self.documents = []
        
        print(f"[RAG] Loading documents from {path}...")
        for f in files:
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    text = file.read()
                    # Split into chunks (simple paragraph split for now)
                    chunks = [c.strip() for c in text.split('\n\n') if c.strip()]
                    self.documents.extend(chunks)
            except Exception as e:
                print(f"[RAG] Error reading file {f}: {e}")
        
        print(f"[RAG] Loaded {len(self.documents)} chunks.")
        # Pre-compute embeddings (TF-IDF)
        self.compute_embeddings()

    def compute_embeddings(self):
        """Computes TF-IDF matrix for the loaded documents."""
        if not self.documents:
            print("[RAG] No documents to vectorize.")
            return

        try:
            print("[RAG] Computing TF-IDF matrix...")
            self.vectorizer = TfidfVectorizer(stop_words='english')
            self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)
            print("[RAG] Vectorization complete.")
        except Exception as e:
            print(f"[RAG] Vectorization Error: {e}")

    def retrieve_context(self, query, top_k=3):
        """Finds top_k relevant chunks for the query using Cosine Similarity on TF-IDF vectors."""
        if not self.documents or self.vectorizer is None or self.tfidf_matrix is None:
            return []

        try:
            # Transform query to vector
            query_vec = self.vectorizer.transform([query])
            
            # Calculate cosine similarity
            # flattened to getting 1D array of scores
            scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
            
            # Get top_k indices
            # argsort returns indices of sorted array (ascending), so we take last k and reverse
            top_indices = scores.argsort()[-top_k:][::-1]
            
            results = []
            for idx in top_indices:
                if scores[idx] > 0.1: # Minimal relevance threshold
                    results.append(self.documents[idx])
            
            return results
            
        except Exception as e:
            print(f"[RAG] Retrieval Error: {e}")
            return []

    def process_chat(self, user_message):
        """
        Full RAG pipeline: Retrieve -> Generate
        State is NOT stored.
        """
        print(f"\n[RAG] Processing: {user_message}")
        
        # 1. Retrieve
        context_chunks = self.retrieve_context(user_message)
        if not context_chunks:
            context_str = "No specific reference material found for this query."
        else:
            context_str = "\n\n".join(context_chunks)
        
        # 2. Generate
        system_prompt = f"""
        You are a therapy chatbot assistant. Use the following context to answer the user's question.
        
        CONTEXT FROM TEXTBOOKS:
        {context_str}
        
        INSTRUCTIONS:
        - Answer solely based on the provided context if possible.
        - Be helpful and professional.
        - Do NOT mention "I found this in the text".
        - Do NOT remember previous conversations. Treat this as a fresh start.
        """
        
        try:
            client = get_groq_client()
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.5,
                max_tokens=800
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[RAG] Generation Error: {e}")
            if "401" in str(e):
                return "I'm having trouble connecting (Invalid API Key). Please check your Groq API key in settings."
            elif "429" in str(e):
                return "I'm feeling a bit overwhelmed (Rate Limit). Please try again in a moment."
            return f"I am unable to access my library right now. ({e})"

# Singleton instance
rag_bot = RAGBot()
