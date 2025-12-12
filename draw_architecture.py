from PIL import Image, ImageDraw, ImageFont
import math

# 이미지 크기 확대
width = 1800
height = 1000
img = Image.new('RGB', (width, height), color='#F8F9FA')
draw = ImageDraw.Draw(img)

# 한글 폰트 (크기 대폭 증가)
try:
    font_title = ImageFont.truetype("malgun.ttf", 50)
    font_box = ImageFont.truetype("malgun.ttf", 42)
    font_sub = ImageFont.truetype("malgun.ttf", 32)
except:
    font_title = ImageFont.load_default()
    font_box = ImageFont.load_default()
    font_sub = ImageFont.load_default()

# 색상 정의
color_react = '#61DAFB'
color_fastapi = '#009688'
color_db = '#4285F4'
color_gpt = '#10A37F'
color_rag = '#FFE9C4'
color_embed = '#9C27B0'
color_border = '#34495E'
color_arrow = '#000000'

# 둥근 박스 함수
def draw_rounded_rect(draw, xy, radius=20, fill=None, outline=None, width=3):
    x1, y1, x2, y2 = xy
    draw.rectangle([x1+radius, y1, x2-radius, y2], fill=fill, outline=outline, width=0)
    draw.rectangle([x1, y1+radius, x2, y2-radius], fill=fill, outline=outline, width=0)
    draw.pieslice([x1, y1, x1+radius*2, y1+radius*2], 180, 270, fill=fill, outline=outline)
    draw.pieslice([x2-radius*2, y1, x2, y1+radius*2], 270, 360, fill=fill, outline=outline)
    draw.pieslice([x1, y2-radius*2, x1+radius*2, y2], 90, 180, fill=fill, outline=outline)
    draw.pieslice([x2-radius*2, y2-radius*2, x2, y2], 0, 90, fill=fill, outline=outline)
    if outline:
        draw.arc([x1, y1, x1+radius*2, y1+radius*2], 180, 270, fill=outline, width=width)
        draw.arc([x2-radius*2, y1, x2, y1+radius*2], 270, 360, fill=outline, width=width)
        draw.arc([x1, y2-radius*2, x1+radius*2, y2], 90, 180, fill=outline, width=width)
        draw.arc([x2-radius*2, y2-radius*2, x2, y2], 0, 90, fill=outline, width=width)
        draw.line([x1+radius, y1, x2-radius, y1], fill=outline, width=width)
        draw.line([x1+radius, y2, x2-radius, y2], fill=outline, width=width)
        draw.line([x1, y1+radius, x1, y2-radius], fill=outline, width=width)
        draw.line([x2, y1+radius, x2, y2-radius], fill=outline, width=width)

# 화살표 함수
def draw_arrow(draw, start, end, width=3):
    draw.line([start, end], fill=color_arrow, width=width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    L = 15
    a = 0.5
    x1 = end[0] - L * math.cos(angle - a)
    y1 = end[1] - L * math.sin(angle - a)
    x2 = end[0] - L * math.cos(angle + a)
    y2 = end[1] - L * math.sin(angle + a)
    draw.polygon([end, (x1, y1), (x2, y2)], fill=color_arrow)

# 텍스트 함수
def draw_text(draw, text, xy, font=font_box, color='black', align='center'):
    x, y = xy
    if align == 'center':
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = x - text_width / 2
    draw.text((x, y), text, fill=color, font=font)

# 제목
draw_text(draw, "Guri Apartment Recommendation System", (900, 40), font=font_title, color='#2C3E50')

# 1. React (좌측)
draw_rounded_rect(draw, [80, 250, 380, 450], fill=color_react, outline=color_border, width=4)
draw_text(draw, "React", (230, 310), font=font_box, color='black')
draw_text(draw, "Frontend", (230, 370), font=font_sub, color='black')

# 2. FastAPI (중앙 상단)
draw_rounded_rect(draw, [600, 250, 900, 450], fill=color_fastapi, outline=color_border, width=4)
draw_text(draw, "FastAPI", (750, 310), font=font_box, color='black')
draw_text(draw, "Backend", (750, 370), font=font_sub, color='black')

# 3. RAG System (중앙 하단 큰 박스)
draw_rounded_rect(draw, [480, 550, 1020, 900], fill=color_rag, outline='#FF6B6B', width=5)
draw_text(draw, "RAG System", (750, 580), font=font_sub, color='black')

# 4. SQLite + ChromaDB
draw_rounded_rect(draw, [520, 650, 730, 860], fill=color_db, outline=color_border, width=3)
draw_text(draw, "SQLite", (625, 705), font=font_sub, color='black')
draw_text(draw, "+", (625, 755), font=font_sub, color='black')
draw_text(draw, "ChromaDB", (625, 800), font=font_sub, color='black')

# 5. Sentence Transformers
draw_rounded_rect(draw, [770, 650, 980, 860], fill=color_embed, outline=color_border, width=3)
draw_text(draw, "Sentence", (875, 725), font=font_sub, color='black')
draw_text(draw, "Transformers", (875, 780), font=font_sub, color='black')

# 6. GPT-4 (우측)
draw_rounded_rect(draw, [1240, 250, 1540, 450], fill=color_gpt, outline=color_border, width=4)
draw_text(draw, "GPT-4", (1390, 310), font=font_box, color='black')
draw_text(draw, "LLM", (1390, 370), font=font_sub, color='black')

# 화살표
draw_arrow(draw, (380, 330), (600, 330), width=4)
draw_arrow(draw, (600, 380), (380, 380), width=4)
draw_arrow(draw, (750, 450), (750, 550), width=4)
draw_arrow(draw, (730, 755), (770, 755), width=3)
draw_arrow(draw, (980, 755), (1240, 350), width=4)
draw_arrow(draw, (1240, 380), (900, 380), width=4)

# 하단 설명
draw_text(draw, "User -> React -> FastAPI -> RAG -> GPT-4 -> Response", (900, 950), font=font_sub, color='#7F8C8D')

# 저장
img.save('system_architecture.png', 'PNG', quality=95)
print("✅ 시스템 아키텍처 생성 완료")