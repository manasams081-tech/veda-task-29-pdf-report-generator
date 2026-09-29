# VEDA Technology — Task 29: Build a PDF Report Generator

A complete Python web application that processes business data with **Pandas** and generates a professional PDF report with **ReportLab**.

## Tools used
- Python
- Pandas
- ReportLab

The web page uses Python's built-in `http.server`, so no Flask, Streamlit, React, Bootstrap, or other third-party framework is required.

## Features
- Unique VEDA-style reporting dashboard
- KPI summary cards
- Regional revenue analysis
- Latest business records table
- CSV upload and validation
- Automatic summary calculations with Pandas
- One-click PDF report generation with ReportLab
- Generated PDF saved in the `reports` folder
- Sample dataset included
- Setup verification script included

## Files
```text
VEDA_Task_29_PDF_Report_Generator/
├── app.py
├── sample_data.csv
├── requirements.txt
├── verify_setup.py
├── setup_windows.bat
├── start_app.bat
├── task_info.json
├── README.md
├── .gitignore
└── reports/
    └── sample_report.pdf
```

## Windows setup — safest method

### 1. Extract the ZIP
Extract the ZIP **as-is**. It already contains one top-level folder:

`VEDA_Task_29_PDF_Report_Generator`

After extraction, all files should be inside that single folder. Do not move the files out individually.

Example:
```text
C:\VEDA\VEDA_Task_29_PDF_Report_Generator\app.py
C:\VEDA\VEDA_Task_29_PDF_Report_Generator\requirements.txt
...
```

### 2. Open Command Prompt in that folder
Open the folder, click the address bar, type `cmd`, and press Enter.

### 3. Create the virtual environment
```bat
py -3.12 -m venv .venv
```

If `py -3.12` is unavailable, use an installed supported Python 3.x version, for example:
```bat
py -3.13 -m venv .venv
```

### 4. Activate it
```bat
.venv\Scripts\activate
```

You should see `(.venv)` in the command prompt.

### 5. Install only the required packages
```bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Verify the setup
```bat
python verify_setup.py
```

Expected result:
```text
[OK] pandas
[OK] reportlab
[OK] Sample CSV loaded: 20 records
[OK] Setup verification passed.
```

### 7. Start the web application
```bat
python app.py
```

Open:
```text
http://127.0.0.1:8000
```

### 8. Generate the PDF
1. Confirm the dashboard loads.
2. Click **Generate PDF Report**.
3. The PDF is downloaded by the browser.
4. A copy is saved under `reports/`.
5. Open the PDF and take a screenshot for the internship report.

## CSV format
For a custom file, use these columns:
```text
date,region,product,customer,quantity,unit_price,revenue
```

The included `sample_data.csv` is ready to use.

## GitHub
GitHub username from the provided profile screenshot:
`manasams081-tech`

Recommended repository:
`veda-task-29-pdf-report-generator`

Recommended description:
`VEDA Technology Task 29 - Python PDF Report Generator using Pandas and ReportLab with a reusable web dashboard.`

Create an **empty Public repository**. Do not add a GitHub README, `.gitignore`, or license because they are already included in this project.

Repository link:
https://github.com/manasams081-tech/veda-task-29-pdf-report-generator

### Push commands — run in this project folder
```bat
git init
git branch -M main
git add .
git status
git commit -m "Complete VEDA Technology Task 29 PDF report generator"
git remote add origin https://github.com/manasams081-tech/veda-task-29-pdf-report-generator.git
git push -u origin main
```

### If `origin already exists`
Do not run `git remote add origin` again. Instead:
```bat
git remote set-url origin https://github.com/manasams081-tech/veda-task-29-pdf-report-generator.git
git push -u origin main
```

### Before pushing
Run:
```bat
git status
git remote -v
```
Confirm `.venv` is not listed and `origin` points to the repository above.

## Task 29 checklist
- [x] Python program
- [x] Pandas data processing
- [x] ReportLab PDF generation
- [x] Professional PDF report
- [x] Tables and summary metrics
- [x] Automated report-generation script
- [x] Sample dataset
- [x] Reusable web application
- [x] CSV validation
- [x] Generated sample PDF
- [x] GitHub-ready project
