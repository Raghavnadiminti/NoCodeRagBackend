import json

def extract_node_info(nodes_json: str | list[dict]):

    # Parse JSON if string
    if isinstance(nodes_json, str):
        nodes = json.loads(nodes_json)
    else:
        nodes = nodes_json

    extracted = {
        "apiKeys": [],
        "queries": [],
        "files": [],
        "llmModels": [],
        "embeddingModels": [],
        "serpApiKeys": []
    }

    for node in nodes:
        data = node.get("data", {})

        # Extract apiKey
        if "apiKey" in data:
            extracted["apiKeys"].append(data["apiKey"])

        # Extract serpApiKey
        if "serpApiKey" in data:
            extracted["serpApiKeys"].append(data["serpApiKey"])

        # Extract query
        if "query" in data:
            extracted["queries"].append(data["query"])

        # Extract file (knowledgeBase)
        if "file" in data:
            extracted["files"].append(data["file"])

        # Extract llm model
        if "model" in data:
            extracted["llmModels"].append(data["model"])

        # Extract embedding model
        if "embeddingModel" in data:
            extracted["embeddingModels"].append(data["embeddingModel"])

    return extracted



