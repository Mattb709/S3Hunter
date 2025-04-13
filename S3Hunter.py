import os
import subprocess
import threading
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Combobox
import re

# Global variable to store the process
current_process = None

def start_scan():
    """Starts the S3Scanner scan and displays results in real-time."""
    global current_process

    prefixes = prefix_entry.get().split(",")
    suffixes = suffix_entry.get().split(",")
    provider = provider_combobox.get()
    delimiters = ["", ".", "-"]

    if not prefixes:
        update_status("Error: Prefixes cannot be empty.")
        return

    if not provider:
        update_status("Error: Please select a provider.")
        return

    # If "Use Suffixes" is not checked, ignore suffixes and delimiters
    if not use_suffixes_var.get():
        suffixes = [""]
        delimiters = [""]  # No delimiters when suffixes are not used

    # Generate bucket name combinations
    bucket_names = []
    for prefix in prefixes:
        for suffix in suffixes:
            for delimiter in delimiters:
                bucket_names.append(f"{prefix}{delimiter}{suffix}")

    # Save to file for S3Scanner
    with open("buckets.txt", "w") as file:
        file.write("\n".join(bucket_names))

    update_status(f"Generated {len(bucket_names)} bucket names. Starting scan with provider: {provider}...")

    # Start S3Scanner in a thread
    threading.Thread(target=run_s3scanner, args=("buckets.txt", provider)).start()

def run_s3scanner(bucket_file, provider):
    """Runs S3Scanner on the generated bucket list and updates the GUI."""
    global current_process
    try:
        current_process = subprocess.Popen(
            ["s3scanner", "-bucket-file", bucket_file, "-enumerate", "-provider", provider],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # Read S3Scanner output in real-time
        for line in iter(current_process.stdout.readline, ""):
            if line.strip():  # Ignore empty lines
                result_box.insert(END, line.strip() + "\n")
                result_box.see(END)

        current_process.stdout.close()
        current_process.wait()
        update_status("Scan complete.")
    except Exception as e:
        update_status(f"Error running S3Scanner: {e}")
    finally:
        current_process = None

def stop_scan():
    """Stops the current scan."""
    global current_process
    if current_process:
        current_process.terminate()
        update_status("Scan stopped.")
        current_process = None
    else:
        update_status("No scan is running.")

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

    # Regex pattern to extract the number of objects
    pattern = re.compile(r'(\d+)\s+objects')

    # Filter and sort the results by the number of objects (if present)
    sorted_results = sorted(results, key=lambda line: int(pattern.search(line).group(1)) if pattern.search(line) else 0, reverse=True)

    # Clear the result box and insert sorted results
    result_box.delete(1.0, END)
    for result in sorted_results:
        result_box.insert(END, result + "\n")
    result_box.see(END)

# GUI Setup
root = Tk()
root.title("S3 Scanner GUI")

# Input Fields
Label(root, text="Prefixes (comma-separated):").pack()
prefix_entry = Entry(root, width=50)
prefix_entry.pack()

Label(root, text="Suffixes (comma-separated):").pack()
suffix_entry = Entry(root, width=50)
suffix_entry.pack()

# Checkbox for "Use Suffixes"
use_suffixes_var = BooleanVar()
use_suffixes_checkbox = Checkbutton(root, text="Use Suffixes", variable=use_suffixes_var)
use_suffixes_checkbox.pack()

Label(root, text="Provider:").pack()
provider_combobox = Combobox(root, values=["aws", "digitalocean", "gcp", "linode", "scaleway", "dreamhost"], state="readonly")
provider_combobox.pack()

# Buttons and Status
run_button = Button(root, text="Run Scan", command=start_scan)
run_button.pack(pady=10)

stop_button = Button(root, text="Stop Scan", command=stop_scan)
stop_button.pack(pady=5)

clear_button = Button(root, text="Clear Console", command=clear_console)
clear_button.pack(pady=5)

sort_button = Button(root, text="Sort Results", command=sort_results)
sort_button.pack(pady=5)

status_label = Label(root, text="Status: Ready", anchor="w")
status_label.pack(fill=X, padx=5, pady=5)

# ScrolledText for Results (adjusted width)
result_box = ScrolledText(root, width=120, height=20)  # Wider window for results
result_box.pack(padx=10, pady=10)

root.mainloop()

