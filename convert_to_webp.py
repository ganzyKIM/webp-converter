import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageOps, ImageTk

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# =====================================================
#   KAWAII RETRO PALETTE  (Windows 9x + Pastel)
# =====================================================
C_DESKTOP    = "#DEC6F0"   # 바탕화면 배경 - 파스텔 라벤더
C_WIN_BG     = "#FFF0FA"   # 창 내부 - 연핑크
C_TITLEBAR   = "#9B72C8"   # 타이틀바 - 파스텔 보라
C_TITLEBAR_H = "#C4A0E8"   # 타이틀바 하이라이트
C_BTN        = "#EDD4F8"   # 버튼 기본
C_BTN_ACT    = "#D8B4EC"   # 버튼 눌림
C_BTN_DK     = "#B890D4"   # 버튼 어두운 테두리
C_TEXT       = "#2E1050"   # 메인 텍스트 - 진보라
C_TEXT_LT    = "#7B5AA0"   # 보조 텍스트
C_TEXT_WHITE = "#FFFFFF"
C_BORDER_LT  = "#F5E0FF"   # 3D 밝은 테두리
C_BORDER_DK  = "#8060A8"   # 3D 어두운 테두리
C_PBAR_BG    = "#EDD8FF"   # 프로그레스 트로프
C_PBAR_FG    = "#B07AE0"   # 프로그레스 채움
C_TASK_BG    = "#FBF0FF"   # 작업 항목 배경
C_HEADER_BG  = "#DEB8F8"   # 헤더 배경
C_SEP        = "#C8A4E4"   # 구분선
C_DONE       = "#7B40B0"   # 완료 색상
C_PAUSE      = "#E06088"   # 일시정지 색상
C_STATUSBAR  = "#8B60B8"   # 하단 상태바

# =====================================================
#   FONTS
# =====================================================
F_TITLE    = ("Courier New", 11, "bold")
F_HEADING  = ("Courier New", 9, "bold")
F_NORMAL   = ("Courier New", 9)
F_SMALL    = ("Courier New", 8)
F_LOGO     = ("Courier New", 13, "bold")
F_MONO     = ("Courier New", 8)

# =====================================================
#   HELPERS
# =====================================================
class TaskState:
    def __init__(self):
        self.is_paused = False
        self.pause_event = threading.Event()
        self.pause_event.set()

def retro_button(parent, text, command=None, width=None, height=None, font=None, **kw):
    """Windows 9x 느낌의 파스텔 버튼"""
    kwargs = dict(
        bg=C_BTN,
        fg=C_TEXT,
        activebackground=C_BTN_ACT,
        activeforeground=C_TEXT,
        relief=tk.RAISED,
        bd=3,
        font=font or F_NORMAL,
        cursor="hand2",
        highlightbackground=C_BORDER_DK,
        highlightthickness=1,
    )
    kwargs.update(kw)
    if width:  kwargs['width']  = width
    if height: kwargs['height'] = height
    if command: kwargs['command'] = command
    return tk.Button(parent, text=text, **kwargs)

def panel(parent, **kw):
    """레트로 패널 프레임"""
    kw.setdefault('bg', C_WIN_BG)
    kw.setdefault('relief', tk.RIDGE)
    kw.setdefault('bd', 2)
    return tk.Frame(parent, **kw)

# =====================================================
#   PROGRESS UPDATE
# =====================================================
def update_progress(pbar, label, current, total, error_count, is_done=False):
    percent = int((current / total) * 100) if total > 0 else 100
    pbar['value'] = percent
    if is_done:
        label.config(
            text=f"[DONE] OK:{total - error_count}  NG:{error_count}",
            fg=C_DONE
        )
    else:
        label.config(text=f"converting... ({current}/{total})", fg=C_TEXT_LT)

