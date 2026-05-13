# NexPay AI Backend - Comprehensive Project Documentation

## 1. PROJECT OVERVIEW

**Project Name:** NexPay-AI-Service  
**Repository:** ibrahimmabrouki/NexPay-AI-Service  
**Current Branch:** newIngestion  
**Default Branch:** main  
**Technology Stack:** Python, FastAPI, PostgreSQL, Qdrant Vector Database, Google Gemini AI  
**Purpose:** AI-powered financial assistant backend service for the NexPay fintech platform

### Project Description
NexPay AI Backend is a Retrieval-Augmented Generation (RAG) powered AI assistant service designed to provide intelligent financial conversation capabilities. It enables users to interact with their transaction history through natural language queries and voice commands, offering contextual financial insights based on their transaction patterns and conversation memory.

---

## 2. CORE ARCHITECTURE & WORKFLOW

### 2.1 RAG Pipeline Architecture

The system implements a **Retrieval-Augmented Generation (RAG)** pipeline:

```
User Query (Text or Voice)
    ↓
[Speech-to-Text] (if voice input)
    ↓
[Query Embedding] (Using SentenceTransformer)
    ↓
[Vector Similarity Search] (Qdrant Database)
    ↓
[Retrieve Relevant Transactions]
    ↓
[LLM Prompt Construction] (With Context: History + Transactions + Memory)
    ↓
[Google Gemini API Call]
    ↓
AI-Generated Financial Answer
```

### 2.2 Key Components Flow

1. **User Question** → Sent via REST API
2. **Vector Search** → Query is embedded and matched against transaction vectors in Qdrant
3. **Context Retrieval** → Relevant transactions are retrieved with user privacy filter
4. **LLM Generation** → Gemini AI generates contextual response using:
   - User's chat history (last 5 messages)
   - Conversation memory summary (max 500 chars)
   - Retrieved transactions (semantic matches)
5. **Response** → Answer returned to client with original question

---

## 3. PROJECT STRUCTURE & MODULES

### 3.1 Directory Layout

```
ai-service/
├── main.py                          # FastAPI application entry point
├── requirements.txt                 # Python dependencies
├── audio_uploads/                   # Temporary audio file storage
├── db/                              # Database layer
│   ├── __init__.py
│   ├── models.py                    # SQLAlchemy ORM models
│   ├── postgres.py                  # PostgreSQL connection setup
│   └── queries.py                   # Database query functions
├── dependencies/                    # Cross-cutting concerns
│   ├── __init__.py
│   └── security.py                  # API key verification
├── ingestion/                       # Data ingestion & embedding pipeline
│   ├── __init__.py
│   └── embed_transactions.py        # Transaction-to-vector conversion
├── prompts/                         # LLM prompt templates
│   ├── __init__.py
│   └── system_prompt.py             # System-level prompts (empty in current version)
├── routes/                          # FastAPI API endpoints
│   ├── __init__.py
│   ├── chat.py                      # Text-based chat endpoint
│   ├── voice_chat.py                # Voice-based chat endpoint
│   └── summarize_memory.py          # Memory summarization endpoint
├── schemas/                         # Pydantic data models
│   ├── __init__.py
│   ├── chat_schema.py               # Chat request/response schemas
│   └── memory_schema.py             # Memory request schema
├── services/                        # Business logic layer
│   ├── __init__.py
│   ├── embedder.py                  # Text-to-vector embedding
│   ├── llm_service.py               # LLM interaction (Gemini)
│   ├── memory_summarizer.py         # Conversation memory compression
│   ├── rag_pipline.py               # RAG orchestration
│   ├── retriever.py                 # Transaction search logic
│   └── speech_to_text.py            # Audio transcription
├── testing/                         # Test & development scripts
│   ├── creating-collections/        # Qdrant collection creation tests
│   ├── creating-index/              # Qdrant index creation tests
│   ├── test-retriever/              # Transaction retrieval tests
│   ├── testing-db-conn/             # Database connection tests
│   └── testing-insertion/           # Transaction insertion tests
├── uploads/                         # User-uploaded audio files
└── vector/                          # Vector database layer
    ├── __init__.py
    └── qdrant_client.py             # Qdrant client initialization
```

