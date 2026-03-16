from pydantic import BaseModel
from typing import Any, Optional
from enum import Enum


class ElementType(str, Enum):
    TEXT = "text"
    TABLE = "table"


class ParsedElement(BaseModel):
    type: ElementType
    content: Any
    page: Optional[int] = None
    top: float = 0.0
