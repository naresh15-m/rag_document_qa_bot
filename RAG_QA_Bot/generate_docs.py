import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from docx import Document

# Create data directory
os.makedirs("data", exist_ok=True)

# 1. Helper to generate a PDF
def create_pdf(filename, title, content_paragraphs):
    doc = SimpleDocTemplate(os.path.join("data", filename), pagesize=letter,
                            rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        spaceAfter=15,
        textColor='#1a365d' # Deep slate blue
    )
    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        spaceBefore=12,
        spaceAfter=6,
        textColor='#2b6cb0' # Slate blue
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=8,
        textColor='#2d3748' # Dark grey
    )
    
    story = []
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 10))
    
    for item in content_paragraphs:
        if item.startswith("## "):
            story.append(Spacer(1, 5))
            story.append(Paragraph(item[3:], h2_style))
        else:
            story.append(Paragraph(item, body_style))
            
    doc.build(story)
    print(f"Generated PDF: {filename}")

# 2. Helper to generate a DOCX
def create_docx(filename, title, content_paragraphs):
    doc = Document()
    doc.add_heading(title, 0)
    
    for item in content_paragraphs:
        if item.startswith("## "):
            doc.add_heading(item[3:], level=1)
        else:
            doc.add_paragraph(item)
            
    doc.save(os.path.join("data", filename))
    print(f"Generated DOCX: {filename}")

# 3. Helper to generate a TXT
def create_txt(filename, title, content_paragraphs):
    filepath = os.path.join("data", filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"{title}\n")
        f.write("=" * len(title) + "\n\n")
        for item in content_paragraphs:
            if item.startswith("## "):
                f.write(f"\n{item}\n" + "-" * len(item) + "\n")
            else:
                f.write(f"{item}\n")
    print(f"Generated TXT: {filename}")


# --- CONTENT DEFINITIONS ---

# Document 1: AI Incident Response Playbook (PDF)
ir_playbook_text = [
    "## 1. Executive Summary & Purpose",
    "This playbook outlines the standard operational procedures for identifying, responding to, containing, and recovering from artificial intelligence and machine learning security incidents. As AI systems are integrated into critical workflows, they introduce unique vulnerabilities, including prompt injection, model inversion, membership inference, training data poisoning, and model evasion. The goal of this document is to minimize operational downtime, protect proprietary intellectual property, ensure compliance with global AI safety regulations, and preserve customer trust.",
    "## 2. Classification of AI Security Incidents",
    "Incidents are categorized into four severity tiers based on their business impact and security risk:",
    "- Severity Level 1 (Critical): Active model exploitation resulting in unauthorized exfiltration of customer PII, systemic generation of toxic or malicious payloads in customer-facing production channels, or complete disruption of core machine learning inference endpoints.",
    "- Severity Level 2 (High): Model manipulation via prompt injection that bypasses system guardrails but remains contained within sandbox environments, or moderate drift in model prediction outputs indicating potential training dataset contamination.",
    "- Severity Level 3 (Medium): Sporadic API errors, minor drift in recommendation system performance metrics, or low-risk data ingestion anomalies.",
    "- Severity Level 4 (Low): General inquiries regarding AI behaviors, system configuration tuning requests, or normal deviations in model latency.",
    "## 3. Incident Containment & Mitigation Procedures",
    "Upon confirmation of an active exploit or high-severity anomaly, the AI Incident Response Team must execute the following containment measures immediately:",
    "- Step 3.1: Isolate affected model inference endpoints. Route incoming traffic to fallback heuristic models or static explanation pages to prevent further exploitation.",
    "- Step 3.2: Capture and freeze state. Take snapshots of model weights, current context window buffers, API request logs, and data pipelines for forensic examination.",
    "- Step 3.3: Re-evaluate safety guardrails. Update the input-output validation layers (e.g., Llama Guard, NeMo Guardrails) to filter the specific payload strings or attack patterns observed.",
    "- Step 3.4: Revert to the last known secure model version. If the active model exhibits systemic instability or weights have been modified, deploy the backup container from the secure repository.",
    "## 4. Recovery and Post-Incident Forensic Auditing",
    "After containment is successful, system restoration can begin. The AI engineering team must audit all training pipelines to identify the vulnerability vector. If the root cause was data poisoning, the contaminated dataset must be isolated and rebuilt. All logs during the incident window must be ingested into the observability stack (e.g., Loki and Prometheus) to refine automated detection rules for prompt injections or evasions. Finally, a structured Post-Incident Report (PIR) detailing the root cause, financial impact, response duration, and preventative action items must be submitted to the Risk Management Committee within 48 hours."
]

