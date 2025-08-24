# routers/workflow.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from scheemas.workflowschema import WorkflowCreate,NodesRequest
from sqlalchemy.ext.asyncio import AsyncSession
from dbconfig.database import get_db
from models.Workflow_model import Workflow
from models.User_model import User # make sure User model exists

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