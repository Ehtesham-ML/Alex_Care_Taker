import os
import base64
import streamlit as st
import pandas as pd
import shutil

# Function to clear all previous data
def clear_all_data():
    """Clear all data from previous sessions"""
    try:
        # List of directories to clear
        dirs_to_clear = [
            "input",
            "output", 
            "Analyzed Results"
        ]

        for directory in dirs_to_clear:
            if os.path.exists(directory):
                shutil.rmtree(directory)

        # Remove temp attendance file if exists
        if os.path.exists("temp_attendance.xlsx"):
            os.remove("temp_attendance.xlsx")
            
        return True
    except Exception as e:
        st.error(f"Error clearing previous data: {e}")
        return False

# Function to initialize directories
def initialize_directories():
    """Create all necessary directories"""
    # Main directories
    INPUT_DIR = "input"
    OUTPUT_DIR = "output"
    OUTPUT_ANALYZED_RESULTS = "Analyzed Results"
    
    # Create main directories
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_ANALYZED_RESULTS, exist_ok=True)

    # Create subdirectories
    OUTPUT_ANALYZED_ATTANDACE = "Analyzed Results/Attendance_comparison"
    OUTPUT_ANALYZED_BRANCH = "Analyzed Results/Branch_Names"
    OUTPUT_ANALYZED_FILTER = "Analyzed Results/Filter_Cases_with_Branch_names"
    OUTPUT_ANALYZED_MISSING = "Analyzed Results/Missing_cases"
    OUTPUT_ANALYZED_LESS_PAID = "Analyzed Results/Less_Paid"
    
    os.makedirs(OUTPUT_ANALYZED_ATTANDACE, exist_ok=True)
    os.makedirs(OUTPUT_ANALYZED_BRANCH, exist_ok=True)
    os.makedirs(OUTPUT_ANALYZED_FILTER, exist_ok=True)
    os.makedirs(OUTPUT_ANALYZED_MISSING, exist_ok=True)
    os.makedirs(OUTPUT_ANALYZED_LESS_PAID, exist_ok=True)
    
    return {
        'INPUT_DIR': INPUT_DIR,
        'OUTPUT_DIR': OUTPUT_DIR,
        'OUTPUT_ANALYZED_RESULTS': OUTPUT_ANALYZED_RESULTS,
        'OUTPUT_ANALYZED_ATTANDACE': OUTPUT_ANALYZED_ATTANDACE,
        'OUTPUT_ANALYZED_BRANCH': OUTPUT_ANALYZED_BRANCH,
        'OUTPUT_ANALYZED_FILTER': OUTPUT_ANALYZED_FILTER,
        'OUTPUT_ANALYZED_MISSING': OUTPUT_ANALYZED_MISSING,
        'OUTPUT_ANALYZED_LESS_PAID': OUTPUT_ANALYZED_LESS_PAID
    }

# Initialize session state for new session detection
if 'session_initialized' not in st.session_state:
    st.session_state.session_initialized = False

# Check if this is a new session
if not st.session_state.session_initialized:
    # # Clear all previous data at the start of new session
    # with st.spinner("🧹 Initializing new session... Clearing previous data..."):
    clear_all_data()
        # st.success("✅ Previous session data cleared successfully!")
        
    # Mark session as initialized
    st.session_state.session_initialized = True
    
    # # Show session info
    # st.info("🔄 **New Session Started** - All previous data has been cleared.")

# Initialize directories
dirs = initialize_directories()
INPUT_DIR = dirs['INPUT_DIR']
OUTPUT_DIR = dirs['OUTPUT_DIR']
OUTPUT_ANALYZED_RESULTS = dirs['OUTPUT_ANALYZED_RESULTS']
OUTPUT_ANALYZED_ATTANDACE = dirs['OUTPUT_ANALYZED_ATTANDACE']
OUTPUT_ANALYZED_BRANCH = dirs['OUTPUT_ANALYZED_BRANCH']
OUTPUT_ANALYZED_FILTER = dirs['OUTPUT_ANALYZED_FILTER']
OUTPUT_ANALYZED_MISSING = dirs['OUTPUT_ANALYZED_MISSING']
OUTPUT_ANALYZED_LESS_PAID = dirs['OUTPUT_ANALYZED_LESS_PAID']

st.title("Care Taker Data Analysis")

