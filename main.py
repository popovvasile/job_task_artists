
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.artist import router
from sessions.session import Base, engine


def init_models():
    with engine.begin() as conn:
        Base.metadata.drop_all
        Base.metadata.create_all

init_models()
app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router, tags=['Artists'], prefix='/api/artists')


@app.get("/api/healthchecker")
def root():
    return {"message": "Welcome to FastAPI with SQLAlchemy"}
