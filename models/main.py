# Importaciones necesarias de FastAPI y Pydantic
from fastapi import FastAPI, HTTPException, Request #fastapi sirve es una libreria para crear apis en python de manera rapida y eficiente 
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, PositiveInt, ValidationError, validator

# Definición del modelo Product usando Pydantic
class Product(BaseModel):
    id: PositiveInt  # El ID debe ser un entero positivo
    name: str  # El nombre debe ser una cadena de texto
    price: float = Field(gt=0, description="The price must be greater than zero")  # El precio debe ser mayor que 0
    stock: int = Field(ge=0, description="The stock must be zero or greater")  # El stock debe ser mayor o igual a 0

    # Validador para asegurarse de que el nombre no esté vacío
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():  # Si el nombre está vacío o solo tiene espacios
            raise ValueError('Name must not be empty')  # Lanza un error
        return v  # Devuelve el nombre si es válido

# Inicialización de la aplicación FastAPI
app = FastAPI()

# Datos iniciales de productos
initial_products = [
    {
        "id": 1,
        "name": "Producto 1",
        "price": 100,
        "stock": 5
    },
    {
        "id": 2,
        "name": "Producto 2",
        "price": 99,
        "stock": 5
    }
]

# Copia de los productos iniciales para manipulación
products = initial_products.copy()

# Manejador de excepciones para errores de validación
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=400,  # Código de estado HTTP 400 (Bad Request)
        content={"detail": exc.errors()}  # Detalles del error
    )

# Endpoint para resetear los productos a su estado inicial
@app.post('/reset')
def reset_products():
    global products  # Indica que se usará la variable global products
    products = initial_products.copy()  # Resetea los productos
    return {"detail": "Products reset"}  # Devuelve un mensaje de confirmación

# Endpoint para crear un nuevo producto
@app.post('/products')
def create_product(product: Product):
    # Verifica si ya existe un producto con el mismo ID
    if any(item['id'] == product.id for item in products):
        raise HTTPException(status_code=400, detail="Product with this ID already exists")  # Lanza un error si el ID ya existe
    products.append(product.dict())  # Añade el nuevo producto a la lista
    return product  # Devuelve el producto creado

# Endpoint para devolver un mensaje simple
@app.get('/')
def message(): 
    return "Bienvenido a mi API Oscar Jimenez"  # Bienvenido a mi API Oscar Jimenez"

# Endpoint para obtener todos los productos
@app.get('/products')
def get_products(): 
    return products  # Devuelve la lista de productos

# Endpoint para obtener un producto por su ID
@app.get('/products/{id}')
def get_product(id: int): 
    # Busca el producto por su ID
    product = next((item for item in products if item['id'] == id), None)
    if product is None:  # Si no se encuentra el producto
        raise HTTPException(status_code=404, detail="Product not found")  # Lanza un error 404
    return product  # Devuelve el producto encontrado

# Endpoint para obtener productos filtrados por stock y precio
@app.get('/products/')
def get_products_by_stock(stock: int, price: float):
    # Filtra los productos por stock y precio
    return [item for item in products if item['stock'] == stock and item['price'] == price]

# Endpoint para actualizar un producto por su ID
@app.put('/products/{id}')
def update_product(id: int, product: Product):
    for index, item in enumerate(products):
        if item['id'] == id:  # Si se encuentra el producto
            products[index] = product.dict()  # Actualiza el producto
            return products[index]  # Devuelve el producto actualizado
    raise HTTPException(status_code=404, detail="Product not found")  # Lanza un error si no se encuentra el producto

# Endpoint para eliminar un producto por su ID
@app.delete("/products/{id}")       
def delete_product(id: int):
    for item in products:
        if item['id'] == id:  # Si se encuentra el producto
            products.remove(item)  # Elimina el producto
            return {"detail": "Product deleted"}  # Devuelve un mensaje de confirmación
    raise HTTPException(status_code=404, detail="Product not found")  # Lanza un error si no se encuentra el producto
