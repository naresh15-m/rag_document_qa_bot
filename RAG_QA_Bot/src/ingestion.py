import os
import re
import pypdf
from docx import Document

def clean_text(text: str) -> str:
    """
    Cleans raw text by stripping leading/trailing whitespace, normalizing newlines,
    and removing redundant control characters.
    """
    if not text:
        return ""
    # Replace carriage returns and multiple consecutive newlines with a single newline
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove multiple spaces
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def load_pdf(file_path: str) -> list[dict]:
    """
    Loads a PDF file page by page.
    Returns a list of dicts: [{"text": page_text, "metadata": {"source": filename, "page": page_num}}]
    """
    filename = os.path.basename(file_path)
    documents = []
    
    try:
        reader = pypdf.PdfReader(file_path)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                cleaned = clean_text(text)
                if cleaned:
                    documents.append({
                        "text": cleaned,
                        "metadata": {
                            "source": filename,
                            "page": i + 1
                        }
                    })
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
        
    return documents

def load_docx(file_path: str) -> list[dict]:
    """
    Loads a DOCX file. Tracks headings to associate paragraphs with sections.
    Returns a list of dicts: [{"text": section_text, "metadata": {"source": filename, "section": section_name}}]
    """
    filename = os.path.basename(file_path)
    documents = []
    
    try:
        doc = Document(file_path)
        current_section = "Introduction"
        section_paragraphs = []
        
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
                
            # Check if this is a heading
            # python-docx has styles starting with 'Heading'
            is_heading = para.style.name.startswith("Heading") or text.startswith("##")
            
            if is_heading:
                # Save previous section if it has text
                if section_paragraphs:
                    section_text = clean_text("\n".join(section_paragraphs))
                    if section_text:
                        documents.append({
                            "text": section_text,
                            "metadata": {
                                "source": filename,
                                "section": current_section
                            }
                        })
                    section_paragraphs = []
                
                # Update current section
                current_section = text.lstrip("#").strip()
            else:
                section_paragraphs.append(text)
                
        # Append the last section
        if section_paragraphs:
            section_text = clean_text("\n".join(section_paragraphs))
            if section_text:
                documents.append({
                    "text": section_text,
                    "metadata": {
                        "source": filename,
                        "section": current_section
                    }
                })
    except Exception as e:
        print(f"Error reading DOCX {file_path}: {e}")
        
    return documents

def load_txt(file_path: str) -> list[dict]:
    """
    Loads a TXT file. If headers are written as '## Heading', groups text by headings.
    Returns a list of dicts: [{"text": text, "metadata": {"source": filename, "section": section_name}}]
    """
    filename = os.path.basename(file_path)
    documents = []
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        current_section = "Introduction"
        section_lines = []
        
        for line in lines:
            trimmed = line.strip()
            # Detect section header
            if trimmed.startswith("## ") or (trimmed.isupper() and len(trimmed) > 3 and not trimmed.startswith("-")):
                # Save previous section
                if section_lines:
                    section_text = clean_text("\n".join(section_lines))
                    if section_text:
                        documents.append({
                            "text": section_text,
                            "metadata": {
                                "source": filename,
                                "section": current_section
                            }
                        })
                    section_lines = []
                current_section = trimmed.lstrip("#").strip()
            else:
                section_lines.append(line)
                
        # Save last section
        if section_lines:
            section_text = clean_text("\n".join(section_lines))
            if section_text:
                documents.append({
                    "text": section_text,
                    "metadata": {
                        "source": filename,
                        "section": current_section
                    }
                })
    except Exception as e:
        print(f"Error reading TXT {file_path}: {e}")
        
    return documents

def load_document(file_path: str) -> list[dict]:
    """
    Loads document based on file extension.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return load_pdf(file_path)
    elif ext == '.docx':
        return load_docx(file_path)
    elif ext in ['.txt', '.md']:
        return load_txt(file_path)
    else:
        print(f"Unsupported file type: {ext} for {file_path}")
        return []

def recursive_split(text: str, separators: list[str], chunk_size: int, chunk_overlap: int) -> list[str]:
    """
    Splits text recursively based on a list of separators.
    """
    if len(text) <= chunk_size:
        return [text]
        
    if not separators:
        # No separators left, split by character index with overlap
        step = chunk_size - chunk_overlap
        if step <= 0:
            step = 1
        return [text[i:i + chunk_size] for i in range(0, len(text), step)]
        
    separator = separators[0]
    next_separators = separators[1:]
    
    parts = text.split(separator)
    chunks = []
    current_chunk = []
    current_len = 0
    
    for part in parts:
        part_len = len(part)
        # If adding this part exceeds chunk_size
        sep_len = len(separator) if current_chunk else 0
        if current_len + part_len + sep_len > chunk_size:
            if current_chunk:
                chunk_text = separator.join(current_chunk)
                chunks.append(chunk_text)
                # Compute overlap
                overlap_text = chunk_text[-chunk_overlap:] if chunk_overlap > 0 else ""
                current_chunk = [overlap_text + part] if overlap_text else [part]
                current_len = len(current_chunk[0])
            else:
                # Part is too big, split recursively
                sub_chunks = recursive_split(part, next_separators, chunk_size, chunk_overlap)
                chunks.extend(sub_chunks)
        else:
            current_chunk.append(part)
            current_len += part_len + sep_len
            
    if current_chunk:
        chunks.append(separator.join(current_chunk))
        
    return chunks

def chunk_documents(documents: list[dict], chunk_size: int = 1000, chunk_overlap: int = 150) -> list[dict]:
    """
    Chunks a list of documents.
    Each input document is a dict: {"text": str, "metadata": dict}
    Returns a list of chunks: [{"text": chunk_text, "metadata": {source, page/section}}]
    """
    separators = ["\n\n", "\n", " ", ""]
    chunks = []
    
    for doc in documents:
        split_texts = recursive_split(doc["text"], separators, chunk_size, chunk_overlap)
        for chunk_text in split_texts:
            if chunk_text.strip():
                chunks.append({
                    "text": chunk_text,
                    "metadata": doc["metadata"].copy()
                })
                
    return chunks

def load_directory(dir_path: str) -> list[dict]:
    """
    Loads all supported files from a directory.
    """
    all_docs = []
    if not os.path.exists(dir_path):
        print(f"Directory {dir_path} does not exist.")
        return all_docs
        
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        if os.path.isfile(file_path):
            docs = load_document(file_path)
            all_docs.extend(docs)
            
    return all_docs
