# routers/workflow.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid
from utils.workflow_execute import extract_details,execute
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from scheemas.workflowschema import WorkflowCreate,NodesRequest
from sqlalchemy.ext.asyncio import AsyncSession
from dbconfig.database import get_db
from models.Workflow_model import Workflow
from models.Knowledge_model import Knowledge
from models.User_model import User # make sure User model exists
from fastapi import  UploadFile, File, Form
from utils.uploadpdf import get_user_collection,store_pdf_in_chroma
workflowrouter = APIRouter(prefix="/workflow", tags=["workflow"])


# Route 1: Create a workflow
@workflowrouter.post("/createflow")
async def create_workflow(workflow: WorkflowCreate, db: AsyncSession = Depends(get_db)):
    # fetch user id from email
    result = await db.execute(select(User).where(User.email == workflow.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_workflow = Workflow(
        id=str(uuid.uuid4()),
        name=workflow.name,
        Description=workflow.description,
        user_id=user.id
    )

    db.add(new_workflow)
    await db.commit()
    await db.refresh(new_workflow)

    return {"status": "success", "workflow": new_workflow}

@workflowrouter.post("/uploadpdf")
async def uploadpdf(
    email: str = Form(...),
    workflow_id: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    # find user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # find workflow
    result = await db.execute(
        select(Workflow).where(
            Workflow.id == workflow_id, Workflow.user_id == user.id
        )
    )
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found or access denied")

    # store pdf into chroma (your function)
    res = await store_pdf_in_chroma(user.id, workflow_id, file)
    print("Chroma result ID:", res["doc_id"])

    # create knowledge entry
    new_knowledge = Knowledge(
        id=str(res["doc_id"]),             # Or generate UUID if res["doc_id"] not unique
        user_id=user.id,
        workflow_id=workflow_id,
        pdfId=res["doc_id"]                # keeping pdfId as chroma doc id
    )

    db.add(new_knowledge)
    await db.commit()
    await db.refresh(new_knowledge)

    return {
        "message": "PDF uploaded successfully",
        "knowledge": {
            "id": new_knowledge.id,
            "user_id": new_knowledge.user_id,
            "workflow_id": new_knowledge.workflow_id,
            "pdfId": new_knowledge.pdfId
        }
    }


@workflowrouter.post("/{workflow_id}")
async def update_workflow_nodes(
    workflow_id: str,
    update: NodesRequest,
    db: AsyncSession = Depends(get_db)
):
    # fetch user
    result = await db.execute(select(User).where(User.email == update.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = await db.execute(
        select(Workflow).where(Workflow.id == workflow_id, Workflow.user_id == user.id)
    )
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found or access denied")

    # convert Pydantic -> dict
    update_json = jsonable_encoder(update)

    # update fields
    if update.name:
        workflow.name = update.name
    workflow.data = update_json["nodes"]   #  list[dict]
    workflow.graph = update_json["edges"]  #  list[dict]

    await db.commit()
    await db.refresh(workflow)

    return {"status": "success", "workflow": workflow}

@workflowrouter.get("/{workflow_id}")
async def get_workflow_nodes(
    workflow_id: str,
    db: AsyncSession = Depends(get_db)
):
     result = await db.execute(
        select(Workflow).where(Workflow.id == workflow_id)
    )
     workflow = result.scalar_one_or_none()
     print(workflow.data,type(workflow.data[0]))

     return {"status": "success", "workflow": workflow}


@workflowrouter.get('/execute/{workflow_id}')
async def execute_workflow_nodes(
    workflow_id: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Workflow).where(Workflow.id == workflow_id)
    )
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found or access denied")

    
    user_id = workflow.user_id
    exec_details,flag=extract_details(workflow.data) 
    response = execute(exec_details,workflow_id,user_id) 

    return response 



    