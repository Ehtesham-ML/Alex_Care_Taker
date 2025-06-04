import os
import base64
import streamlit as st
import pandas as pd

# Directories
INPUT_DIR = "input"
OUTPUT_DIR = "output"
OUTPUT_ANALYZED_RESULTS = "Analyzed Results"
os.makedirs(OUTPUT_ANALYZED_RESULTS, exist_ok=True)

# Create directories if they don't exist
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_ANALYZED_ATTANDACE = "Analyzed Results/Attendance_comparison"
os.makedirs(OUTPUT_ANALYZED_ATTANDACE, exist_ok=True)

OUTPUT_ANALYZED_BRANCH = "Analyzed Results/Branch_Names"
os.makedirs(OUTPUT_ANALYZED_BRANCH, exist_ok=True)

OUTPUT_ANALYZED_FILTER = "Analyzed Results/Filter_Cases_with_Branch_names"
os.makedirs(OUTPUT_ANALYZED_FILTER, exist_ok=True)

OUTPUT_ANALYZED_MISSING = "Analyzed Results/Missing_cases"
os.makedirs(OUTPUT_ANALYZED_MISSING, exist_ok=True)

OUTPUT_ANALYZED_LESS_PAID = "Analyzed Results/Less_Paid"
os.makedirs(OUTPUT_ANALYZED_LESS_PAID, exist_ok=True)

st.title("Care Taker Data Analysis")


# Define tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "View and Upload Data", "Absence No", "Branches", "Cases Against Branches", 
    "Missing Cases", "Less Paid"
])

with tab1:
    

    # File uploader
    uploaded_files = st.file_uploader("Upload your PDF files", type="pdf", accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = os.path.join(INPUT_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        st.success(f"Uploaded {len(uploaded_files)} PDF(s) to the **input** directory!")

    with st.expander(":open_file_folder: View Uploaded PDFs"):
        pdf_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".pdf")]
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

    if st.button("Process PDFs"):
        with st.spinner("Processing PDFs..."):
            os.system("python pdf_converter.py")
        # st.success("PDFs have been processed! Check the **output** directory.")

    with st.expander(":bar_chart: View Converted Excel Files"):
        excel_files = [f for f in os.listdir(OUTPUT_DIR) if f.lower().endswith(".xlsx")]
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
           
    if st.button("Delete Previous Data", type="primary"):
        import shutil

        # List of directories to clear
        dirs_to_clear = [INPUT_DIR, OUTPUT_DIR, OUTPUT_ANALYZED_RESULTS]

        try:
            for directory in dirs_to_clear:
                if os.path.exists(directory):
                    shutil.rmtree(directory)
                    os.makedirs(directory)  # Recreate the folder after deletion

            # Recreate subdirectories under Analyzed Results
            os.makedirs(OUTPUT_ANALYZED_ATTANDACE, exist_ok=True)
            os.makedirs(OUTPUT_ANALYZED_BRANCH, exist_ok=True)
            os.makedirs(OUTPUT_ANALYZED_FILTER, exist_ok=True)
            os.makedirs(OUTPUT_ANALYZED_MISSING, exist_ok=True)
            os.makedirs(OUTPUT_ANALYZED_LESS_PAID, exist_ok=True)

            st.success("All previous data and directories have been deleted.")
        except Exception as e:
            st.error(f"Error while deleting data: {e}")    
        
