import os

class DocumentEmbedder:
    """
    Handles generating dense vector embeddings for text chunks.
    Supports:
    - 'local': Offline embeddings using SentenceTransformers (default model: all-MiniLM-L6-v2)
    - 'gemini': Google Generative AI embeddings (default model: text-embedding-004)
    - 'openai': OpenAI embeddings (default model: text-embedding-3-small)
    
    All calls to embed_documents are processed in batches.
    """
    def __init__(self, provider: str = "local", model_name: str = None, api_key: str = None):
        self.provider = provider.lower()
        self.api_key = api_key
        
        if self.provider == "local":
            self.model_name = model_name or "all-MiniLM-L6-v2"
            print(f"Initializing local embedding model: {self.model_name}...")
            # Lazy load sentence_transformers to save startup time if not used
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            print("Local embedding model loaded.")
            
        elif self.provider == "gemini":
            self.model_name = model_name or "models/text-embedding-004"
            print(f"Initializing Gemini embeddings client with model: {self.model_name}...")
            import google.generativeai as genai
            if not api_key:
                api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY must be provided for Gemini embeddings.")
            genai.configure(api_key=api_key)
            self.model = genai
            
        elif self.provider == "openai":
            self.model_name = model_name or "text-embedding-3-small"
            print(f"Initializing OpenAI embeddings client with model: {self.model_name}...")
            from openai import OpenAI
            if not api_key:
                api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY must be provided for OpenAI embeddings.")
            self.client = OpenAI(api_key=api_key)
            
        else:
            raise ValueError(f"Unsupported embedding provider: {self.provider}")

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Embeds a list of text strings in batch.
        """
        if not texts:
            return []
            
        if self.provider == "local":
            # SentenceTransformers encode handles batching internally
            embeddings = self.model.encode(texts, show_progress_bar=False, batch_size=32)
            # Convert NumPy float32 arrays to list of python floats
            return [emb.tolist() for emb in embeddings]
            
        elif self.provider == "gemini":
            # Gemini embed_content supports passing a list of strings
            try:
                response = self.model.embed_content(
                    model=self.model_name,
                    content=texts
                )
                # Response is a dict with 'embedding' key containing a list of dicts with 'values'
                if isinstance(response, dict) and 'embedding' in response:
                    # In some versions, the response structure varies, so let's handle both
                    raw_embs = response['embedding']
                    if len(raw_embs) > 0 and isinstance(raw_embs[0], dict) and 'values' in raw_embs[0]:
                        return [e['values'] for e in raw_embs]
                    return raw_embs
                elif hasattr(response, 'embeddings'):
                    return [e.values for e in response.embeddings]
                return response
            except Exception as e:
                print(f"Error calling Gemini embeddings API: {e}")
                raise e
                
        elif self.provider == "openai":
            try:
                response = self.client.embeddings.create(
                    input=texts,
                    model=self.model_name
                )
                # Sort elements by index to preserve order
                sorted_data = sorted(response.data, key=lambda x: x.index)
                return [item.embedding for item in sorted_data]
            except Exception as e:
                print(f"Error calling OpenAI embeddings API: {e}")
                raise e
                
        return []

    def embed_query(self, text: str) -> list[float]:
        """
        Embeds a single query string.
        """
        embeddings = self.embed_documents([text])
        return embeddings[0] if embeddings else []
