from pydantic import BaseModel


class PlatbandPostInternalSchema(BaseModel):
    depth: float
    width: float
    button_hole: str | None

    def __hash__(self) -> int:
        return hash((self.depth, self.width, self.button_hole))
