from utils.uploadpdf import get_user_collection
from langchain_google_genai import ChatGoogleGenerativeAI 
def extract_details(data: list):
    flag = {
        "dndnode_0": False,
        "dndnode_1": False, 
        "dndnode_2": False,
        "dndnode_3": False
    }
    exec = {}
    # Mark which IDs exist
    for node in data:
        if node["id"] in flag:
            flag[node["id"]] = True 
    # Extract details
    for node in data:
        if node['type'] == "userQuery":
            exec["query"] = node["data"]["query"] 

        elif node['type'] == "llm":
            data2 = node["data"]
            if "model" in data2:
                exec["model"] = data2["model"] 
            if "apiKey" in data2:
                exec["model_api_key"] = data2["apiKey"]
            if "prompt" in data2:
                exec["prompt"] = data2["prompt"]
            if "temperature" in data2:
                exec["temperature"] = data2["temperature"]
            if "serpApiKey" in data2:
                exec["serp_api_key"] = data2["serpApiKey"]

        elif node['type'] == "knowledgeBase":
            data2 = node["data"]
            if "file" in data2:
                exec["knowledge_file"] = data2["file"]
            if "embeddingModel" in data2:
                exec["embedding_model"] = data2["embeddingModel"]
            if "apiKey" in data2:
                exec["kb_api_key"] = data2["apiKey"]

        elif node['type'] == "output":
            exec["output_label"] = node["data"]["label"]

    return exec, flag


def get_pdfs(user_id: str, workflow_id: str,  k=3):
    # Get user's knowledge collection
    chroma_knowledge_db = get_user_collection(user_id)

    # Query PDFs by workflow_id
    results = chroma_knowledge_db.get(
        where={"workflow_id": workflow_id},   # metadata filter
     
    )

    # Return docs and metadata
    pdfs = []
    for doc, meta in zip(results["documents"], results["metadatas"]):
        if meta.get("workflow_id") == workflow_id:
            pdfs.append({"document": doc, "metadata": meta})

    return pdfs

def get_gemini_llm(model_name: str, api_key: str, temperature: float = 0):
    return ChatGoogleGenerativeAI(
        model=model_name,  
        google_api_key=api_key, 
        temperature=temperature
    )

def execute(data: dict,workflow_id:str,user_id:str):
    # Must have model + api key
    if "model" not in data or "model_api_key" not in data:
        return {"error": "Missing model or API key"}

    # Setup LLM
    llm = get_gemini_llm(
        model_name=data["model"],
        api_key=data["model_api_key"],
        temperature=data.get("temperature", 0)
    )

    query = data.get("query", "")
    response_context = []

    # 1. If PDF KnowledgeBase is provided → retrieve docs
    if "knowledge_file" in data:

        pdfs = get_pdfs(
            user_id=user_id,
            workflow_id=workflow_id, 
            k=3
        )
        response_context.append({"pdf_results": pdfs})
    print("knowledge_file" in data and "workflow_id" in data and "doc_id" in data)
    # 2. If SERP API is provided → do a web search
    # if "serp_api_key" in data:
    #     # dummy integration point, you can plug in serpapi client
    #     response_context.append({"serp_search": f"Search would run with key {data['serp_api_key']} and query {query}"})

    # 3. Generate LLM response
    final_prompt = data.get("prompt", "") + "\n" + query + "\nContext: " + str(response_context)
    llm_response = llm.invoke(final_prompt)

    return {
        "query": query,
        "context": response_context,
        "llm_output": llm_response
    }

        
    

    
    


