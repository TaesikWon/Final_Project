from PIL import Image, ImageDraw, ImageFont

# 가로로 길게
width = 1600
height = 800
img = Image.new('RGB', (width, height), color='#F8F9FA')
draw = ImageDraw.Draw(img)

# 한글 폰트
try:
    font_title = ImageFont.truetype("malgun.ttf", 42)
    font_large = ImageFont.truetype("malgun.ttf", 30)
    font_medium = ImageFont.truetype("malgun.ttf", 24)
    font_small = ImageFont.truetype("malgun.ttf", 20)
except:
    font_title = ImageFont.load_default()
    font_large = ImageFont.load_default()
    font_medium = ImageFont.load_default()
    font_small = ImageFont.load_default()

# 색상
color_header = '#3B82F6'
color_input = '#FFFFFF'
color_button = '#3B82F6'
color_chat_bg = '#F7FAFC'
color_user_msg = '#E3F2FD'
color_bot_msg = '#FFFFFF'
color_border = '#CBD5E0'

# 둥근 박스
def draw_rounded_rect(draw, xy, radius=15, fill=None, outline=None, width=2):
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

# 텍스트
def draw_text(draw, text, xy, font=font_medium, color='black'):
    x, y = xy
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = x - text_width / 2
    draw.text((x, y), text, fill=color, font=font)

# 제목
draw_text(draw, "UI Flow - 구리시 아파트 추천 챗봇", (800, 30), font=font_title, color='#2C3E50')

# 음영 배경 (초록색 테두리 대신)
shadow_width = 1100
shadow_x = (width - shadow_width) // 2
y_start = 100

# 그림자 효과 (여러 겹)
for i in range(5):
    alpha = 50 - i * 10
    offset = i * 2
    draw_rounded_rect(draw, [shadow_x-offset, y_start-offset, shadow_x+shadow_width+offset, y_start+620+offset], 
                      fill=None, outline=f'#{"10B981" if i == 0 else "CCCCCC"}', width=1, radius=20)

# 흰색 배경 박스
draw_rounded_rect(draw, [shadow_x, y_start, shadow_x+shadow_width, y_start+620], 
                  fill='#FFFFFF', outline='#E5E7EB', width=2)

# ========== 화면 1: 초기 화면 (좌측) ==========
x1 = shadow_x + 50
screen_y = y_start + 30

# 파란색 헤더
draw_rounded_rect(draw, [x1, screen_y, x1+420, screen_y+60], fill=color_header, outline=color_header, width=3, radius=15)
draw_text(draw, "구리시 AI 아파트 추천 - 챗봇", (x1+210, screen_y+18), font=font_large, color='white')

# 입력창
draw_rounded_rect(draw, [x1, screen_y+100, x1+420, screen_y+160], fill=color_input, outline=color_border, width=2)
draw_text(draw, "예: 구리고 반경 500m 내 아파트 추천해줘", (x1+210, screen_y+120), font=font_small, color='#A0AEC0')

# 보내기 버튼
draw_rounded_rect(draw, [x1, screen_y+190, x1+420, screen_y+250], fill=color_button, outline=color_button, width=2)
draw_text(draw, "보내기", (x1+210, screen_y+208), font=font_medium, color='white')

# 대화 영역
draw_rounded_rect(draw, [x1, screen_y+280, x1+420, screen_y+510], fill=color_chat_bg, outline=color_border, width=2)
draw_text(draw, "대화", (x1+210, screen_y+295), font=font_medium, color='#718096')
draw_text(draw, "아직 대화가 없습니다.", (x1+210, screen_y+380), font=font_small, color='#A0AEC0')

# 레이블
draw_text(draw, "[1] 초기 화면", (x1+210, screen_y+540), font=font_medium, color='#2C3E50')

# 화살표
arrow_x = x1 + 480
draw.line([(arrow_x, 400), (arrow_x+70, 400)], fill='black', width=5)
draw.polygon([(arrow_x+70, 400), (arrow_x+55, 390), (arrow_x+55, 410)], fill='black')

# ========== 화면 2: 응답 화면 (우측) ==========
x2 = arrow_x + 120

# 파란색 헤더
draw_rounded_rect(draw, [x2, screen_y, x2+420, screen_y+60], fill=color_header, outline=color_header, width=3, radius=15)
draw_text(draw, "구리시 AI 아파트 추천 - 챗봇", (x2+210, screen_y+18), font=font_large, color='white')

# 입력창
draw_rounded_rect(draw, [x2, screen_y+100, x2+420, screen_y+160], fill=color_input, outline=color_border, width=2)
draw_text(draw, "예: 가장 가까운 곳은?", (x2+210, screen_y+120), font=font_small, color='#A0AEC0')

# 보내기 버튼
draw_rounded_rect(draw, [x2, screen_y+190, x2+420, screen_y+250], fill=color_button, outline=color_button, width=2)
draw_text(draw, "보내기", (x2+210, screen_y+208), font=font_medium, color='white')

# 대화 영역
draw_rounded_rect(draw, [x2, screen_y+280, x2+420, screen_y+510], fill=color_chat_bg, outline=color_border, width=2)
draw_text(draw, "대화", (x2+210, screen_y+295), font=font_medium, color='#718096')

# 사용자 메시지
draw_rounded_rect(draw, [x2+200, screen_y+330, x2+410, screen_y+370], fill=color_user_msg, outline='#90CAF9', width=2, radius=10)
draw_text(draw, "구리고 반경 500m", (x2+305, screen_y+342), font=font_small, color='black')

# 봇 응답
draw_rounded_rect(draw, [x2+10, screen_y+390, x2+410, screen_y+500], fill=color_bot_msg, outline='#E0E0E0', width=2, radius=10)
draw.text((x2+30, screen_y+405), "1. 수택엘지원앙 (110m)", fill='black', font=font_small)
draw.text((x2+30, screen_y+440), "2. 수택한성3차 (115m)", fill='black', font=font_small)
draw.text((x2+30, screen_y+475), "3. 토평한일 (200m)", fill='black', font=font_small)

# 레이블
draw_text(draw, "[2] 응답 표시 화면", (x2+210, screen_y+540), font=font_medium, color='#2C3E50')

# 저장
img.save('ui_flow_diagram.png', 'PNG', quality=95)
print("✅ UI Flow 다이어그램 생성 완료 (음영 효과)")