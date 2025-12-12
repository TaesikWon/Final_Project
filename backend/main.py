# backend/main.py

import os
import re
import chromadb
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

from backend.llm_parser import LLMParser
from backend.rag.rag_service import RAGService
from backend.chat_memory import chat_memory

# ---------------------------------------------------------
# 기본 설정
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

app = FastAPI(
    title="Guri Apartment Recommendation API",
    description="구리시 아파트 추천 AI 서버 (대화형 챗봇 모드)",
    version="2.0.0",
)

from fastapi.middleware.cors import CORSMiddleware

origins = ["http://localhost:5173", "http://127.0.0.1:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# 서비스 로딩
# ---------------------------------------------------------
parser = LLMParser()
rag = RAGService()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
embedder = SentenceTransformer("jhgan/ko-sroberta-multitask")
chroma_client = chromadb.PersistentClient(path="./backend/rag/vector_db")

# ---------------------------------------------------------
# Request Model
# ---------------------------------------------------------
class AskRequest(BaseModel):
    question: str

# ---------------------------------------------------------
# GPT 대화형 응답 생성 (핵심)
# ---------------------------------------------------------
def gpt_with_memory(user_question, facility_info=None, apartments=None):
    messages = [
        {
            "role": "system",
            "content": (
                "너는 구리시 지역을 잘 아는 부동산 전문 챗봇이다. "
                "사용자의 질문 맥락을 기억하며 자연스럽게 대화한다."
            ),
        }
    ]

    # 최근 10턴 대화 히스토리
    for turn in chat_memory.history[-10:]:
        messages.append({"role": "user", "content": turn["user"]})
        messages.append({"role": "assistant", "content": turn["ai"]})

    # RAG 검색 결과도 참고용으로 전달
    if facility_info or apartments:
        messages.append(
            {
                "role": "assistant",
                "content": f"시설 정보: {facility_info}\n아파트 검색 결과: {apartments}",
            }
        )

    # 이번 질문
    messages.append({"role": "user", "content": user_question})

    resp = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=2000,
        temperature=0.7,
    )

    return resp.choices[0].message.content.strip()

# ---------------------------------------------------------
# 후속 질문 처리 ("몇 개야?", "가장 가까운 곳은?" 등)
# ---------------------------------------------------------
def handle_followup_question(question: str):
    """
    메모리에 저장된 최근 추천 결과 기반으로 후속 질문 처리
    """
    ctx = chat_memory.get_recent_context()

    if ctx["last_recommendations"] is None:
        return None  # 이전 검색이 없으면 후속 질문 아님

    apts = ctx["last_recommendations"]
    q = question.replace(" ", "")  # 띄어쓰기 제거한 버전

    # 1) 가장 가까운 아파트?
    if "가까운" in question or "최단거리" in question:
        nearest = sorted(apts, key=lambda x: x["distance_school"])[0]
        return (
            f"가장 가까운 아파트는 {nearest['apartment']}이며 "
            f"{int(nearest['distance_school'])}m 떨어져 있습니다."
        )

    # 2) 가장 먼 아파트?
    if "가장멀" in q or "제일멀" in q or "멀리" in question:
        far = sorted(apts, key=lambda x: x["distance_school"], reverse=True)[0]
        return (
            f"가장 먼 아파트는 {far['apartment']}이며 "
            f"{int(far['distance_school'])}m 떨어져 있습니다."
        )

    # 3) 개수 관련 질문
    if re.search(r"몇\s*개", question) or "몇개" in q or "개수" in question:
        return f"총 {len(apts)}개의 아파트가 검색되었습니다."

    return None

# ---------------------------------------------------------
# 추천 API (대화형 모드)
# ---------------------------------------------------------
recommend_router = APIRouter(prefix="/recommend", tags=["Recommendation"])

@recommend_router.post("/ask")
def recommend_api(req: AskRequest):
    user_question = req.question

    # 1) 먼저 후속 질문인지 확인
    followup_answer = handle_followup_question(user_question)
    if followup_answer is not None:
        # 후속 질문이면 RAG 안 돌리고 바로 답변
        chat_memory.save_turn(user_question, followup_answer)
        return {"ok": True, "summary": followup_answer, "result": []}

    # 2) LLM 파싱
    parsed = parser.parse(user_question)
    print("📌 파싱:", parsed)

    if parsed.get("error"):
        chat_memory.save_turn(user_question, parsed["message"])
        return {"ok": False, "error": parsed["message"], "result": []}

    mode = parsed.get("mode")
    limit = parsed.get("limit")
    apartments = []
    facility_info = None

    # 3) 실제 검색 (RAG)
    if mode == "BETWEEN":
        facilities = parsed["facilities"]
        
        # 안전하게 2개만 사용
        if len(facilities) < 2:
            error_msg = "두 개의 시설이 필요합니다."
            chat_memory.save_turn(user_question, error_msg)
            return {"ok": False, "error": error_msg, "result": []}
        
        f1 = facilities[0]
        f2 = facilities[1]
        
        apartments = rag.search_apartments_hybrid(
            parsed=parsed,
            radius=parsed.get("distance_max"),
            query=user_question,
            limit=limit,
        )

        # 실제 시설의 정식 명칭 사용
        facility_info = {
            "mode": "between", 
            "f1": f1["name"],  # dict에서 name 꺼내기
            "f2": f2["name"]   # dict에서 name 꺼내기
        }

    else:
        facility_name = parsed["facility_name"]
        radius = parsed["distance_max"]

        apartments = rag.search_apartments_hybrid(
            facility_name=facility_name,
            radius=radius,
            query=user_question,
            parsed=parsed,
            limit=limit,
        )

        facility_detail = rag.search_facility_best_match(facility_name)
        address = (
            facility_detail.get("address", "주소 없음") if facility_detail else "주소 없음"
        )

        # 실제 시설의 정식 명칭 사용
        facility_info = {
            "facility_name": facility_detail.get("name", facility_name) if facility_detail else facility_name,
            "category": parsed["facility_category"],
            "address": address,
            "radius": radius,
        }

    # 4) GPT 대화형 응답 생성
    summary = gpt_with_memory(user_question, facility_info, apartments)

    # 5) 메모리에 저장
    chat_memory.save_recommendations(facility_info, apartments, mode)
    chat_memory.save_turn(user_question, summary)

    return {"ok": True, "summary": summary, "result": apartments}

# ---------------------------------------------------------
# 라우터 등록 & 헬스체크
# ---------------------------------------------------------
app.include_router(recommend_router)

@app.get("/")
def home():
    return {"message": "Guri AI Recommendation API running (chatbot mode)"}

@app.get("/ping")
def ping():
    return {"msg": "pong"}