# Setup Guide

## 1. Create Environment

```bash
python -m venv venv
```

Activate:

Windows:
```bash
venv\Scripts\activate
```

Mac/Linux:
```bash
source venv/bin/activate
```

## 2. Install Requirements

```bash
pip install -r requirements.txt
```

Suggested packages:
```text
streamlit
fastapi
uvicorn
python-dotenv
pydantic
langgraph
langchain
langchain-openai
langchain-google-genai
tavily-python
duckduckgo-search
chromadb
sqlalchemy
pymupdf
pdfplumber
pillow
pytesseract
reportlab
```

## 3. Create .env

```text
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key
TAVILY_API_KEY=your_key
```

## 4. Run Streamlit MVP

```bash
streamlit run app/ui/streamlit_app.py
```

## 5. Run FastAPI Backend

```bash
uvicorn app.main:app --reload
```

## 6. Recommended Development Order
1. Streamlit UI
2. LLM call
3. Claim extraction
4. Web search
5. Source scoring
6. TraceBack timeline
7. Memory
8. Report generation
