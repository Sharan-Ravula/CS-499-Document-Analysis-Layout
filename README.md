# DAL (Document Analysis Layout) - OpenText Exstream

---
## ‼️ University Industry-Collaboration Project

> Note: This project was developed as a senior design collaboration with OpenText Exstream. Originally intended as an exploratory tool for layout analysis, the final implementation exceeded stakeholder expectations.

The DAL project provides an automated solution for analyzing complex document communications, breaking them down into respective logical pieces (text blocks, images, logos, and barcodes) to facilitate easy importing into the [OpenText Exstream](https://www.opentext.com/products/customer-communications-management) ecosystem.

---

## 🚀 Project Overview

The primary challenge was to automate the segmentation of enterprise-scale communications based on whitespace and layout density. The solution leverages a Flask-based web interface to perform high-speed OCR and layout analysis, meeting a critical performance requirement of less than 10 seconds per image.

Key highlights include:

- Dual OCR Engines: Support for both `TesseractOCR` and `EasyOCR`

- Intelligent Scaling: `Adaptive DPI adjustment` (Small/Large analysis modes) to optimize character recognition.

- Barcode Integration: Native detection using `pyzbar` merged with spatial text data.

- Visual Debugging: A browser-based display that overlays analyzed zones (`bounding boxes`) onto the original image.

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

- Company: `OpenText Exstream`

- Primary Contacts:

	- `Nathan McConathy`: **OpenText Senior Design Project Customer**

	- `Billy Kidwell`: **OpenText Senior Design Project Instructor**

- Development Process: Conducted via `weekly agile meetings` to review updates, discuss algorithm refinements, and validate against enterprise document samples.

- Outcome: Successfully transitioned from a university prototype to a document analysis pipeline.

---

## ⚙️ Technical Specifications

- Backend: `Python` (**Flask**)

- OCR Engines: `EasyOCR` (Deep Learning based) and `PyTesseract`

- Image Processing: `Pillow`, `NumPy`, and `pdfplumber`

- Barcode Detection: `pyzbar`

- Performance: Optimized for `<10s processing time` per document page.

- Frontend: Clean, professional `HTML`,`JS`,`CSS` suite for real-time visualization of extracted "zones."

---

## 🧪 Key Features

- Analysis Modes: Users can select "`Small`," "`Large`," or "`Custom`" modes which dynamically adjust the image DPI to ensure the OCR engine captures text accurately regardless of font size.

- Coordinate Mapping: A custom `coordinates.py` module ensures that bounding boxes found on processed/resized images are accurately mapped back to the original document's dimensions.

- Data Export: Generates computer-readable `JSON outputs` containing text content, spatial coordinates, and corner-point arrays.

- Layout Visualization: Highlights `text blocks in blue/red` and `barcodes in green` to verify the "whitespace-based" segmentation algorithm.

---

## 📐 Coordinate Transformation & Scaling

To ensure the analysis is accurate regardless of the display size, the project includes a specialized script, `coordinates.py`, to map OCR results from the "processed" (resized/DPI-adjusted) image back to the "original" document dimensions. 

🛠 How `coordinates.py` Works:

The script does not guess resolutions based on a filename; instead, it uses the actual file properties from the most recent execution: 

- `last_paths.json` Integration: When you run the main Flask app (`dal-ocr_project.py`), it automatically saves the absolute paths of the original file, the processed image, and the OCR JSON output into `last_paths.json` 

- Automatic Retrieval: When you execute `python3 coordinates.py`, it reads this JSON file to identify exactly which files need coordinate correction. 

- Dynamic Dimension Detection:

	- For PDFs: The script uses `pdf2image` to convert the first page at 300 DPI to establish the "original" reference dimensions. 
	
	- For Images: It utilizes the `Pillow` library to read the pixel dimensions directly from the source file. 

- Scaling Calculation: The script compares the original dimensions against the processed image dimensions to calculate the $`ratio\_x`$ and $`ratio\_y`$ scaling factors. 

---

## 📐 Mathematical Formulas

- Scaling Factor Calculation

	- First, the script determines how much the image was scaled during processing by comparing the dimensions of the processed image to the original.
	
		- $`ratio_x` = `\frac{\text{processed\_width}}{\text{original\_width}}`$
		
		- $`ratio_y` = `\frac{\text{processed\_height}}{\text{original\_height}}`$
	
	- Original Dimensions: For PDFs, this is established by rendering the first page at a standard 300 DPI.
	
	- Processed Dimensions: These are the pixel dimensions of the image actually sent to the OCR engine.

- Coordinate Inverse Transformation

	- Once the ratios are known, the script converts the bounding box coordinates $(`x, y`)$ and dimensions (width, height) from the "processed" system back to the "original" system using division.

		- For Points:

			- $`x_{orig}` = `\frac{x_{proc}}{ratio_x}`$
     
			- $`y_{orig}` = `\frac{y_{proc}}{ratio_y}`$

		- For Bounding Boxes:

			- $`\text{width}_{orig}` = `\frac{\text{width}_{proc}}{ratio_x}`$

			- $`\text{height}_{orig}` = `\frac{\text{height}_{proc}}{ratio_y}`$

- Corner Point Mapping

	- The script also updates the four corners of each detected text block. If the OCR data includes corner coordinates, they are transformed individually; otherwise, they are reconstructed from the original $`x`$, $`y`$, width, and height:

		- Top-Left: $`(x_{orig}, y_{orig})`$
		
		- Top-Right: $`(x_{orig} + \text{width}_{orig}, y_{orig})`$
		
		- Bottom-Left: $`(x_{orig}, y_{orig} + \text{height}_{orig})`$
		
		- Bottom-Right: $`(x_{orig} + \text{width}_{orig}, y_{orig} + \text{height}_{orig})`$

	- This ensures that regardless of whether the analysis was done in Small or Large mode, the resulting JSON data aligns perfectly with the original file's coordinate space.

----

## 💥 Setup and Installation:

> After opening the zip file

> Please open the DAL-Project.py in VS-code or any of your preferred editor, 

> In the terminal make sure you `cd` to the project folder i.e. ~/CS-499-Document-Analysis-Layout/

1. Create a Virtual Environment in the path you open the file:
	
	- macOS/Linux:

      ```bash
	  python3 -m venv venv
	  source venv/bin/activate
      
	- Windows:

	  ```powershell
	  python -m venv venv
	  .\venv\Scripts\activate
   
2. Install Homebrew (optional but recommended):

	- macOS/Linux:

	  ```bash
	  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

   - Windows: On Windows, you can use Chocolatey as a package manager.

		> Note: If you prefer to use Homebrew on Windows, consider installing it via WSL (Windows Subsystem for Linux) and following the macOS instructions within your WSL terminal.

	    > Open PowerShell as Administrator.
       
	   - Run the following command to install Chocolatey:
       
	     ```powershell
		 Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
      
	  	- **Close and reopen your PowerShell, then verify Chocolatey is installed**:
       
		  ```powershell
          choco --version
    
3. Install Dependencies: First, make sure pip is updated:
		
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

4. Run the App:

	- macOS/Linux:

	  ```bash
	  python3 dal_ocr_project.py
      python3 coordinates.py
   
	- Windows:

	  ```powershell
	  python dal_ocr_project.py
      python coordinates.py

5. Usage:

   ```text
   http://127.0.0.1:5000
6. Troubleshooting:

	- For large PDFs, ensure you have enough `RAM` and `CPU` cores.

	- If `EasyOCR` fails to load, make sure `PyTorch` is correctly installed.

	- "CropBox missing from /Page, defaulting to MediaBox" is just a info which we can safely ignore as it wont effect any functionality of the project.

	- If you encounter the problem where the website is not launching when you run the program, Please either clear your cache or use a different browser.

	- Please allow pop-up Windows enabled in the browser for this project to work properly.

	- If you find any red highlights in any html file ignore it, as it is a editor issue and wont effect the main program.

	- The drag box wont move when you first upload the file, you have to delete the drag box by clicking the "x" icon on the top right corner of the border, and press the button "More Drag-Boxes" only then it works properly, I dont know why this glitch is happening but it is a very small one so I ignored it.

7. Additional Nerdy-Stuff:

	- The other modules like `json`, `time`, `os`, `re`, and `multiprocessing` are part of Python’s standard library, so you don’t need to install them separately.

	- API Endpoints

| Endpoint | Method | Description |
| :--- | :---: | ---: |
| /	| GET | Upload interface |
| /upload | POST | Uploads PDF and triggers OCR |
| /results/<pdf_name> | GET | Shows total processed pages |
| /json_data/<pdf_name>/<int:page> | GET | Returns JSON of extracted text |
| /highlighted_image/<pdf_name>/<int:page> | GET | Returns image with bounding boxes |

---
