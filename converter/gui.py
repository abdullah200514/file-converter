
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path


# Locate the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Ensure the project root is available for imports
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# Import conversion engine
from converter.convert import CONVERSIONS, convert_file


# Check command-line arguments
if len(sys.argv) != 2:
    raise SystemExit("Usage: python gui.py <input_file>")


# Get selected input file
input_path = Path(sys.argv[1])

if not input_path.is_file():
    raise SystemExit(f"File not found: {input_path}")


# Detect input format
input_format = input_path.suffix.lower()

if input_format not in CONVERSIONS:
    raise SystemExit(f"Unsupported input format: {input_format}")


# Retrieve supported output formats
available_formats = CONVERSIONS[input_format]["outputs"]


# Create the main window
root = tk.Tk()
root.title("File Converter")
root.geometry("420x300")
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


# Format dropdown
format_var = tk.StringVar(value=available_formats[0])

format_dropdown = ttk.Combobox(
    frame,
    textvariable=format_var,
    values=available_formats,
    state="readonly"
)
format_dropdown.pack(fill="x", pady=(8, 0))


# Conversion status
status_label = ttk.Label(
    frame,
    text="Ready"
)
status_label.pack(anchor="w", pady=(12, 0))


# Handle successful conversion
def show_success(output_path):

    convert_button.config(state="normal")
    format_dropdown.config(state="readonly")
    status_label.config(text="Conversion complete!")

    messagebox.showinfo(
        "Conversion complete",
        f"Your file was saved to:\n{output_path}",
        parent=root
    )


# Handle failed conversion
def show_error(error_message):

    convert_button.config(state="normal")
    format_dropdown.config(state="readonly")
    status_label.config(text="Conversion failed")

    messagebox.showerror(
        "Conversion failed",
        error_message,
        parent=root
    )


# Perform conversion in background
def perform_conversion(selected_format):

    try:
        output_path = convert_file(input_path, selected_format)

    except Exception as error:
        root.after(0, show_error, str(error))

    else:
        root.after(0, show_success, output_path)


# Handle Convert button click
def on_convert():

    selected_format = format_var.get()

    # Prevent duplicate conversions
    convert_button.config(state="disabled")
    format_dropdown.config(state="disabled")

    status_label.config(text="Converting...")

    # Start background conversion thread
    conversion_thread = threading.Thread(
        target=perform_conversion,
        args=(selected_format,),
        daemon=True
    )

    conversion_thread.start()


# Convert button
convert_button = ttk.Button(
    frame,
    text="Convert",
    command=on_convert
)
convert_button.pack(fill="x", pady=(20, 0))


# Start GUI event loop
root.mainloop()
