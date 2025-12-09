"""
Main FastAPI application with user management endpoints.
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from typing import List
from datetime import datetime
from uuid import UUID

from app.database import get_db, engine, Base
from app.models import User, Calculation
from app.schemas import (
    UserCreate, UserRead, UserUpdate, UserLogin,
    PasswordChange,
    CalculationCreate, CalculationRead, CalculationUpdate, OperationType, CalculationSummary
)
from app.security import hash_password, verify_password, create_access_token, get_current_user_id

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Secure FastAPI Application",
    description="User management with secure password hashing and database integration",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup."""
    Base.metadata.create_all(bind=engine)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Application is running"}

# --- User Endpoints ---

@app.post("/users/register", response_model=UserRead, status_code=status.HTTP_201_CREATED, tags=["Users"])
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    """
    Register a new user.
    
    - **username**: Unique username (3-50 characters)
    - **email**: Valid, unique email address
    - **password**: Password (minimum 8 characters)
    
    Returns the created user without password_hash.
    """
    try:
        # Hash the password before storing
        password_hash = hash_password(user_data.password)
        
        # Create new user instance
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=password_hash
        )
        
        # Add to database
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    except IntegrityError as e:
        db.rollback()
        if "username" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )
        elif "email" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User creation failed due to data conflict"
        )

@app.post("/users/login", tags=["Users"])
async def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login a user.
    
    Verifies username and password.
    """
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    if not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    user.last_login = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer", "user_id": str(user.id)}

@app.get("/users/me", response_model=UserRead, tags=["Users"])
async def get_my_profile(
    db: Session = Depends(get_db),
    current_username: str = Depends(get_current_user_id)
) -> UserRead:
    """Return the currently authenticated user's profile."""
    return get_authenticated_user(db, current_username)


@app.put("/users/me", response_model=UserRead, tags=["Users"])
async def update_my_profile(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_username: str = Depends(get_current_user_id)
) -> UserRead:
    """Update profile details for the authenticated user."""
    user = get_authenticated_user(db, current_username)

    try:
        if user_data.username is not None:
            user.username = user_data.username
        if user_data.email is not None:
            user.email = user_data.email
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        if user_data.bio is not None:
            user.bio = user_data.bio

        db.commit()
        db.refresh(user)
        return user

    except IntegrityError as e:
        db.rollback()
        if "username" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )
        elif "email" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Update failed due to data conflict"
        )


@app.get("/users/{user_id}", response_model=UserRead, tags=["Users"])
async def get_user(user_id: str, db: Session = Depends(get_db)) -> UserRead:
    """Get a user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@app.post("/users/change-password", status_code=status.HTTP_204_NO_CONTENT, tags=["Users"])
async def change_password(
    payload: PasswordChange,
    db: Session = Depends(get_db),
    current_username: str = Depends(get_current_user_id)
):
    """Change password for the authenticated user after verifying current password."""
    user = get_authenticated_user(db, current_username)

    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    user.password_hash = hash_password(payload.new_password)
    db.commit()
    return None


@app.get("/users", response_model=List[UserRead], tags=["Users"])
async def list_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)) -> List[UserRead]:
    """
    List all users with pagination.
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@app.put("/users/{user_id}", response_model=UserRead, tags=["Users"])
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
) -> UserRead:
    """Update user information (username or email)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        if user_data.username is not None:
            user.username = user_data.username
        if user_data.email is not None:
            user.email = user_data.email
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        if user_data.bio is not None:
            user.bio = user_data.bio
        
        db.commit()
        db.refresh(user)
        return user
    
    except IntegrityError as e:
        db.rollback()
        if "username" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )
        elif "email" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Update failed due to data conflict"
        )


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Users"])
async def delete_user(user_id: str, db: Session = Depends(get_db)):
    """Delete a user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()

# --- Calculation Endpoints ---

def perform_calculation(a: float, b: float, op: OperationType) -> float:
    """Helper function to perform arithmetic operations."""
    if op == OperationType.ADD:
        return a + b
    elif op == OperationType.SUBTRACT:
        return a - b
    elif op == OperationType.MULTIPLY:
        return a * b
    elif op == OperationType.DIVIDE:
        if b == 0:
            raise ValueError("Division by zero")
        return a / b
    elif op == OperationType.POWER:
        return a ** b
    elif op == OperationType.MODULO:
        if b == 0:
            raise ValueError("Division by zero")
        return a % b
    raise ValueError("Invalid operation")


