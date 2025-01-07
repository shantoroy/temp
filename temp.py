from openpyxl import load_workbook
import streamlit as st

# Path to your Excel file
file_path = "Activities_Demodata_template.xlsx"

# Load the workbook and target the "Current" worksheet
workbook = load_workbook(file_path, data_only=True)
sheet = workbook["Current"]

# Extract column headers from the 5th row
headers = [cell.value for cell in sheet[5]]  # Column names are in the 5th row

# Extract data starting from the 6th row
data_entries = []
for row in sheet.iter_rows(min_row=6, values_only=False):  # Include formatting for colors
    row_data = {}
    for idx, cell in enumerate(row):
        column_name = headers[idx]
        cell_value = cell.value
        cell_color = cell.fill.start_color.index if cell.fill.fill_type else None
        row_data[column_name] = (cell_value, cell_color)
    data_entries.append(row_data)

# Display headers and first few data entries for inspection
st.write("Headers:", headers)
st.write("First 5 rows of data entries:")
for entry in data_entries[:5]:
    st.table(entry)
