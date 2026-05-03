# WebPM Converter

이미지를 WebP로, 영상을 WebM으로 변환하는 내부 툴.

---

## 필수 설치

```bash
brew install python-tk@3.14
brew install ffmpeg
```

---

## 최초 설정 (1회)

```bash
cd /Users/cjstmdduq/Desktop/app/WebPM_Converter

python3.14 -m venv venv
source venv/bin/activate
pip install Pillow customtkinter pyinstaller
```

---

## 개발 중 실행 (빠른 테스트)

```bash
cd /Users/cjstmdduq/Desktop/app/WebPM_Converter
source venv/bin/activate
python app.py
```

---

## 앱 빌드

코드 수정 후 `.app` 파일로 패키징:

```bash
./build.sh
```

빌드 결과물: `dist/WebPM Converter.app`

---

## 앱 설치 (Applications 등록)

```bash
cp -R "dist/WebPM Converter.app" /Applications/
```

이후 런치패드에서 바로 실행 가능.

---

## 사용법

1. 상단 옵션에서 저장 위치 및 품질 설정
2. 원하는 변환 방식 선택
   - **일괄 변환** — 폴더 안 이미지/영상 전체 변환
   - **이미지 변환** — 단일 이미지 파일 WebP 변환
   - **영상 변환** — 단일 영상 파일 WebM 변환
3. 변환 버튼 클릭 → 완료 시 폴더 열기 옵션 제공

---

## 지원 포맷

| 방향 | 입력 | 출력 |
|------|------|------|
| 이미지 | JPG, PNG, GIF, BMP, TIFF | WebP |
| 영상 | MP4, MOV, AVI, MKV, FLV, WMV | WebM |

---

## 파일 구조

```
WebPM_Converter/
  app.py          진입점
  converter.py    변환 로직 (Pillow, ffmpeg)
  ui.py           GUI (CustomTkinter)
  build.sh        앱 빌드 스크립트
  icon.png        앱 아이콘 원본
  icon.icns       macOS 아이콘 (빌드용)
  dist/           빌드 결과물 (.app)
  venv/           가상환경 (git 제외)
```
