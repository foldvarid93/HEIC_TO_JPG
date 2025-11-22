import os
import sys
import threading
import queue
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()


def convert_to_jpg(input_file, output_file):
    try:
        img = Image.open(input_file)
        img = img.convert("RGB")
        img.save(output_file, "JPEG", quality=95)
    except Exception as e:
        raise


def _collect_heic_without_jpeg(input_directory, output_directory):
    """Return list of (input_path, output_path) for .heic files that have no JPEG pair in output_directory."""
    pairs = []
    for root, _, files in os.walk(input_directory):
        for file in files:
            file_ext = os.path.splitext(file)[1].lower()
            if file_ext == '.heic':
                input_file = os.path.join(root, file)
                output_file = os.path.join(output_directory, os.path.splitext(file)[0] + ".jpg")
                if not os.path.exists(output_file):
                    pairs.append((input_file, output_file))
    return pairs


def conversion_worker(input_dir, output_dir, msg_queue):
    try:
        os.makedirs(output_dir, exist_ok=True)
    except Exception as e:
        msg_queue.put(("error", f"Failed to create output directory: {e}"))
        return

    to_convert = _collect_heic_without_jpeg(input_dir, output_dir)
    total = len(to_convert)
    msg_queue.put(("info", f"Found {total} HEIC file(s) without JPEG in output folder."))

    for idx, (inp, outp) in enumerate(to_convert, start=1):
        try:
            msg_queue.put(("status", f"Converting ({idx}/{total}): {os.path.basename(inp)}"))
            convert_to_jpg(inp, outp)
            msg_queue.put(("info", f"Converted: {os.path.basename(outp)}"))
        except Exception as e:
            msg_queue.put(("error", f"Error converting {inp}: {e}"))

    msg_queue.put(("done", f"Conversion complete. {total} file(s) processed."))


def build_gui():
    root = tk.Tk()
    root.title("HEIC to JPEG Converter")
    root.resizable(False, False)
    # Determine application directory (exe folder when frozen, otherwise script directory)
    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))

    msg_queue = queue.Queue()
    worker_thread = None

    def browse_input():
        path = filedialog.askdirectory(initialdir=app_dir)
        if path:
            input_var.set(path)

    def browse_output():
        path = filedialog.askdirectory(initialdir=app_dir)
        if path:
            output_var.set(path)

    def start_conversion():
        nonlocal worker_thread
        inp = input_var.get().strip()
        out = output_var.get().strip()
        if not inp or not os.path.isdir(inp):
            messagebox.showerror("Invalid input folder", "Please select a valid input directory.")
            return
        if not out:
            # If empty, default to sibling folder_jpeg in script dir
            script_dir = os.path.dirname(os.path.abspath(__file__))
            out = os.path.join(script_dir, "folder_jpeg")
            output_var.set(out)

        # Disable buttons while running
        browse_in_btn.config(state=tk.DISABLED)
        browse_out_btn.config(state=tk.DISABLED)
        start_btn.config(state=tk.DISABLED)

        msg_queue.put(("info", "Starting conversion..."))
        worker_thread = threading.Thread(target=conversion_worker, args=(inp, out, msg_queue), daemon=True)
        worker_thread.start()

    def poll_queue():
        try:
            while True:
                typ, text = msg_queue.get_nowait()
                if typ == 'status' or typ == 'info' or typ == 'error':
                    status_var.set(text)
                    # append to log
                    log_box.config(state=tk.NORMAL)
                    log_box.insert(tk.END, text + "\n")
                    log_box.see(tk.END)
                    log_box.config(state=tk.DISABLED)
                if typ == 'done':
                    status_var.set(text)
                    browse_in_btn.config(state=tk.NORMAL)
                    browse_out_btn.config(state=tk.NORMAL)
                    start_btn.config(state=tk.NORMAL)
        except queue.Empty:
            pass
        root.after(200, poll_queue)

    frm = tk.Frame(root, padx=10, pady=10)
    frm.pack(fill=tk.BOTH, expand=True)

    input_var = tk.StringVar()
    output_var = tk.StringVar()
    status_var = tk.StringVar(value="Idle")

    tk.Label(frm, text="Input folder:").grid(row=0, column=0, sticky=tk.W)
    tk.Entry(frm, textvariable=input_var, width=60).grid(row=0, column=1, padx=5)
    browse_in_btn = tk.Button(frm, text="Browse...", command=browse_input)
    browse_in_btn.grid(row=0, column=2)

    tk.Label(frm, text="Output folder:").grid(row=1, column=0, sticky=tk.W)
    tk.Entry(frm, textvariable=output_var, width=60).grid(row=1, column=1, padx=5)
    browse_out_btn = tk.Button(frm, text="Browse...", command=browse_output)
    browse_out_btn.grid(row=1, column=2)

    start_btn = tk.Button(frm, text="Start Conversion", command=start_conversion, width=20)
    start_btn.grid(row=2, column=0, columnspan=3, pady=(10, 0))

    tk.Label(frm, text="Status:").grid(row=3, column=0, sticky=tk.W, pady=(10, 0))
    tk.Label(frm, textvariable=status_var, anchor='w').grid(row=3, column=1, columnspan=2, sticky=tk.W, pady=(10, 0))

    tk.Label(frm, text="Log:").grid(row=4, column=0, sticky=tk.NW, pady=(6, 0))
    log_box = tk.Text(frm, width=80, height=12, state=tk.DISABLED)
    log_box.grid(row=4, column=1, columnspan=2, pady=(6, 0))

    # Pre-fill defaults using previously-determined app_dir (exe folder when frozen, else script dir)
    default_in = os.path.join(app_dir, "folder_heic")
    default_out = os.path.join(app_dir, "folder_jpeg")
    input_var.set(default_in)
    output_var.set(default_out)

    root.after(200, poll_queue)
    root.mainloop()


if __name__ == "__main__":
    build_gui()
