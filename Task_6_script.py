import pandas as pd
import os
import zipfile

# Directory containing CSV files
data_dir = os.path.expanduser("Case_Study_Data_For_Share")

# Initialize lists to hold dataframes
dataframes = []

# Function to extract data from a single CSV file
def extract_data(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            data = [line.strip().split('|') for line in lines]
            df = pd.DataFrame(data[1:], columns=data[0])
            return df
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

# Extract data from all files
for file_name in os.listdir(data_dir):
    if file_name.endswith(".csv"):
        file_path = os.path.join(data_dir, file_name)
        df = extract_data(file_path)
        if df is not None:
            dataframes.append(df)

# Combine all dataframes into one
if not dataframes:
    print("No dataframes were loaded. Please check the file paths and formats.")
else:
    all_data = pd.concat(dataframes, ignore_index=True)

# Data Cleansing Function
def clean_data(df):
    # Remove duplicates
    df.drop_duplicates(inplace=True)

    # Handle missing values
    df['Customer Name'].fillna('Unknown', inplace=True)
    df.dropna(subset=['Order ID', 'Product ID', 'Customer ID', 'Order Date', 'Sales'], inplace=True)

    # Correct data types
    df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], errors='coerce')
    df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce')
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
    df['Discount'] = pd.to_numeric(df['Discount'], errors='coerce')
    df['Profit'] = pd.to_numeric(df['Profit'], errors='coerce')
    df['Postal Code'] = df['Postal Code'].astype(str)

    # Remove records with zero sales and zero quantity
    df = df[~((df['Sales'] == 0) & (df['Quantity'] == 0))]

    # Remove records where the ship date is before the order date
    df = df[~(df['Ship Date'] < df['Order Date'])]

    # Remove records with negative profit values
    df = df[df['Profit'] >= 0]

    # Remove records with invalid postal codes (assuming US postal codes here for simplicity)
    df = df[df['Postal Code'].str.match(r'^\d{5}(-\d{4})?$')]

    return df

# Clean the combined data
cleaned_data = clean_data(all_data)

# Ensure 'Postal Code' column exists
if 'Postal Code' not in cleaned_data.columns:
    print("Error: 'Postal Code' column is missing from the cleaned data.")
else:
    print("Success: 'Postal Code' column found in the cleaned data.")

# Directory to save the Data Marts CSV files
output_dir = "Data_Marts"
os.makedirs(output_dir, exist_ok=True)

# Create Dimension Tables
customer_dim = cleaned_data[['Customer ID', 'Customer Name', 'Segment']].drop_duplicates().copy()
customer_dim['Segment ID'] = pd.factorize(customer_dim['Segment'])[0] + 1

product_dim = cleaned_data[['Product ID', 'Product Name', 'Sub-Category', 'Category']].drop_duplicates().copy()
product_dim['Sub-Category ID'] = pd.factorize(product_dim['Sub-Category'])[0] + 1

geography_dim = cleaned_data[['Country', 'State', 'City', 'Postal Code', 'Region']].drop_duplicates().copy()
geography_dim['Geography ID'] = pd.factorize(geography_dim.apply(lambda x: f"{x['Country']}_{x['State']}_{x['Postal Code']}", axis=1))[0] + 1
geography_dim['Region ID'] = pd.factorize(geography_dim['Region'])[0] + 1

time_dim = cleaned_data[['Order Date', 'Ship Date']].drop_duplicates().copy()
time_dim['Date ID'] = pd.factorize(time_dim['Order Date'].astype(str) + "_" + time_dim['Ship Date'].astype(str))[0] + 1

segment_dim = customer_dim[['Segment ID', 'Segment']].drop_duplicates().copy()
segment_dim.columns = ['Segment ID', 'Segment Name']

product_category_dim = product_dim[['Sub-Category ID', 'Category']].drop_duplicates().copy()
product_category_dim['Category ID'] = pd.factorize(product_category_dim['Category'])[0] + 1
product_category_dim['Category Name'] = product_category_dim['Category']

