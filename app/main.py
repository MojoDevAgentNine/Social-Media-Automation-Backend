from fastapi import FastAPI, Request
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from .routes import user_routes

app = FastAPI(
    title="Mojo API",
    description="This is the API for the Mojo platform, providing social platform management and more.",
    version="1.0.0",
    docs_url="/",
    redoc_url="/redoc"
)

# Allow CORS from any origin (for development purposes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (for development, be more restrictive in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"message": "Invalid data", "details": exc.errors()},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error", "details": str(exc)},
    )

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API is healthy"}


app.include_router(user_routes.router, prefix="/user", tags=["User Accounts"])