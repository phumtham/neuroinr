
import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io

st.set_page_config(page_title="Neurosurgery Equipment Cost App", layout="centered")

# Load equipment data
df = pd.read_excel("ค่าอุปกรณ์.xlsx", engine="openpyxl")
df.set_index("equipment", inplace=True)

# Mapping for healthcare schemes
scheme_map = {
    "A: universal healthcare": "Universal healthcare",
    "B: UCEP": "UCEP",
    "C: Social security": "Social Security",
    "D: Civil service": "Civil Servant",
    "E: Self pay": "Self pay"
}

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = 0
if "patient_data" not in st.session_state:
    st.session_state.patient_data = {}
if "operation" not in st.session_state:
    st.session_state.operation = ""
if "equipment" not in st.session_state:
    st.session_state.equipment = {}

# Navigation buttons
def next_page():
    st.session_state.page += 1

def prev_page():
    st.session_state.page -= 1

# Page 0: Patient Data
if st.session_state.page == 0:
    st.title("Patient Information")
    st.session_state.patient_data["ชื่อ"] = st.text_input("ชื่อ")
    st.session_state.patient_data["นามสกุล"] = st.text_input("นามสกุล")
    st.session_state.patient_data["HN"] = st.text_input("HN")
    st.session_state.patient_data["Diagnosis"] = st.text_input("Diagnosis")
    scheme = st.selectbox("Healthcare Scheme", list(scheme_map.keys()))
    st.session_state.patient_data["Scheme"] = scheme
    if st.button("Next"):
        next_page()

# Page 1: Operation Selection
elif st.session_state.page == 1:
    st.title("Select Operation")
    operations = [
        "Diagnostic angiogram",
        "Cerebral angiogram with simple coiling",
        "Cerebral angiogram with transarterial ONYX embolization",
        "Cerebral angiogram with transvenous coiling",
        "Cerebral angiogram with stent assisted coiling",
        "Others"
    ]
    selected_op = st.selectbox("Operation", operations)
    if selected_op == "Others":
        custom_op = st.text_input("Enter operation name")
        st.session_state.operation = custom_op
    else:
        st.session_state.operation = selected_op
    if st.button("Previous"):
        prev_page()
    if st.button("Next"):
        next_page()

# Page 2: Equipment Selection
elif st.session_state.page == 2:
    st.title("Equipment Selection")
    st.subheader(f"Operation: {st.session_state.operation}")
    default_equipment = {
        "Diagnostic angiogram": {
            "Angiogram": 1, "Contrast media": 4, "femoral sheath": 1,
            "Diagnostic catheter": 1, "0.038 Wire": 1
        },
        "Cerebral angiogram with simple coiling": {
            "Angiogram": 1, "Contrast media": 6, "femoral sheath": 1,
            "Softip guider": 1, "0.038 Wire": 1, "SL10": 1,
            "Synchro": 1, "Rhya": 2, "Coil": 5
        },
        "Cerebral angiogram with transarterial ONYX embolization": {
            "Angiogram": 1, "Contrast media": 6, "femoral sheath": 1,
            "Softip guider": 1, "0.038 Wire": 1, "Apollo": 1,
            "Mirage": 1, "Rhya": 1, "ONYX ": 2
        },
        "Cerebral angiogram with transvenous coiling": {
            "Angiogram": 1, "Contrast media": 6, "femoral sheath": 2,
            "Diagnostic catheter": 2, "Softip guider": 1, "0.038 Wire": 1,
            "SL10": 1, "Synchro": 1, "Rhya": 3, "Coil": 10
        },
        "Cerebral angiogram with stent assisted coiling": {
            "Angiogram": 1, "Contrast media": 6, "femoral sheath": 1,
            "Softip guider": 1, "0.038 Wire": 1, "SL10": 2,
            "Synchro": 1, "Coil": 5, "Neuroform ATLAS": 1, "Rhya": 3
        }
    }
    limited_items = [
        "Destination longsheath", "Fubuki Longsheath", "NeuronMAX Longsheath",
        "Fargo/ FargoMAX", "Sofia 5F ", "Neuroform ATLAS", "Surpass",
        "Silk Vista", "Copernic balloon ", "Hyperglide balloon",
        "Exchange wire", "mariner"
    ]
    selected_defaults = default_equipment.get(st.session_state.operation, {})
    for item in df.index:
        if item in limited_items:
            val = st.radio(f"{item}", [0, 1], index=selected_defaults.get(item, 0))
        else:
            val = st.number_input(f"{item}", min_value=0, value=selected_defaults.get(item, 0))
        st.session_state.equipment[item] = val
    if st.button("Previous"):
        prev_page()
    if st.button("Next"):
        next_page()

# Page 3: Cost Summary
elif st.session_state.page == 3:
    st.title("Cost Summary")
    scheme_col = scheme_map[st.session_state.patient_data["Scheme"]]
    total_cost = 0
    total_reimbursement = 0
    for item, qty in st.session_state.equipment.items():
        cost = df.at[item, "Cost"] * qty
        reimb = df.at[item, scheme_col] * qty
        total_cost += cost
        total_reimbursement += reimb
    out_of_pocket = max(total_cost - total_reimbursement, 0)
    st.write(f"**Total Cost:** {total_cost:.2f}")
    st.write(f"**Total Reimbursement:** {total_reimbursement:.2f}")
    st.write(f"**Out-of-pocket Cost:** {out_of_pocket:.2f}")
    if st.button("Previous"):
        prev_page()
    if st.button("Next"):
        next_page()

# Page 4: PDF Generation
elif st.session_state.page == 4:
    st.title("Generate PDF Summary")
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    x = 50
    y = height - 50
    pd = st.session_state.patient_data
    c.drawString(width - 200, y, f"ชื่อ: {pd['ชื่อ']}")
    c.drawString(width - 200, y - 20, f"นามสกุล: {pd['นามสกุล']}")
    c.drawString(width - 200, y - 40, f"HN: {pd['HN']}")
    c.drawString(width - 200, y - 60, f"Diagnosis: {pd['Diagnosis']}")
    y -= 100
    c.drawString(x, y, f"Healthcare Scheme: {pd['Scheme']}")
    c.drawString(x, y - 20, f"Operation: {st.session_state.operation}")
    y -= 60
    c.drawString(x, y, "Equipment Used:")
    y -= 20
    for item, qty in st.session_state.equipment.items():
        if qty > 0:
            c.drawString(x + 20, y, f"{item}: {qty}")
            y -= 15
    y -= 20
    c.drawString(x, y, f"Total Cost: {total_cost:.2f}")
    c.drawString(x, y - 15, f"Total Reimbursement: {total_reimbursement:.2f}")
    c.drawString(x, y - 30, f"Out-of-pocket Cost: {out_of_pocket:.2f}")
    y -= 60
    c.drawString(x, y, "Patient Signature: __________________________")
    c.save()
    buffer.seek(0)
    st.download_button("Download PDF", buffer, file_name="summary.pdf")
    if st.button("Previous"):
        prev_page()