---

## 4. DETAILED COMPONENT DESCRIPTIONS

### 4.1 DATABASE LAYER (`db/`)

#### `models.py` - SQLAlchemy ORM Models

**User Model:**
- `id` (Primary Key): String
- `full_name`: String
- `phone_number`: String

**LedgerTransaction Model:**
- `id` (Primary Key): String
- `user_id` (Foreign Key): Links to User
- `type`: String (TRANSFER, TOPUP, CONVERSION, LEDGER)
- `amount`: Integer
- `currency`: String
- `reference_id`: String
- `reference_type`: String
- `created_at`: DateTime
- `embedded`: Boolean (flag indicating if transaction is embedded in Qdrant)

**Transfer Model:**
- `id` (Primary Key): String
- `sender_id` (Foreign Key): Links to User
- `receiver_id` (Foreign Key): Links to User
- `amount`: Integer
- `currency`: String
- `created_at`: DateTime

**CurrencyConversion Model:**
- `id` (Primary Key): String
- `user_id` (Foreign Key): Links to User
- `from_currency`: String
- `to_currency`: String
- `amount_from`: Integer
- `amount_to`: Integer
- `created_at`: DateTime

**StripeTopup Model:**
- `id` (Primary Key): String
- `user_id` (Foreign Key): Links to User
- `amount`: Integer
- `currency`: String
- `created_at`: DateTime

#### `postgres.py` - Database Connection

```python
- Uses SQLAlchemy ORM
- Connects to PostgreSQL via DATABASE_URL environment variable
- SessionLocal: Factory for creating database sessions
- engine: SQLAlchemy engine managing the connection pool
```

### 4.2 VECTOR DATABASE LAYER (`vector/`)

#### `qdrant_client.py`

- **Purpose:** Centralized Qdrant client initialization
- **Configuration:**
  - URL: From `QDRANT_URL` environment variable
  - API Key: From `QDRANT_API_KEY` environment variable
- **Usage:** Imported and reused across retriever, embedder, and ingestion modules

### 4.3 EMBEDDING & INGESTION (`ingestion/` & `services/embedder.py`)

#### `embedder.py` - Text Vectorization

```python
- Model: SentenceTransformer (default: "sentence-transformers/all-MiniLM-L6-v2")
- Input: Plain text string
- Output: Vector (list of floats) representing semantic meaning
- Lazy Loading: Model loaded on first call, cached for reuse
```

#### `embed_transactions.py` - Transaction Processing Pipeline

**Main Functions:**

1. **`transaction_to_text(transaction: dict) -> str`**
   - Converts structured transaction data into human-readable text
   - Handles multiple transaction types:
     - **TRANSFER**: "TRANSFER | sender: {name} | sender_phone: {phone} | receiver: {name} | receiver_phone: {phone} | amount: {amount} {currency} | date: {created_at}"
     - **TOPUP**: "TOPUP | user: {name} | phone: {phone} | amount: {amount} {currency} | date: {created_at}"
     - **CONVERSION**: "CONVERSION | user: {name} | phone: {phone} | from: {amount_from} {from_currency} | to: {amount_to} {to_currency} | date: {created_at}"
     - **Generic**: "TRANSACTION | user: {name} | phone: {phone} | date: {created_at}"

2. **`upsert_transaction(transaction: dict)`**
   - Converts transaction to text representation
   - Embeds text using SentenceTransformer
   - Creates PointStruct for Qdrant:
     - **id**: UUID4 (unique vector ID)
     - **vector**: Embedding vector
     - **payload**: Metadata including:
       - `event_id`, `user_id`, `user_name`, `phone_number`
       - `event_type`, `created_at`, `text`
       - Transaction-specific fields (receiver info, currency conversion details, amount, currency)
   - Upserts to Qdrant collection (insert or update if exists)

**Important Privacy Feature:** Uses `user_id` in payload to enable filtering during search

### 4.4 RETRIEVAL LOGIC (`services/retriever.py`)

#### `search_transactions(user_id: str, question: str, limit: int = 5) -> list[dict]`

