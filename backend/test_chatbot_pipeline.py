# backend/test_chatbot_pipeline.py

import sys
import os
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.abspath("./"))
sys.path.append(os.path.abspath("../"))

from backend.llm_parser import LLMParser
from backend.scripts.data.find_nearest_apartment import find_nearest_apartment
from backend.scripts.data.haversine_distance import find_apartments_between

from openai import OpenAI
import chromadb
from sentence_transformers import SentenceTransformer


# API Client (GPT만 사용)
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# RAG 설정
DB_PATH_VEC = "C:/Projects/Final_Project/backend/rag/vector_db"
embedder = SentenceTransformer("jhgan/ko-sroberta-multitask")
chroma_client = chromadb.PersistentClient(path=DB_PATH_VEC)

parser = LLMParser()

# 카테고리별 핵심 장점
CATEGORY_BENEFITS = {
    "school": "자녀 통학이 편리하고 학군 환경이 좋습니다",
    "hospital": "응급 상황 대응과 정기 진료가 편리합니다",
    "cafe": "재택근무나 약속 장소로 활용하기 좋습니다",
    "restaurant": "다양한 외식과 배달 이용이 편리합니다",
    "shopping": "일상 장보기와 생활용품 구매가 편리합니다",
    "sports": "꾸준한 운동 습관 유지에 도움이 됩니다"
}


def get_distance_evaluation(actual_distance):
    """거리에 대한 평가"""
    if actual_distance < 200:
        return "매우 가까운 편으로", "도보 2~3분 거리로 매우 편리합니다"
    elif actual_distance < 400:
        return "가까운 편으로", "도보 5분 내외로 접근성이 좋습니다"
    elif actual_distance < 600:
        return "적당한 거리로", "도보 7~8분 정도로 부담 없는 거리입니다"
    else:
        return "다소 거리가 있지만", "도보 10분 내외로 이용 가능한 거리입니다"


def get_smart_rules(category, actual_distance):
    """상황에 맞는 스마트한 규칙 추출"""
    
    try:
        rules_collection = chroma_client.get_collection("facility_rules")
        
        # 카테고리 기본 규칙
        query1 = f"{category} 시설 적정 거리 기준"
        result1 = rules_collection.query(
            query_embeddings=embedder.encode([query1]).tolist(),
            n_results=1
        )
        
        # 실제 거리 평가
        query2 = f"{int(actual_distance)}미터 도보 시간"
        result2 = rules_collection.query(
            query_embeddings=embedder.encode([query2]).tolist(),
            n_results=1
        )
        
        return {
            "basic": result1['documents'][0][0] if result1['documents'][0] else "",
            "distance": result2['documents'][0][0] if result2['documents'][0] else ""
        }
    except:
        return {"basic": "", "distance": ""}


def generate_final_answer_smart(facility_name, distance, apartment, category):
    """개선된 GPT 답변 생성 (간결하고 전문적)"""
    
    actual_distance = apartment["distance_m"]
    distance_eval, distance_detail = get_distance_evaluation(actual_distance)
    rules = get_smart_rules(category, actual_distance)
    benefit = CATEGORY_BENEFITS.get(category, "생활이 편리합니다")
    
    # ✅ 수정: f-string 내부에서 딕셔너리 접근 시 변수로 분리
    rule_basic = rules["basic"]
    rule_distance = rules["distance"]
    
    # 전문 지식 문자열 생성
    expert_knowledge = ""
    if rule_basic:
        expert_knowledge += f"- {rule_basic}\n"
    if rule_distance:
        expert_knowledge += f"- {rule_distance}"
    
    if not expert_knowledge:
        expert_knowledge = "- 적절한 거리의 시설은 생활 편의성을 높입니다"
    
    apt_name = apartment["apartment_name"]
    apt_address = apartment["address"]
    
    prompt = f"""당신은 구리시 부동산 전문 상담사입니다.

<검색 결과>
시설: {facility_name}
아파트: {apt_name}
주소: {apt_address}
거리: {actual_distance}m

<전문 기준>
{expert_knowledge}

<답변 작성 지침>
1. 3-4문장으로 간결하게 (150자 이내)
2. "{facility_name}에서 약 {int(actual_distance)}m 거리" 언급
3. "{distance_detail}" 평가 포함
4. "{benefit}" 강조
5. 자연스러운 대화체, 이모지/표 금지

답변:"""

    gpt = openai_client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=200
    )

    return gpt.choices[0].message.content.strip()


