import os
import subprocess
import threading
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Combobox
from tkinter import filedialog, messagebox
import random
import re

# Define modern light blue color palette with lighter buttons
BG_COLOR = "#E6F0FA"  # Light blue-gray background
BUTTON_BG = "#A3BFFA"  # Lighter soft blue for buttons
BUTTON_ACTIVE = "#7F9CF5"  # Lighter blue for button hover/active
ENTRY_BG = "#F5F8FF"  # Very light blue for entries
TEXT_FG = "#2C3E50"  # Dark navy for text
FRAME_BORDER = "#D3E0F7"  # Slightly darker light blue for grid

# Global variables
current_processes = []
processes_lock = threading.Lock()
proxy_list = []
completed_threads = 0
threads_lock = threading.Lock()

def load_proxies():
    """Loads proxies from a file if provided."""
    global proxy_list
    proxy_file = proxy_entry.get().strip()
    if proxy_file and os.path.exists(proxy_file):
        with open(proxy_file, 'r') as f:
            proxy_list = [line.strip() for line in f if line.strip()]
        # Ensure proxy format (e.g., http://IP:PORT)
        proxy_list = [f"http://{proxy}" if not proxy.startswith(("http://", "socks5://")) else proxy for proxy in proxy_list]
        update_status(f"Loaded {len(proxy_list)} proxies.")
    else:
        proxy_list = []

def browse_proxy_file():
    """Opens a file explorer dialog to select a proxy file."""
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        proxy_entry.delete(0, END)
        proxy_entry.insert(0, file_path)

def show_proxy_help():
    """Displays a pop-up explaining the proxy file format."""
    message = (
        "Proxy File Format:\n\n"
        "The proxy file should be a plain text file (.txt) with one proxy per line.\n"
        "Supported formats:\n"
        "- http://IP:PORT (e.g., http://192.168.1.100:8080)\n"
        "- socks5://IP:PORT (e.g., socks5://proxy.example.com:1080)\n\n"
        "Example proxy file content:\n"
        "http://192.168.1.100:8080\n"
        "http://proxy2.example.com:3128\n"
        "socks5://proxy3.example.com:1080"
    )
    messagebox.showinfo("Proxy File Format Help", message)

def get_random_proxy():
    """Returns a random proxy or None if no proxies are loaded."""
    return random.choice(proxy_list) if proxy_list else None