**Workflow:**
1. Embeds the user's question using SentenceTransformer
2. Performs vector similarity search in Qdrant:
   - `collection_name`: From `QDRANT_TRANSACTIONS_COLLECTION` env (default: "transactions")
   - `query`: Question embedding vector
   - `limit`: Number of results to return (default: 5)
   - **query_filter**: Critical privacy filter ensuring only results with matching `user_id`
3. Returns list of top-5 semantic matches
4. Extracts `text` field from each result's payload

**Privacy Protection:** The filter ensures users can ONLY see their own transactions

### 4.5 LLM SERVICE (`services/llm_service.py`)

#### Configuration

- **Primary Model**: From `GEMINI_MODEL` env (default: "gemini-2.5-flash")
- **Fallback Model**: "gemini-1.5-pro-002"
- **API Key**: From `GEMINI_API_KEY` env
- **Temperature**: 0.2 (deterministic, factual responses)
- **Max Output Tokens**: 150 (concise answers)

#### `safe_generate(prompt: str, retries: int = 3) -> str`

**Features:**
- **Model Fallback**: Tries primary model first, then fallback if error
- **Retry Logic**: Up to 3 retries with exponential backoff (2^i seconds)
- **Error Handling**:
  - ServerError (503): Waits before retry
  - Other Errors: Switches model immediately
- **Fallback Response**: Returns "AI service is temporarily busy..." if all attempts fail

#### `generate_answer(question: str, transactions: list, history: list, summary: str) -> str`

**Context Optimization:**
- **Summary**: Limited to 500 characters
- **History**: Last 5 messages, each message content limited to 200 characters
- **Transactions**: All retrieved transactions included

**Prompt Structure:**
```
You are NexPay AI, a financial assistant.

RULES:
- Use ONLY provided context
- Never guess missing data
- If missing → say "not available"
- If unclear → say "I don't have enough information"

CONTEXT:
[MEMORY section - if summary provided]
[CHAT HISTORY section - if history provided]
[TRANSACTIONS section - if transactions provided]

QUESTION:
{user_question}

Answer briefly and clearly.
```

### 4.6 RAG PIPELINE (`services/rag_pipline.py`)

#### `rag_pipeline(user_id: str, question: str, history: list, summary: str) -> str`

**Orchestration Logic:**
1. Calls `search_transactions()` to retrieve relevant transactions
2. Passes results to `generate_answer()` with context
3. Returns AI-generated response

### 4.7 SPEECH-TO-TEXT (`services/speech_to_text.py`)

#### Configuration

- **Model**: Faster-Whisper "base"
- **Device**: CPU (no GPU required)
- **Compute Type**: int8 (quantized, lower memory footprint)

#### `transcribe_audio(file_path: str) -> str`

- Converts audio file to text using Faster-Whisper
- Returns concatenated text from all segments

### 4.8 MEMORY SUMMARIZATION (`services/memory_summarizer.py`)

#### `generate_memory_summary(messages: list[dict]) -> str`

**Purpose:** Compress chat history into condensed financial memory

**Prompt Instructions:**
- Focus on financially relevant information:
  - Frequent transactions
  - Users interacted with
  - Currencies used
  - Spending/transfer patterns
  - Important preferences
- Ignore greetings, small talk, irrelevant chat
- Keep output 8-12 lines maximum
- Never hallucinate or assume missing data

**Usage:** Called by `/summarize-memory` endpoint to compress conversation context

### 4.9 SECURITY (`dependencies/security.py`)

#### `verify_internal_key(x_internal_api_key: str = Header(...)) -> None`

**Authentication Mechanism:**
- Extracts `X-Internal-API-Key` header
- Compares against `INTERNAL_API_KEY` environment variable
- Raises `HTTPException` (403 Forbidden) if mismatch
- Applied as dependency on protected endpoints

---

## 5. API ENDPOINTS

### 5.1 Text Chat Endpoint

**Endpoint:** `POST /api/chat-AI`

**Request Schema (ChatRequest):**
```json
{
  "user_id": "string (required)",
  "question": "string (required)",
  "history": [
    {
      "role": "user|assistant",
      "content": "string"
    }
  ],
  "summary": "string (optional)"
}
```

**Response Schema (ChatResponse):**
```json
{
  "question": "string",
  "answer": "string"
}
```