# =====================================================
#   BACKGROUND THREAD
# =====================================================
def process_files_thread(files_to_convert, pbar, label, delete_originals,
                         task_state, btn_pause, target_width, quality):
    total = len(files_to_convert)
    converted_count = 0
    error_count = 0
    successful_files = []

    for i, file_path in enumerate(files_to_convert):
        if task_state.is_paused:
            root.after(0, lambda idx=i: label.config(
                text=f"[PAUSE] ({idx}/{total})", fg=C_PAUSE))
        task_state.pause_event.wait()
        if not task_state.is_paused:
            root.after(0, lambda idx=i: label.config(
                text=f"converting... ({idx}/{total})", fg=C_TEXT_LT))

        output_path = os.path.splitext(file_path)[0] + ".webp"
        try:
            with Image.open(file_path) as img:
                img = ImageOps.exif_transpose(img)
                if img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGBA')
                # 가로 해상도 리사이즈 (비율 유지)
                if target_width > 0 and img.width > target_width:
                    ratio = target_width / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((target_width, new_height), Image.LANCZOS)
                img.save(output_path, 'webp', quality=quality)
            converted_count += 1
            successful_files.append(file_path)
        except Exception:
            error_count += 1

        root.after(0, update_progress, pbar, label, i + 1, total, error_count, False)

    root.after(0, update_progress, pbar, label, total, total, error_count, True)
    root.after(0, lambda: btn_pause.config(state=tk.DISABLED, text="[END]"))

    if delete_originals:
        for file_path in successful_files:
            try:
                os.remove(file_path)
            except Exception:
                pass

# =====================================================
#   TASK UI BUILDER
# =====================================================
def start_task(task_name, files_to_convert):
    if not files_to_convert:
        messagebox.showwarning("안내", "변환할 이미지를 찾지 못했습니다.")
        return

    # 작업 항목 카드
    card = tk.Frame(
        progress_frame,
        bg=C_TASK_BG,
        relief=tk.RIDGE,
        bd=2,
    )
    card.pack(fill=tk.X, pady=3, padx=3)

    # 카드 헤더
    card_header = tk.Frame(card, bg=C_HEADER_BG, relief=tk.FLAT)
    card_header.pack(fill=tk.X)

    tk.Label(
        card_header,
        text=f" >> {task_name}",
        bg=C_HEADER_BG, fg=C_TEXT,
        font=F_HEADING, anchor='w',
        pady=3,
    ).pack(side=tk.LEFT, padx=4, fill=tk.X, expand=True)

    task_state = TaskState()
    btn_pause = retro_button(card_header, "[STOP]", width=8, font=F_MONO)
    btn_pause.pack(side=tk.RIGHT, padx=4, pady=2)

    lbl_status = tk.Label(
        card_header,
        text=f"wait... (0/{len(files_to_convert)})",
        bg=C_HEADER_BG, fg=C_TEXT_LT,
        font=F_MONO, anchor='e',
    )
    lbl_status.pack(side=tk.RIGHT, padx=6)

    # 프로그레스 바
    bar_frame = tk.Frame(card, bg=C_TASK_BG, pady=4)
    bar_frame.pack(fill=tk.X, padx=6)

    pbar = ttk.Progressbar(
        bar_frame,
        style="Kawaii.Horizontal.TProgressbar",
        orient=tk.HORIZONTAL,
        mode='determinate',
    )
    pbar.pack(fill=tk.X, expand=True)

    def toggle_pause():
        if task_state.is_paused:
            task_state.is_paused = False
            task_state.pause_event.set()
            btn_pause.config(text="[STOP]")
        else:
            task_state.is_paused = True
            task_state.pause_event.clear()
            btn_pause.config(text="[RUN]")

    btn_pause.config(command=toggle_pause)

    delete_originals = delete_var.get()

    # 옵션 읽기: 가로 해상도, 퀄리티
    try:
        tw = int(width_var.get())
    except (ValueError, tk.TclError):
        tw = 0
    if tw <= 0:
        tw = 0  # 0 = 리사이즈 안 함

    try:
        q = int(quality_var.get())
    except (ValueError, tk.TclError):
        q = 90
    q = max(1, min(100, q))

    t = threading.Thread(
        target=process_files_thread,
        args=(files_to_convert, pbar, lbl_status, delete_originals,
              task_state, btn_pause, tw, q)
    )
    t.daemon = True
    t.start()

    # 새 항목 추가 시 스크롤 하단으로
    root.after(100, lambda: canvas.yview_moveto(1.0))