def generate_between_answer_smart(facilities, apartment):
    """두 시설 사이 답변 생성 (개선)"""
    
    fac1_name = facilities[0]['name']
    fac2_name = facilities[1]['name']
    apt_name = apartment["apartment_name"]
    apt_address = apartment["address"]
    dist_base = apartment["distance_from_base"]
    dist_target = apartment["distance_from_target"]
    
    prompt = f"""당신은 구리시 부동산 전문 상담사입니다.

<검색 결과>
기준 시설: {fac1_name}
목표 시설: {fac2_name}
아파트: {apt_name}
주소: {apt_address}
거리 정보:
- {fac1_name}로부터: {dist_base}m
- {fac2_name}로부터: {dist_target}m

<답변 작성 지침>
1. 3-4문장으로 간결하게
2. 두 시설 모두 가깝다는 점 강조
3. 기준 시설과의 거리를 먼저 언급
4. 자연스러운 대화체, 이모지/표 금지

답변:"""

    gpt = openai_client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=200
    )

    return gpt.choices[0].message.content.strip()


def run_test():
    print("⚡ 테스트 시작\n")

    user_input = input("사용자 질문: ")

    parsed = parser.parse(user_input)
    print("\n[1] 파싱 결과:", parsed)

    # 파싱 실패
    if "error" in parsed:
        print("\n" + "="*60)
        print("❌ 시설을 찾을 수 없습니다")
        print("="*60)
        
        if "message" in parsed:
            print(f"\n📝 {parsed['message']}")
        
        if "suggestion" in parsed:
            print(f"💡 {parsed['suggestion']}")
        
        print(f"\n📋 현재 지원하는 시설 종류:")
        categories_kr = {
            "school": "학교 (초등학교, 중학교, 고등학교)",
            "hospital": "병원 (의원, 한의원, 클리닉 등)",
            "cafe": "카페 (스타벅스, 투썸, 이디야 등)",
            "restaurant": "음식점 (식당, 레스토랑 등)",
            "shopping": "쇼핑 (마트, 편의점, 백화점 등)",
            "sports": "스포츠 (헬스장, 체육관, 수영장 등)"
        }
        
        for cat in parsed["allowed_categories"]:
            if cat in categories_kr:
                print(f"   • {categories_kr[cat]}")
        
        print("\n" + "="*60)
        return

    # ✅ 사이 검색 모드
    if parsed.get("mode") == "BETWEEN":
        facilities = parsed["facilities"]
        
        print(f"\n{'='*60}")
        print(f"🔍 두 시설 사이 아파트 검색")
        print(f"{'='*60}")
        print(f"  1️⃣ 기준점: {facilities[0]['name']}")
        print(f"  2️⃣ 목표점: {facilities[1]['name']}")
        print(f"  📏 검색 반경: {parsed['distance_max']}m")
        print(f"{'='*60}\n")
        
        apartment = find_apartments_between(
            facilities[0],
            facilities[1],
            search_radius=parsed["distance_max"]
        )
        
        if apartment is None:
            print("\n❌ 조건에 맞는 아파트 없음")
            return
        
        print("\n[2] 아파트 검색 결과:", apartment)
        
        # 답변 생성
        answer = generate_between_answer_smart(facilities, apartment)
    
    # ✅ 단일 시설 검색 모드
    else:
        print(f"\n{'='*60}")
        print(f"🔍 단일 시설 기준 검색")
        print(f"{'='*60}")
        print(f"  📍 시설: {parsed['facility_name']}")
        print(f"  📏 반경: {parsed['distance_max']}m")
        print(f"  🏷️  카테고리: {parsed['facility_category']}")
        print(f"{'='*60}\n")
        
        apartment = find_nearest_apartment(
            facility_id=parsed["facility_id"],
            radius=parsed["distance_max"]
        )
        
        if apartment is None:
            print("\n❌ 반경 내 아파트 없음")
            return
        
        print("\n[2] 아파트 검색 결과:", apartment)
        
        # 답변 생성 (개선된 버전)
        answer = generate_final_answer_smart(
            parsed['facility_name'],
            parsed["distance_max"],
            apartment,
            parsed['facility_category']
        )

    print("\n" + "="*60)
    print("=== 💬 GPT 답변 ===")
    print("="*60)
    print(answer)
    print("="*60)


if __name__ == "__main__":
    run_test()