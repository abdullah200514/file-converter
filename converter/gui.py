
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

from converter.convert import CONVERSIONS, convert_file


# Check that an input file was supplied
if len(sys.argv) != 2:
    raise SystemExit("Usage: python -m converter.gui <input_file>")

input_path = Path(sys.argv[1])

if not input_path.is_file():
    raise SystemExit(f"File not found: {input_path}")

# Detect input format
input_format = input_path.suffix.lower()

if input_format not in CONVERSIONS:
    raise SystemExit(f"Unsupported input format: {input_format}")

# Retrieve available output formats
available_formats = CONVERSIONS[input_format]["outputs"]


# Create the main window
root = tk.Tk()
root.title("File Converter")
root.geometry("420x280")
root.resizable(False, False)


# Main container
frame = ttk.Frame(root, padding=20)
frame.pack(fill="both", expand=True)


# Window heading
title = ttk.Label(
    frame,
    text="Convert your file",
    font=("Segoe UI", 16, "bold")
)
title.pack(anchor="w")


# Display selected filename
file_label = ttk.Label(
    frame,
    text=f"Selected file: {input_path.name}"
)
file_label.pack(anchor="w", pady=(15, 20))


# Output format label
format_label = ttk.Label(
    frame,
    text="Choose output format:"
)
format_label.pack(anchor="w")


# Dropdown
format_var = tk.StringVar(value=available_formats[0])

format_dropdown = ttk.Combobox(
    frame,
    textvariable=format_var,
    values=available_formats,
    state="readonly"
)
format_dropdown.pack(fill="x", pady=(8, 0))


# Handle the Convert button
def on_convert():

    selected_format = format_var.get()

    try:
        output_path = convert_file(input_path, selected_format)

    except (FileNotFoundError, ValueError, RuntimeError) as error:
        messagebox.showerror(
            "Conversion failed",
            str(error),
            parent=root
        )
        return

    messagebox.showinfo(
        "Conversion complete",
        f"Your file was saved to:\n{output_path}",
        parent=root
    )


# Convert button
convert_button = ttk.Button(
    frame,
    text="Convert",
    command=on_convert
)
convert_button.pack(fill="x", pady=(20, 0))


# Start GUI event loop
root.mainloop()