# =====================================================
#   FILE HELPERS
# =====================================================
def get_valid_files(file_list):
    valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')
    return [f for f in file_list if os.path.splitext(f)[1].lower() in valid_extensions]

def select_files():
    file_paths = filedialog.askopenfilenames(
        title="변환할 이미지들을 선택하세요 (Ctrl+A: 전체선택)",
        filetypes=[("이미지 파일", "*.png *.jpg *.jpeg *.bmp *.tiff"), ("모든 파일", "*.*")]
    )
    if file_paths:
        valid_files = get_valid_files(file_paths)
        first_name = os.path.basename(valid_files[0])
        if len(first_name) > 15:
            first_name = first_name[:12] + "..."
        task_name = f"[IMG] {first_name}" + (f" +{len(valid_files)-1}" if len(valid_files) > 1 else "")
        start_task(task_name, valid_files)

def select_folder():
    folder_path = filedialog.askdirectory(title="변환할 폴더를 선택하세요")
    if not folder_path:
        return
    include_subfolders = messagebox.askyesno("옵션", "하위 폴더의 이미지도 모두 포함하시겠습니까?")
    all_files = []
    if include_subfolders:
        for dirpath, _, filenames in os.walk(folder_path):
            for filename in filenames:
                all_files.append(os.path.join(dirpath, filename))
    else:
        for filename in os.listdir(folder_path):
            full_path = os.path.join(folder_path, filename)
            if os.path.isfile(full_path):
                all_files.append(full_path)

    valid_files = get_valid_files(all_files)
    folder_name = os.path.basename(folder_path)
    if len(folder_name) > 15:
        folder_name = folder_name[:12] + "..."
    task_name = f"[DIR] {folder_name}"
    start_task(task_name, valid_files)

# =====================================================
#   MAIN WINDOW
# =====================================================
root = tk.Tk()
root.title("WebP Converter")
root.geometry("660x600")
root.configure(bg=C_DESKTOP)
root.resizable(True, True)

try:
    _ico_path = resource_path('logo.ico')
    _ico_img = Image.open(_ico_path).resize((256, 256), Image.LANCZOS)
    _icon_photo = ImageTk.PhotoImage(_ico_img)
    root.iconphoto(True, _icon_photo)
    root._icon_photo = _icon_photo  # GC 방지
except Exception:
    try:
        root.iconbitmap(resource_path('logo.ico'))
    except Exception:
        pass

# ── TTK 스타일 ──
style = ttk.Style()
style.theme_use('default')
style.configure(
    "Kawaii.Horizontal.TProgressbar",
    troughcolor=C_PBAR_BG,
    background=C_PBAR_FG,
    bordercolor=C_BORDER_DK,
    lightcolor=C_TITLEBAR_H,
    darkcolor=C_TITLEBAR,
    thickness=14,
)

# =====================================================
#   OUTER WINDOW FRAME  (레트로 창 느낌)
# =====================================================
outer = tk.Frame(root, bg=C_DESKTOP, padx=5, pady=5)
outer.pack(fill=tk.BOTH, expand=True)

win = tk.Frame(outer, bg=C_WIN_BG, relief=tk.RAISED, bd=3)
win.pack(fill=tk.BOTH, expand=True)

# ── 타이틀 바 ──
titlebar = tk.Frame(win, bg=C_TITLEBAR, height=26, relief=tk.FLAT)
titlebar.pack(fill=tk.X)
titlebar.pack_propagate(False)

title_icon = tk.Label(
    titlebar, text=" \u2665",
    bg=C_TITLEBAR, fg=C_TEXT_WHITE,
    font=("Courier New", 10, "bold"),
)
title_icon.pack(side=tk.LEFT, padx=(4, 0))

title_lbl = tk.Label(
    titlebar,
    text="WebP \uBCC0\uD658\uAE30  v1.3",
    bg=C_TITLEBAR, fg=C_TEXT_WHITE,
    font=F_TITLE,
)
title_lbl.pack(side=tk.LEFT, padx=4)

