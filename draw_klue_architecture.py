from PIL import Image, ImageDraw, ImageFont
import math

# 이미지 설정
width = 1000
height = 1200
img = Image.new('RGB', (width, height), color='#F8F9FA')
draw = ImageDraw.Draw(img)

# 한글 폰트
try:
    font_title = ImageFont.truetype("malgun.ttf", 40)
    font_large = ImageFont.truetype("malgun.ttf", 28)
    font_medium = ImageFont.truetype("malgun.ttf", 24)
    font_small = ImageFont.truetype("malgun.ttf", 20)
except:
    font_title = ImageFont.load_default()
    font_large = ImageFont.load_default()
    font_medium = ImageFont.load_default()
    font_small = ImageFont.load_default()

# 색상
color_input = '#61DAFB'
color_embedding = '#9C27B0'
color_encoder = '#4285F4'
color_output = '#10A37F'
color_border = '#34495E'
color_arrow = '#000000'

# 둥근 박스 함수
def draw_rounded_rect(draw, xy, radius=20, fill=None, outline=None, width=3):
    x1, y1, x2, y2 = xy
    draw.rectangle([x1+radius, y1, x2-radius, y2], fill=fill)
    draw.rectangle([x1, y1+radius, x2, y2-radius], fill=fill)
    draw.pieslice([x1, y1, x1+radius*2, y1+radius*2], 180, 270, fill=fill)
    draw.pieslice([x2-radius*2, y1, x2, y1+radius*2], 270, 360, fill=fill)
    draw.pieslice([x1, y2-radius*2, x1+radius*2, y2], 90, 180, fill=fill)
    draw.pieslice([x2-radius*2, y2-radius*2, x2, y2], 0, 90, fill=fill)
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
def draw_arrow(draw, start, end, width=4):
    draw.line([start, end], fill=color_arrow, width=width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    L = 18
    a = 0.4
    x1 = end[0] - L * math.cos(angle - a)
    y1 = end[1] - L * math.sin(angle - a)
    x2 = end[0] - L * math.cos(angle + a)
    y2 = end[1] - L * math.sin(angle + a)
    draw.polygon([end, (x1, y1), (x2, y2)], fill=color_arrow)

# 텍스트 함수
def draw_text(draw, text, xy, font=font_medium, color='black'):
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = xy[0] - text_width / 2
    draw.text((x, xy[1]), text, fill=color, font=font)

# 제목
draw_text(draw, "KLUE 모델 아키텍처", (500, 40), font=font_title, color='#2C3E50')

# 1. 입력 텍스트
y_pos = 120
draw_rounded_rect(draw, [150, y_pos, 850, y_pos+100], fill=color_input, outline=color_border, width=4)
draw_text(draw, "입력 텍스트", (500, y_pos+25), font=font_large, color='black')
draw_text(draw, '"구리고등학교"', (500, y_pos+60), font=font_small, color='#333')

# 화살표
draw_arrow(draw, (500, y_pos+100), (500, y_pos+160), width=5)

# 2. Tokenizer + Embedding
y_pos = y_pos + 160
draw_rounded_rect(draw, [150, y_pos, 850, y_pos+90], fill=color_embedding, outline=color_border, width=4)
draw_text(draw, "Tokenizer + Embedding", (500, y_pos+30), font=font_large, color='white')

# 화살표
draw_arrow(draw, (500, y_pos+90), (500, y_pos+150), width=5)

# 3. RoBERTa Encoder (6층)
y_pos = y_pos + 150
draw_rounded_rect(draw, [150, y_pos, 850, y_pos+320], fill=color_encoder, outline=color_border, width=4)
draw_text(draw, "RoBERTa Encoder", (500, y_pos+25), font=font_large, color='white')
draw_text(draw, "(6 Layers)", (500, y_pos+60), font=font_medium, color='white')

# 인코더 레이어 표시
layer_y = y_pos + 110
for i in range(6):
    draw_rounded_rect(draw, [200, layer_y + i*32, 800, layer_y + i*32 + 25], 
                      fill='white', outline='#1565C0', width=2, radius=10)
    draw_text(draw, f"Encoder Layer {i}", (500, layer_y + i*32 + 5), font=font_small, color='#1565C0')

# 화살표
draw_arrow(draw, (500, y_pos+320), (500, y_pos+380), width=5)

# 4. Dense Layer + Softmax
y_pos = y_pos + 380
draw_rounded_rect(draw, [150, y_pos, 850, y_pos+100], fill=color_output, outline=color_border, width=4)
draw_text(draw, "Dense Layer + Softmax", (500, y_pos+30), font=font_large, color='white')
draw_text(draw, "7개 카테고리 확률 계산", (500, y_pos+65), font=font_small, color='white')

# 화살표
draw_arrow(draw, (500, y_pos+100), (500, y_pos+160), width=5)

# 5. 출력
y_pos = y_pos + 160
draw_rounded_rect(draw, [150, y_pos, 850, y_pos+80], fill='#FFB74D', outline=color_border, width=4)
draw_text(draw, "출력: school", (500, y_pos+28), font=font_large, color='black')

# 저장
img.save('klue_architecture.png', 'PNG', quality=95)
print("✅ KLUE 아키텍처 다이어그램 생성 완료: klue_architecture.png")