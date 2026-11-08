import ctypes
import os
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import font as tkfont
from tkinter import messagebox, ttk

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from converter.convert import CONVERSIONS, convert_file  # noqa: E402

BG = "#FAFAF9"
TEXT = "#1C1917"
MUTED = "#78716C"
BORDER = "#D6D3D1"
TRACK = "#E7E5E4"
HOVER = "#44403C"
SUCCESS = "#15803D"
ERROR = "#B91C1C"


def enable_sharp_text():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass


def pick_font(root, candidates):
    installed = set(tkfont.families(root))
    for name in candidates:
        if name in installed:
            return name
    return "TkDefaultFont"


def shorten(name, limit=30):
    if len(name) <= limit:
        return name
    keep = (limit - 1) // 2
    return name[:keep] + "…" + name[-keep:]


def apply_style(root):
    body = pick_font(root, ["Segoe UI Variable Text", "Segoe UI"])
    display = pick_font(root, ["Segoe UI Variable Display", "Segoe UI"])

    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("TFrame", background=BG)
    style.configure("TLabel", background=BG, foreground=TEXT, font=(body, 10))
    style.configure("Caption.TLabel", foreground=MUTED, font=(body, 8, "bold"))
    style.configure("Title.TLabel", font=(display, 16, "bold"))
    style.configure("Badge.TLabel", font=(display, 12, "bold"))
    style.configure("Arrow.TLabel", foreground=MUTED, font=(body, 12))
    style.configure("Status.TLabel", foreground=MUTED, font=(body, 9))

    style.configure(
        "TCombobox",
        fieldbackground="white", background="white", foreground=TEXT,
        bordercolor=BORDER, lightcolor="white", darkcolor="white",
        arrowcolor=TEXT, padding=8, font=(body, 10),
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", "white"), ("disabled", BG)],
        foreground=[("disabled", MUTED)],
        bordercolor=[("focus", TEXT)],
    )
    root.option_add("*TCombobox*Listbox.font", (body, 10))
    root.option_add("*TCombobox*Listbox.selectBackground", TEXT)
    root.option_add("*TCombobox*Listbox.selectForeground", "white")

    # Primary (dark) button
    style.configure(
        "Accent.TButton",
        background=TEXT, foreground="white", bordercolor=TEXT,
        lightcolor=TEXT, darkcolor=TEXT, borderwidth=0,
        focusthickness=0, padding=(0, 11), font=(body, 10, "bold"),
    )
    style.map(
        "Accent.TButton",
        background=[("disabled", BORDER), ("active", HOVER)],
        bordercolor=[("disabled", BORDER), ("active", HOVER)],
        lightcolor=[("disabled", BORDER), ("active", HOVER)],
        darkcolor=[("disabled", BORDER), ("active", HOVER)],
        foreground=[("disabled", "white")],
    )

    # Secondary (outlined) button
    style.configure(
        "Ghost.TButton",
        background=BG, foreground=TEXT, bordercolor=BORDER,
        lightcolor=BG, darkcolor=BG, focusthickness=0,
        padding=(0, 9), font=(body, 9),
    )
    style.map(
        "Ghost.TButton",
        background=[("active", TRACK)],
        bordercolor=[("active", MUTED)],
    )

    style.configure(
        "Thin.Horizontal.TProgressbar",
        troughcolor=TRACK, background=TEXT, bordercolor=TRACK,
        lightcolor=TEXT, darkcolor=TEXT, thickness=3,
    )


