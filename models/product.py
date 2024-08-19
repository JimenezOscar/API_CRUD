from pydantic import BaseModel, Field, validator

class Product(BaseModel):
    id: int
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)

    @validator('name')
    def nombre_no_debe_estar_vacio(cls, v):
        if not v.strip():
            raise ValueError('El nombre no debe estar vacío')
        return v