def get_authenticated_user(db: Session, current_username: str) -> User:
    """Retrieve the authenticated user or raise 404."""
    user = db.query(User).filter(User.username == current_username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@app.post("/calculations", response_model=CalculationRead, status_code=status.HTTP_201_CREATED, tags=["Calculations"])
async def create_calculation(
    calc_data: CalculationCreate, 
    db: Session = Depends(get_db),
    current_username: str = Depends(get_current_user_id)
) -> CalculationRead:
    """
    Add (Create) a new calculation for the authenticated user.
    
    - **a**: First operand
    - **b**: Second operand  
    - **type**: Operation type (Add, Subtract, Multiply, Divide)
    
    Returns the created calculation with computed result.
    """
    user = get_authenticated_user(db, current_username)
    
    try:
        result = perform_calculation(calc_data.a, calc_data.b, calc_data.type)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    db_calc = Calculation(
        a=calc_data.a,
        b=calc_data.b,
        type=calc_data.type,
        result=result,
        user_id=user.id
    )
    db.add(db_calc)
    db.commit()
    db.refresh(db_calc)
    return db_calc


@app.get("/calculations", response_model=List[CalculationRead], tags=["Calculations"])
async def list_calculations(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_username: str = Depends(get_current_user_id)
) -> List[CalculationRead]:
    """
    Browse (List) all calculations for the authenticated user.
    
    Supports pagination with skip and limit parameters.
    """
    # Get user from database
    user = get_authenticated_user(db, current_username)
    
    # Filter calculations by user_id
    calcs = db.query(Calculation).filter(
        Calculation.user_id == user.id
    ).offset(skip).limit(limit).all()
    return calcs


@app.get("/calculations/summary", response_model=CalculationSummary, tags=["Calculations"])
async def calculations_summary(
    db: Session = Depends(get_db),
    current_username: str = Depends(get_current_user_id)
) -> CalculationSummary:
    """Return aggregated metrics for the authenticated user's calculations."""
    user = get_authenticated_user(db, current_username)

    base_query = db.query(Calculation).filter(Calculation.user_id == user.id)
    total = base_query.count()

    breakdown_pairs = db.query(Calculation.type, func.count(Calculation.id)).filter(
        Calculation.user_id == user.id
    ).group_by(Calculation.type).all()
    operations_breakdown = {op: count for op, count in breakdown_pairs}

    average_result = base_query.with_entities(func.avg(Calculation.result)).scalar()
    last_calc = base_query.order_by(Calculation.created_at.desc()).first()

    most_used_operation = None
    if operations_breakdown:
        most_used_operation = max(operations_breakdown, key=operations_breakdown.get)

    return CalculationSummary(
        total=total,
        average_result=float(average_result) if average_result is not None else None,
        last_result=last_calc.result if last_calc else None,
        operations_breakdown=operations_breakdown,
        most_used_operation=most_used_operation,
    )


@app.get("/calculations/{calc_id}", response_model=CalculationRead, tags=["Calculations"])
async def get_calculation(
    calc_id: str, 
    db: Session = Depends(get_db),
    current_username: str = Depends(get_current_user_id)
) -> CalculationRead:
    """
    Read (Get) a specific calculation by ID for the authenticated user.
    
    Returns 404 if calculation not found or doesn't belong to the user.
    """
    # Get user from database
    user = get_authenticated_user(db, current_username)
    
    # Find calculation by ID and ensure it belongs to the user
    calc = db.query(Calculation).filter(
        Calculation.id == calc_id,
        Calculation.user_id == user.id
    ).first()
    
    if not calc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Calculation not found"
        )
    return calc


@app.put("/calculations/{calc_id}", response_model=CalculationRead, tags=["Calculations"])
@app.patch("/calculations/{calc_id}", response_model=CalculationRead, tags=["Calculations"])
async def update_calculation(
    calc_id: UUID, 
    calc_data: CalculationUpdate, 
    db: Session = Depends(get_db),
    current_username: str = Depends(get_current_user_id)
) -> CalculationRead:
    """
    Edit (Update) a calculation for the authenticated user.
    
    Supports both PUT and PATCH methods.
    Updates operands and/or operation type, then recalculates the result.
    """
    try:
        # Get user from database
        user = get_authenticated_user(db, current_username)
        
        # Find calculation by ID and ensure it belongs to the user
        calc = db.query(Calculation).filter(
            Calculation.id == calc_id,
            Calculation.user_id == user.id
        ).first()
        
        if not calc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Calculation not found"
            )

        # Update fields if provided
        if calc_data.a is not None:
            calc.a = calc_data.a
        if calc_data.b is not None:
            calc.b = calc_data.b
        if calc_data.type is not None:
            calc.type = calc_data.type

        # Recompute result
        calc.result = perform_calculation(calc.a, calc.b, OperationType(calc.type))

        db.commit()
        db.refresh(calc)
        return calc
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        print(f"Error updating calculation: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/calculations/{calc_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Calculations"])
async def delete_calculation(
    calc_id: UUID, 
    db: Session = Depends(get_db),
    current_username: str = Depends(get_current_user_id)
):
    """
    Delete a calculation by ID for the authenticated user.
    
    Returns 204 No Content on success, 404 if not found.
    """
    try:
        # Get user from database
        user = get_authenticated_user(db, current_username)
        
        # Find calculation by ID and ensure it belongs to the user
        calc = db.query(Calculation).filter(
            Calculation.id == calc_id,
            Calculation.user_id == user.id
        ).first()
        
        if not calc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Calculation not found"
            )
        
        db.delete(calc)
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        print(f"Error deleting calculation: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
