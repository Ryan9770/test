import os
from PIL import Image, ImageDraw
import wave
import struct
import math

def create_dirs():
    os.makedirs('output/assets/images', exist_ok=True)
    os.makedirs('output/assets/sfx', exist_ok=True)

def create_image(filename, size, color, text=""):
    img = Image.new('RGBA', size, color)
    if text:
        draw = ImageDraw.Draw(img)
        # 텍스트 크기 계산을 대략적으로 수행하여 중앙에 배치
        text_w = len(text) * 6
        text_h = 10
        x = (size[0] - text_w) / 2
        y = (size[1] - text_h) / 2
        draw.text((x, y), text, fill=(255, 255, 255))
    img.save(f'output/assets/images/{filename}')

def create_sound(filename, freq, duration=0.1):
    sample_rate = 44100.0
    with wave.open(f'output/assets/sfx/{filename}', 'w') as obj:
        obj.setnchannels(1)
        obj.setsampwidth(2)
        obj.setframerate(sample_rate)
        
        for i in range(int(duration * sample_rate)):
            value = int(32767.0 * math.sin(2.0 * math.PI * freq * (i / sample_rate)))
            obj.writeframes(struct.pack('h', value))

if __name__ == '__main__':
    create_dirs()
    
    # 이미지 생성
    create_image('paddle.png', (64, 16), (59, 130, 246))   # 파란색 패들
    create_image('ball.png', (16, 16), (255, 255, 255))    # 하얀색 공
    create_image('brick.png', (16, 16), (239, 68, 68))     # 빨간색 벽돌
    create_image('item.png', (16, 16), (34, 197, 94), "I") # 초록색 아이템
    create_image('bg.png', (32, 32), (30, 30, 30))         # 어두운 배경 패턴
    
    # 효과음 생성 (간단한 비프음)
    create_sound('hit.mp3', 440)     # mp3 확장자지만 wave 파일로 저장 (html5 오디오 태그는 대체로 둘다 재생 가능)
    create_sound('bounce.mp3', 220)
    create_sound('item.mp3', 880, 0.3)
    
    print("에셋 생성 완료!")
