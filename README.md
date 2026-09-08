# RuleGuard

**RuleGuard** is an AI-powered rule and policy analysis system designed to answer questions from institutional policy documents, retrieve relevant policy sections, and identify potential conflicts between rules.

The application combines document processing, semantic search, rule retrieval, conflict detection, and answer generation in a simple web interface.

---

## Features

* 📄 **Policy Document Processing**

  * Loads and processes institutional policy documents.
  * Splits documents into searchable chunks.

* 🔎 **Semantic Search**

  * Uses embeddings and a vector index to retrieve relevant policy passages.
  * Returns the most relevant sections for a user's question.

* 🤖 **AI-Powered Answers**

  * Generates answers based on retrieved policy information.
  * Answers are grounded in the available policy documents.

* ⚠️ **Conflict Detection**

  * Detects potentially conflicting or inconsistent rules.
  * Displays the relevant sections and explanations.

* 📚 **Source References**

  * Shows the policy sections used to generate an answer.
  * Displays similarity scores and source information.

* 🌐 **Web Interface**

  * Simple browser-based interface for asking questions.
  * Provides loading, error, answer, conflict, and source sections.

* ☁️ **Deployment Ready**

  * FastAPI backend can be deployed as a web service.
  * The project is configured to work with services such as Render.

---

## Project Structure

```text
RuleGuard/
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── answer_generator.py
│   ├── chunker.py
│   ├── conflict_detector.py
│   ├── document_loader.py
│   ├── embeddings.py
│   ├── models.py
│   ├── retriever.py
│   └── vector_store.py
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── scripts/
│   └── build_index.py
│
├── data/
│   └── policy documents / vector index files
│
├── requirements.txt
└── README.md
```

---

## How It Works

The basic workflow of RuleGuard is:

```text
User Question
      ↓
FastAPI Backend
      ↓
Question Embedding
      ↓
Vector Search
      ↓
Relevant Policy Sections
      ↓
Conflict Detection
      ↓
Answer Generation
      ↓
Answer + Sources + Conflicts
```

### 1. Document Loading

Policy documents are loaded from the project's data sources.

### 2. Chunking

Large documents are divided into smaller sections or chunks so that individual policy rules can be retrieved efficiently.

### 3. Embeddings

Text chunks are converted into vector representations using an embedding model.

### 4. Vector Retrieval

When a user asks a question, the question is converted into an embedding and compared against the stored vectors.

The most relevant policy passages are retrieved.

### 5. Conflict Detection

Retrieved rules are analyzed to identify potential contradictions or conflicts between policy sections.

### 6. Answer Generation

The system generates an answer using the retrieved policy information.

The response also includes relevant sources so that the user can verify the answer against the original rules.

---

## Requirements

* Python 3.10+
* pip
* Virtual environment
* Required Python packages listed in `requirements.txt`

---

## Local Installation

Clone the repository:

```bash
git clone https://github.com/Nidhi-Pathe/RuleGuard.git
cd RuleGuard
```

Create a virtual environment:

### Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

---

## Building the Vector Index

If the vector index needs to be generated, run:

```powershell
python scripts/build_index.py
```

This processes the available policy documents and creates the data required for semantic retrieval.

---

## Running the Application

The FastAPI application is located in:

```text
backend/main.py
```

Start the server with:

```powershell
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

If port `8000` is already in use, use another port:

```powershell
uvicorn backend.main:app --host 127.0.0.1 --port 8001
```

Then open the application in your browser:

```text
http://127.0.0.1:8001
```

or, if using port 8000:

```text
http://127.0.0.1:8000
```

---

## API

### Health Check

```http
GET /health
```

Used to check whether the backend is running correctly.

### Ask a Question

```http
POST /ask
```

Example request:

```json
{
  "question": "What attendance is required to appear for semester examinations?"
}
```

The endpoint returns the generated answer along with relevant sources and detected conflicts.

---

## Frontend

The frontend is built using standard:

* HTML
* CSS
* JavaScript

The frontend communicates with the FastAPI backend through the `/ask` endpoint.

Example:

```javascript
fetch("/ask", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    question: question
  })
});
```

The interface displays:

* Generated answer
* Rule status
* Relevant policy sources
* Similarity scores
* Detected conflicts
* Error messages

---

## Error Handling

The frontend handles both JSON and non-JSON backend responses.

This prevents errors such as:

```text
Unexpected end of JSON input
```

when the backend returns an empty or non-JSON error response.

---

## Deployment

RuleGuard can be deployed as a Python web service.

For a Render deployment, the application should use the platform-provided port.

Example start command:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

The application should also ensure that all required data files, including the vector index, are available in the deployed environment.

---

## Example Questions

RuleGuard can answer questions such as:

```text
What attendance is required to appear for semester examinations?

When is Odd Semester undergraduate tuition due?

What is the weekday hostel curfew for resident students?

Can I pay my fees using cryptocurrency?

What is the library borrowing limit for undergraduate students?
```

---

## Technologies Used

| Technology    | Purpose                                |
| ------------- | -------------------------------------- |
| Python        | Core programming language              |
| FastAPI       | Backend API                            |
| Uvicorn       | ASGI application server                |
| Embeddings    | Semantic representation of policy text |
| Vector Search | Relevant rule retrieval                |
| JavaScript    | Frontend interaction                   |
| HTML/CSS      | Web interface                          |
| Git/GitHub    | Version control                        |
| Render        | Cloud deployment                       |

---

## Project Goal

The goal of RuleGuard is to make institutional policies easier to understand and verify.

Instead of manually searching through lengthy policy documents, users can ask questions in natural language and receive:

1. A direct answer
2. The relevant policy sections
3. Source information
4. Potential conflicts between rules

This makes policy analysis faster, more transparent, and easier to audit.

---

## Future Improvements

Potential future improvements include:

* Support for additional document formats
* Improved citation and source linking
* More advanced conflict classification
* User authentication
* Document version tracking
* Policy update notifications
* Improved answer evaluation
* Persistent vector database
* Better handling of very large policy collections

---

## Author

**Nidhi Pathe**

GitHub:
https://github.com/Nidhi-Pathe/RuleGuard

---

## License

This project is intended for educational and project demonstration purposes.
