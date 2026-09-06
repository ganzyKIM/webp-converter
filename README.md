# WebP 변환기

PNG·JPG·BMP·TIFF를 WebP로 일괄 변환하는 데스크톱 툴. Windows 9x 풍 파스텔 UI.

## 기능

- 파일 단위 또는 폴더 단위(하위 폴더 포함) 선택
- 변환 작업을 여러 개 큐에 올릴 수 있고, 작업마다 진행률 바와 일시정지·재개 버튼이 붙는다
- 가로 해상도 리사이즈 — 720 / 1080 / 1440 / 1920 프리셋 또는 직접 입력. `0`이면 원본 유지, 비율은 항상 유지
- 퀄리티 슬라이더 10~100%
- 변환 후 원본 자동 삭제 옵션

작업마다 스레드를 따로 쓰기 때문에 여러 폴더를 동시에 돌려도 UI가 멈추지 않는다.

## 실행

```bash
pip install pillow
python convert_to_webp.py
```

## exe 빌드

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=logo.ico convert_to_webp.py
```

`make_icon.py`는 배포용 `.ico`를 만드는 보조 스크립트.

## 스택

Python 3 · Tkinter/ttk · [Pillow](https://python-pillow.org/)
