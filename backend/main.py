# backend/main.py

from fastapi import FastAPI, APIRouter
from pydantic import BaseModel

from backend.llm_parser import LLMParser
from backend.recommender import Recommender

parser = LLMParser()
recommender = Recommender()

app = FastAPI(
    title="Guri Apartment Recommendation API",
    description="구리시 아파트 입지 추천 AI 서버",
    version="1.0.0"
)

class Query(BaseModel):
    text: str

class RecommendRequest(BaseModel):
    conditions: dict

class SharedRequest(BaseModel):
    apt1: str
    apt2: str
    category: str = "school"
    radius: int = 800

parse_router = APIRouter(prefix="/parse", tags=["Parser"])
recommend_router = APIRouter(prefix="/recommend", tags=["Recommendation"])
shared_router = APIRouter(prefix="/shared", tags=["Shared-Area"])

@parse_router.post("/")
def parse_text(req: Query):
    return {
        "input_text": req.text,
        "parsed_conditions": parser.parse_to_conditions(req.text)
    }

@recommend_router.post("/")
def recommend_api(req: RecommendRequest):
    return {
        "input_conditions": req.conditions,
        "recommendations": recommender.recommend(req.conditions)
    }

@shared_router.post("/")
def shared_api(req: SharedRequest):
    return recommender.shared_radius(
        aptA_name=req.apt1,
        aptB_name=req.apt2,
        category=req.category,
        radius=req.radius
    )

app.include_router(parse_router)
app.include_router(recommend_router)
app.include_router(shared_router)

@app.get("/")
def home():
    return {"message": "Guri AI Recommendation API is running"}