def start_scan():
    """Starts the S3Scanner scan with optional multi-threading and proxy support."""
    global current_processes, completed_threads
    try:
        prefixes = prefix_entry.get().split(",")
        suffixes = suffix_entry.get().split(",")
        provider = provider_combobox.get()
        delimiters = ["", ".", "-"]
        num_threads = int(thread_scale.get())

        if not prefixes:
            update_status("Error: Prefixes cannot be empty.")
            return
        if not provider:
            update_status("Error: Please select a provider.")
            return

        # If "Use Suffixes" is not checked, ignore suffixes and delimiters
        if not use_suffixes_var.get():
            suffixes = [""]
            delimiters = [""]

        # Generate bucket name combinations
        bucket_names = []
        for prefix in prefixes:
            for suffix in suffixes:
                for delimiter in delimiters:
                    bucket_names.append(f"{prefix}{delimiter}{suffix}")

        # Load proxies before generating status message
        load_proxies()

        # Split bucket names into chunks for multi-threading
        chunk_size = max(1, len(bucket_names) // num_threads)
        bucket_chunks = [bucket_names[i:i + chunk_size] for i in range(0, len(bucket_names), chunk_size)]

        # Set status message exactly as in original
        update_status(f"Generated {len(bucket_names)} bucket names. Starting scan with provider: {provider}...")

        with processes_lock:
            current_processes.clear()
        completed_threads = 0

        # Start S3Scanner for each chunk in a separate thread
        for i, chunk in enumerate(bucket_chunks):
            bucket_file = f"buckets_{i}.txt" if num_threads > 1 else "buckets.txt"
            with open(bucket_file, "w") as file:
                file.write("\n".join(chunk))
            threading.Thread(target=run_s3scanner, args=(bucket_file, provider, i, num_threads)).start()

    except Exception as e:
        update_status(f"Error starting scan: {e}")

def run_s3scanner(bucket_file, provider, chunk_id, num_threads):
    """Runs S3Scanner on the generated bucket list and updates the GUI."""
    global completed_threads
    try:
        # Set up proxy if available
        proxy = get_random_proxy()
        env = os.environ.copy() if proxy else None
        if proxy:
            env['HTTP_PROXY'] = proxy
            env['HTTPS_PROXY'] = proxy

        process = subprocess.Popen(
            ["s3scanner", "-bucket-file", bucket_file, "-enumerate", "-provider", provider],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env
        )

        with processes_lock:
            current_processes.append(process)

        # Read S3Scanner output in real-time
        for line in iter(process.stdout.readline, ""):
            if line.strip():  # Ignore empty lines
                result_box.insert(END, line.strip() + "\n")
                result_box.see(END)

        process.stdout.close()
        process.wait()

        # Update completed threads count
        with threads_lock:
            completed_threads += 1
            if completed_threads == num_threads:
                update_status("Scan complete.")

    except Exception as e:
        update_status(f"Error running S3Scanner in thread {chunk_id}: {e}")
    finally:
        with processes_lock:
            if 'process' in locals() and process in current_processes:
                current_processes.remove(process)
        if os.path.exists(bucket_file):
            os.remove(bucket_file)

def stop_scan():
    """Stops all current scans."""
    global current_processes
    with processes_lock:
        for process in current_processes:
            process.terminate()
        current_processes = []
    update_status("Scan stopped.")

def clear_console():
    """Clears the console output in the result box."""
    result_box.delete(1.0, END)
    update_status("Console cleared.")

def update_status(message):
    """Updates the status label."""
    status_label.config(text=message)
    root.update_idletasks()

def sort_results():
    """Sorts the displayed results by the number of objects, from highest to lowest."""
    results = result_box.get(1.0, END).strip().split("\n")
    pattern = re.compile(r'(\d+)\s+objects')
    sorted_results = sorted(results, key=lambda line: int(pattern.search(line).group(1)) if pattern.search(line) else 0, reverse=True)
    result_box.delete(1.0, END)
    for result in sorted_results:
        result_box.insert(END, result + "\n")
    result_box.see(END)

# GUI Setup
root = Tk()
root.title("S3Hunter")
root.configure(bg=BG_COLOR)  # Set window background

# Input Fields
Label(root, text="Prefixes (comma-separated):", bg=BG_COLOR, fg=TEXT_FG).pack()
prefix_entry = Entry(root, width=50, bg=ENTRY_BG, fg=TEXT_FG)
prefix_entry.pack()

Label(root, text="Suffixes (comma-separated):", bg=BG_COLOR, fg=TEXT_FG).pack()
suffix_entry = Entry(root, width=50, bg=ENTRY_BG, fg=TEXT_FG)
suffix_entry.pack()

# Checkbox for "Use Suffixes"
use_suffixes_var = BooleanVar()
use_suffixes_checkbox = Checkbutton(root, text="Use Suffixes", variable=use_suffixes_var, bg=BG_COLOR, fg=TEXT_FG)
use_suffixes_checkbox.pack()

Label(root, text="Provider:", bg=BG_COLOR, fg=TEXT_FG).pack()
provider_combobox = Combobox(root, values=["aws", "digitalocean", "gcp", "linode", "scaleway", "dreamhost"], state="readonly", background=ENTRY_BG)
provider_combobox.pack()

# Proxy File Input with Browse and Help Buttons
Label(root, text="Proxy File Path (optional, one proxy per line):", bg=BG_COLOR, fg=TEXT_FG).pack()
proxy_frame = Frame(root, bg=BG_COLOR)
proxy_frame.pack()

proxy_entry = Entry(proxy_frame, width=40, bg=ENTRY_BG, fg=TEXT_FG)
proxy_entry.pack(side=LEFT, padx=5)

browse_button = Button(proxy_frame, text="Browse", command=browse_proxy_file, bg=BUTTON_BG, fg=TEXT_FG, activebackground=BUTTON_ACTIVE)
browse_button.pack(side=LEFT, padx=5)

help_button = Button(proxy_frame, text="?", command=show_proxy_help, bg=BUTTON_BG, fg=TEXT_FG, activebackground=BUTTON_ACTIVE)
help_button.pack(side=LEFT, padx=5)

# Thread Count Scrollbar (changed max to 20)
Label(root, text="Number of Threads (1-20):", bg=BG_COLOR, fg=TEXT_FG).pack()
thread_scale = Scale(root, from_=1, to=20, orient=HORIZONTAL, length=200, bg=BG_COLOR, fg=TEXT_FG)
thread_scale.set(1)
thread_scale.pack()

# Buttons in 2x2 Grid
button_frame = Frame(root, bg=FRAME_BORDER, borderwidth=2, relief="groove")
button_frame.pack(pady=10)

# Load icons if available, fall back to text-only if not
try:
    start_icon = PhotoImage(file="start.png")  # Replace with your start icon path
    stop_icon = PhotoImage(file="stop.png")   # Replace with your stop icon path
    run_button = Button(button_frame, text="Run Scan", image=start_icon, compound=LEFT, command=start_scan, bg=BUTTON_BG, fg=TEXT_FG, activebackground=BUTTON_ACTIVE)
    stop_button = Button(button_frame, text="Stop Scan", image=stop_icon, compound=LEFT, command=stop_scan, bg=BUTTON_BG, fg=TEXT_FG, activebackground=BUTTON_ACTIVE)
except Exception:
    run_button = Button(button_frame, text="Run Scan", command=start_scan, bg=BUTTON_BG, fg=TEXT_FG, activebackground=BUTTON_ACTIVE)
    stop_button = Button(button_frame, text="Stop Scan", command=stop_scan, bg=BUTTON_BG, fg=TEXT_FG, activebackground=BUTTON_ACTIVE)

clear_button = Button(button_frame, text="Clear Console", command=clear_console, bg=BUTTON_BG, fg=TEXT_FG, activebackground=BUTTON_ACTIVE)
sort_button = Button(button_frame, text="Sort Results", command=sort_results, bg=BUTTON_BG, fg=TEXT_FG, activebackground=BUTTON_ACTIVE)

# Arrange buttons in 2x2 grid
run_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
stop_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
clear_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
sort_button.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

# Ensure uniform button sizes
button_frame.grid_columnconfigure(0, weight=1)
button_frame.grid_columnconfigure(1, weight=1)

status_label = Label(root, text="Status: Ready", anchor="w", bg=BG_COLOR, fg=TEXT_FG)
status_label.pack(fill=X, padx=5, pady=5)

# ScrolledText for Results (larger window)
result_box = ScrolledText(root, width=140, height=30, bg=ENTRY_BG, fg=TEXT_FG)
result_box.pack(padx=10, pady=10)

root.mainloop()
