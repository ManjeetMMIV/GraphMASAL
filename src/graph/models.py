from pydantic import BaseModel, Field
from typing import List, Optional

class Concept(BaseModel):
    id: str = Field(..., description="Unique identifier for the concept, usually a slugified name.")
    name: str = Field(..., description="The human-readable name of the concept.")
    description: str = Field(..., description="A detailed explanation of the concept.")
    prerequisites: List[str] = Field(default_factory=list, description="List of concept IDs that are prerequisites for this concept.")
    domain: str = Field(..., description="The domain or subject area (e.g., 'Operating Systems').")
    
class Student(BaseModel):
    id: str = Field(..., description="Unique identifier for the student.")
    name: str = Field(..., description="Name of the student.")
    mastery_levels: dict[str, float] = Field(default_factory=dict, description="A dictionary mapping concept IDs to a mastery level between 0.0 and 1.0.")
