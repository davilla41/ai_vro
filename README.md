# AI VRO (Artificial Intelligence Verbal Recovery Operator)

## Project Overview

AI VRO is an innovative software application designed to empower individuals with aphasia to communicate verbally with those around them. Aphasia, a condition affecting language and communication abilities, can significantly impact daily interactions. This project aims to bridge that gap by leveraging Artificial Intelligence, specifically Large Language Models (LLMs) and structured knowledge bases, to generate contextual and easy-to-select verbal responses for the user.

The initial phase (Phase 1) focuses on building a robust backend API that can intelligently process natural language queries, retrieve relevant information from a comprehensive knowledge graph and document repository, and propose suitable, pre-formulated answers.

## Problem Solved

Individuals with aphasia often struggle with speech production, word retrieval, and forming coherent sentences, even if their comprehension remains largely intact. This leads to frustration and isolation. AI VRO seeks to provide a tool that acts as a communication aid, offering pre-generated verbal options based on an understood context, enabling the user to select and convey their thoughts effectively.

## Key Features (Phase 1)

* **Intelligent Query Processing:** Receives natural language questions (currently via text input, transitioning to voice-to-text in future phases).
* **Contextual Knowledge Retrieval:**
    * **Graph Database (Neo4j):** Stores complex personal relationships (family, friends, acquaintances) and their connections, allowing for rich relational queries.
    * **Vector Database (ChromaDB):** Stores factual information and personal narratives (e.g., from PDF documents) as embeddings, enabling semantic search and retrieval.
* **LLM-Powered Response Generation (Google Gemini):** Utilizes Google's Gemini LLMs to:
    * Classify incoming queries as "simple" (e.g., "How are you feeling?") or "knowledge-based" (e.g., "When were you born?", "Do you know David?").
    * Generate 2-4 clear, concise, and contextually relevant response options based on retrieved knowledge or general common sense.
* **API-First Approach:** A FastAPI backend provides a clean and efficient interface for interaction, ready for future integration with a user interface.

## Architecture Overview (Phase 1)

The system is built as a microservice-oriented application, primarily focused on the backend API and knowledge management in this phase.

```mermaid
graph LR
    A[User Query (via Postman/Future UI)] --POST /api/v1/ask--> B(FastAPI Application)
    B --Classify Query & Orchestrate Retrieval--> C{AI Agent / LLM Service (Gemini)}
    C --1. Query Relationships--> D[Graph Database (Neo4j)]
    C --2. Query Facts (Embeddings)--> E[Vector Database (ChromaDB)]
    E --Uses Embeddings from--> F[Gemini Embedding Model]
    C --Generate Possible Answers--> G[JSON Response with Options]
    G --Return to User--> A