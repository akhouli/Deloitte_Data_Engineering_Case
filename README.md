# Deloitte Data Engineering Assessment

## Overview
This repository contains the scripts for the Deloitte Data Engineering assessment, which includes tasks for data extraction, profiling, cleansing, loading into a data warehouse, and creating data marts.

## Scripts

### Task 4: Data Warehouse Creation
The `Task_4_ddl.sql` script contains SQL statements to create the data warehouse structure, including schemas and tables. The design is based on the dimensional model provided.

### Task 5: ETL and Data Cleansing
The `task5.py` script performs the following steps:

1. **Data Extraction**: Reads data from multiple CSV files in a specified directory.
2. **Data Profiling**: Identifies inconsistencies in the data, such as:
   - **Missing Columns**: Checks if required columns are missing in the dataset.
   - **Invalid Data Formats**: Identifies invalid date formats in the `Order Date` column.
   - **Zero Sales and Quantity**: Identifies rows where both `Sales` and `Quantity` are zero.
   - **Negative Sales Values**: Identifies rows with negative sales values.
   - **Unrealistic Discount Values**: Identifies discount values that are less than 0 or greater than 1.
   - **Invalid Postal Codes**: Ensures postal codes follow the correct format (e.g., US ZIP codes).
   - **Inconsistent Country Names**: Checks for country names that are not 'United States'.
   - **Mismatched Order and Ship Dates**: Ensures that `Ship Date` is not before `Order Date`.
   - **Inconsistent Customer IDs**: Ensures that each customer name has a consistent customer ID.
   - **Negative Profit Values**: Identifies rows with negative profit values.
3. **Data Cleansing**: Cleans the data by:
   - Removing duplicates.
   - Filling missing `Customer Name` values with 'Unknown'.
   - Dropping rows with missing essential fields (`Order ID`, `Product ID`, `Customer ID`, `Order Date`, `Sales`).
   - Converting data types to appropriate formats.
   - Handling identified inconsistencies programmatically.
4. **Report Generation**: Generates an Excel report with three sheets:
   - `Inconsistencies_Summary`: Summarizes the types of inconsistencies found, their descriptions, suggestions to handle them, and the count of affected rows.
   - `Inconsistencies_Examples`: Provides examples of rows with inconsistencies.
   - `Quality_Report`: Lists all rows with inconsistencies that need business review.

### Task 6: Data Mart Creation
The `task6.py` script performs the following steps:

1. **Data Extraction and Cleansing**: Extracts and cleanses data as described in Task 5.
2. **Dimension and Fact Table Creation**: Creates dimension and fact tables based on the cleansed data, including:
   - **Customer Dimension**: Contains `Customer ID`, `Customer Name`, and `Segment ID`.
   - **Product Dimension**: Contains `Product ID`, `Product Name`, `Sub-Category ID`, and `Category ID`.
   - **Geography Dimension**: Contains `Geography ID`, `Country`, `State`, `City`, `Postal Code`, and `Region ID`.
   - **Time Dimension**: Contains `Date ID`, `Order Date`, and `Ship Date`.
   - **Segment Dimension**: Contains `Segment ID` and `Segment Name`.
   - **Product Category Dimension**: Contains `Category ID`, `Category Name`, and `Sub-Category ID`.
   - **Region Dimension**: Contains `Region ID` and `Region Name`.
   - **Sales Fact Table**: Contains `Order ID`, `Product ID`, `Customer ID`, `Date ID`, `Geography ID`, `Sales`, `Quantity`, `Discount`, and `Profit`.
3. **Data Mart Export**: Exports each data mart to individual CSV files and archives them into a zip file (`Task_6_1_Data_Marts.zip`).
4. **Data Mart Statistics**: Generates a CSV file (`Task_6_2_Data_Marts_Rows.csv`) with the count of rows and distinct primary keys for each data mart.


## Repository Structure
- `Task_4_ddl.txt`: SQL script for creating the data warehouse structure.
- `Task_5_script.py`: Script for data extraction, profiling, cleansing, and inconsistency report generation.
- `Task_6_script.py`: Script for data mart creation and export.
