# import streamlit as st
# import pandas as pd
# import os
# import csv

# UPLOAD_FOLDER = "uploads"
# st.set_page_config(page_title="Violence Detection CSV Dashboard", layout="wide")

# st.title("📊 Violence Detection - CSV Analysis")

# # List files in upload folder
# uploaded_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(".csv")]

# if uploaded_files:
#     # Pick the latest uploaded file
#     latest_file = max(
#         [os.path.join(UPLOAD_FOLDER, f) for f in uploaded_files],
#         key=os.path.getctime
#     )
#     st.success(f"✅ Found uploaded CSV: {os.path.basename(latest_file)}")

#     # Try multiple read options
#     read_success = False
#     for sep in [",", ";", "\t", "|"]:
#         if read_success:
#             break
#         try:
#             df = pd.read_csv(
#                 latest_file,
#                 sep=sep,
#                 on_bad_lines="skip",
#                 quoting=csv.QUOTE_MINIMAL,
#                 encoding="utf-8"
#             )
#             read_success = True
#         except Exception:
#             continue

#     if read_success:
#         # Clean up column names
#         df.columns = df.columns.str.strip().str.replace('"', '').str.replace("'", "")
#         st.write("🔍 Cleaned columns:", list(df.columns))
#         st.dataframe(df.head(20))
#     else:
#         st.error("⚠️ Could not read CSV file. Try uploading with UTF-8 encoding and commas/semicolons.")
# else:
#     st.info("📂 No file uploaded yet. Please upload through the HTML interface.")import streamlit as st
import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(
    page_title="CSV Analysis Dashboard", 
    layout="wide", 
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
        margin-bottom: 20px;
    }
    .dataframe {
        width: 100%;
    }
    .stDataFrame {
        border: 1px solid #e6e6e6;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">📊 CSV Analysis Dashboard</h1>', unsafe_allow_html=True)

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    st.error("Upload folder not found. Please upload CSV files first.")
    st.info("Go to the main application and upload CSV files to get started.")
    st.stop()

# Get list of uploaded files with timestamps
uploaded_files = [
    (f, os.path.getmtime(os.path.join(UPLOAD_FOLDER, f)))
    for f in os.listdir(UPLOAD_FOLDER)
    if f.endswith(".csv")
]

if not uploaded_files:
    st.warning("No CSV files uploaded yet. Please upload CSV files through the main interface.")
    st.info("Go to http://localhost:5000 to upload your CSV files")
    st.stop()

# Sort files by upload time (newest first)
uploaded_files.sort(key=lambda x: x[1], reverse=True)
file_names = [f[0] for f in uploaded_files]

# Display file information
st.sidebar.markdown("### 📁 Uploaded Files")
for i, (file_name, timestamp) in enumerate(uploaded_files):
    upload_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    st.sidebar.write(f"{i+1}. {file_name}")
    st.sidebar.caption(f"Uploaded: {upload_time}")

# Select box with the most recent file pre-selected
selected_file = st.sidebar.selectbox("Select a CSV file", file_names)

file_path = os.path.join(UPLOAD_FOLDER, selected_file)

try:
   # Try different encodings and separators
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    separators = [',', ';', '\t', '|']
    
    df = None
    for encoding in encodings:
        for separator in separators:
            try:
                df = pd.read_csv(file_path, encoding=encoding, sep=separator, on_bad_lines='skip')
                st.sidebar.success(f"Successfully read with {encoding} encoding and '{separator}' separator")
                break
            except:
                continue
        if df is not None:
            break
    
    if df is None:
        st.error("Could not read the CSV file with any known encoding or separator.")
        st.stop()
    
    # Display file info
    st.markdown(f'<div class="success-box">✅ CSV loaded successfully: <b>{selected_file}</b></div>', unsafe_allow_html=True)
    
    # File statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Rows", df.shape[0])
    with col2:
        st.metric("Total Columns", df.shape[1])
    with col3:
        st.metric("File Size", f"{os.path.getsize(file_path) / 1024:.2f} KB")
    
    # Display dataframe
    st.subheader("📋 Data Preview")
    st.dataframe(df, use_container_width=True)
    
    # Column information
    st.subheader("📊 Column Information")
    col_info = pd.DataFrame({
        'Column Name': df.columns,
        'Data Type': df.dtypes.values,
        'Non-Null Count': df.count().values,
        'Null Count': df.isnull().sum().values
    })
    st.dataframe(col_info, use_container_width=True)
    
    # Basic statistics for numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        st.subheader("📈 Basic Statistics")
        st.dataframe(df[numeric_cols].describe(), use_container_width=True)
    
      # Data visualization
    st.subheader("📊 Data Visualization")
    if len(numeric_cols) >= 2:
        x_col = st.selectbox("Select X-axis column", numeric_cols)
        y_col = st.selectbox("Select Y-axis column", numeric_cols)
        
        if x_col and y_col:
            st.line_chart(df[[x_col, y_col]].dropna())
    else:
        st.info("Need at least 2 numeric columns for visualization")
    
except Exception as e:
    st.error(f"❌ Error processing file: {str(e)}")
    st.info("Try uploading a different CSV file or check the file format")