# WebPM Converter — 구현 기획

## 개요

혼자 쓰는 내부 툴. 이미지 → WebP, 영상 → WebM 변환을 Tkinter GUI로 제공한다.

---

## 기술 스택

| 역할 | 선택 | 이유 |
|------|------|------|
| GUI | Tkinter | 별도 설치 없이 Python 기본 포함 |
| 이미지 변환 | Pillow (`pip install Pillow`) | WebP 인코딩 지원 |
| 영상 변환 | ffmpeg (시스템) + subprocess | WebM(VP9/Opus) 인코딩 |
| 언어 | Python 3.x | 메모 권장 스택 그대로 |

---

## 파일 구조

```
WebPM_Converter/
  app.py          # 진입점. App 인스턴스 생성 및 mainloop 실행
  converter.py    # 변환 로직 (Pillow, ffmpeg subprocess)
  ui.py           # Tkinter 윈도우, 레이아웃, 이벤트 바인딩
  PLAN.md         # 이 파일
  webp-webm-app-note.md
```

---

## 화면 레이아웃

```
┌──────────────────────────────────────┐
│       WebPM Converter                │  ← 타이틀
├──────────────────────────────────────┤
│  [이미지 선택]  selected_file.png    │  ← 이미지 파일 선택 행
│  [영상 선택]   selected_file.mp4    │  ← 영상 파일 선택 행
├──────────────────────────────────────┤
│  저장 위치: /Users/.../output  [변경]│  ← 출력 폴더 선택
├──────────────────────────────────────┤
│  [ Convert to WebP ]                 │
│  [ Convert to WebM ]                 │
├──────────────────────────────────────┤
│  로그 영역 (스크롤 가능)             │  ← 진행 상태 / 완료 메시지
└──────────────────────────────────────┘
```

---

## 모듈별 책임

### `converter.py`
- `convert_to_webp(src: str, dst_dir: str, quality: int = 80) -> str`
  - Pillow로 이미지 열고 `.webp` 저장
  - 반환값: 저장된 파일 경로
- `convert_to_webm(src: str, dst_dir: str) -> str`
  - `ffmpeg -i src -c:v libvpx-vp9 -c:a libopus output.webm` subprocess 실행
  - 반환값: 저장된 파일 경로
- ffmpeg 미설치 시 명확한 에러 메시지 반환

### `ui.py`
- `AppWindow(tk.Tk)` 클래스
  - `_build_layout()`: 위젯 배치
  - `_on_select_image()`: filedialog로 이미지 파일 선택
  - `_on_select_video()`: filedialog로 영상 파일 선택
  - `_on_select_output()`: askdirectory로 저장 폴더 선택
  - `_on_convert_webp()`: converter 호출 → 로그 출력
  - `_on_convert_webm()`: converter 호출 → 로그 출력 (별도 스레드로 실행, UI 블로킹 방지)
  - `_log(msg)`: 로그 영역에 타임스탬프 포함 메시지 추가

### `app.py`
- `AppWindow` 인스턴스 생성 후 `mainloop()` 실행

---

## 변환 흐름

```
파일 선택 → 저장 위치 확인 → Convert 버튼 클릭
  → 별도 스레드에서 converter 함수 실행
  → 성공/실패 결과를 로그 영역에 출력
```

영상 변환은 ffmpeg 실행 시간이 길 수 있으므로 `threading.Thread`로 분리해 UI가 멈추지 않게 한다.

---

## 의존성 설치

```bash
pip install Pillow
brew install ffmpeg   # macOS
```

---

## 구현 순서

1. `converter.py` 작성 및 단독 테스트
2. `ui.py` 작성 (레이아웃 + 이벤트)
3. `app.py` 작성 (진입점)
4. 실제 파일로 WebP / WebM 변환 동작 확인
