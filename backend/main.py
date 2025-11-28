# backend/main.py

from fastapi import FastAPI, APIRouter
from pydantic import BaseModel

from backend.llm_parser import LLMParser
from backend.recommender import Recommender
from utils.rag_service import RAGService

# -------------------------------
# FastAPI 앱 생성
# -------------------------------
app = FastAPI(
    title="Guri Apartment Recommendation API",
    description="구리시 아파트 입지 추천 AI 서버",
    version="1.0.0"
)

# -------------------------------
# 서비스 객체 생성
# -------------------------------
parser = LLMParser()
recommender = Recommender()
rag = RAGService()   # RAG 서비스

# -------------------------------
# 요청 모델
# -------------------------------
class Query(BaseModel):
    text: str

class RecommendRequest(BaseModel):
    conditions: dict

class SharedRequest(BaseModel):
    apt1: str
    apt2: str
    category: str = "school"
    radius: int = 800

# -------------------------------
# 라우터 그룹
# -------------------------------
parse_router = APIRouter(prefix="/parse", tags=["Parser"])
recommend_router = APIRouter(prefix="/recommend", tags=["Recommendation"])
shared_router = APIRouter(prefix="/shared", tags=["Shared-Area"])
rag_router = APIRouter(prefix="/rag", tags=["RAG"])

# -------------------------------
# 파서 API
# -------------------------------
@parse_router.post("/")
def parse_text(req: Query):
    return {
        "input_text": req.text,
        "parsed_conditions": parser.parse_to_conditions(req.text)
    }

# -------------------------------
# 추천 API
# -------------------------------
@recommend_router.post("/")
def recommend_api(req: RecommendRequest):
    return {
        "input_conditions": req.conditions,
        "recommendations": recommender.recommend(req.conditions)
    }

# -------------------------------
# 두 지점 공유 반경 API
# -------------------------------
@shared_router.post("/")
def shared_api(req: SharedRequest):
    return recommender.shared_radius(
        aptA_name=req.apt1,
        aptB_name=req.apt2,
        category=req.category,
        radius=req.radius
    )

# -------------------------------
# RAG 검색 API
# -------------------------------
@rag_router.get("/search")
def rag_query(q: str):
    return rag.search(q)

# -------------------------------
# 라우터 등록
# -------------------------------
app.include_router(parse_router)
app.include_router(recommend_router)
app.include_router(shared_router)
app.include_router(rag_router)

# -------------------------------
# 기본 엔드포인트
# -------------------------------
@app.get("/")
def home():
    return {"message": "Guri AI Recommendation API is running"}
