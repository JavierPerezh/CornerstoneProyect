from fastapi import FastAPI

from routers import historial, progreso, usuarios

app = FastAPI(
    title="Posparto API",
    description="API para seguimiento y acompañamiento posparto",
    version="1.0.0",
)

app.include_router(usuarios.router)
app.include_router(historial.router)
app.include_router(progreso.router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Posparto API funcionando"}
