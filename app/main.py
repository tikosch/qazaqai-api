from fastapi import FastAPI
from app.routers import auth, profile, tests, testres, model
from app.db.base import Base
from app.db.session import engine
from fastapi.middleware.cors import CORSMiddleware

# Create all tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow your frontend's origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(profile.router, prefix="/api", tags=["profile"])
app.include_router(tests.router, prefix="/api", tags=["tests"])
app.include_router(testres.router, prefix="/api", tags=["tests"])
app.include_router(model.router, prefix="/api/model", tags=["Model"])


@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}
