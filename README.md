# DAL (Document Analysis Layout) - OpenText Exstream

---
## ‼️ University Industry-Collaboration Project

> Note: This project was developed as a senior design collaboration with OpenText Exstream. Originally intended as an exploratory tool for layout analysis, the final implementation exceeded stakeholder expectations, resulting in a company-filed patent for the unique approach to document decomposition.

The DAL project provides an automated solution for analyzing complex document communications, breaking them down into respective logical pieces (text blocks, images, logos, and barcodes) to facilitate easy importing into the [OpenText Exstream](https://www.opentext.com/products/customer-communications-management) ecosystem.

---

## 🚀 Project Overview

The primary challenge was to automate the segmentation of enterprise-scale communications based on whitespace and layout density. The solution leverages a Flask-based web interface to perform high-speed OCR and layout analysis, meeting a critical performance requirement of less than 10 seconds per image.

Key highlights include:

- **Dual OCR Engines**: Support for both `TesseractOCR` and `EasyOCR`

- **Intelligent Scaling**: `Adaptive DPI adjustment` (Small/Large analysis modes) to optimize character recognition.

- **Barcode Integration**: Native detection using `pyzbar` merged with spatial text data.

- **Visual Debugging**: A browser-based display that overlays analyzed zones (`bounding boxes`) onto the original image.

---

## 📂 Repository Structure

```text
DAL-Project/
├── scripts/                 	 			# Utility scripts for data processing
│	├── templates/               			# UI Layer
│   │	├── upload.html          			# File upload interface with analysis mode selection
│   │	├── results.html         			# Interactive results viewer
│   │	├── results.js           			# Dynamic bounding box rendering logic
│   │	├── upload.js            			# Frontend file handling
│   │	├── upload.css           			# Styling for the upload portal
│   │	└── styles.css           			# Global application styles
│	├── dal_ocr_project.py       			# Main Flask application & OCR orchestration logic
│	├── coordinates.py           			# Logic for coordinate scaling between processed & original images
│	├── last_paths.json          			# Persistent storage for session-based file paths (Automatically generated when you run coordinates.pyt)
├── docs/                    				# Technical Documentation
│   ├── patent_discussion_flow_diagram.pdf
│   └── s25008_project_description.pdf
│
├── tests/                   				# Extensive test suite
│   ├── others/              				# Various PDF/JPEG test cases
│   └── tests_used_for_analysis/ 			# Controlled samples for benchmark testing
│
├── results/                 				# Output directory for visualized PNGs and JSON data
│
├──	LICENSE                             	# License information for the repository
└── README.md                				# Project documentation
```

---

## 🛠 Project Stakeholders & History

- **Company**: `OpenText Exstream`

- **Primary Contacts**:

	- `Nathan McConathy`: **OpenText Senior Design Project Customer**

	- `Billy Kidwell`: **OpenText Senior Design Project Instructor**

- **Development Process**: Conducted via `weekly agile meetings` to review updates, discuss algorithm refinements, and validate against enterprise document samples.

- **Outcome**: Successfully transitioned from a university prototype to a `patented document` analysis methodology.

---

## ⚙️ Technical Specifications

- **Backend**: `Python` (**Flask**)

- **OCR Engines**: `EasyOCR` (Deep Learning based) and `PyTesseract`

- **Image Processing**: `Pillow`, `NumPy`, and `pdfplumber`

- **Barcode Detection**: `pyzbar`

- **Performance**: Optimized for `<10s processing time` per document page.

- **Frontend**: Clean, professional `HTML`,`JS`,`CSS` suite for real-time visualization of extracted "zones."

---

## 🧪 Key Features

- **Analysis Modes**: Users can select "`Small`," "`Large`," or "`Custom`" modes which dynamically adjust the image DPI to ensure the OCR engine captures text accurately regardless of font size.

- **Coordinate Mapping**: A custom `coordinates.py` module ensures that bounding boxes found on processed/resized images are accurately mapped back to the original document's dimensions.

- **Data Export**: Generates computer-readable `JSON outputs` containing text content, spatial coordinates, and corner-point arrays.

- **Layout Visualization**: Highlights `text blocks in blue/red` and `barcodes in green` to verify the "whitespace-based" segmentation algorithm.

---

## 🔥 Getting Started

💥 Setup and Installation:

> After opening the zip file

> Please open the DAL-Project.py in VS-code or any of your preferred editor, 

> In the terminal make sure you `cd` to the project folder i.e. ~/CS-499-Document-Analysis-Layout/

1. Create a Virtual Environment in the path you open the file:
	
	- macOS / Linux:

      ```bash
	  python3 -m venv venv
	  source venv/bin/activate
      
	- Windows:

	  ```powershell
	  python -m venv venv
	  .\venv\Scripts\activate
   
2. Install Homebrew (optional but recommended):

	- macOS:

	  ```bash
	  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

   - Windows: On Windows, you can use Chocolatey as a package manager.

		> (Note: If you prefer to use Homebrew on Windows, consider installing it via WSL (Windows Subsystem for Linux) and following the macOS instructions within your WSL terminal.)

	   - Open PowerShell as Administrator.
       
	   - Run the following command to install Chocolatey:
       
	     ```powershell
		 Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
      
	   - Close and reopen your PowerShell, then verify Chocolatey is installed:
       
	     ```
         choco --version
    
4. Install Dependencies: First, make sure pip is updated:
		
	- macOS/Linux:

	  ```bash
	  python3 -m pip install --upgrade pip
	  pip --version
	  pip install flask pdfplumber easyocr pyzbar pillow numpy pytesseract
   
   > A new file will be added to the DAL-Project Folder i.e. venv

	- Windows:

	  ```powershell
	  python -m pip install --upgrade pip
	  pip --version
	  pip install flask pdfplumber easyocr pyzbar pillow numpy pytesseract
   
  > A new file will be added to the DAL-Project Folder i.e. venv

5. Run the App:

	- macOS:

	  ```bash
	  python3 dal_ocr_project.py
   
	- Windows:

	  ```powershell
	  python dal_ocr_project.py

6. Usage:
   
   ```text
   http://127.0.0.1:5000
   
8. Troubleshooting:

	- For large PDFs, ensure you have enough RAM and CPU cores.

	- If EasyOCR fails to load, make sure PyTorch is correctly installed.

	- "CropBox missing from /Page, defaulting to MediaBox" is just a info which we can safely ignore as it wont effect any functionality of the project.

	- If you encounter the problem where the website is not launching when you run the program, Please either clear your cache or use a different browser.

	- Please allow pop-up Windows enabled in the browser for this project to work properly.

	- If you find any red highlights in any html file ignore it, as it is a editor issue and wont effect the main program.

	- The drag box wont move when you first upload the file, you have to delete the drag box by clicking the "x" icon on the top right corner of the border, and press the button "More Drag-Boxes" only then it works properly, I dont know why this glitch is happening but it is a very small one so I ignored it.

9. Additional Nerdy-Stuff:

	- The other modules like `json`, `time`, `os`, `re`, and `multiprocessing` are part of Python’s standard library, so you don’t need to install them separately.

	- API Endpoints

| Endpoint | Method | Description |
| :--- | :---: | ---: |
| /	| GET | Upload interface |
| /upload | POST | Uploads PDF and triggers OCR |
| /results/<pdf_name> | GET | Shows total processed pages |
| /json_data/<pdf_name>/<int:page> | GET | Returns JSON of extracted text |
| /highlighted_image/<pdf_name>/<int:page> | GET | Returns image with bounding boxes |
