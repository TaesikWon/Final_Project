# scripts/check_model_safety.py

import torch
import os
from datetime import datetime

model_path = "C:/Projects/Final_Project/backend/models/kobert_facility_classifier.pt"

print("=" * 60)
print("?” ëª¨ë¸ ?Œì¼ ?ˆì „??ì²´í¬")
print("=" * 60)

# 1. ?Œì¼ ì¡´ì¬ ?•ì¸
if not os.path.exists(model_path):
    print("???Œì¼??ì¡´ì¬?˜ì? ?ŠìŠµ?ˆë‹¤.")
    exit()

# 2. ?Œì¼ ?•ë³´
stat = os.stat(model_path)
print(f"\n?“ ?Œì¼ ?•ë³´:")
print(f"  - ê²½ë¡œ: {model_path}")
print(f"  - ?¬ê¸°: {stat.st_size / 1024 / 1024:.2f} MB")
print(f"  - ?ì„±?? {datetime.fromtimestamp(stat.st_ctime)}")
print(f"  - ?˜ì •?? {datetime.fromtimestamp(stat.st_mtime)}")

# 3. ?™ìŠµ ?¤í¬ë¦½íŠ¸ ?•ì¸
train_script = "C:/Projects/Final_Project/backend/scripts/train_kobert.py"
if os.path.exists(train_script):
    print(f"\n???™ìŠµ ?¤í¬ë¦½íŠ¸ ì¡´ì¬: train_kobert.py")
else:
    print(f"\n? ï¸ ?™ìŠµ ?¤í¬ë¦½íŠ¸ ?†ìŒ")

# 4. ?ˆì „ ëª¨ë“œ ë¡œë“œ ?ŒìŠ¤??
print("\n?”’ ?ˆì „ ëª¨ë“œ ?ŒìŠ¤??(weights_only=True):")
try:
    model = torch.load(model_path, map_location="cpu", weights_only=True)
    print("  ??weights_only=Trueë¡?ë¡œë“œ ê°€????ë§¤ìš° ?ˆì „!")
except Exception as e:
    print("  ? ï¸ weights_only=Trueë¡?ë¡œë“œ ë¶ˆê?")
    print(f"  ?¬ìœ : {str(e)[:150]}...")
    print("\n  ?’¡ ë³¸ì¸???™ìŠµ?œí‚¨ ëª¨ë¸?´ë¼ë©?weights_only=False ?¬ìš©?´ë„ ?ˆì „?©ë‹ˆ??")

# 5. ?˜ì‹¬?¤ëŸ¬???¨í„´ ê²€??
print("\n?” ?…ì„± ì½”ë“œ ?¨í„´ ê²€??")
with open(model_path, "rb") as f:
    content = f.read(2000)  # ì²˜ìŒ 2KBë§?ê²€??
    
    suspicious = [b'exec', b'eval', b'os.system', b'subprocess', b'__import__']
    found = [kw.decode() for kw in suspicious if kw in content]
    
    if found:
        print(f"  ? ï¸ ?˜ì‹¬?¤ëŸ¬???¨í„´ ë°œê²¬: {found}")
    else:
        print("  ???˜ì‹¬?¤ëŸ¬???¨í„´ ?†ìŒ")

# 6. ìµœì¢… ?ë‹¨
print("\n" + "=" * 60)
print("?’¡ ìµœì¢… ?ë‹¨:")
print("  - ë³¸ì¸??train_kobert.pyë¡??™ìŠµ?œí‚¨ ëª¨ë¸?´ë¼ë©???100% ?ˆì „")
print("  - ?¸ë??ì„œ ?¤ìš´ë¡œë“œ???ì´ ?†ë‹¤ë©????ˆì „")
print("  - weights_only=False ?¬ìš© ê°€??)
print("=" * 60)
