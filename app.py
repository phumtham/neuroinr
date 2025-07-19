
import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io

# Load equipment data
equipment_df = pd.read_excel("ค่าอุปกรณ์.xlsx", engine="openpyxl")

# Mapping for healthcare schemes
scheme_map = {
    "A": "Universal healthcare",
    "B": "UCEP",
    "C": "Social Security",
    "D": "Civil Service",
    "E": "Self pay"
}

# Default equipment per operation
operation_defaults = {
    "Diagnostic angiogram": {
        "Angiogram": 1,
        "Contrast media": 4,
        "femoral sheath": 1,
        "Diagnostic catheter": 1,
        "0.038 Wire": 1
    },
    "Cerebral angiogram with simple coiling": {
        "Angiogram": 1,
        "Contrast media": 6,
        "femoral sheath": 1,
        "Softip guider": 1,
        "0.038 Wire": 1,
        "SL10": 1,
        "Synchro": 1,
        "Rhya": 2,
        "Coil": 5
    },
    "Cerebral angiogram with transarterial ONYX embolization": {
        "Angiogram": 1,
        "Contrast media": 6,
        "femoral sheath": 1,
        "Softip guider": 1,
        "0.038 Wire": 1,
        "Apollo": 1,
        "Mirage": 1,
        "Rhya": 1,
        "ONYX": 2
    },
    "Cerebral angiogram with transvenous coiling": {
        "Angiogram": 1,
        "Contrast media": 6,
        "femoral sheath": 2,
        "Diagnostic catheter": 2,
        "Softip guider": 1,
        "0.038 Wire": 1,
        "SL10": 1,
        "Synchro": 1,
        "Rhya": 3,
        "Coil": 10
    },
    "Cerebral angiogram with stent assisted coiling": {
        "Angiogram": 1,
        "Contrast media": 6,
        "femoral sheath": 1,
        "Softip guider": 1,
        "0.038 Wire": 1,
        "SL10": 2,
        "Synchro": 1,
        "Coil": 5,
        "Neuroform ATLAS": 1,
        "Rhya": 3
    }
}

# Equipment limited to 0 or 1
limited_equipment = [
    "destination", "Fubuki", "NeuronMax", "Fargo", "Sofia", "Neuroform atlas",
    "Supass", "Silk Vista", "Copernic balloon", "Hyperglide balloon",
    "exchange wire", "mariner"
]

# Session state initialization
if "page" not in st.session_state:
    st.session_state.page = 0
if "patient_data" not in st.session_state:
    st.session_state.patient_data = {}
if "operation" not in st.session_state:
    st.session_state.operation = ""
if "equipment" not in st.session_state:
    st.session_state.equipment = {}

def next_page():
    st.session_state.page += 1

def prev_page():
    st.session_state.page -= 1

def page1():
    st.title("Patient Information")
    st.session_state.patient_data["ชื่อ"] = st.text_input("ชื่อ")
    st.session_state.patient_data["นามสกุล"] = st.text_input("นามสกุล")
    st.session_state.patient_data["HN"] = st.text_input("HN")
    st.session_state.patient_data["Diagnosis"] = st.text_input("Diagnosis")
    scheme = st.selectbox("Healthcare Scheme", list(scheme_map.keys()))
    st.session_state.patient_data["Scheme"] = scheme
    if st.button("Next"):
        next_page()

def page2():
    st.title("Select Operation")
    operations = list(operation_defaults.keys()) + ["Others"]
    selected = st.selectbox("Operation", operations)
    if selected == "Others":
        custom_op = st.text_input("Enter operation name")
        st.session_state.operation = custom_op
    else:
        st.session_state.operation = selected
    if st.button("Previous"):
        prev_page()
    if st.button("Next"):
        next_page()

def page3():
    st.title("Select Equipment")
    st.subheader(f"Operation: {st.session_state.operation}")
    defaults = operation_defaults.get(st.session_state.operation, {})
    equipment_used = {}
    for _, row in equipment_df.iterrows():
        name = row["equipment"]
        if name in limited_equipment:
            val = st.radio(f"{name}", [0, 1], index=defaults.get(name, 0))
        else:
            val = st.number_input(f"{name}", min_value=0, value=defaults.get(name, 0))
        equipment_used[name] = val
    st.session_state.equipment = equipment_used
    if st.button("Previous"):
        prev_page()
    if st.button("Next"):
        next_page()

def page4():
    st.title("Cost Summary")
    scheme = st.session_state.patient_data["Scheme"]
    total_cost = 0
    total_reimburse = 0
    for name, qty in st.session_state.equipment.items():
        row = equipment_df[equipment_df["equipment"] == name]
        if not row.empty:
            cost = row.iloc[0]["Cost"] * qty
            reimburse = row.iloc[0][scheme_map[scheme]] * qty
            total_cost += cost
            total_reimburse += reimburse
    out_of_pocket = max(total_cost - total_reimburse, 0)
    st.write(f"Total Cost: {total_cost} THB")
    st.write(f"Total Reimbursement: {total_reimburse} THB")
    st.write(f"Out-of-pocket: {out_of_pocket} THB")
    st.session_state.summary = {
        "Total Cost": total_cost,
        "Total Reimbursement": total_reimburse,
        "Out-of-pocket": out_of_pocket
    }
    if st.button("Previous"):
        prev_page()
    if st.button("Next"):
        next_page()

def page5():
    st.title("Generate PDF Summary")
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    x = 50
    y = height - 50
    pd = st.session_state.patient_data
    c.drawString(x + 300, y, f"ชื่อ: {pd['ชื่อ']} {pd['นามสกุล']}")
    c.drawString(x + 300, y - 20, f"HN: {pd['HN']}")
    c.drawString(x + 300, y - 40, f"Diagnosis: {pd['Diagnosis']}")
    c.drawString(x, y - 80, f"Healthcare Scheme: {scheme_map[pd['Scheme']]}")
    c.drawString(x, y - 100, f"Operation: {st.session_state.operation}")
    c.drawString(x, y - 140, "Equipment Used:")
    y_pos = y - 160
    for name, qty in st.session_state.equipment.items():
        if qty > 0:
            c.drawString(x + 20, y_pos, f"{name}: {qty}")
            y_pos -= 20
    summary = st.session_state.summary
    y_pos -= 20
    c.drawString(x, y_pos, f"Total Cost: {summary['Total Cost']} THB")
    y_pos -= 20
    c.drawString(x, y_pos, f"Total Reimbursement: {summary['Total Reimbursement']} THB")
    y_pos -= 20
    c.drawString(x, y_pos, f"Out-of-pocket: {summary['Out-of-pocket']} THB")
    y_pos -= 40
    c.drawString(x, y_pos, "Patient Signature: __________________________")
    c.showPage()
    c.save()
    buffer.seek(0)
    st.download_button("Download PDF", buffer, file_name="summary.pdf")

    if st.button("Previous"):
        prev_page()

# Page routing
pages = [page1, page2, page3, page4, page5]
pages[st.session_state.page]()
