# WebP 변환기

PNG/JPG/BMP/TIFF 이미지를 WebP로 일괄 변환하는 Windows 9x 감성 파스텔 카와이 UI 데스크톱 툴입니다.

## 기능

- **파일 선택 / 폴더 선택(하위 폴더 포함)** 두 가지 방식으로 변환 대상을 고를 수 있습니다.
- 여러 변환 작업을 동시에 큐에 올릴 수 있고, 작업마다 진행률 바 + **일시정지/재개** 버튼이 붙습니다.
- **가로 해상도 리사이즈**: 720 / 1080 / 1440 / 1920 프리셋 버튼 또는 직접 입력(0이면 원본 유지, 비율은 항상 유지).
- **퀄리티 슬라이더**(10~100%)로 압축률 조절.
- 변환 완료 후 원본 파일을 자동 삭제하는 옵션.
- 각 작업은 별도 스레드에서 처리되어 여러 폴더를 동시에 돌려도 UI가 멈추지 않습니다.

## 스크린샷

*(추가 예정)*

## 실행 방법

```bash
pip install pillow
python convert_to_webp.py
```

## exe로 빌드하기

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=logo.ico convert_to_webp.py
```

`make_icon.py`는 배포용 `.ico` 아이콘을 생성하는 보조 스크립트입니다.

## 기술 스택

- Python 3 + Tkinter/ttk (GUI)
- [Pillow](https://python-pillow.org/) — 이미지 디코딩·리사이즈·WebP 인코딩
