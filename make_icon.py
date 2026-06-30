"""
귀염뽀짝 파스텔 카와이 아이콘 생성기
실행하면 logo.ico 가 생성됩니다.
"""
from PIL import Image, ImageDraw, ImageFont
import struct, os

def draw_heart(draw, cx, cy, size, color):
    """픽셀 하트 그리기"""
    s = size
    for y in range(-s, s + 1):
        for x in range(-s, s + 1):
            # 하트 방정식: (x²+y²-1)³ - x²y³ ≤ 0
            nx = x / s
            ny = -y / s
            if (nx**2 + ny**2 - 1)**3 - nx**2 * ny**3 <= 0:
                draw.point((cx + x, cy + y), fill=color)

def draw_star(draw, cx, cy, r, color):
    """5각 별 그리기"""
    import math
    pts = []
    for i in range(5):
        angle = math.radians(i * 72 - 90)
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
        angle2 = math.radians(i * 72 - 90 + 36)
        pts.append((cx + r * 0.4 * math.cos(angle2), cy + r * 0.4 * math.sin(angle2)))
    draw.polygon(pts, fill=color)

def make_icon(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # 배경 원 (파스텔 보라)
    margin = size // 16
    d.ellipse(
        [margin, margin, size - margin, size - margin],
        fill=(180, 140, 220, 255),
        outline=(140, 100, 190, 255),
        width=max(1, size // 32),
    )

    # 안쪽 밝은 원 (하이라이트)
    inner = size // 5
    d.ellipse(
        [inner, inner, size - inner, size - inner],
        fill=(235, 210, 255, 255),
    )

    cx, cy = size // 2, size // 2

    # 큰 하트 (진한 핑크)
    heart_size = size // 5
    draw_heart(d, cx, cy + size // 30, heart_size, (220, 100, 160, 255))

    # 작은 하트 (흰색 하이라이트)
    small = max(2, heart_size // 3)
    draw_heart(d, cx - heart_size // 3, cy - heart_size // 4, small, (255, 230, 245, 200))

    # 반짝이 별들
    star_color = (255, 210, 80, 220)
    if size >= 32:
        draw_star(d, cx + heart_size + 2, cy - heart_size, max(2, size // 14), star_color)
        draw_star(d, cx - heart_size - 2, cy - heart_size + 2, max(2, size // 18), star_color)
        draw_star(d, cx + heart_size // 2, cy + heart_size + 2, max(2, size // 20), (255, 180, 220, 200))

    return img


out_path = os.path.join(os.path.dirname(__file__), "logo.ico")

# 가장 큰 사이즈로 그린 뒤, ICO 저장 시 다중 크기 자동 생성
base = make_icon(256)
base.save(
    out_path,
    format="ICO",
    sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)],
)
print(f"OK: {out_path}")