with tab2:
    
    st.header("Attendance Comparison")
    if not excel_files:
        st.warning("No Excel files found in the output directory.")
    else:
        selected_file = st.selectbox("Select an Excel file for comparison", excel_files)
        if selected_file:
            
            if st.button("Compare Attandance"):
                # Define paths
                PROVIDER_TABLE_PATH = os.path.join(OUTPUT_DIR, selected_file)
                ATTENDANCE_PATH = "Attandance_data/attendance_report_excel_03_14_2025_1120040509.xlsx"
                
                # Determine output filename
                provider_name = os.path.splitext(selected_file)[0]
                output_file = f"attendance_comparison_result_{provider_name}.xlsx"
                OUTPUT_ANALYSIS_PATH = os.path.join(OUTPUT_ANALYZED_ATTANDACE, output_file)
                try:
                    # Load Excel files
                    extracted_df = pd.read_excel(PROVIDER_TABLE_PATH, dtype={'Suffix': str})
                    attendance_df = pd.read_excel(ATTENDANCE_PATH)
                    # Generate case number
                    extracted_df['Case number'] = extracted_df['Client'].astype(str) + '/' + extracted_df['Suffix']
                    # Prepare DataFrames
                    attendance_grouped = attendance_df.groupby('Case number', as_index=False)['Attendance'].sum()
                    attendance_grouped.rename(columns={'Attendance': 'Attendance_data'}, inplace=True)
                    extracted_df = extracted_df[['Case number', 'Days Attended']]
                    extracted_df.rename(columns={'Days Attended': 'Extracted_data'}, inplace=True)
                    # Merge and calculate differences
                    merged_df = pd.merge(attendance_grouped, extracted_df, on='Case number', how='inner')
                    merged_df['Attendance_data'] = pd.to_numeric(merged_df['Attendance_data'], errors='coerce')
                    merged_df['Extracted_data'] = pd.to_numeric(merged_df['Extracted_data'], errors='coerce')
                    merged_df['Difference'] = merged_df['Attendance_data'] - merged_df['Extracted_data']
                    # Filter mismatches
                    mismatch_df = merged_df[merged_df['Difference'] != 0]
                    # If file exists, load and merge with existing data
                    if os.path.exists(OUTPUT_ANALYSIS_PATH):
                        existing_df = pd.read_excel(OUTPUT_ANALYSIS_PATH)
                        mismatch_df = pd.concat([existing_df, mismatch_df], ignore_index=True).drop_duplicates(subset=['Case number'])
                    # Save merged result
                    mismatch_df.to_excel(OUTPUT_ANALYSIS_PATH, index=False)
                    st.success(f"Mismatched entries found: {len(mismatch_df)}")
                    # st.info(f"File saved as: {OUTPUT_ANALYSIS_PATH}")
                    st.markdown("### Mismatch Result Preview")
                    st.dataframe(mismatch_df)
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                               
with tab3:
    st.header("Identify Unique Branch Names")
    if not excel_files:
        st.warning("No Excel files found in the output directory.")
    else:
        selected_file = st.selectbox("Select an Excel file for Branch Names", excel_files)
        if selected_file:
            if st.button("Check Unique Branches"):
                # Define paths
                PROVIDER_TABLE_PATH = os.path.join(OUTPUT_DIR, selected_file)
                ATTENDANCE_PATH = "Attandance_data/attendance_report_excel_03_14_2025_1120040509.xlsx"

                # Determine output filename
                provider_name = os.path.splitext(selected_file)[0]
                output_file = f"Branch_Names_{provider_name}.xlsx"
                OUTPUT_ANALYSIS_PATH = os.path.join(OUTPUT_ANALYZED_BRANCH, output_file)
                try:
                    # Load Excel files
                    extracted_df = pd.read_excel(PROVIDER_TABLE_PATH, dtype={'Suffix': str})
                    attendance_df = pd.read_excel(ATTENDANCE_PATH)
                    # Generate case number
                    extracted_df['Case number'] = extracted_df['Client'].astype(str) + '/' + extracted_df['Suffix']
                    attendance_df['Case number'] = attendance_df['Case number'].astype(str)
                    attendance_df = attendance_df.set_index('Case number')
                    # Collect branches corresponding to the 'Case number'
                    branches = []
                    for case_number in extracted_df['Case number']:
                        if case_number in attendance_df.index:
                            branch_value = attendance_df.loc[case_number, 'Branch']
                            if isinstance(branch_value, pd.Series):
                                for item in branch_value:
                                    if pd.notna(item):
                                        branches.append(item)
                            else:
                                if pd.notna(branch_value):
                                    branches.append(branch_value)
                    # Remove duplicates, keep only unique branches
                    unique_branches = list(set(branches))
                    final_df = pd.DataFrame({'Branch': unique_branches})
                    # If file exists, load and merge with existing data
                    if os.path.exists(OUTPUT_ANALYSIS_PATH):
                        existing_df = pd.read_excel(OUTPUT_ANALYSIS_PATH)
                        final_df = pd.concat([existing_df, final_df], ignore_index=True).drop_duplicates(subset=['Branch'])
                    # Save merged result
                    final_df.to_excel(OUTPUT_ANALYSIS_PATH, index=False)
                    st.success(f"Unique Branches Found: {len(final_df)}")
                    # st.info(f"File saved as: {OUTPUT_ANALYSIS_PATH}")
                    st.markdown("### Unique Branches Preview")
                    st.dataframe(final_df)
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                
with tab4:
    
    st.header("Filter Attandance File by Target Branches")
    # Define constants
    OUTPUT_DIR = "Analyzed Results/Branch_Names"
    ATTENDANCE_PATH = "Attandance_data/attendance_report_excel_03_14_2025_1120040509.xlsx"

    # Find all Excel files for branch selection
    excel_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".xlsx")]
    if not excel_files:
        st.warning("No Excel files found in the output directory.")
    else:
        selected_file = st.selectbox("Select a file with Target Branch Names", excel_files)
        if selected_file:
            try:
                if st.button("Check All Case Number against Branches in Attandance File"):
                    # Step 1: Load the attendance file
                    attendance_df = pd.read_excel(ATTENDANCE_PATH)
                    # Step 2: Load target branch names
                    target_branch_path = os.path.join(OUTPUT_DIR, selected_file)
                    target_branches_df = pd.read_excel(target_branch_path)
                    target_branches = target_branches_df['Branch'].astype(str).str.strip()
                    # Step 3: Drop rows with missing Branch or Case Number
                    attendance_df = attendance_df.dropna(subset=['Branch', 'Case number'])
                    # Step 4: Convert 'Branch' and 'Case number' to string and strip whitespace
                    attendance_df['Branch'] = attendance_df['Branch'].astype(str).str.strip()
                    attendance_df['Case number'] = attendance_df['Case number'].astype(str).str.strip()
                    # Display branch selection (keeping your existing UI)
                    branch_list = sorted(target_branches.unique())
                    selected_branches = st.multiselect("Select Target Branch(es)", branch_list, default=branch_list)
                    if selected_branches:
                        # Step 5: Filter rows with branches in the target list
                        filtered_df = attendance_df[attendance_df['Branch'].isin(selected_branches)]
                        # Step 6: Extract only 'Case number' and 'Branch' columns
                        output_df = filtered_df[['Case number', 'Branch']].reset_index(drop=True)
                        # Step 7: Drop duplicate 'Case number' rows
                        output_df = output_df.drop_duplicates(subset=['Case number'])
                        # Ensure consistent data types for display
                        output_df['Case number'] = output_df['Case number'].astype(str)
                        output_df['Branch'] = output_df['Branch'].astype(str)
                        # Step 8: Save to Excel file
                        provider_name = os.path.splitext(selected_file)[0]
                        output_file = f"filtered_case_numbers_by_branch_{provider_name}.xlsx"
                        OUTPUT_ANALYSIS_PATH = os.path.join(OUTPUT_ANALYZED_FILTER, output_file)
                        # Handle existing file (append and remove duplicates)
                        if os.path.exists(OUTPUT_ANALYSIS_PATH):
                            existing_df = pd.read_excel(OUTPUT_ANALYSIS_PATH)
                            # Ensure consistent data types before concatenation
                            existing_df['Case number'] = existing_df['Case number'].astype(str)
                            existing_df['Branch'] = existing_df['Branch'].astype(str)
                            output_df = pd.concat([existing_df, output_df], ignore_index=True)
                            output_df = output_df.drop_duplicates(subset=['Case number'])
                        # Save the final result
                        output_df.to_excel(OUTPUT_ANALYSIS_PATH, index=False)
                        # Display results
                        # st.success(f"Filtered data with unique 'Case number' saved to '{OUTPUT_ANALYSIS_PATH}'")
                        st.success(f"Total unique case numbers: {len(output_df)}")
                        st.markdown("### Preview of Filtered Case Numbers")
                        st.dataframe(output_df)
                    else:
                        st.warning("Please select at least one branch to filter.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
                
with tab5:
    
    st.header("Find Missing Case Numbers Between Filtered and Extracted Data")
    # Define directories
    OUTPUT_DIR = "output"
    FILTERED_CASES_PATH = "Analyzed Results/Filter_Cases_with_Branch_names"
    # OUTPUT_ANALYZED_RESULTS = "Analyzed Results/Missing_cases"
    # os.makedirs(OUTPUT_ANALYZED_RESULTS, exist_ok=True)
    # Get file lists
    excel_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".xlsx")]
    filtered_files = [f for f in os.listdir(FILTERED_CASES_PATH) if "filtered_case_numbers_by_branch" in f and f.endswith(".xlsx")]
    # File selection dropdowns
    selected_extracted = st.selectbox("Select Extracted Provider Table File", excel_files) if excel_files else None
    selected_filtered = st.selectbox("Select Filtered Case Numbers File", filtered_files) if filtered_files else None
    # Proceed button
    if selected_extracted and selected_filtered:
        if st.button("Find Missing Case Numbers"):
            try:
                # Load filtered case numbers
                filtered_path = os.path.join(FILTERED_CASES_PATH, selected_filtered)
                filtered_df = pd.read_excel(filtered_path)
                filtered_df.drop_duplicates(inplace=True)
                # Load extracted provider data
                extracted_path = os.path.join(OUTPUT_DIR, selected_extracted)
                extracted_df = pd.read_excel(extracted_path, dtype={'Suffix': str})
                extracted_df.drop_duplicates(inplace=True)
                # Generate case numbers
                extracted_df['Case number'] = extracted_df['Client'].astype(str) + '/' + extracted_df['Suffix']
                # Compare case numbers
                filtered_case_numbers = set(filtered_df['Case number'].astype(str).str.strip())
                extracted_case_numbers = set(extracted_df['Case number'].astype(str).str.strip())
                missing_case_numbers = filtered_case_numbers - extracted_case_numbers
                # Save results
                missing_df = pd.DataFrame(list(missing_case_numbers), columns=['Missing Case number'])
                missing_df.drop_duplicates(inplace=True)
                provider_name = os.path.splitext(selected_extracted)[0]
                output_file = f"missing_case_numbers_{provider_name}.xlsx"
                output_path = os.path.join(OUTPUT_ANALYZED_MISSING, output_file)
                missing_df.to_excel(output_path, index=False)
                # Show result
                st.success(f"Missing case numbers identified: {len(missing_df)}")
                # st.info(f"File saved as: {output_path}")
                st.markdown("### Preview of Missing Case Numbers")
                st.dataframe(missing_df)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please select both files to proceed.")

