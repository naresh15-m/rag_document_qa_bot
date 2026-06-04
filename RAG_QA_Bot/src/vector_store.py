import os
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

class QdrantVectorStore:
    """
    Manages vector storage and retrieval using Qdrant.
    Uses Qdrant's local in-process storage (persisted to a folder) for simplicity and speed.
    """
    def __init__(self, collection_name: str = "documents", path: str = "./qdrant_db"):
        self.collection_name = collection_name
        self.path = path
        
        # Ensure path directory exists
        os.makedirs(os.path.dirname(os.path.abspath(path)) if os.path.dirname(path) else path, exist_ok=True)
        
        print(f"Connecting to persistent Qdrant database at: {self.path}...")
        self.client = QdrantClient(path=self.path)
        print("Connected to Qdrant database.")

    def create_collection(self, vector_size: int, force_recreate: bool = True):
        """
        Creates or recreates the document collection in Qdrant.
        """
        # Check if collection exists
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        
        if exists and not force_recreate:
            print(f"Collection '{self.collection_name}' already exists. Skipping recreation.")
            return
            
        print(f"Creating collection '{self.collection_name}' with vector dimension {vector_size}...")
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )
        print(f"Collection '{self.collection_name}' created successfully.")

    def add_documents(self, chunks: list[dict], embeddings: list[list[float]]):
        """
        Adds text chunks and their embeddings to the vector store.
        
        chunks: list of dicts, each with {"text": str, "metadata": dict}
        embeddings: list of embedding vectors (list of floats) matching the chunks
        """
        if not chunks or not embeddings:
            print("No documents or embeddings to add.")
            return
            
        if len(chunks) != len(embeddings):
            raise ValueError(f"Mismatch: Got {len(chunks)} chunks and {len(embeddings)} embeddings.")
            
        print(f"Uploading {len(chunks)} document chunks to Qdrant collection '{self.collection_name}'...")
        
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            # Generate a deterministic UUID based on text content to avoid duplicate inserts if re-indexing
            # Alternatively, use random UUIDs. Using uuid.uuid4() for unique indexing on each run.
            point_id = str(uuid.uuid4())
            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "text": chunk["text"],
                        "metadata": chunk["metadata"]
                    }
                )
            )
            
        # Upload points
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        print(f"Uploaded {len(points)} chunks successfully.")

    def search(self, query_embedding: list[float], top_k: int = 3) -> list[dict]:
        """
        Searches the collection for vectors similar to the query embedding.
        Returns a list of dicts: [{"text": str, "metadata": dict, "score": float}]
        """
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=top_k
        )
        
        hits = []
        for res in results.points:
            hits.append({
                "text": res.payload["text"],
                "metadata": res.payload["metadata"],
                "score": res.score
            })
            
        return hits
