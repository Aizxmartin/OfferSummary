
import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
import tempfile
import os
import re

def extract_contract_summary(text):
    summary = {}
    summary["2.1. Buyer Buyer(s) Names"] = re.search(r"Buyer\.\s*(.*?)\s*\(Buyer\)", text).group(1).strip() if re.search(r"Buyer\.\s*(.*?)\s*\(Buyer\)", text) else "Not found"
    summary["2.1. Title Box Checked or In Severalty"] = (
        "☒ Other – In Severalty" if "☒ Other In Severalty" in text or "X Other In Severalty" in text
        else "☒ Joint Tenants" if "☒ Joint Tenants" in text or "X Joint Tenants" in text
        else "☒ Tenants In Common" if "☒ Tenants In Common" in text or "X Tenants In Common" in text
        else "None Selected"
    )
    patterns = {
        "2.5.3. Other Inclusions": r"2\.5\.3\..*?included in the Purchase Price:\s*(.*?)\s*If the box",
        "2.6. Exclusions": r"2\.6\. Exclusions:\s*(.*?)\s*2\.7",
        "3.1. Time of Day Deadline": r"Time of Day Deadline\s*(\S+)",
        "3.1. Alternative Earnest Money Deadline": r"Alternative Earnest Money Deadline\s*(\S+)",
        "3.1. New Loan Terms Deadline": r"New Loan Terms Deadline\s*(\S+)",
        "3.1. New Loan Availability Deadline": r"New Loan Availability Deadline\s*(\S+)",
        "3.1. Inspection Termination Deadline": r"Inspection Termination Deadline\s*(\S+)",
        "3.1. Closing Date": r"Closing Date\s*(\S+)",
        "3.1. Possession Date": r"Possession Date\s*(.*?)\s*Possession Time",
        "3.1. Possession Time": r"Possession Time\s*(\S+)",
        "3.1. Purchase Price": r"Purchase Price.*?\$([\d,\.]+)",
        "4.1. Earnest Money": r"Earnest Money.*?\$([\d,\.]+)",
        "4.1. Cash at Closing": r"Cash at Closing.*?\$([\d,\.]+)",
        "4.2 Seller Concession": r"4\.2.*?credit to Buyer \$(.*?)\s*\(",
        "4.3 Earnest held by": r"Earnest Money.*?in the form of a (.*?)\,",
        "4.4.3. Available Funds": r"Available Funds.*?Buyer represents that Buyer.*?(Does|Does Not)",
        "4.5.3. Loan Limitations": r"Loan Limitations.*?(Conventional|FHA|VA|Bond|Other)",
        "6.4. Cost of Appraisal": r"Cost of the Appraisal.*?paid by\s*(Buyer|Seller)",
        "8.1.1. Seller Selects": r"8\.1\.1.*?(☒|X)",
        "8.1.2. Buyer Selects": r"8\.1\.2.*?(☒|X)",
        "10.6.1.6. Other Docs": r"10\.6\.1\.6.*?Other documents and information:\s*(.*?)\s*10\.6\.2",
        "13. Transfer of Title": r"Transfer of Title.*?deliver the following good and sufficient deed.*?(special warranty deed|general warranty deed|bargain and sale deed|quit claim deed|personal representative’s deed)",
        "Section 29 (29.1/29.2/29.3)": r"29\.1.*?(\d\.\d+%) of the Purchase Price",
        "Section 30 Additional Provisions": r"30.*?Additional Provisions.*?Seller agrees to (.*?)\."
    }
    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.DOTALL)
        summary[field] = match.group(1).strip() if match else "Not found"
    return summary

def run_app():
    st.title("Contract Summary Table Generator")
    uploaded = st.file_uploader("Upload a Colorado Contract PDF", type="pdf")

    if uploaded:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded.read())
            pdf_path = tmp.name

        reader = PdfReader(pdf_path)
        contract_text = "".join([page.extract_text() or "" for page in reader.pages])

        data = extract_contract_summary(contract_text)

        doc = Document()
        doc.add_heading("Contract Summary Table", 0)
        table = doc.add_table(rows=1, cols=2)
        table.style = 'Table Grid'
        table.rows[0].cells[0].text = "Field"
        table.rows[0].cells[1].text = "Extracted Value"
        for field, value in data.items():
            row = table.add_row().cells
            row[0].text = field
            row[1].text = value

        output_docx_path = os.path.join(tempfile.gettempdir(), "Contract_Summary_Table.docx")
        doc.save(output_docx_path)

        with open(output_docx_path, "rb") as file:
            st.download_button("Download DOCX Summary", file, file_name="Contract_Summary_Table.docx")

if __name__ == "__main__":
    run_app()
