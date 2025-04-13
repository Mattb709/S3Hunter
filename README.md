# S3Hunter
 
A **user-friendly GUI** for [s3scanner](https://github.com/sa7mon/s3scanner) that helps security researchers and bug bounty hunters find **misconfigured S3 buckets** across multiple cloud providers.  

### **Features**  
✔ **Smart Bucket Generation** – Combine prefixes, suffixes, and delimiters automatically  
✔ **Multi-Cloud Support** – AWS, GCP, DigitalOcean, Linode, and more  
✔ **Real-Time Results** – Live output with auto-scrolling  
✔ **Sort & Filter** – Organize results by bucket size (object count)  
✔ **Lightweight** – No bloated dependencies, just pure Python + `s3scanner`  

![S3Hunter1](https://github.com/user-attachments/assets/97a7953a-27ec-495c-a253-bcafd5e4eb87)
---

## **🚀 Installation**  

### **1. Install s3scanner (Required Backend)**  
S3Hunter relies on **[s3scanner](https://github.com/sa7mon/s3scanner)** for scanning.  

#### **Linux/macOS (via Go):**  
```bash
go install github.com/sa7mon/s3scanner@latest
export PATH=$PATH:~/go/bin  # Add to PATH if not already
```

#### **Windows:**  
- Download the latest `release` from [s3scanner releases](https://github.com/sa7mon/s3scanner/releases)  
- Place it in a directory included in your `PATH`  

---

### **2. Run S3Hunter (No Python Dependencies Needed!)**  
The tool uses **built-in Python modules** (`tkinter`, `subprocess`, etc.).  

#### **Linux (Debian/Ubuntu) - Fix Missing Tkinter:**  
```bash
sudo apt install python3-tk  # Only needed if GUI fails to open
```

#### **Launch S3Hunter:**  
```bash
python s3hunter.py
```

---

## **🎯 Usage**  
1. **Enter Prefixes** - Comma seperated, no spaces (e.g., `company,prod,test`)  
2. **(Optional) Add Suffixes** (e.g., `backup,storage,logs`)  
3. **Select a Cloud Provider** (AWS, GCP, DigitalOcean, etc.)  
4. **Click "Run Scan"** – Results appear in real-time!  
5. **Sort Results** – Click "Sort" to organize by bucket size  

*(Tip: Disable "Use Suffixes" to scan raw prefixes only.)*  

---

## **📌 Notes & Troubleshooting**  
- **Requires `s3scanner` in `PATH`** – Otherwise, you'll get `s3scanner not found`.  
 
---

## **📜 License**  
MIT License – Free for personal and commercial use.

## **Sample Usage**


