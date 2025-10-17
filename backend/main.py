from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "TAX-2 Backend: Operativo"}