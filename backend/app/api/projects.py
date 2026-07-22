from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.project import SimulationProject
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.services.predefined_templates import get_predefined_projects
from app.api.auth import get_current_user
from app.models.project import User

router = APIRouter(prefix="/projects", tags=["Simulation Projects"])

def seed_default_projects_if_empty(db: Session):
    """
    Checks if simulation_projects is empty and seeds default templates.
    """
    count = db.query(SimulationProject).count()
    if count == 0:
        templates = get_predefined_projects()
        for t in templates:
            proj = SimulationProject(
                id=t["id"],
                name=t["name"],
                description=t["description"],
                domain=t["domain"],
                layout=t["layout"],
                rules=t["rules"],
                agents=t["agents"],
                system_dynamics=t["system_dynamics"],
                global_variables=t["global_variables"]
            )
            db.add(proj)
        db.commit()

@router.get("", response_model=List[ProjectResponse])
def get_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    seed_default_projects_if_empty(db)
    return db.query(SimulationProject).all()

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    seed_default_projects_if_empty(db)
    project = db.query(SimulationProject).filter(SimulationProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project_in: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Check permissions
    if current_user.role not in ["admin", "editor"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions to create projects")
        
    existing = db.query(SimulationProject).filter(SimulationProject.id == project_in.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Project ID already exists")

    project = SimulationProject(
        id=project_in.id,
        name=project_in.name,
        description=project_in.description,
        domain=project_in.domain,
        layout=project_in.layout,
        rules=project_in.rules,
        agents=project_in.agents,
        system_dynamics=project_in.system_dynamics,
        global_variables=project_in.global_variables
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: str, 
    project_in: ProjectUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "editor"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions to update projects")

    project = db.query(SimulationProject).filter(SimulationProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = project_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete projects")

    project = db.query(SimulationProject).filter(SimulationProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()
    return None

@router.post("/{project_id}/reset", response_model=ProjectResponse)
def reset_project_to_template(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "editor"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions to reset projects")
        
    templates = get_predefined_projects()
    matching_template = next((t for t in templates if t["id"] == project_id), None)
    if not matching_template:
        raise HTTPException(status_code=400, detail="Cannot reset project; no default template matches this ID")

    project = db.query(SimulationProject).filter(SimulationProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.name = matching_template["name"]
    project.description = matching_template["description"]
    project.layout = matching_template["layout"]
    project.rules = matching_template["rules"]
    project.agents = matching_template["agents"]
    project.system_dynamics = matching_template["system_dynamics"]
    project.global_variables = matching_template["global_variables"]

    db.commit()
    db.refresh(project)
    return project