def main():
    enable_sharp_text()

    root = tk.Tk()
    root.title("Convert to...")
    root.configure(bg=BG)
    root.resizable(False, False)
    apply_style(root)

    if len(sys.argv) != 2:
        root.destroy()
        return 1

    input_path = Path(sys.argv[1])
    input_format = input_path.suffix.lower()

    if not input_path.is_file() or input_format not in CONVERSIONS:
        root.destroy()
        return 1

    # --- Layout -------------------------------------------------------
    frame = ttk.Frame(root, padding=(28, 26), width=420)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="CONVERT FILE", style="Caption.TLabel").pack(anchor="w")
    ttk.Label(frame, text=shorten(input_path.name), style="Title.TLabel").pack(
        anchor="w", pady=(4, 22)
    )

    # "MP4  →  [ MP3 v ]" reads as a sentence: from this, to that
    row = ttk.Frame(frame)
    row.pack(fill="x")
    row.columnconfigure(2, weight=1)

    ttk.Label(row, text=input_format[1:].upper(), style="Badge.TLabel").grid(
        row=0, column=0
    )
    ttk.Label(row, text="→", style="Arrow.TLabel").grid(row=0, column=1, padx=14)

    formats = [f.upper() for f in CONVERSIONS[input_format]["outputs"]]
    format_var = tk.StringVar(value=formats[0])
    format_box = ttk.Combobox(
        row, textvariable=format_var, values=formats, state="readonly"
    )
    format_box.grid(row=0, column=2, sticky="ew")

    convert_button = ttk.Button(frame, text="Convert", style="Accent.TButton")
    convert_button.pack(fill="x", pady=(22, 0))

    # Determinate while idle (zero = empty track); indeterminate while converting
    progress = ttk.Progressbar(
        frame, style="Thin.Horizontal.TProgressbar", mode="determinate"
    )
    progress.pack(fill="x", pady=(22, 0))

    status_label = ttk.Label(
        frame, text="Ready", style="Status.TLabel", wraplength=364, justify="left"
    )
    status_label.pack(anchor="w", pady=(10, 0))

    # Shown only after a successful conversion
    result_frame = ttk.Frame(frame)
    result_frame.columnconfigure((0, 1), weight=1)
    open_button = ttk.Button(result_frame, text="Open file", style="Ghost.TButton")
    folder_button = ttk.Button(
        result_frame, text="Show in folder", style="Ghost.TButton"
    )
    open_button.grid(row=0, column=0, sticky="ew", padx=(0, 6))
    folder_button.grid(row=0, column=1, sticky="ew", padx=(6, 0))

    # --- Behaviour ----------------------------------------------------
    def set_status(text, colour=MUTED):
        status_label.configure(text=text, foreground=colour)

    def set_busy(busy):
        if busy:
            convert_button.state(["disabled"])
            format_box.configure(state="disabled")
            progress.configure(mode="indeterminate")
            progress.start(12)
        else:
            progress.stop()
            progress.configure(mode="determinate", value=0)
            convert_button.state(["!disabled"])
            format_box.configure(state="readonly")

    def on_success(output_path):
        set_busy(False)
        set_status(f"Done. Saved as {output_path.name}", SUCCESS)
        convert_button.configure(text="Convert again")
        open_button.configure(command=lambda: os.startfile(output_path))
        folder_button.configure(
            command=lambda: subprocess.Popen(["explorer", f"/select,{output_path}"])
        )
        result_frame.pack(fill="x", pady=(14, 0))

    def on_failure(message):
        set_busy(False)
        set_status(f"Failed: {message}", ERROR)
        convert_button.configure(text="Try again")

    def worker(target):
        """Background thread. Never touch widgets directly from here."""
        try:
            output = convert_file(
                input_path,
                target,
                on_status=lambda msg: root.after(0, set_status, msg),
            )
        except (FileNotFoundError, ValueError, RuntimeError) as err:
            root.after(0, on_failure, str(err))
        except Exception as err:
            root.after(0, on_failure, f"Unexpected error: {err}")
        else:
            root.after(0, on_success, output)

    def start_conversion():
        result_frame.pack_forget()

        target = format_var.get().lower()

        # Same rule the engine uses: same folder, same name, new extension
        output_path = input_path.with_suffix(f".{target}")

        if output_path.exists():
            replace = messagebox.askyesno(
                "File already exists",
                f"{output_path.name} already exists.\n\nReplace it?",
                default="no",
                icon="warning",
                parent=root,
            )
            if not replace:
                set_status("Cancelled. Nothing was changed.")
                return

        set_busy(True)
        set_status("Getting ready...")
        threading.Thread(target=worker, args=(target,), daemon=True).start()

    convert_button.configure(command=start_conversion)

    # Centre the window using its natural size
    root.update_idletasks()
    x = (root.winfo_screenwidth() - root.winfo_reqwidth()) // 2
    y = (root.winfo_screenheight() - root.winfo_reqheight()) // 3
    root.geometry(f"+{x}+{y}")

    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())