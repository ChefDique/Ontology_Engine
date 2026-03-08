"""
Ontology Engine — Universal Analog-to-Digital Translation Middleware

Automates extraction of unstructured data (PDFs, scans) into structured,
system-ready formats (CSV, JSON, API payloads) using a 4-node pipeline:

    Node 1: Ingestion (OCR + PII Redaction)
    Node 2: Semantic Extraction (LLM → Structured JSON)
    Node 3: Deterministic Calculus (Python math, O&P stripping)
    Node 4: Output Routing (CSV / REST API to CRM)
"""

__version__ = "0.1.0"