region_dim = geography_dim[['Region', 'Region ID']].drop_duplicates().copy()
region_dim.columns = ['Region Name', 'Region ID']

# Create Fact Table
sales_fact = cleaned_data[['Order ID', 'Product ID', 'Customer ID', 'Order Date', 'Ship Date', 'Sales', 'Quantity', 'Discount', 'Profit', 'Postal Code']].copy()
sales_fact['Date ID'] = pd.factorize(sales_fact['Order Date'].astype(str) + "_" + sales_fact['Ship Date'].astype(str))[0] + 1

# Debugging: Check if 'Postal Code' column exists in both DataFrames
print(f"Columns in sales_fact: {sales_fact.columns}")
print(f"Columns in geography_dim: {geography_dim.columns}")

# Ensure 'Postal Code' column exists before merging
if 'Postal Code' in sales_fact.columns and 'Postal Code' in geography_dim.columns:
    sales_fact = sales_fact.merge(geography_dim[['Postal Code', 'Geography ID']], on='Postal Code', how='left')
else:
    print("Error: 'Postal Code' column is missing from one of the DataFrames.")

# Save data marts to CSV files
customer_dim.to_csv(os.path.join(output_dir, "Customer_Dimension.csv"), index=False)
product_dim.to_csv(os.path.join(output_dir, "Product_Dimension.csv"), index=False)
geography_dim.to_csv(os.path.join(output_dir, "Geography_Dimension.csv"), index=False)
time_dim.to_csv(os.path.join(output_dir, "Time_Dimension.csv"), index=False)
segment_dim.to_csv(os.path.join(output_dir, "Segment_Dimension.csv"), index=False)
product_category_dim.to_csv(os.path.join(output_dir, "Product_Category_Dimension.csv"), index=False)
region_dim.to_csv(os.path.join(output_dir, "Region_Dimension.csv"), index=False)
sales_fact.to_csv(os.path.join(output_dir, "Sales_Fact.csv"), index=False)

# Create a zip archive of the data marts
with zipfile.ZipFile("Task_6_1_Data_Marts.zip", 'w') as zipf:
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            zipf.write(os.path.join(root, file), file)

# Count rows and distinct primary keys
data_mart_stats = {
    "Customer_Dimension": {
        "rows": len(customer_dim),
        "distinct_primary_keys": len(customer_dim['Customer ID'].unique())
    },
    "Product_Dimension": {
        "rows": len(product_dim),
        "distinct_primary_keys": len(product_dim['Product ID'].unique())
    },
    "Geography_Dimension": {
        "rows": len(geography_dim),
        "distinct_primary_keys": len(geography_dim['Geography ID'].unique())
    },
    "Time_Dimension": {
        "rows": len(time_dim),
        "distinct_primary_keys": len(time_dim['Date ID'].unique())
    },
    "Segment_Dimension": {
        "rows": len(segment_dim),
        "distinct_primary_keys": len(segment_dim['Segment ID'].unique())
    },
    "Product_Category_Dimension": {
        "rows": len(product_category_dim),
        "distinct_primary_keys": len(product_category_dim['Category ID'].unique())
    },
    "Region_Dimension": {
        "rows": len(region_dim),
        "distinct_primary_keys": len(region_dim['Region ID'].unique())
    },
    "Sales_Fact": {
        "rows": len(sales_fact),
        "distinct_primary_keys": len(sales_fact['Order ID'].unique()),
        "distinct_row_ids": len(sales_fact['Date ID'].unique()) if 'Date ID' in sales_fact.columns else 'N/A'
    }
}

# Save the data mart statistics to a CSV file
stats_df = pd.DataFrame.from_dict(data_mart_stats, orient='index')
stats_df.reset_index(inplace=True)
stats_df.columns = ['Data Mart System Name', 'Count Rows', 'Count Distinct Primary Key', 'Count Distinct Row ID']
stats_df.to_csv("Task_6_2_Data_Marts_Rows.csv", index=False)

print("Task_6 deliverables created successfully.")
