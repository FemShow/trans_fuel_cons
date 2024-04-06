import pandas as pd

# Data dictionary for ons_geography_code and region
data_dictionary = {
    'neast': {'ons_geography_code': 'E12000001', 'region': 'North East'},
    'nwest': {'ons_geography_code': 'E12000002', 'region': 'North West'},
    'ykhu': {'ons_geography_code': 'E12000003', 'region': 'Yorkshire and The Humber'},
    'emids': {'ons_geography_code': 'E12000004', 'region': 'East Midlands'},
    'wmids': {'ons_geography_code': 'E12000005', 'region': 'West Midlands'},
    'east': {'ons_geography_code': 'E12000006', 'region': 'East of England'},
    'lon': {'ons_geography_code': 'E12000007', 'region': 'London'},
    'seast': {'ons_geography_code': 'E12000008', 'region': 'South East'},
    'swest': {'ons_geography_code': 'E12000009', 'region': 'South West'},
    'wal': {'ons_geography_code': 'W92000004', 'region': 'Wales'},
    'scot': {'ons_geography_code': 'S92000003', 'region': 'Scotland'},
    'nire': {'ons_geography_code': 'N92000002', 'region': 'Northern Ireland'}
}

# Specify the path to the Excel file
excel_file_path = "/Users/femisokoya/Documents/GitHub/X01/regionalemploymentbyage (1).xlsx"

# Use pandas to read the Excel file
xls = pd.ExcelFile(excel_file_path)

# Get the names of all worksheets in the Excel file
sheet_names = xls.sheet_names

# Define the excluded sheet names
excluded_sheets = ['Export Summary', 'Note', 'Index', 'Information']

# Create an empty list to store DataFrames
dfs = []

# Iterate over worksheet names
for sheet_name in sheet_names:
    # Skip excluded sheets
    if sheet_name in excluded_sheets:
        continue
    
    # Strip off the last two characters of the sheet name
    suffix = sheet_name[-2:]
    stripped_sheet_name = sheet_name[:-2]
    
    # Process each sheet
    df = pd.read_excel(excel_file_path,
                       sheet_name=sheet_name,
                       header=6, # Use row 7 as the column header
                       skiprows=[7, 8, 9],
                       nrows=270)  
    
    # Insert columns 'ons_geography_code' and 'sex' based on the data dictionary and worksheet suffix
    df['ons_geography_code'] = data_dictionary[stripped_sheet_name]['ons_geography_code']
    df['sex'] = '_T' if suffix == '_p' else ('M' if suffix == '_m' else 'F')
    
    # Insert a column 'region' with the amended value of the sheet name
    df['region'] = data_dictionary[stripped_sheet_name]['region']
    
    # Rename the first column to 'period' and format the time period
    first_month = df.columns[0]
    df.rename(columns={first_month: 'time_period'}, inplace=True)
    df['time_period'] = df['time_period'].apply(lambda x: f"{x.split()[1]}-{x.split()[0][:3]}-01/P3M")
    
    # Append the processed DataFrame to the list
    dfs.append(df)

# Concatenate all DataFrames in the list into a single DataFrame
merged_data = pd.concat(dfs, ignore_index=True)

# Rename columns using the data dictionary
merged_data.rename(columns={
    'All aged       16 & over': '>16_num',
    '16 - 64': '16 - 64_num',
    '16 - 17': '16 - 17_num',
    '18 - 24': '18 - 24_num',
    '25 - 34': '25 - 34_num',
    '35 - 49': '35 - 49_num',
    '50 - 64': '50 - 64_num',
    '65+': '>65_num',
    'All aged       16 & over.1': '>16_perc',
    '16 - 64.1': '16 - 64_perc',
    '16 - 17.1': '16 - 17_perc',
    '18 - 24.1': '18 - 24_perc',
    '25 - 34.1': '25 - 34_perc',
    '35 - 49.1': '35 - 49_perc',
    '50 - 64.1': '50 - 64_perc',
    '65+.1': '>65_perc'
}, inplace=True)

# Melt the DataFrame
melted_df = pd.melt(
    merged_data,
    id_vars=['time_period', 'region', 'ons_geography_code', 'sex'],
    value_vars=['>16_num', '16 - 64_num', '16 - 17_num', '18 - 24_num', '25 - 34_num', '35 - 49_num', '50 - 64_num', '>65_num', '>16_perc', '16 - 64_perc', 
    '16 - 17_perc', '18 - 24_perc', '25 - 34_perc', '35 - 49_perc', '50 - 64_perc', '>65_perc'],
    var_name='age_band', value_name='observations'
)

# Add 'measures' column based on suffix of 'age_band'
melted_df['measures'] = melted_df['age_band'].apply(lambda x: 'count' if '_num' in x else 'portion')

# Add 'units' column based on suffix of 'age_band'
melted_df['units'] = melted_df['age_band'].apply(lambda x: 'number' if '_num' in x else 'percent')

def process_age_band(df):
    for index, row in df.iterrows():
        if '_num' in row['age_band']:
            df.at[index, 'age_band'] = row['age_band'].replace('_num', '')
        elif '_perc' in row['age_band']:
            df.at[index, 'age_band'] = row['age_band'].replace('_perc', '')
            # Check if the value is a float and round it to 2 decimal places if it is
            if isinstance(row['observations'], float):
                df.at[index, 'observations'] = round(row['observations'], 2)

# Call the function to process age_band and observations
process_age_band(melted_df)

# Specify the path to save the CSV file
output_file_path = "/Users/femisokoya/Documents/GitHub/X01/melted.csv"

# Write the melted data to the CSV file
melted_df.to_csv(output_file_path, index=False)

# Print a message indicating the process is complete
print("Melted data saved to melted.csv")
