DAL (Document Analysis Layout): Sharan Ravula

In this project, in the upload UI, you have to choose the analysis mode, which is basically changing the dpi of an Image, when we use OCR in a project dpi of the image is really important for OCR to detect text.
I have shared the necessary info on DPI change for the small and Large analysis mode, obviously you can use custom option and customize the dpi of an image however you like! Enjoy this Project of Mine.

DAL-Project/
│
├── DAL-ProjectOCR.py        # Main Flask app
├── last_paths.json          # Stores info on previously used paths
├── coordinates.py           # Script for handling Original Scaling coordinate-related logic
├── templates/
│   ├── upload.html          # Upload page
│   ├── results.html         # Results display
│   ├── results.js           # JavaScript for results page
│   ├── upload.js            # JavaScript for upload page
│   ├── upload.css           # CSS for upload page
│   └── styles.css           # CSS file for styling pages
├── uploads/                 # Storing the PDF/Image files users upload. (Auto-created)
├── static/                  # Saving annotated images and JSON output. (Auto-created)
├── Test-Cases/              # Contains multiple test-case files
└── README.txt               # Instruction Manual - Please read it

After opening the zip file, 

Please open the DAL-Project.py in VS-code or any your preferred editor, 

In the terminal make sure you cd to the project folder i.e. ~/DAL-Project/

1. Create a Virtual Environment in the path you open the file:
	
	a. macOS / Linux:
		
		python3 -m venv venv
		source venv/bin/activate
	
	b. Windows:
		
		python -m venv venv
		.\venv\Scripts\activate

2. Install Homebrew (optional but recommended):

	a. macOS:
	
		/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

	b. Windows: On Windows, you can use Chocolatey as a package manager. (Note: If you prefer to use Homebrew on Windows, consider installing it via WSL (Windows Subsystem for Linux) and following the macOS instructions within your WSL terminal.)

	   1. Open PowerShell as Administrator.
	   2. Run the following command to install Chocolatey:
	
		Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

	   3. Close and reopen your PowerShell, then verify Chocolatey is installed:

		choco --version
	
3. Install Dependencies: First, make sure pip is updated:
		
	a. macOS/Linux
		
		python3 -m pip install --upgrade pip
		pip --version
		pip install flask pdfplumber easyocr pyzbar pillow numpy pytesseract
		A new file will be added to the DAL-Project Folder i.e. venv

	b. Windows
		
		python -m pip install --upgrade pip
		pip --version
		pip install flask pdfplumber easyocr pyzbar pillow numpy pytesseract
		A new file will be added to the DAL-Project Folder i.e. venv

4. Run the App:

	a. macOS
	
		python3 DAL-ProjectOCR.py

	b. Windows
		
		python DAL-ProjectOCR.py

5. Usage:

	http://127.0.0.1:5000

6. Troubleshooting:

	a. For large PDFs, ensure you have enough RAM and CPU cores.
	b. If EasyOCR fails to load, make sure PyTorch is correctly installed.
	c. "CropBox missing from /Page, defaulting to MediaBox" is just a info which we can safely ignore as it wont effect any functionality of the project.
	d. If you encounter the problem where the website is not launching when you run the program, Please either clear your cache or use a different browser.
	e. Please allow pop-up Windows enabled in the browser for this project to work properly.
	f. If you find any red highlights in any html file ignore it, as it is a editor issue and wont effect the main program.
	h. The drag box wont move when you first upload the file, you have to delete the drag box by clicking the "x" icon on the top right corner of the border, and press the button "More Drag-Boxes" only then it works properly, I dont know why this glitch is happening but it is a very small one so I ignored it.

7. Additional Nerdy-Stuff:

a. The other modules like json, time, os, re, and multiprocessing are part of Python’s standard library, so you don’t need to install them separately.

b. API Endpoints

Endpoint										Method			Description
/												GET				Upload interface
/upload											POST			Uploads PDF and triggers OCR
/results/<pdf_name>								GET				Shows total processed pages
/json_data/<pdf_name>/<int:page>				GET				Returns JSON of extracted text
/highlighted_image/<pdf_name>/<int:page>		GET				Returns image with bounding boxes