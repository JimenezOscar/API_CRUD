# Este código utiliza FastAPI para definir y gestionar rutas en la aplicación web, así como para manejar errores mediante HTTPException. JSONResponse se emplea para enviar respuestas en formato JSON.
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, PositiveInt, ValidationError, field_validator

# La clase Product define la estructura de los datos para un producto en la aplicación. Utiliza la biblioteca Pydantic para validar los datos: el id debe ser un entero positivo, el name debe ser una cadena de texto no 
# vacía, el price debe ser un número mayor que cero, y el stock debe ser un número mayor o igual a cero. Esta validación asegura que todos los datos del producto cumplan con las reglas especificadas antes de ser procesados.
class Product(BaseModel):
    id: PositiveInt 
    name: str  
    price: float = Field(gt=0, description="El precio debe ser mayor a 0")
    stock: int = Field(ge=0, description="el stock debe ser mayor o igual a 0")

#El decorador @field_validator('name') en la clase Product asegura que el campo name no esté vacío. La función name_must_not_be_empty verifica si el valor del nombre, después de eliminar los espacios en blanco, es una cadena vacía. 
# Si es así, lanza un error indicando que el nombre no puede estar vacío; de lo contrario, devuelve el valor del nombre para su uso en la aplicación.    
    @field_validator('name')
    def name_must_not_be_empty(cls, v): #cls se refiere a la clase propia v es el valor del campo que se esta validando 
        if not v.strip():       #v.strip()
            raise ValueError('El nombre no puede estar vacio')
        return v  

# FastAPI() crea una instancia de la aplicación FastAPI / luego de instanciarla podemos crear los endpoinds @app.post, @app.get ETC...
app = FastAPI()

# variable que contiene un array y dentro de ella esta una lista de datos.
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

# La variable products se inicializa como una copia de initial_products para permitir la manipulación de los datos de los productos sin afectar el estado original. 
# El manejador de excepciones @app.exception_handler(ValidationError) se encarga de capturar los errores de validación, devolviendo una respuesta JSON con un código de estado 400 y los detalles del error para 
# que el usuario pueda entender qué salió mal.
 
products = initial_products.copy() 

@app.exception_handler(ValidationError) #se lanzara este error que nos proporciona pydantic cuando no se cumplan las condiciones de la clase products 

def validation_exception_handler(exc: ValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors()}
    )


# El endpoint @app.post('/reset') define una ruta que ejecuta una solicitud HTTP POST cuando se accede a /reset. La función reset_products usa la variable global products para restaurarla a su estado inicial, 
# copiando los datos de initial_products. Luego, devuelve un mensaje JSON confirmando que los productos han sido reiniciados.
@app.post('/reset')
def reset_products():
    global products  
    products = initial_products.copy()  
    return {"detail": "Products reset"}  

# El endpoint @app.post('/products') maneja una solicitud HTTP POST en la ruta /products. La función create_product recibe un objeto Product, verifica si ya existe un producto con el mismo ID en la lista products,
# y si es así, lanza un error. Si el ID es único, añade el nuevo producto a la lista usando product.model_dump() y devuelve el producto creado en formato JSON.
@app.post('/products')
def create_product(product: Product):
    
    if any(item['id'] == product.id for item in products): 
        raise HTTPException(
            status_code=400, detail="El producto con este ID ya existe")
    products.append(product.model_dump())  
    return product  
# El endpoint @app.get('/') maneja solicitudes HTTP GET en la ruta raíz (/). La función message devuelve un mensaje simple en formato de texto que dice "Bienvenido a mi API Oscar Jimenez". 
# Este endpoint sirve como una bienvenida o punto de entrada básico para la API.
@app.get('/')
def message():
    return "Bienvenido a mi API Oscar Jimenez"  # Bienvenido a mi API Oscar Jimenez"

# El endpoint @app.get('/products') maneja solicitudes HTTP GET en la ruta /products. La función get_products devuelve la lista actual de productos en formato JSON. Este endpoint permite a los usuarios obtener 
# todos los productos disponibles en la API.
@app.get('/products')
def get_products():
    return products  
#____
# El endpoint @app.get('/products/{id}') maneja solicitudes HTTP GET en la ruta /products/{id}, donde {id} es un parámetro de ruta. La función get_product busca un producto en la lista de productos usando el ID proporcionado. 
# Si el producto se encuentra, se devuelve; si no, se lanza un error 404 con el mensaje "Producto no encontrado". Este endpoint permite a los usuarios obtener detalles de un producto específico por su ID.
@app.get('/products/{id}')
def get_product(id: int):
    
    product = next((item for item in products if item['id'] == id), None)
    if product is None: 
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product  

#El endpoint @app.put('/products/{id}') maneja solicitudes HTTP PUT en la ruta /products/{id}, donde {id} es el identificador del producto que se desea actualizar. 
# La función update_product busca el producto con el ID especificado en la lista products. Si lo encuentra, actualiza ese producto con los nuevos datos proporcionados y devuelve el producto actualizado.
# Si no encuentra el producto, lanza un error 404 indicando que el producto no fue encontrado.
@app.put('/products/{id}')
def update_product(id: int, product: Product):
    for index, item in enumerate(products):
        if item['id'] == id: 
            products[index] = product.model_dump()  
            return products[index]  
    raise HTTPException(status_code=404, detail="Producto no encontrado")


#El endpoint @app.delete("/products/{id}") maneja solicitudes HTTP DELETE en la ruta /products/{id}, donde {id} es el identificador del producto que se desea eliminar. 
# La función delete_product busca el producto con el ID proporcionado en la lista products. Si encuentra el producto, lo elimina de la lista y devuelve un mensaje confirmando la eliminación.
# Si no encuentra el producto, lanza un error 404 indicando que el producto no fue encontrado.
@app.delete("/products/{id}")
def delete_product(id: int):
    for item in products:
        if item['id'] == id:  
            products.remove(item)  
            return {"detail": "Product eliminado"}
    raise HTTPException(status_code=404, detail="Producto no encontrado")

