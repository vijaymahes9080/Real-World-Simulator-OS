from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    role: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "viewer"

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True

# Projects
class ProjectCreate(BaseModel):
    id: str
    name: str
    description: Optional[str] = ""
    domain: str = "general"
    layout: Dict[str, Any] = Field(default_factory=dict)
    rules: List[Dict[str, Any]] = Field(default_factory=list)
    agents: List[Dict[str, Any]] = Field(default_factory=list)
    system_dynamics: Dict[str, Any] = Field(default_factory=dict)
    global_variables: Dict[str, Any] = Field(default_factory=dict)

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    domain: Optional[str] = None
    layout: Optional[Dict[str, Any]] = None
    rules: Optional[List[Dict[str, Any]]] = None
    agents: Optional[List[Dict[str, Any]]] = None
    system_dynamics: Optional[Dict[str, Any]] = None
    global_variables: Optional[Dict[str, Any]] = None

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str
    domain: str
    layout: Dict[str, Any]
    rules: List[Dict[str, Any]]
    agents: List[Dict[str, Any]]
    system_dynamics: Dict[str, Any]
    global_variables: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Runs
class RunCreate(BaseModel):
    project_id: str
    run_type: str  # "agent", "des", "monte_carlo", "system_dynamics"

class RunResponse(BaseModel):
    id: str
    project_id: str
    status: str
    run_type: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    metrics_summary: Dict[str, Any]

    class Config:
        from_attributes = True
