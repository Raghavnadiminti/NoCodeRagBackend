import os
from uuid import uuid4
from fastapi import UploadFile
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI 
from serpapi import GoogleSearch
from langchain.chains import RetrievalQA
CHROMA_PATH = "chroma_db"
def get_embeddings(model_name: str = "all-MiniLM-L6-v2"):
   
    
        # For local sentence-transformers
    return SentenceTransformerEmbeddings(model_name=model_name)
embeddings=get_embeddings()

def get_user_collection(user_id: str):
   
    return Chroma(
        persist_directory=CHROMA_PATH,
        collection_name=f"user_{user_id}",
        embedding_function=embeddings
    )


async def store_pdf_in_chroma(user_id: str, workflow_id: str, file: UploadFile):

    # Save PDF temporarily to disk
    temp_path = f"temp_{uuid4()}.pdf"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    # Load & split PDF
    loader = PyPDFLoader(temp_path)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)

    # Add metadata
    doc_id = str(uuid4())
    for c in chunks:
        c.metadata.update({
            "doc_id": doc_id,
            "workflow_id": workflow_id,
            "filename": file.filename,
            "type": "pdf"
        })

    # Store in Chroma
    db = get_user_collection(user_id)
    db.add_documents(chunks)
    db.persist()

    # cleanup
    os.remove(temp_path)

    return {"message": "PDF stored successfully", "doc_id": doc_id}
def get_gemini_llm(model_name: str, api_key: str, temperature: float = 0):
   
    # Replace ChatGemini with the actual Gemini LLM class in your LangChain version
    return ChatGoogleGenerativeAI(
        model_name=model_name,
        api_key=api_key,
        temperature=temperature
    )

def retrieve_by_workflow(user_id: str, workflow_id: str, query: str, k: int = 3):

    # Load user's collection
    db = get_user_collection(user_id)
    
    # Create a retriever that filters by metadata
    retriever = db.as_retriever(search_kwargs={
        "k": k,
        "filter": {"workflow_id": workflow_id}  # filter by workflow_id in metadata
    })

    # Initialize LLM
    llm = get_gemini_llm()

    # Create RetrievalQA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        return_source_documents=True
    )

    # Run query
    result = qa_chain({"query": query})
    return result


def get_serp_results(query: str, api_key: str, num_results: int = 5):
    
    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key,
        "num": num_results
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    output = []
    for res in results.get("organic_results", [])[:num_results]:
        output.append({
            "title": res.get("title", ""),
            "link": res.get("link", ""),
            "snippet": res.get("snippet", "")
        })

    return output