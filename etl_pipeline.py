import pdfplumber
import pandas as pd
import json
import os

def parse_spending_trends(pdf_path):
    """
    Extracts the FY24, FY25, and FY26 tabular financial data from the Spending Trends PDF.
    """
    print(f"Processing Financial Data: {pdf_path}")
    extracted_data = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Extract tables using pdfplumber's built-in table finder
            tables = page.extract_tables()
            for table in tables:
                # Clean up empty rows/columns
                df = pd.DataFrame(table[1:], columns=table[0])
                df = df.dropna(how='all')
                extracted_data.append(df)
                
    if extracted_data:
        # Combine all found financial tables
        financial_df = pd.concat(extracted_data, ignore_index=True)
        # Clean currency strings to floats for calculation
        cols_to_clean = financial_df.columns.drop(financial_df.columns[0]) # Skip 'FYXX' column
        for col in cols_to_clean:
            financial_df[col] = financial_df[col].replace('[\$,]', '', regex=True).astype(float, errors='ignore')
            
        financial_df.to_csv("Cleaned_Spending_Trends.csv", index=False)
        print("Successfully exported Cleaned_Spending_Trends.csv")
        return financial_df
    return None

def parse_employee_roster(pdf_path):
    """
    Extracts the employee roster, normalizing job families and departments.
    """
    print(f"Processing Employee Roster: {pdf_path}")
    
    with pdfplumber.open(pdf_path) as pdf:
        # The roster is essentially a giant table, we'll extract it as such
        all_rows = []
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                all_rows.extend(table)
                
    if all_rows:
        # First row is headers
        headers = [str(h).replace('\n', ' ') for h in all_rows[0]]
        df = pd.DataFrame(all_rows[1:], columns=headers)
        
        # Clean up line breaks in cells caused by PDF wrapping
        df = df.replace('\n', ' ', regex=True)
        
        df.to_csv("Cleaned_Employee_Roster.csv", index=False)
        print("Successfully exported Cleaned_Employee_Roster.csv")
        return df
    return None

def parse_financial_reserves(pdf_path):
    """
    Extracts the unallocated and recurring reserve balances from the Muncie-Henry Co Financials PDF.
    """
    print(f"Processing Financial Reserves: {pdf_path}")
    
    extracted_data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                df = pd.DataFrame(table[1:], columns=table[0])
                df = df.dropna(how='all')
                extracted_data.append(df)
                
    if extracted_data:
        financial_df = pd.concat(extracted_data, ignore_index=True)
        # Clean currency formats for financial calculations
        for col in financial_df.columns:
            if financial_df[col].dtype == 'object':
                financial_df[col] = financial_df[col].replace('[\$,\(\)]', '', regex=True)
                
        financial_df.to_csv("Cleaned_Financial_Reserves.csv", index=False)
        print("Successfully exported Cleaned_Financial_Reserves.csv")
        return financial_df
    return None

def main():
    # Define file paths based on your working directory
    base_dir = "/Users/epeck7/Documents/01 - Projects/Workload Measure Analysis"
    
    spending_pdf = os.path.join(base_dir, "Spending trends.pdf")
    roster_pdf = os.path.join(base_dir, "Organization_Members_(with_Photo).xlsx.pdf")
    reserves_pdf = os.path.join(base_dir, "Muncie-Henry Co Financials P08 Feb 2026.pdf")
    
    # Run Parsers
    if os.path.exists(spending_pdf):
        parse_spending_trends(spending_pdf)
    else:
        print(f"File not found: {spending_pdf}")
        
    if os.path.exists(roster_pdf):
        parse_employee_roster(roster_pdf)
    else:
        print(f"File not found: {roster_pdf}")
        
    if os.path.exists(reserves_pdf):
        parse_financial_reserves(reserves_pdf)
    else:
        print(f"File not found: {reserves_pdf}")

if __name__ == "__main__":
    main()