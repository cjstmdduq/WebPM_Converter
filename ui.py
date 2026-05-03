import subprocess
import threading
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

import converter

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

VERSION = "v1.0.0"

C_BG          = "#F2F2F7"
C_CARD        = "#FFFFFF"
C_BORDER      = "#E5E5EA"
C_TEXT        = "#1C1C1E"
C_SUB         = "#8E8E93"
C_BLUE        = "#3B82F6"
C_BLUE_HOVER  = "#2563EB"
C_GREEN       = "#22C55E"
C_GREEN_HOVER = "#16A34A"
C_RED         = "#EF4444"


class AppWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("WebPM Converter")
        self.geometry("660x680")
        self.resizable(True, True)
        self.minsize(520, 600)
        self.configure(fg_color=C_BG)

        self._image_path = ctk.StringVar(value="")
        self._video_path = ctk.StringVar(value="")
        self._batch_dir = ctk.StringVar(value="")
        self._output_dir = ctk.StringVar(value=str(Path.home() / "Downloads"))
        self._use_source_dir = ctk.BooleanVar(value=False)
        self._delete_original = ctk.BooleanVar(value=False)
        self._quality = ctk.StringVar(value="보통")
        self._last_dst_dir = None

        self._build_layout()

    # ── 전체 레이아웃 ─────────────────────────────────────────
    def _build_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)  # spacer — pushes status bar to bottom

        self._build_header()
        self._build_output_section()
        self._build_batch_section()
        self._build_image_section()
        self._build_video_section()
        self._build_statusbar()

    # ── 헤더 ─────────────────────────────────────────────────
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=C_CARD, corner_radius=0, border_width=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(header, fg_color="transparent")
        inner.pack(fill="x", padx=24, pady=14)

        ctk.CTkLabel(inner, text="WebPM Converter",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=C_TEXT).pack(side="left")
        ctk.CTkLabel(inner, text=VERSION,
                     font=ctk.CTkFont(size=12),
                     text_color=C_SUB).pack(side="left", padx=(8, 0))

        ctk.CTkFrame(header, height=1, fg_color=C_BORDER).pack(fill="x")

    # ── 저장 위치 + 옵션 ──────────────────────────────────────
    def _build_output_section(self):
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.grid(row=1, column=0, sticky="ew", padx=24, pady=(16, 0))
        wrap.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(wrap, fg_color=C_CARD, corner_radius=10,
                            border_width=1, border_color=C_BORDER)
        card.grid(row=0, column=0, sticky="ew")
        card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(card, text="저장 위치", width=64, anchor="w",
                     font=ctk.CTkFont(size=13), text_color=C_TEXT).grid(
            row=0, column=0, padx=(18, 8), pady=(14, 10), sticky="w"
        )
        self._output_entry = ctk.CTkEntry(
            card, textvariable=self._output_dir,
            font=ctk.CTkFont(size=12), fg_color="#F9F9F9",
            border_color=C_BORDER, text_color=C_TEXT, state="disabled"
        )
        self._output_entry.grid(row=0, column=1, pady=(14, 10), sticky="ew")
        self._btn_output_change = ctk.CTkButton(
            card, text="변경", width=58, height=30,
            font=ctk.CTkFont(size=12),
            fg_color="transparent", hover_color=C_BG,
            border_width=1, border_color=C_BORDER, text_color=C_SUB,
            command=self._on_select_output
        )
        self._btn_output_change.grid(row=0, column=2, padx=(10, 16), pady=(14, 10))

        ctk.CTkFrame(card, height=1, fg_color=C_BORDER).grid(
            row=1, column=0, columnspan=3, sticky="ew"
        )

        opt_row = ctk.CTkFrame(card, fg_color="transparent")
        opt_row.grid(row=2, column=0, columnspan=3, sticky="w", padx=14, pady=10)

        _checkbox(opt_row, text="원본 파일 위치에 저장",
                  variable=self._use_source_dir,
                  command=self._on_toggle_source_dir
                  ).pack(side="left", padx=(0, 24))
        _checkbox(opt_row, text="변환 후 원본 파일 삭제",
                  variable=self._delete_original
                  ).pack(side="left")

        ctk.CTkFrame(card, height=1, fg_color=C_BORDER).grid(
            row=3, column=0, columnspan=3, sticky="ew"
        )
        q_row = ctk.CTkFrame(card, fg_color="transparent")
        q_row.grid(row=4, column=0, columnspan=3, sticky="w", padx=14, pady=10)

        ctk.CTkLabel(q_row, text="품질", font=ctk.CTkFont(size=12),
                     text_color=C_SUB).pack(side="left", padx=(0, 16))
        for step in QUALITY_STEPS:
            ctk.CTkRadioButton(
                q_row, text=step, value=step, variable=self._quality,
                font=ctk.CTkFont(size=12), text_color=C_TEXT,
                radiobutton_width=16, radiobutton_height=16,
                border_width_unchecked=1, border_width_checked=4,
                fg_color=C_BLUE, border_color=C_BORDER,
                hover_color="#DDEEFF",
            ).pack(side="left", padx=(0, 18))

    # ── 일괄 변환 섹션 ───────────────────────────────────────
    def _build_batch_section(self):
        card = ctk.CTkFrame(self, fg_color=C_CARD, corner_radius=10,
                            border_width=1, border_color=C_BORDER)
        card.grid(row=2, column=0, sticky="ew", padx=24, pady=(12, 0))
        card.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(card, text="일괄 변환", width=90,
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=C_TEXT, anchor="w").grid(
            row=0, column=0, padx=(18, 0), pady=(14, 2), sticky="w"
        )
        ctk.CTkLabel(card, text="폴더 안의 이미지·영상을 모두 변환",
                     font=ctk.CTkFont(size=11), text_color=C_SUB, anchor="w").grid(
            row=0, column=1, columnspan=3, padx=10, pady=(14, 2), sticky="w"
        )
        ctk.CTkFrame(card, height=1, fg_color=C_BORDER).grid(
            row=1, column=0, columnspan=5, sticky="ew"
        )
        ctk.CTkLabel(card, text="폴더", width=36, anchor="w",
                     font=ctk.CTkFont(size=12), text_color=C_SUB).grid(
            row=2, column=0, padx=(18, 6), pady=12, sticky="w"
        )
        self._batch_entry = ctk.CTkEntry(
            card, textvariable=self._batch_dir,
            font=ctk.CTkFont(size=12), fg_color="#F9F9F9",
            border_color=C_BORDER, text_color=C_TEXT,
            placeholder_text="변환할 파일이 있는 폴더를 선택하세요", state="disabled"
        )
        self._batch_entry.grid(row=2, column=1, columnspan=2, pady=12, sticky="ew")
        self._btn_batch_select = _select_btn(card, command=self._on_select_batch_dir)
        self._btn_batch_select.grid(row=2, column=3, padx=(8, 8), pady=12)
        self._btn_batch_run = _convert_btn(card, text="변환", command=self._on_batch_convert)
        self._btn_batch_run.grid(row=2, column=4, padx=(0, 16), pady=12)

    # ── 이미지 변환 섹션 ──────────────────────────────────────
    def _build_image_section(self):
        card = ctk.CTkFrame(self, fg_color=C_CARD, corner_radius=10,
                            border_width=1, border_color=C_BORDER)
        card.grid(row=3, column=0, sticky="ew", padx=24, pady=(12, 0))
        card.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(card, text="이미지 변환", width=90,
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=C_TEXT, anchor="w").grid(
            row=0, column=0, padx=(18, 0), pady=(14, 2), sticky="w"
        )
        ctk.CTkLabel(card, text="JPG, PNG, GIF 등 → WebP",
                     font=ctk.CTkFont(size=11), text_color=C_SUB, anchor="w").grid(
            row=0, column=1, columnspan=3, padx=10, pady=(14, 2), sticky="w"
        )
        ctk.CTkFrame(card, height=1, fg_color=C_BORDER).grid(
            row=1, column=0, columnspan=5, sticky="ew"
        )
        ctk.CTkLabel(card, text="파일", width=36, anchor="w",
                     font=ctk.CTkFont(size=12), text_color=C_SUB).grid(
            row=2, column=0, padx=(18, 6), pady=12, sticky="w"
        )
        self._img_entry = ctk.CTkEntry(
            card, textvariable=self._image_path,
            font=ctk.CTkFont(size=12), fg_color="#F9F9F9",
            border_color=C_BORDER, text_color=C_TEXT,
            placeholder_text="파일을 선택하세요", state="disabled"
        )
        self._img_entry.grid(row=2, column=1, columnspan=2, pady=12, sticky="ew")
        self._btn_img_select = _select_btn(card, command=self._on_select_image)
        self._btn_img_select.grid(row=2, column=3, padx=(8, 8), pady=12)
        self._btn_convert_webp = _convert_btn(card, command=self._on_convert_webp)
        self._btn_convert_webp.grid(row=2, column=4, padx=(0, 16), pady=12)

    # ── 영상 변환 섹션 ────────────────────────────────────────
    def _build_video_section(self):
        card = ctk.CTkFrame(self, fg_color=C_CARD, corner_radius=10,
                            border_width=1, border_color=C_BORDER)
        card.grid(row=4, column=0, sticky="ew", padx=24, pady=(12, 0))
        card.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(card, text="영상 변환", width=90,
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=C_TEXT, anchor="w").grid(
            row=0, column=0, padx=(18, 0), pady=(14, 2), sticky="w"
        )
        ctk.CTkLabel(card, text="MP4, MOV, MKV 등 → WebM",
                     font=ctk.CTkFont(size=11), text_color=C_SUB, anchor="w").grid(
            row=0, column=1, columnspan=3, padx=10, pady=(14, 2), sticky="w"
        )
        ctk.CTkFrame(card, height=1, fg_color=C_BORDER).grid(
            row=1, column=0, columnspan=5, sticky="ew"
        )
        ctk.CTkLabel(card, text="파일", width=36, anchor="w",
                     font=ctk.CTkFont(size=12), text_color=C_SUB).grid(
            row=2, column=0, padx=(18, 6), pady=12, sticky="w"
        )
        self._vid_entry = ctk.CTkEntry(
            card, textvariable=self._video_path,
            font=ctk.CTkFont(size=12), fg_color="#F9F9F9",
            border_color=C_BORDER, text_color=C_TEXT,
            placeholder_text="파일을 선택하세요", state="disabled"
        )
        self._vid_entry.grid(row=2, column=1, columnspan=2, pady=12, sticky="ew")
        self._btn_vid_select = _select_btn(card, command=self._on_select_video)
        self._btn_vid_select.grid(row=2, column=3, padx=(8, 8), pady=12)
        self._btn_convert_webm = _convert_btn(card, command=self._on_convert_webm)
        self._btn_convert_webm.grid(row=2, column=4, padx=(0, 16), pady=12)

    # ── 하단 상태바 ───────────────────────────────────────────
    def _build_statusbar(self):
        bar = ctk.CTkFrame(self, fg_color=C_CARD, corner_radius=0)
        bar.grid(row=6, column=0, sticky="ew")
        bar.grid_columnconfigure(0, weight=1)

        ctk.CTkFrame(bar, height=1, fg_color=C_BORDER).grid(
            row=0, column=0, columnspan=2, sticky="ew"
        )
        self._status_label = ctk.CTkLabel(
            bar, text="",
            font=ctk.CTkFont(size=12),
            text_color=C_SUB, anchor="w"
        )
        self._status_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        self._btn_open_folder = ctk.CTkButton(
            bar, text="폴더 열기", width=80, height=26,
            font=ctk.CTkFont(size=12),
            fg_color="transparent", hover_color=C_BG,
            border_width=1, border_color=C_BORDER, text_color=C_BLUE,
            command=self._on_open_folder
        )
        self._btn_open_folder.grid(row=1, column=1, padx=(0, 16), pady=8)
        self._btn_open_folder.grid_remove()

    # ── 이벤트 ────────────────────────────────────────────────
    def _on_select_batch_dir(self):
        directory = filedialog.askdirectory(title="일괄 변환할 폴더 선택")
        if directory:
            self._batch_dir.set(directory)

    def _on_batch_convert(self):
        src_dir = self._batch_dir.get()
        if not src_dir:
            self._set_status("폴더를 먼저 선택해주세요.", C_RED)
            return
        dst_dir = src_dir if self._use_source_dir.get() else self._output_dir.get()
        self._set_busy(True)
        self._set_status("변환 준비 중...", C_SUB)

        def on_progress(current, total, filename):
            self.after(0, lambda: self._set_status(
                f"변환 중...  {filename}  ({current}/{total})", C_SUB
            ))

        def task():
            try:
                results = converter.batch_convert(
                    src_dir, dst_dir,
                    delete_original=self._delete_original.get(),
                    quality=_IMG_QUALITY[self._quality.get()],
                    crf=_VID_CRF[self._quality.get()],
                    on_progress=on_progress,
                )
                msg = f"완료  {results['success']}개 성공"
                if results["fail"]:
                    msg += f",  {results['fail']}개 실패"
                    self.after(0, lambda: self._set_status(msg, C_RED, dst_dir))
                else:
                    self.after(0, lambda: self._set_status(msg, C_GREEN, dst_dir))
            except Exception as e:
                self.after(0, lambda: self._set_status(f"오류: {e}", C_RED))
            finally:
                self.after(0, lambda: self._set_busy(False))

        threading.Thread(target=task, daemon=True).start()

    def _on_select_image(self):
        path = filedialog.askopenfilename(
            title="이미지 파일 선택",
            filetypes=[("이미지", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff"), ("전체", "*.*")],
        )
        if path:
            self._image_path.set(path)

    def _on_select_video(self):
        path = filedialog.askopenfilename(
            title="영상 파일 선택",
            filetypes=[("영상", "*.mp4 *.mov *.avi *.mkv *.flv *.wmv"), ("전체", "*.*")],
        )
        if path:
            self._video_path.set(path)

    def _on_select_output(self):
        directory = filedialog.askdirectory(title="저장 위치 선택")
        if directory:
            self._output_dir.set(directory)

    def _on_toggle_source_dir(self):
        use_source = self._use_source_dir.get()
        self._btn_output_change.configure(state="disabled" if use_source else "normal")
        self._output_entry.configure(fg_color=C_BORDER if use_source else "#F9F9F9")

    def _resolve_dst_dir(self, src: str) -> str:
        if self._use_source_dir.get():
            return str(Path(src).parent)
        return self._output_dir.get()

    def _on_convert_webp(self):
        src = self._image_path.get()
        if not src:
            self._set_status("이미지 파일을 먼저 선택해주세요.", C_RED)
            return
        dst_dir = self._resolve_dst_dir(src)
        quality = _IMG_QUALITY[self._quality.get()]
        self._set_busy(True)
        self._set_status("변환 중...", C_SUB)

        def task():
            try:
                out = converter.convert_to_webp(src, dst_dir, quality=quality)
                if self._delete_original.get():
                    Path(src).unlink()
                    self.after(0, lambda: self._image_path.set(""))
                self.after(0, lambda: self._set_status(
                    f"완료  {Path(out).name}", C_GREEN, dst_dir
                ))
            except Exception as e:
                self.after(0, lambda: self._set_status(f"오류: {e}", C_RED))
            finally:
                self.after(0, lambda: self._set_busy(False))

        threading.Thread(target=task, daemon=True).start()

    def _on_convert_webm(self):
        src = self._video_path.get()
        if not src:
            self._set_status("영상 파일을 먼저 선택해주세요.", C_RED)
            return
        dst_dir = self._resolve_dst_dir(src)
        crf = _VID_CRF[self._quality.get()]
        self._set_busy(True)
        self._set_status("변환 중...", C_SUB)

        def task():
            try:
                out = converter.convert_to_webm(src, dst_dir, crf=crf)
                if self._delete_original.get():
                    Path(src).unlink()
                    self.after(0, lambda: self._video_path.set(""))
                self.after(0, lambda: self._set_status(
                    f"완료  {Path(out).name}", C_GREEN, dst_dir
                ))
            except Exception as e:
                self.after(0, lambda: self._set_status(f"오류: {e}", C_RED))
            finally:
                self.after(0, lambda: self._set_busy(False))

        threading.Thread(target=task, daemon=True).start()

    def _on_open_folder(self):
        if self._last_dst_dir:
            subprocess.run(["open", self._last_dst_dir])

    # ── 유틸 ──────────────────────────────────────────────────
    def _set_status(self, text: str, color: str = C_SUB, dst_dir: str = None):
        self._status_label.configure(text=text, text_color=color)
        self._last_dst_dir = dst_dir
        if dst_dir:
            self._btn_open_folder.grid()
        else:
            self._btn_open_folder.grid_remove()

    def _set_busy(self, busy: bool):
        state = "disabled" if busy else "normal"
        self._btn_batch_run.configure(state=state)
        self._btn_batch_select.configure(state=state)
        self._btn_convert_webp.configure(state=state)
        self._btn_convert_webm.configure(state=state)
        self._btn_img_select.configure(state=state)
        self._btn_vid_select.configure(state=state)


QUALITY_STEPS = ["최하", "낮음", "보통", "높음", "최고"]
_IMG_QUALITY  = {"최하": 20, "낮음": 50, "보통": 80, "높음": 90, "최고": 100}
_VID_CRF      = {"최하": 55, "낮음": 43, "보통": 33, "높음": 22, "최고": 10}


def _select_btn(parent, command):
    return ctk.CTkButton(
        parent, text="선택", width=52, height=28,
        font=ctk.CTkFont(size=12),
        fg_color="transparent", hover_color=C_BG,
        border_width=1, border_color=C_BORDER, text_color=C_SUB,
        command=command,
    )


def _convert_btn(parent, command, text="변환"):
    return ctk.CTkButton(
        parent, text=text, width=72, height=28,
        font=ctk.CTkFont(size=12, weight="bold"),
        fg_color=C_BLUE, hover_color=C_BLUE_HOVER, corner_radius=8,
        command=command,
    )


def _checkbox(parent, text: str, variable, command=None):
    kwargs = dict(
        text=text,
        variable=variable,
        font=ctk.CTkFont(size=12),
        text_color=C_SUB,
        checkbox_width=16,
        checkbox_height=16,
        border_width=1,
        border_color=C_BORDER,
        fg_color=C_BLUE,
        hover_color="#DDEEFF",
        checkmark_color="white",
        corner_radius=4,
    )
    if command:
        kwargs["command"] = command
    return ctk.CTkCheckBox(parent, **kwargs)