**Security:** Requires `X-Internal-API-Key` header

**Workflow:**
1. Validates API key
2. Extracts question and context
3. Runs RAG pipeline
4. Returns AI-generated answer

### 5.2 Voice Chat Endpoint

**Endpoint:** `POST /api/voice-chat`

**Request Type:** Multipart Form Data

**Parameters:**
- `audio` (File): Audio file to transcribe
- `user_id` (Form): User identifier
- `summary` (Form, optional): Memory summary
- `history` (Form, optional): JSON string of chat history

**Response Schema:** ChatResponse (same as text chat)

**Processing:**
1. Saves uploaded audio file
2. Transcribes using Faster-Whisper
3. Parses history JSON
4. Runs RAG pipeline with transcribed text
5. Returns answer

### 5.3 Memory Summarization Endpoint

**Endpoint:** `POST /api/summarize-memory`

**Request Schema (MemoryRequest):**
```json
{
  "messages": [
    {
      "role": "string",
      "content": "string"
    }
  ]
}
```

**Response:**
```json
{
  "summary": "string"
}
```

**Security:** Requires `X-Internal-API-Key` header

**Purpose:** Compresses chat history into financial memory for context optimization

---

## 6. DATA FLOW EXAMPLES

### 6.1 Text Chat Flow

```
1. Client sends POST /api/chat-AI
   {
     "user_id": "user123",
     "question": "How much did I transfer to Ahmed last month?",
     "history": [{"role": "user", "content": "What are my recent transactions?"}],
     "summary": "User frequently transfers to Ahmed. Often uses USD and LBP."
   }

2. Endpoint verifies X-Internal-API-Key header

3. RAG Pipeline:
   a) search_transactions("user123", "How much did I transfer to Ahmed last month?")
      - Embeds question → vector
      - Searches Qdrant with user_id filter
      - Returns top 5 matching transactions
   
   b) generate_answer(question, retrieved_transactions, history, summary)
      - Constructs prompt with all context
      - Calls Gemini API with optimized prompt
      - Gets response (max 150 tokens)

4. Returns ChatResponse:
   {
     "question": "How much did I transfer to Ahmed last month?",
     "answer": "$500 USD on March 15"
   }
```

### 6.2 Voice Chat Flow

```
1. Client sends POST /api/voice-chat (multipart)
   - audio: [audio file]
   - user_id: "user123"
   - history: "[{\"role\": \"user\", \"content\": \"What are my recent transfers?\"}]"
   - summary: "User frequently transfers abroad"

2. Server:
   a) Saves audio to uploads/ directory
   b) Transcribes using Faster-Whisper → "How much did I transfer to Ahmed?"
   c) Parses history JSON
   d) Runs rag_pipeline(user_id, transcribed_text, history, summary)
   e) Returns response as ChatResponse
```

### 6.3 Transaction Embedding & Ingestion Flow

```
1. New transfer in PostgreSQL:
   {
     "id": "tx_abc123",
     "user_id": "user123",
     "type": "TRANSFER",
     "sender_id": "user123",
     "receiver_id": "user456",
     "amount": 500,
     "currency": "USD",
     "created_at": "2026-05-12T10:30:00",
     "user_name": "John Doe",
     "phone_number": "+961123456",
     "receiver_name": "Ahmed Smith",
     "receiver_phone": "+961654321"
   }

2. embed_transactions.upsert_transaction() called:
   a) transaction_to_text() converts to:
      "TRANSFER | sender: John Doe | sender_phone: +961123456 | receiver: Ahmed Smith | receiver_phone: +961654321 | amount: 500 USD | date: 2026-05-12T10:30:00"
   
   b) embed_text() vectorizes text → [0.123, -0.456, ...]
   
   c) Creates PointStruct with:
      - id: uuid (unique ID)
      - vector: [0.123, -0.456, ...]
      - payload: {all transaction metadata + text}
   
   d) qdrant_client.upsert() stores in Qdrant

3. Now searchable via semantic query: "transfers to Ahmed"
```

---

## 7. ENVIRONMENT VARIABLES

**Required Configuration:**

