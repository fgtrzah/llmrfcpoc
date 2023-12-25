from fastapi import FastAPI

# Instantiate the class
app = FastAPI()

# Define a GET method on the specified endpoint
@app.get("/")
def hello():
    return {"result": "Welcome to FastAPI"}
