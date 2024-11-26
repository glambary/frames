from typing import TypeVar

from pydantic import BaseModel


BaseModelChildType = TypeVar("BaseModelChildType", bound=BaseModel)
