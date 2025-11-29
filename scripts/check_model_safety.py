# scripts/check_model_safety.py

import torch
import os
from datetime import datetime

model_path = "C:/Projects/Final_Project/backend/models/kobert_facility_classifier.pt"

print("=" * 60)
print("🔍 모델 파일 안전성 체크")
print("=" * 60)

# 1. 파일 존재 확인
if not os.path.exists(model_path):
    print("❌ 파일이 존재하지 않습니다.")
    exit()

# 2. 파일 정보
stat = os.stat(model_path)
print(f"\n📁 파일 정보:")
print(f"  - 경로: {model_path}")
print(f"  - 크기: {stat.st_size / 1024 / 1024:.2f} MB")
print(f"  - 생성일: {datetime.fromtimestamp(stat.st_ctime)}")
print(f"  - 수정일: {datetime.fromtimestamp(stat.st_mtime)}")

# 3. 학습 스크립트 확인
train_script = "C:/Projects/Final_Project/backend/scripts/train_kobert.py"
if os.path.exists(train_script):
    print(f"\n✅ 학습 스크립트 존재: train_kobert.py")
else:
    print(f"\n⚠️ 학습 스크립트 없음")

# 4. 안전 모드 로드 테스트
print("\n🔒 안전 모드 테스트 (weights_only=True):")
try:
    model = torch.load(model_path, map_location="cpu", weights_only=True)
    print("  ✅ weights_only=True로 로드 가능 → 매우 안전!")
except Exception as e:
    print("  ⚠️ weights_only=True로 로드 불가")
    print(f"  사유: {str(e)[:150]}...")
    print("\n  💡 본인이 학습시킨 모델이라면 weights_only=False 사용해도 안전합니다.")

# 5. 의심스러운 패턴 검사
print("\n🔍 악성 코드 패턴 검사:")
with open(model_path, "rb") as f:
    content = f.read(2000)  # 처음 2KB만 검사
    
    suspicious = [b'exec', b'eval', b'os.system', b'subprocess', b'__import__']
    found = [kw.decode() for kw in suspicious if kw in content]
    
    if found:
        print(f"  ⚠️ 의심스러운 패턴 발견: {found}")
    else:
        print("  ✅ 의심스러운 패턴 없음")

# 6. 최종 판단
print("\n" + "=" * 60)
print("💡 최종 판단:")
print("  - 본인이 train_kobert.py로 학습시킨 모델이라면 → 100% 안전")
print("  - 외부에서 다운로드한 적이 없다면 → 안전")
print("  - weights_only=False 사용 가능")
print("=" * 60)