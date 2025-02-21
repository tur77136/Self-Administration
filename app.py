#to run this code, type this command in bash: python -m streamlit run .\app.py


import streamlit as st
import pandas as pd
import os

# Set title
st.title("Self-Administration Data Analyzer")

st.markdown("<h3 style='font-size: 30px;'>Summary of the lever presses per box using med associate .txt files, version_1 by Paige Morris 2025</h3>", unsafe_allow_html=True)

# Upload file
uploaded_files = st.file_uploader("Upload TXT file(s)", type=["txt"], accept_multiple_files=True)

# Function to process the file
def parse_file(file):
    lines = file.read().decode("utf-8").strip().split("\n")
    box_data = []
    current_box = None
    b_section_started = False
    row_0_values = {}

    for line in lines:
        line = line.strip()
        if line.startswith("Box:"):
            current_box = line.split(":")[1].strip()
            box_data.append({"Box": current_box, "Active Lever Presses": 0, "Inactive Lever Presses": 0, "Infusions": 0})
            b_section_started = False
        if current_box and line.startswith("B:"):
            b_section_started = True
            continue
        if b_section_started:
            if line.startswith("C:"):
                b_section_started = False
                continue
            parts = line.split()
            if len(parts) > 0:
                try:
                    row_index = int(parts[0][:-1])  # Remove the colon
                    if row_index == 0 and len(parts) >= 6:
                        box_data[-1]["Active Lever Presses"] = sum(float(parts[i]) for i in range(1, 4))
                        row_0_values[current_box] = {"col_4": float(parts[4]), "col_5": float(parts[5])}
                    elif row_index == 5 and len(parts) >= 4:
                        inactive_lever = float(parts[1]) + row_0_values[current_box]["col_4"] + row_0_values[current_box]["col_5"]
                        box_data[-1]["Inactive Lever Presses"] = inactive_lever
                        box_data[-1]["Infusions"] = float(parts[3])
                except (IndexError, ValueError):
                    continue
    return pd.DataFrame(box_data)

# Display results after file upload
if uploaded_files:
    for uploaded_file in uploaded_files:
        st.write(f"### Results for {uploaded_file.name}")
        # Process file and convert to DataFrame
        df = parse_file(uploaded_file)
        # Show DataFrame as a table
        st.dataframe(df)
        
        # Convert the DataFrame to CSV
        csv = df.to_csv(index=False).encode("utf-8")
        
        # Provide a download button
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"{uploaded_file.name.split('.')[0]}_results.csv",
            mime="text/csv",
        )