# Document 2: NIST AI Risk Management Framework (PDF)
nist_framework_text = [
    "## 1. Overview of the NIST AI RMF",
    "The National Institute of Standards and Technology (NIST) Artificial Intelligence Risk Management Framework (AI RMF) is a voluntary guidance document designed to help organizations manage the unique risks associated with AI systems. The framework emphasizes a structured approach to improving the trustworthiness of AI models throughout their entire lifecycle—from design and development to deployment and decommissioning. Trustworthy AI systems, according to NIST, are safe, secure, resilient, accountable, transparent, explainable, privacy-enhanced, and fair.",
    "## 2. The Core Framework Components",
    "The AI RMF is organized into four distinct functions, which serve as the operational pillars for managing AI risk:",
    "- Function 2.1: GOVERN. This function establishes the organizational culture, policies, and structures necessary to govern risk management activities. It involves setting up ethical guidelines, allocating roles and responsibilities, and ensuring executive oversight of AI deployments.",
    "- Function 2.2: MAP. The Map function helps organizations understand the context of their AI systems. Organizations identify the intended users, define the system's operational parameters, map potential negative impacts, and document the metadata of the training data and models.",
    "- Function 2.3: MEASURE. The Measure function focuses on quantitative and qualitative evaluation of AI systems. This includes running evaluations to detect bias, checking model accuracy, testing robustness against adversarial attacks, and monitoring semantic drift in live production settings.",
    "- Function 2.4: MANAGE. The Manage function involves allocating resources to respond to mapped and measured risks. It includes implementing continuous guardrails, deploying fallback systems, setting up alerts, and establishing incident response protocols when models fail.",
    "## 3. Key Trustworthiness Characteristics",
    "To achieve compliance with the NIST AI RMF, AI systems must demonstrate specific characteristics:",
    "- Robustness and Resilience: Systems must resist adversarial inputs (like evasion attacks) and maintain baseline performance during network anomalies.",
    "- Explainability and Transparency: The inner workings of the model, or at least the logic behind specific outputs, must be explainable to users. Training pipelines and algorithm choices should be documented transparently.",
    "- Fairness and Bias Mitigation: Developers must actively audit training sets to prevent systemic biases that could lead to discriminatory outcomes in lending, hiring, or medical diagnostics."
]

# Document 3: RAG Systems Architecture Guide (DOCX)
rag_guide_text = [
    "## 1. Ingestion Pipeline and Data Preprocessing",
    "Retrieval-Augmented Generation (RAG) is an architectural pattern that enhances Large Language Models by retrieving context from external datasets before generating answers. The pipeline begins with ingestion. Source documents (such as PDFs, DOCX files, and spreadsheets) are extracted and converted into clean, normalized text. This pre-processing step involves removing formatting noise, page headers, footers, page numbers, and system logs. Ensuring clean text is vital: if a chunk contains fragmented footer text, it can pollute the vector representations and degrade semantic retrieval quality.",
    "## 2. Text Chunking Strategies",
    "Once the clean text is extracted, it must be split into smaller, manageable units called chunks. Large text blocks cannot be sent to embedding models or LLMs due to context window constraints. The choice of chunking strategy directly influences RAG performance:",
    "- Fixed-size Chunking: Splits text into a set number of characters or tokens (e.g., 500 characters) regardless of semantic structure. It is simple but often cuts off sentences mid-thought.",
    "- Paragraph-based/Semantic Chunking: Respects paragraph double-newlines or sentence boundaries. Chunks are split dynamically to keep complete ideas intact.",
    "- Overlap Configuration: To prevent losing context at the boundaries where chunks are split, an overlap (typically 10% to 20% of the chunk size) is configured. This ensures that adjacent chunks share a short sequence of sentences.",
    "## 3. Embedding Generation and Vector Indexing",
    "Each chunk is then converted into a dense numerical vector (embedding) using a specialized model (such as all-MiniLM-L6-v2 or text-embedding-3-small). These embeddings represent the semantic meaning of the text. Chunks are uploaded to a Vector Database (e.g., Qdrant, ChromaDB, or FAISS) along with their metadata. The database creates an index (using algorithms like HNSW - Hierarchical Navigable Small World) to enable rapid similarity search during querying.",
    "## 4. Query Processing, Retrieval, and LLM Synthesis",
    "When a user asks a question, the query is embedded using the same embedding model. The vector database performs a cosine similarity search, comparing the query vector to the stored chunk vectors. The database retrieves the top-k most similar chunks. These chunks are stuffed into a prompt template alongside the user's question, creating a context-rich prompt. The LLM reads this context and synthesizes a grounded answer, citing the source files and page numbers stored in the retrieved chunks' metadata. Grounded generation prevents hallucinations and ensures factual accuracy."
]

