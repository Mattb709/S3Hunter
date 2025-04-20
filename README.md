# S3Hunter
 
A **user-friendly GUI** for [s3scanner](https://github.com/sa7mon/s3scanner) that helps security researchers and bug bounty hunters find **misconfigured S3 buckets** across multiple cloud providers.  

### **Features**  
✔ **Smart Bucket Generation** – Combine prefixes, suffixes, and delimiters automatically  
✔ **Multi-Cloud Support** – AWS, GCP, DigitalOcean, Linode, and more  
✔ **Real-Time Results** – Live output with auto-scrolling  
✔ **Sort & Filter** – Organize results by bucket size (object count)  
✔ **Lightweight** – No bloated dependencies, just pure Python + `s3scanner`  

![S3Image1](https://github.com/user-attachments/assets/643aebb5-aa5a-4e63-9c2b-88cb5790707f)

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

## 📌 Notes & Troubleshooting  

### **1. Requires `s3scanner` in PATH**  
If you get `s3scanner not found`:  
```bash
# Install (if missing):
go install github.com/sa7mon/s3scanner@latest

# Verify it's in PATH:
s3scanner --version
```

---

### **2. Manual Browser Access**  
Replace `BUCKETNAME` in these URLs to check buckets directly:  

#### **AWS S3**  
```
https://BUCKETNAME.s3.amazonaws.com/  
https://BUCKETNAME.s3.[region].amazonaws.com/  # e.g., s3.us-east-1
```

#### **DigitalOcean Spaces**  
```
https://BUCKETNAME.[region].digitaloceanspaces.com/  # e.g., nyc3
```

#### **Google Cloud (GCP)**  
```
https://storage.googleapis.com/BUCKETNAME/   
```

#### **Scaleway**  
*(Requires object path—try appending a file)*  
```
https://BUCKETNAME.[region].scw.cloud/example.txt  # e.g., fr-par
```

#### **DreamHost**  
```
https://BUCKETNAME.objects-[region].dream.io/  # e.g., us-east-1
```

#### **Linode**  
```
https://BUCKETNAME.[region].linodeobjects.com/  
```
### **3. Exfiltrate Bucket Contents**
First install AWS CLI on your system and then from the command line run:
```
aws s3 sync s3://BUCKETNAME/ BUCKETNAME --no-sign-request  
```

---

### **4. Common Errors**  
- **"Access Denied"**: Bucket exists but is properly locked.  
- **"NoSuchBucket"**: Bucket doesn’t exist (or was deleted).  
- **Timeout**: Region mismatch—try different endpoints.  

---

## **Sample Output**
![S3Hunter2](https://github.com/user-attachments/assets/0681e12e-9dc8-4f27-a869-3e17bed0a984)

## **Disclaimer**
This tool is for authorized security testing and educational purposes only. The author accepts no liability for misuse of this software.

## **📜 License**  
MIT License – Free for personal and commercial use.

## **TODOs for S3Hunter**

- [ ] Add optional multi-threading for faster scans
- [ ] Add support for rotating proxies (S3Hunter may experience rate-limiting when scanning batches of 100,000+ bucket names) 