| Variable | Purpose | Example |
|----------|---------|---------|
| `POSTGRES_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/nexpay` |
| `QDRANT_URL` | Qdrant vector DB URL | `http://localhost:6333` |
| `QDRANT_API_KEY` | Qdrant authentication | `your-api-key` |
| `QDRANT_TRANSACTIONS_COLLECTION` | Qdrant collection name | `transactions` |
| `GEMINI_API_KEY` | Google Gemini API key | `AIza...` |
| `GEMINI_MODEL` | Primary Gemini model | `gemini-2.5-flash` |
| `EMBEDDING_MODEL_NAME` | SentenceTransformer model | `sentence-transformers/all-MiniLM-L6-v2` |
| `INTERNAL_API_KEY` | API authentication key | `your-secret-key` |

---

## 8. DEPENDENCIES (requirements.txt)

**Key Libraries:**

- **FastAPI**: REST framework
- **Uvicorn**: ASGI server
- **SQLAlchemy**: ORM (PostgreSQL)
- **Qdrant Client**: Vector database client
- **SentenceTransformers**: Text embedding model
- **Google GenAI**: Gemini API integration
- **Faster-Whisper**: Speech-to-text
- **python-dotenv**: Environment variable management
- **Pydantic**: Data validation

---

## 9. TESTING & DEVELOPMENT

### Testing Structure (`testing/`)

- **creating-collections/**: Initialize Qdrant collections
- **creating-index/**: Create vector indices (e.g., by user_id)
- **test-retriever/**: Verify transaction search functionality
- **testing-db-conn/**: Test PostgreSQL and Qdrant connections
- **testing-insertion/**: Verify transaction insertion in databases

---

## 10. KEY FEATURES & DESIGN PATTERNS

### 10.1 Privacy & Security
- **User ID Filtering**: All vector searches filtered by user_id
- **API Key Authentication**: Internal API key required for endpoints
- **No Cross-User Data Leakage**: Isolation at database query level

### 10.2 Performance Optimization
- **Context Limiting**:
  - Summary: max 500 chars
  - History: last 5 messages, each 200 chars
  - Transactions: top 5 results
- **Token Optimization**: Max 150 output tokens for faster responses
- **Lazy Model Loading**: Embedding model loaded on first use, cached
- **Exponential Backoff**: Handles API rate limiting gracefully

### 10.3 Error Handling
- **Model Fallback**: If primary Gemini model fails, switches to backup
- **Retry Logic**: 3 attempts with exponential backoff
- **Graceful Degradation**: Returns user-friendly error message if all attempts fail

### 10.4 Semantic Search
- **Vector Embeddings**: Uses pre-trained SentenceTransformer for understanding meaning
- **User-Scoped Search**: Filters results to user's own transactions only
- **Top-K Retrieval**: Returns most semantically similar transactions

---

## 11. WORKFLOW SUMMARY

### Typical User Interaction:
1. **Input**: User asks question (text or voice)
2. **Processing**:
   - If voice: Transcribe to text
   - Embed question as vector
   - Search Qdrant for relevant transactions (with user filter)
   - Compile context (history + transactions + memory)
   - Call Gemini API with optimized prompt
3. **Output**: Return AI-generated financial answer

### Data Ingestion:
1. New financial transaction in PostgreSQL
2. Convert to human-readable text
3. Generate embedding vector
4. Store in Qdrant with user_id filter
5. Now accessible for semantic search

---

## 12. BRANCH & DEPLOYMENT INFO

- **Current Branch**: newIngestion
- **Default Branch**: main
- **Repository**: ibrahimmabrouki/NexPay-AI-Service

---

## 13. NOTES & CONSIDERATIONS

### Current Limitations:
- Audio files stored temporarily in `uploads/` (should implement cleanup)
- `system_prompt.py` is empty (reserved for future use)
- No pagination for large result sets
- No caching mechanism for repeated queries

### Future Enhancements:
- Implement query result caching
- Add admin dashboard for monitoring
- Support multiple languages
- Implement user feedback loop for model refinement
- Add transaction categorization
- Implement financial alerts and predictions

---

This documentation provides a complete overview of the NexPay AI Backend system, suitable for technical discussions, integration planning, and troubleshooting with other AI systems or developers.