# # Session Status Info
# with st.expander("📊 Session Information"):
#     st.write(f"**Session Status:** Active")
#     st.write(f"**Data Storage:** Current session only")
#     st.write(f"**Auto-cleanup:** Enabled")

# File Upload Section
st.header("📁 File Upload Section")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Upload PDF Files")
    # File uploader for PDFs
    uploaded_files = st.file_uploader("Upload your PDF files", type="pdf", accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = os.path.join(INPUT_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        st.success(f"Uploaded {len(uploaded_files)} PDF(s) to the **input** directory!")

with col2:
    st.subheader("Upload Attendance Data")
    # File uploader for attendance data
    attendance_file = st.file_uploader("Upload Attendance Excel File", type="xlsx", key="attendance_upload")
    attendance_file_path = None
    if attendance_file:
        attendance_file_path = os.path.join("temp_attendance.xlsx")
        with open(attendance_file_path, "wb") as f:
            f.write(attendance_file.getbuffer())
        st.success("Attendance file uploaded successfully!")

# View Uploaded Files Section
with st.expander("📄 View Uploaded PDFs"):
    pdf_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".pdf")] if os.path.exists(INPUT_DIR) else []
    if pdf_files:
        selected_pdf = st.selectbox("Select a PDF to view", pdf_files)
        if selected_pdf:
            pdf_path = os.path.join(INPUT_DIR, selected_pdf)
            with open(pdf_path, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode("utf-8")
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="900" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        st.info("No PDF files found.")

# Process PDFs Section
st.header("🔄 Process PDFs")
if st.button("Process PDFs", type="primary"):
    with st.spinner("Processing PDFs..."):
        os.system("python pdf_converter.py")
    st.success("PDFs have been processed!")

# View Converted Excel Files
with st.expander("📊 View Converted Excel Files"):
    excel_files = [f for f in os.listdir(OUTPUT_DIR) if f.lower().endswith(".xlsx")] if os.path.exists(OUTPUT_DIR) else []
    if excel_files:
        selected_excel = st.selectbox("Select a converted Excel file to view", excel_files)
        if selected_excel:
            file_path = os.path.join(OUTPUT_DIR, selected_excel)
            try:
                df = pd.read_excel(file_path)
                st.dataframe(df)
            except Exception as e:
                st.error(f"Could not read the Excel file: {e}")
    else:
        st.info("No Excel files found in the output directory.")

# Main Compare Data Button
st.header("🔍 Data Analysis")
if st.button("Compare Data", type="primary", use_container_width=True):
    if not attendance_file_path or not os.path.exists(attendance_file_path):
        st.error("Please upload the attendance file first!")
    elif not excel_files:
        st.error("No processed Excel files found. Please process PDFs first!")
    else:
        st.success("Starting comprehensive data analysis...")
        
        # Load attendance data once
        try:
            attendance_df = pd.read_excel(attendance_file_path)
            st.info(f"✅ Loaded attendance data with {len(attendance_df)} records")
        except Exception as e:
            st.error(f"Error loading attendance file: {e}")
            st.stop()
        
        # Process each Excel file
        for selected_file in excel_files:
            st.subheader(f"📋 Analysis Results for: {selected_file}")
            
            try:
                # Load the provider table
                PROVIDER_TABLE_PATH = os.path.join(OUTPUT_DIR, selected_file)
                extracted_df = pd.read_excel(PROVIDER_TABLE_PATH, dtype={'Suffix': str})
                provider_name = os.path.splitext(selected_file)[0]
                
                st.write(f"Processing {len(extracted_df)} records from {selected_file}")
                
                # Generate case numbers
                extracted_df['Case number'] = extracted_df['Client'].astype(str) + '/' + extracted_df['Suffix']
                
                # === 1. ATTENDANCE COMPARISON ===
                st.write("**1. 📊 Attendance Comparison Analysis**")
                try:
                    # Prepare attendance data
                    attendance_grouped = attendance_df.groupby('Case number', as_index=False)['Attendance'].sum()
                    attendance_grouped.rename(columns={'Attendance': 'Attendance_data'}, inplace=True)
                    
                    # Prepare extracted data
                    extracted_comparison = extracted_df[['Case number', 'Days Attended']].copy()
                    extracted_comparison.rename(columns={'Days Attended': 'Extracted_data'}, inplace=True)
                    
                    # Merge and calculate differences
                    merged_df = pd.merge(attendance_grouped, extracted_comparison, on='Case number', how='inner')
                    merged_df['Attendance_data'] = pd.to_numeric(merged_df['Attendance_data'], errors='coerce')
                    merged_df['Extracted_data'] = pd.to_numeric(merged_df['Extracted_data'], errors='coerce')
                    merged_df['Difference'] = merged_df['Attendance_data'] - merged_df['Extracted_data']
                    
                    # Filter mismatches
                    mismatch_df = merged_df[merged_df['Difference'] != 0]
                    
                    # Save results
                    output_file = f"attendance_comparison_result_{provider_name}.xlsx"
                    OUTPUT_ANALYSIS_PATH = os.path.join(OUTPUT_ANALYZED_ATTANDACE, output_file)
                    mismatch_df.to_excel(OUTPUT_ANALYSIS_PATH, index=False)
                    
                    st.write(f"   ✅ Attendance mismatches found: **{len(mismatch_df)}**")
                    if len(mismatch_df) > 0:
                        st.dataframe(mismatch_df.head(10), use_container_width=True)
                        
                except Exception as e:
                    st.error(f"   ❌ Attendance comparison error: {e}")
                    
                    
                    
                    
                    
                    
                    
                
# === 2. BRANCH NAMES ANALYSIS ===
                st.write("**2. 🏢 Branch Names Analysis**")
                try:
                    # Set up attendance data for branch lookup
                    attendance_lookup = attendance_df.set_index('Case number')
                    
                    # Collect branches
                    branches = []
                    for case_number in extracted_df['Case number']:
                        if case_number in attendance_lookup.index:
                            branch_value = attendance_lookup.loc[case_number, 'Branch']
                            if isinstance(branch_value, pd.Series):
                                for item in branch_value:
                                    if pd.notna(item):
                                        # Convert to string to handle mixed data types
                                        branches.append(str(item))
                            else:
                                if pd.notna(branch_value):
                                    # Convert to string to handle mixed data types
                                    branches.append(str(branch_value))
                    
                    # Get unique branches - all are already strings from above conversion
                    unique_branches = list(set(branches))
                    branches_df = pd.DataFrame({'Branch': unique_branches})
                    
                    # Save results
                    output_file = f"Branch_Names_{provider_name}.xlsx"
                    OUTPUT_ANALYSIS_PATH = os.path.join(OUTPUT_ANALYZED_BRANCH, output_file)
                    branches_df.to_excel(OUTPUT_ANALYSIS_PATH, index=False)
                    
                    st.write(f"   ✅ Unique branches found: **{len(branches_df)}**")
                    if len(branches_df) > 0:
                        # Display first 10 branches - no need to convert again since they're already strings
                        st.write("   Branches:", ", ".join(unique_branches[:10]))
                        
                except Exception as e:
                    st.error(f"   ❌ Branch analysis error: {e}")
                    
                    
                    
                    
                    
                
                # === 3. FILTERED CASES ANALYSIS ===
                st.write("**3. 🔍 Filtered Cases Analysis**")
                try:
                    # Use the unique branches found above
                    if 'unique_branches' in locals() and unique_branches:
                        # Filter attendance data by branches
                        attendance_clean = attendance_df.dropna(subset=['Branch', 'Case number']).copy()
                        attendance_clean['Branch'] = attendance_clean['Branch'].astype(str).str.strip()
                        attendance_clean['Case number'] = attendance_clean['Case number'].astype(str).str.strip()
                        
                        # Filter by branches
                        filtered_df = attendance_clean[attendance_clean['Branch'].isin(unique_branches)]
                        output_df = filtered_df[['Case number', 'Branch']].drop_duplicates(subset=['Case number'])
                        
                        # Save results
                        output_file = f"filtered_case_numbers_by_branch_{provider_name}.xlsx"
                        OUTPUT_ANALYSIS_PATH = os.path.join(OUTPUT_ANALYZED_FILTER, output_file)
                        output_df.to_excel(OUTPUT_ANALYSIS_PATH, index=False)
                        
                        st.write(f"   ✅ Filtered unique case numbers: **{len(output_df)}**")
                        
                        # === 4. MISSING CASES ANALYSIS ===
                        st.write("**4. ❓ Missing Cases Analysis**")
                        try:
                            # Compare case numbers
                            filtered_case_numbers = set(output_df['Case number'].astype(str).str.strip())
                            extracted_case_numbers = set(extracted_df['Case number'].astype(str).str.strip())
                            missing_case_numbers = filtered_case_numbers - extracted_case_numbers
                            
                            # Save missing cases
                            missing_df = pd.DataFrame(list(missing_case_numbers), columns=['Missing Case number'])
                            output_file = f"missing_case_numbers_{provider_name}.xlsx"
                            output_path = os.path.join(OUTPUT_ANALYZED_MISSING, output_file)
                            missing_df.to_excel(output_path, index=False)
                            
                            st.write(f"   ✅ Missing case numbers: **{len(missing_df)}**")
                            if len(missing_df) > 0:
                                st.dataframe(missing_df.head(10), use_container_width=True)
                                
                        except Exception as e:
                            st.error(f"   ❌ Missing cases analysis error: {e}")
                    
                except Exception as e:
                    st.error(f"   ❌ Filtered cases analysis error: {e}")
                
                # === 5. OVERPAID CASES ANALYSIS ===
                st.write("**5. 💰 Overpaid Cases Analysis**")
                try:
                    # Prepare data for payment analysis
                    extracted_payment = extracted_df.copy()
                    extracted_payment['Rate'] = extracted_payment['Rate'].replace(r'[\$,]', '', regex=True).astype(float)
                    extracted_payment['Gross Pay'] = extracted_payment['Gross Pay'].replace(r'[\$,]', '', regex=True).astype(float)
                    
                    # Sum attendance by case number
                    attendance_sum = attendance_df.groupby('Case number', as_index=False)['Attendance'].sum()
                    
                    # Merge for payment calculation
                    payment_merged = pd.merge(
                        attendance_sum[['Case number', 'Attendance']],
                        extracted_payment[['Case number', 'Rate', 'Gross Pay']],
                        on='Case number',
                        how='inner'
                    )
                    
                    # Calculate expected payment
                    payment_merged['Attendance'] = payment_merged['Attendance'].astype(float)
                    payment_merged['Calculated Pay'] = payment_merged['Attendance'] * payment_merged['Rate']
                    
                    # Find overpaid cases
                    overpaid_df = payment_merged[payment_merged['Calculated Pay'] > payment_merged['Gross Pay']].copy()
                    overpaid_df['Amount Difference'] = (overpaid_df['Calculated Pay'] - overpaid_df['Gross Pay']).round(2)
                    
                    # Save results
                    final_overpaid = overpaid_df[['Case number', 'Amount Difference']]
                    output_file = f"attendance_overpaid_cases_filtered_{provider_name}.xlsx"
                    output_path = os.path.join(OUTPUT_ANALYZED_LESS_PAID, output_file)
                    final_overpaid.to_excel(output_path, index=False)
                    
                    st.write(f"   ✅ Overpaid cases found: **{len(final_overpaid)}**")
                    if len(final_overpaid) > 0:
                        st.dataframe(final_overpaid.head(10), use_container_width=True)
                        
                except Exception as e:
                    st.error(f"   ❌ Overpaid cases analysis error: {e}")
                
                st.divider()
                
            except Exception as e:
                st.error(f"❌ Error processing {selected_file}: {e}")
                continue
        
        st.success("🎉 **All analyses completed successfully!**")
        # st.info("📁 All results have been saved to the 'Analyzed Results' directories.")

# # Data Management Section
# st.header("🗑️ Data Management")

# col1, col2 = st.columns(2)

# with col1:
#     if st.button("🔄 Reset Current Session", type="secondary", use_container_width=True):
#         if clear_all_data():
#             # Reinitialize directories
#             initialize_directories()
#             # Reset session state
#             st.session_state.session_initialized = False
#             st.success("✅ Current session has been reset!")
#             st.info("🔄 Page will refresh to start a clean session.")
#             st.rerun()
#         else:
#             st.error("❌ Failed to reset session data.")

# with col2:
#     if st.button("🗑️ Clear All Data", type="secondary", use_container_width=True):
#         try:
#             if clear_all_data():
#                 initialize_directories()
#                 st.success("✅ All data has been cleared successfully!")
#             else:
#                 st.error("❌ Failed to clear all data.")
#         except Exception as e:
#             st.error(f"❌ Error while clearing data: {e}")

# Footer info
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
     All files are stored temporarily and will be removed when the session ends
    </div>
    """, 
    unsafe_allow_html=True
)