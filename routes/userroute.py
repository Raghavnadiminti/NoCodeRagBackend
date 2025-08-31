from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from dbconfig.database import get_db
from models.User_model import User
from models.Workflow_model import Workflow
from scheemas.user_auth import UserCreate, UserLogin

router = APIRouter(
    prefix="/user",
    tags=["UserAuth"]
)

# ---------------- SIGNUP ----------------
@router.post("/signup")
async def signup(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # check if email already exists
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        return {"success": False, "message": "Email already registered"}

    # check if mobile already exists
    result = await db.execute(select(User).where(User.mobile_number == user.mobile_number))
    existing_mobile = result.scalar_one_or_none()
    if existing_mobile:
        return {"success": False, "message": "Mobile number already registered"}

    new_user = User(
        full_name=user.name,
        email=user.email,
        mobile_number=user.mobile_number,
        password=user.password  # in real apps, hash the password!
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"success": True, "message": new_user}

# ---------------- LOGIN ----------------
@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    db_user = result.scalar_one_or_none()

    if not db_user or db_user.password != user.password:
        return {"success": False, "message": "Invalid email or password"}
    
    return {"success": True, "message": {"email": db_user.email}}


@router.get("/workflows/")
async def get_workflows(email:str, db: AsyncSession = Depends(get_db)):
        
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # find workflow
        result = await db.execute(
            select(Workflow).where(
               Workflow.user_id == user.id
            )
        )
        workflow = result.scalars().all()
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found or access denied")
        return workflow