# Document 4: EU AI Act Compliance Overview (TXT)
eu_ai_act_text = [
    "## 1. Risk-Based Categorization of AI Systems",
    "The European Union Artificial Intelligence Act (EU AI Act) is the world's first comprehensive legal framework regulating artificial intelligence. The law enforces a strict risk-based categorization system, applying different obligations depending on the potential harm an AI system can cause:",
    "- Category 1.1: Unacceptable Risk. Systems in this class are strictly banned. Examples include cognitive behavioral manipulation (e.g., voice-activated toys encouraging dangerous behavior), untargeted scraping of facial images from the internet, and social scoring systems by governments.",
    "- Category 1.2: High Risk. These systems are highly regulated. They include AI used in critical infrastructure, medical devices, educational grading, employee recruitment, credit scoring, and law enforcement. High-risk systems must undergo conformant assessments before deployment.",
    "- Category 1.3: Limited Risk / Transparency obligations. Systems like chatbots, deepfakes, or AI-generated text must be clearly labeled so that users are aware they are interacting with AI.",
    "- Category 1.4: Minimal Risk. This includes applications like spam filters, AI in video games, or search engines. These systems face no additional legal obligations under the Act.",
    "## 2. Legal Requirements for High-Risk AI Systems",
    "Organizations deploying High-Risk AI systems must comply with six core technical and administrative requirements:",
    "- 1. Risk Management: Establish a continuous risk management system to identify and mitigate known risks throughout the model's operational lifecycle.",
    "- 2. Data Governance: Ensure training, validation, and testing datasets are high quality, free of systematic errors, and representative of the deployment population.",
    "- 3. Technical Documentation: Maintain detailed documentation of the system's design, architecture, datasets, and training algorithms to demonstrate compliance to regulatory authorities.",
    "- 4. Automatic Logging: Embed automated logging capabilities to track execution logs, system outputs, and user interactions, allowing trace audits during failures.",
    "- 5. Human Oversight: Design the system to enable meaningful oversight by human supervisors, including override buttons, output verification steps, and emergency kill switches.",
    "- 6. Cybersecurity: Implement high levels of cybersecurity robustness to protect the system against data poisoning, model inversion, and adversarial evasion attacks.",
    "## 3. Enforcement Timelines and Non-Compliance Penalties",
    "The EU AI Act enters into force in phases. Banned systems must be phased out within 6 months of enactment. Obligations for General Purpose AI (GPAI) models apply after 12 months, and full compliance rules for high-risk systems become legally binding after 24 to 36 months. Failure to comply carry severe financial penalties: up to 35 million Euros or 7% of an organization's global annual turnover (whichever is higher) for using banned AI systems, and up to 15 million Euros or 3% of turnover for violating standard compliance requirements."
]

# Document 5: Data Privacy in LLMs Guide (TXT)
llm_privacy_text = [
    "## 1. Data Collection and Consent Policies",
    "Large Language Models (LLMs) require massive datasets for pre-training and fine-tuning. When these datasets contain personal data, organizations face serious compliance risks under frameworks like GDPR and CCPA. Organizations must establish clear data collection and consent policies. Users must be informed if their prompts, chats, or document uploads are used to train future model iterations. Under standard privacy guidelines, users must have the right to opt-out of training pipelines without losing access to the core AI utility.",
    "## 2. PII Filtering and Data Scrubbing",
    "To prevent LLMs from memorizing and subsequently leaking sensitive user data, developers must implement robust pre-processing filters. Personally Identifiable Information (PII)—including social security numbers, credit card details, phone numbers, home addresses, and private email addresses—must be scrubbed from text corpora before embedding or fine-tuning occurs. Standard scrubbing techniques include regular expression matching, named entity recognition (NER) using spaCy or HuggingFace tokenizers, and hashing algorithms that mask PII with generic placeholders (e.g., replacing a name with [REDACTED_NAME]).",
    "## 3. Model Inference Security and fine-tuning leakage",
    "Even with data scrubbing, LLMs can accidentally leak confidential info through semantic associations. To mitigate this risk during fine-tuning, teams can employ Differential Privacy (DP), which adds mathematical noise to gradient updates, ensuring the model does not overfit on any single user's unique text structure. During inference, prompt filters must check both input questions and model outputs. Output filters act as a final guardrail, scanning generated answers for potential leakages of database keys, internal IP addresses, or PII before sending the response to the user's browser interface."
]

# --- EXECUTION ---

# Create the documents
create_pdf("ai_incident_response_playbook.pdf", "AI Incident Response Playbook", ir_playbook_text)
create_pdf("nist_ai_risk_management_framework.pdf", "NIST AI Risk Management Framework (AI RMF)", nist_framework_text)
create_docx("rag_systems_architecture_guide.docx", "RAG Systems Architecture Guide", rag_guide_text)
create_txt("eu_ai_act_compliance_overview.txt", "EU AI Act Compliance Overview", eu_ai_act_text)
create_txt("data_privacy_in_llms_guide.txt", "Data Privacy in Large Language Models", llm_privacy_text)

print("\nAll sample documents generated successfully in data/ directory!")
