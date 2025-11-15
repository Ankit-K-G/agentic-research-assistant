# Simple data schemas and helpers used by agents
from typing import List, Dict, Any
from pydantic import BaseModel

class Domain(BaseModel):
    name: str
    confidence: float

class Question(BaseModel):
    text: str

class Dataset(BaseModel):
    rows: List[Dict[str, Any]]
    meta: Dict[str, Any] = {}

class ExperimentResult(BaseModel):
    summary: Dict[str, Any]
    details: Dict[str, Any] = {}
