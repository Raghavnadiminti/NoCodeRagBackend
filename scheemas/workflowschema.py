from pydantic import BaseModel
from typing import Dict, Any, List,Optional

class Position(BaseModel):
    x: float
    y: float
class Edge(BaseModel):
    id: str
    source: str
    target: str
    sourceHandle: Optional[str]
    targetHandle: Optional[str]
class Node(BaseModel):
    id: str
    type: str
    data: Dict[str, Any]   # <--- flexible for any node data
    position: Position

class NodesRequest(BaseModel):
    nodes: List[Node]
    edges:Optional[List[Edge]]
    email:str 
    name:str

class WorkflowCreate(BaseModel):
    name: str
    description: str
    email: str 

 

def verify_nodes(request: NodesRequest) -> bool:
    for node in request.nodes:
        data = node.data
        if node.type == "userQuery":
            if not data.get("query"):
                return False
        elif node.type == "knowledgeBase":
            if not data.get("embeddingModel") or not data.get("apiKey"):
                return False
            # file can be optional
        elif node.type == "llm":
            required_fields = ["model", "apiKey", "prompt", "temperature"]
            for field in required_fields:
                if field not in data or data[field] is None or data[field] == "":
                    return False
        elif node.type == "output":
            continue  # no required fields
        else:
            # unknown node type
            return False
    return True