# 가짜 창 제어 버튼
for sym, clr in [("\u25ac", "#F0C8D8"), ("\u25a1", "#C8D8F0"), ("\u2715", "#F0A0A0")]:
    lbl = tk.Label(
        titlebar, text=sym,
        bg=clr, fg=C_TEXT,
        font=("Courier New", 8, "bold"),
        width=3, relief=tk.RAISED, bd=2,
        cursor="hand2",
    )
    lbl.pack(side=tk.RIGHT, padx=2, pady=3)

# ── 메뉴바 느낌의 서브타이틀 ──
menubar = tk.Frame(win, bg=C_HEADER_BG, height=20, relief=tk.FLAT)
menubar.pack(fill=tk.X)
menubar.pack_propagate(False)

for txt in ["File", "Convert", "Options", "Help"]:
    tk.Label(
        menubar, text=f"  {txt}  ",
        bg=C_HEADER_BG, fg=C_TEXT,
        font=F_SMALL, cursor="hand2",
        relief=tk.FLAT,
    ).pack(side=tk.LEFT)

# ── 본문 영역 ──
body = tk.Frame(win, bg=C_WIN_BG)
body.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

# ── 로고 + 설명 ──
logo_frame = tk.Frame(body, bg=C_WIN_BG)
logo_frame.pack(fill=tk.X, pady=(0, 4))

tk.Label(
    logo_frame,
    text="\u2665  PNG / JPG  \u2192  WebP  \u2665",
    bg=C_WIN_BG, fg=C_TITLEBAR,
    font=F_LOGO,
).pack(side=tk.LEFT)

tk.Label(
    logo_frame,
    text="v1.3",
    bg=C_WIN_BG, fg=C_TEXT_LT,
    font=F_SMALL,
).pack(side=tk.RIGHT, padx=4)

# 구분선
tk.Frame(body, bg=C_SEP, height=2).pack(fill=tk.X, pady=4)

# ── 옵션 패널 ──
opt_frame = panel(body, bg=C_WIN_BG, relief=tk.GROOVE, bd=2)
opt_frame.pack(fill=tk.X, pady=(0, 6))

# 옵션 헤더
tk.Label(
    opt_frame, text=" >> Options",
    bg=C_HEADER_BG, fg=C_TEXT,
    font=F_HEADING, anchor='w', pady=2,
).pack(fill=tk.X)

opt_body = tk.Frame(opt_frame, bg=C_WIN_BG)
opt_body.pack(fill=tk.X, padx=8, pady=4)

# 1행: 가로 해상도 + 퀄리티
row1 = tk.Frame(opt_body, bg=C_WIN_BG)
row1.pack(fill=tk.X, pady=2)

tk.Label(row1, text="Width :", bg=C_WIN_BG, fg=C_TEXT,
         font=F_NORMAL).pack(side=tk.LEFT)

width_var = tk.StringVar(value="0")
width_entry = tk.Entry(row1, textvariable=width_var, width=6,
                       bg="#FDF5FF", fg=C_TEXT, relief=tk.SUNKEN, bd=2,
                       font=F_NORMAL, justify='center')
width_entry.pack(side=tk.LEFT, padx=(4, 0))

tk.Label(row1, text="px  (0=원본유지)", bg=C_WIN_BG, fg=C_TEXT_LT,
         font=F_SMALL).pack(side=tk.LEFT, padx=(2, 0))

# 프리셋 버튼
preset_frame = tk.Frame(row1, bg=C_WIN_BG)
preset_frame.pack(side=tk.LEFT, padx=(10, 0))

for pw in [720, 1080, 1440, 1920]:
    retro_button(
        preset_frame, str(pw),
        command=lambda v=pw: width_var.set(str(v)),
        font=("Courier New", 7), width=5,
        bd=2,
    ).pack(side=tk.LEFT, padx=1)

# 2행: 퀄리티 슬라이더
row2 = tk.Frame(opt_body, bg=C_WIN_BG)
row2.pack(fill=tk.X, pady=2)

tk.Label(row2, text="Quality:", bg=C_WIN_BG, fg=C_TEXT,
         font=F_NORMAL).pack(side=tk.LEFT)

quality_var = tk.IntVar(value=90)

quality_label = tk.Label(row2, text="90%", bg=C_WIN_BG, fg=C_TITLEBAR,
                         font=("Courier New", 10, "bold"), width=4)
