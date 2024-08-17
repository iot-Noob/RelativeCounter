from pydantic import BaseModel,validator,ValidationError


class PathModel(BaseModel):
    path: str

    @validator('path',always=True,pre=True)
    def no_dots_in_path(cls, value):
        if '../' in value or '.../' in value:
            raise ValueError("Path must not contain '../' or '.../'")
        return value