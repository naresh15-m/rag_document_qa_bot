import os

class LLMGenerator:
    """
    Generates grounded answers to user questions using retrieved context chunks.
    Supports Groq (Llama models) and Google Gemini models.
    Enforces strict grounding (no hallucination) and source citations.
    """
    def __init__(self, provider: str = "groq", model_name: str = None, api_key: str = None):
        self.provider = provider.lower()
        self.model_name = model_name
        self.api_key = api_key
        
        if self.provider == "groq":
            from groq import Groq
            if not self.api_key:
                # Retrieve from environment and clean if necessary (stripping custom prefixes)
                raw_key = os.environ.get("GROQ_API_KEY", "")
                if "gsk_" in raw_key:
                    self.api_key = raw_key[raw_key.index("gsk_"):]
                else:
                    self.api_key = raw_key
                    
            if not self.api_key:
                raise ValueError("GROQ_API_KEY must be provided for Groq generator.")
                
            self.model_name = model_name or "llama-3.3-70b-versatile"
            print(f"Initializing Groq client with model: {self.model_name}...")
            self.client = Groq(api_key=self.api_key)
            
        elif self.provider == "gemini":
            import google.generativeai as genai
            if not self.api_key:
                self.api_key = os.environ.get("GEMINI_API_KEY")
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY must be provided for Gemini generator.")
                
            self.model_name = model_name or "gemini-2.5-flash"
            print(f"Initializing Gemini client with model: {self.model_name}...")
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model_name)
            
        else:
            raise ValueError(f"Unsupported generator provider: {self.provider}")

    def generate_answer(self, query: str, context_chunks: list[dict]) -> str:
        """
        Generates a grounded answer based on the retrieved context chunks.
        
        context_chunks: list of dicts with {"text": str, "metadata": dict}
        """
        if not context_chunks:
            return "I cannot find the answer in the provided documents because no relevant context was retrieved."
            
        # Format the context text for the prompt
        context_blocks = []
        for i, chunk in enumerate(context_chunks):
            meta = chunk["metadata"]
            source = meta.get("source", "Unknown Source")
            
            # Format location string based on whether page (PDF) or section (DOCX/TXT) is present
            if "page" in meta:
                location = f"Page {meta['page']}"
            elif "section" in meta:
                location = f"Section: {meta['section']}"
            else:
                location = "Unknown location"
                
            context_blocks.append(
                f"--- CONTEXT CHUNK {i+1} ---\n"
                f"Source File: {source}\n"
                f"Location: {location}\n"
                f"Content:\n{chunk['text']}\n"
            )
            
        context_text = "\n".join(context_blocks)
        
        system_prompt = (
            "You are a professional document Q&A assistant. Your job is to answer the user's question "
            "based strictly on the provided retrieved context chunks. You must adhere to the following rules:\n\n"
            "1. Grounding: Answer the question relying ONLY on the facts directly mentioned in the context. "
            "Do NOT extrapolate, make assumptions, or bring in outside knowledge.\n"
            "2. Failure Mode: If the context does not contain enough information to answer the question, "
            "you MUST state exactly: 'I cannot find the answer in the provided documents.' Do not attempt to answer using "
            "your training data.\n"
            "3. Citations: You MUST cite the source filename and page/section number for every fact you present. "
            "Use inline markdown citations, e.g., '[source_file.pdf, Page X]' or '[document.docx, Section Y]'. "
            "Do not output general citations at the end of the text; cite inline right after the claim.\n"
            "4. Language: Keep your response concise, structured (using bullet points where appropriate), and objective."
        )
        
        user_prompt = (
            f"Here are the retrieved document context chunks:\n\n"
            f"{context_text}\n"
            f"Question: {query}\n\n"
            f"Generate your grounded answer below following all instructions:"
        )
        
        if self.provider == "groq":
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.0, # Enforce deterministic grounded answers
                    max_tokens=1000
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"Error during Groq completion call: {e}")
                return f"Error generating response from Groq: {e}"
                
        elif self.provider == "gemini":
            try:
                # For Gemini, system instructions are passed to the GenerativeModel constructor
                # or in generation config, but we can also prepend it in a combined prompt
                combined_prompt = f"{system_prompt}\n\n{user_prompt}"
                response = self.client.generate_content(
                    combined_prompt,
                    generation_config={"temperature": 0.0, "max_output_tokens": 1000}
                )
                return response.text.strip()
            except Exception as e:
                print(f"Error during Gemini generation call: {e}")
                return f"Error generating response from Gemini: {e}"
                
        return ""