quality_label.pack(side=tk.RIGHT, padx=(4, 0))

def _on_quality_change(val):
    v = int(float(val))
    quality_var.set(v)
    quality_label.config(text=f"{v}%")

quality_scale = tk.Scale(
    row2, from_=10, to=100, orient=tk.HORIZONTAL,
    variable=quality_var, command=_on_quality_change,
    bg=C_WIN_BG, fg=C_TEXT, activebackground=C_BTN_ACT,
    troughcolor=C_PBAR_BG, highlightthickness=0,
    font=("Courier New", 7), length=200,
    showvalue=False, bd=2, relief=tk.GROOVE,
    cursor="hand2",
)
quality_scale.pack(side=tk.LEFT, padx=(4, 0), fill=tk.X, expand=True)

# 3행: 원본 삭제 체크박스
row3 = tk.Frame(opt_body, bg=C_WIN_BG)
row3.pack(fill=tk.X, pady=(2, 0))

delete_var = tk.BooleanVar(value=False)
tk.Checkbutton(
    row3,
    text="\u25b8 변환 완료 후 원본 파일(PNG/JPG 등) 자동 삭제",
    variable=delete_var,
    bg=C_WIN_BG, fg=C_TEXT,
    activebackground=C_WIN_BG, activeforeground=C_TEXT,
    selectcolor=C_BTN,
    font=F_NORMAL,
    cursor="hand2",
).pack(anchor='w')

# ── 버튼 2개 ──
btn_row = tk.Frame(body, bg=C_WIN_BG)
btn_row.pack(fill=tk.X, pady=(0, 6))

btn_files = retro_button(
    btn_row,
    "\u2665  이미지 직접 선택\n    (파일 조회 가능)",
    command=select_files,
    width=24, height=3,
    font=F_HEADING,
)
btn_files.pack(side=tk.LEFT, padx=(0, 8))

btn_folder = retro_button(
    btn_row,
    "\u2666  폴더 통째로 선택\n    (하위 폴더 포함)",
    command=select_folder,
    width=24, height=3,
    font=F_HEADING,
)
btn_folder.pack(side=tk.LEFT)

# ── 진행 현황 헤더 ──
progress_header = tk.Frame(body, bg=C_HEADER_BG, relief=tk.RIDGE, bd=2)
progress_header.pack(fill=tk.X)

tk.Label(
    progress_header,
    text="\u25bc  변환 진행 현황  \u25bc",
    bg=C_HEADER_BG, fg=C_TEXT,
    font=F_HEADING, pady=3,
).pack()

# ── 스크롤 가능한 진행 목록 ──
scroll_outer = tk.Frame(body, bg=C_WIN_BG, relief=tk.SUNKEN, bd=2)
scroll_outer.pack(fill=tk.BOTH, expand=True)

canvas = tk.Canvas(scroll_outer, bg=C_DESKTOP, highlightthickness=0)
scrollbar = tk.Scrollbar(scroll_outer, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

progress_frame = tk.Frame(canvas, bg=C_DESKTOP)
canvas_win_id = canvas.create_window((0, 0), window=progress_frame, anchor='nw')

def _on_frame_config(e):
    canvas.configure(scrollregion=canvas.bbox("all"))

def _on_canvas_config(e):
    canvas.itemconfig(canvas_win_id, width=e.width)

progress_frame.bind("<Configure>", _on_frame_config)
canvas.bind("<Configure>", _on_canvas_config)

def _on_mousewheel(e):
    canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

canvas.bind_all("<MouseWheel>", _on_mousewheel)

# ── 하단 상태바 ──
statusbar = tk.Frame(win, bg=C_STATUSBAR, height=20, relief=tk.SUNKEN, bd=1)
statusbar.pack(fill=tk.X, side=tk.BOTTOM)
statusbar.pack_propagate(False)

tk.Label(
    statusbar,
    text="  Ready \u2665  |  WebP Converter v1.3  |  PNG \u00b7 JPG \u00b7 BMP \u00b7 TIFF",
    bg=C_STATUSBAR, fg=C_TEXT_WHITE,
    font=F_MONO, anchor='w',
).pack(side=tk.LEFT, fill=tk.Y)

root.mainloop()
