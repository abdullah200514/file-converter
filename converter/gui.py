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


class ThinProgress(tk.Canvas):
    """A slim track with a sliding segment while work is running.

    Drawn by hand because the clam ttk progress bar rendered far thicker
    than the thickness it was given.
    """

    STEP_MS = 16

    def __init__(self, parent, thickness):
        # width=1: let pack(fill="x") decide, or the Canvas default widens the window
        super().__init__(
            parent, width=1, height=thickness, bg=TRACK,
            highlightthickness=0, borderwidth=0,
        )
        self._segment = self.create_rectangle(0, 0, 0, 0, fill=TEXT, width=0)
        self._job = None
        self._position = 0

    def start(self):
        self.stop()
        self._tick()

    def stop(self):
        if self._job is not None:
            self.after_cancel(self._job)
            self._job = None
        self._position = 0
        self.coords(self._segment, 0, 0, 0, 0)

    def _tick(self):
        width = self.winfo_width()
        segment = width // 4
        self._position += max(1, width // 90)
        if self._position > width + segment:
            self._position = 0
        self.coords(
            self._segment,
            self._position - segment, 0, self._position, self.winfo_height(),
        )
        self._job = self.after(self.STEP_MS, self._tick)


def set_window_icon(root):
    """Draw a small arrow icon in code, so no image file has to be packaged."""
    size = 32
    icon = tk.PhotoImage(master=root, width=size, height=size)
    icon.put(TEXT, to=(0, 0, size, size))
    icon.put("white", to=(7, 14, 20, 18))
    for step in range(9):
        icon.put("white", to=(17 + step, 7 + step, 18 + step, 25 - step))
    root.iconphoto(True, icon)


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
        # Stop the chosen format being highlighted in blue
        selectbackground=[("readonly", "white")],
        selectforeground=[("readonly", TEXT)],
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


def main():
    enable_sharp_text()

    root = tk.Tk()
    root.withdraw()  # Stay hidden until the layout is ready
    root.title("File Converter")
    root.configure(bg=BG)
    root.resizable(False, False)
    set_window_icon(root)
    apply_style(root)

    if len(sys.argv) != 2:
        messagebox.showinfo(
            "File Converter",
            "To convert a file, right-click it in File Explorer and choose "
            "Convert to...\n\nOn Windows 11 it is under Show more options.",
        )
        root.destroy()
        return 1

    input_path = Path(sys.argv[1])
    input_format = input_path.suffix.lower()

    if not input_path.is_file():
        messagebox.showerror("File Converter", f"File not found:\n{input_path}")
        root.destroy()
        return 1

    if input_format not in CONVERSIONS:
        messagebox.showerror(
            "File Converter", f"{input_path.name} is not a supported file type."
        )
        root.destroy()
        return 1

    # Pixel sizes below were chosen at 100% display scaling
    scale = root.winfo_fpixels("1i") / 96
    content_width = round(364 * scale)

    # --- Layout -------------------------------------------------------
    frame = ttk.Frame(root, padding=(28, 26))
    frame.pack(fill="both", expand=True)

    # Keeps the window the same width whatever the filename
    ttk.Frame(frame, width=content_width, height=0).pack()

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

    progress = ThinProgress(frame, thickness=max(3, round(3 * scale)))
    progress.pack(fill="x", pady=(22, 0))

    status_label = ttk.Label(
        frame, style="Status.TLabel", wraplength=content_width, justify="left"
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

    def is_busy():
        return convert_button.instate(["disabled"])

    def selected_output():
        # Same rule the engine uses: same folder, same name, new extension
        return input_path.with_suffix(f".{format_var.get().lower()}")

    def show_ready(_event=None):
        """Reset to the idle state, including after picking another format."""
        format_box.selection_clear()
        result_frame.pack_forget()
        convert_button.configure(text="Convert")
        set_status(f"Will save as {shorten(selected_output().name, 44)}")

    def set_busy(busy):
        if busy:
            convert_button.state(["disabled"])
            format_box.configure(state="disabled")
            progress.start()
        else:
            progress.stop()
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
        output_path = selected_output()

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

    def on_return(_event):
        if not is_busy():
            start_conversion()

    def on_escape(_event):
        if not is_busy():
            root.destroy()

    convert_button.configure(command=start_conversion)
    format_box.bind("<<ComboboxSelected>>", show_ready)
    root.bind("<Return>", on_return)
    root.bind("<Escape>", on_escape)
    show_ready()

    # Centre the window using its natural size
    root.update_idletasks()
    x = (root.winfo_screenwidth() - root.winfo_reqwidth()) // 2
    y = (root.winfo_screenheight() - root.winfo_reqheight()) // 3
    root.geometry(f"+{x}+{y}")
    root.deiconify()

    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())