with tab6:
    
    st.header("Find Overpaid Cases Based on Attendance vs Gross Pay")
    # Define paths
    OUTPUT_DIR = "output"
    ATTENDANCE_PATH = "Attandance_data/attendance_report_excel_03_14_2025_1120040509.xlsx"
    
    # List available extracted files
    excel_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".xlsx")]
    # Dropdown for extracted file
    selected_file = st.selectbox("Select Extracted Provider Table File", options=excel_files, key="extracted_file_selectbox") if excel_files else None
    
    if not excel_files:
        st.warning("No extracted Excel files found in the 'output' directory.")
    elif selected_file:
        if st.button("Find Overpaid Case Numbers"):
            try:
                # Load selected extracted file
                extracted_path = os.path.join(OUTPUT_DIR, selected_file)
                extracted_df = pd.read_excel(extracted_path, dtype={'Suffix': str})
                # Load attendance data
                attendance_df = pd.read_excel(ATTENDANCE_PATH)
                # Create 'Case number'
                extracted_df['Case number'] = extracted_df['Client'].astype(str) + '/' + extracted_df['Suffix']
                # Convert currency fields to float
                extracted_df['Rate'] = extracted_df['Rate'].replace(r'[\$,]', '', regex=True).astype(float)
                extracted_df['Gross Pay'] = extracted_df['Gross Pay'].replace(r'[\$,]', '', regex=True).astype(float)
                # Sum attendance values by case number
                attendance_df = attendance_df.groupby('Case number', as_index=False)['Attendance'].sum()
                # Merge data
                merged_df = pd.merge(
                    attendance_df[['Case number', 'Attendance']],
                    extracted_df[['Case number', 'Rate', 'Gross Pay']],
                    on='Case number',
                    how='inner'
                )
                # Ensure numeric conversion
                merged_df['Attendance'] = merged_df['Attendance'].astype(float)
                merged_df['Calculated Pay'] = merged_df['Attendance'] * merged_df['Rate']
                # Identify overpaid cases
                overpaid_df = merged_df[merged_df['Calculated Pay'] > merged_df['Gross Pay']].copy()
                overpaid_df['Amount Difference'] = (overpaid_df['Calculated Pay'] - overpaid_df['Gross Pay']).round(2)
                # Final DataFrame
                final_df = overpaid_df[['Case number', 'Amount Difference']]
                # Save to Excel
                provider_name = os.path.splitext(selected_file)[0]
                output_file = f"attendance_overpaid_cases_filtered_{provider_name}.xlsx"
                output_path = os.path.join(OUTPUT_ANALYZED_LESS_PAID, output_file)
                final_df.to_excel(output_path, index=False)
                # Show results
                st.success(f"Overpaid cases identified: {len(final_df)}")
                # st.info(f"File saved as: {output_path}")
                st.markdown("### Preview of Overpaid Case Differences")
                st.dataframe(final_df)
            except Exception as e:
                st.error(f"An error occurred: {e}")





