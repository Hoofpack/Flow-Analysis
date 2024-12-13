import os
import pandas as pd

# Load the sample file and the platemap file
sample_file_path = '20241204_RFF OP1 col12 rpt_CB.csv'
platemap_file_path = '20241203_OG1 rpt_RF + TXTL plate map.csv'

# Extract the base name of the sample file (without the extension)
base_name = os.path.splitext(os.path.basename(sample_file_path))[0]

# Read the sample file into a DataFrame
sample_df = pd.read_csv(sample_file_path)

# Read the platemap file into a DataFrame
platemap_df = pd.read_csv(platemap_file_path, encoding='ISO-8859-1')  # or 'latin1' as an alternative

# Reshape the platemap DataFrame to get well names in format 'A1', 'B2', etc.
platemap_df_melted = platemap_df.melt(id_vars=['Unnamed: 0'], var_name='Column', value_name='Sample_Name')
platemap_df_melted['Well'] = platemap_df_melted['Unnamed: 0'] + platemap_df_melted['Column'].astype(str)

# Merge the sample information with the platemap based on well positions
df = sample_df.merge(platemap_df_melted[['Well', 'Sample_Name']], left_on='Sample', right_on='Well', how='left')

# Drop unnecessary columns after merging
df = df.drop(columns=['Well'])

# Filter df for 'Gate' == 'R6' and 'Y Parameter' containing 'methanogen'
filtered_df1 = df[(df['Gate'] == 'R6') & (df['Y Parameter'].str.contains('methanogen', case=False, na=False))]

# Filter df2 similarly
# filtered_df2 = df[(df['Gate'] == 'R3') & (df['Y Parameter'].str.contains('methanogen', case=False, na=False))]

# Concatenate the filtered dataframes
#concatenated_df = pd.concat([filtered_df1, filtered_df2])
# If needed in the future, change Line 39 also

# Select only the required columns
selected_columns = ['Plate', 'Sample_Name', 'Gate', 'Y Parameter', '%Gated']
filtered_data = filtered_df1[selected_columns]

# Specify the output file path using the same base name as the sample file
output_dir = '/home/themagikscientist/Flow_Data_Analysis/Spreadsheets'
os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist
output_file_path = os.path.join(output_dir, f'{base_name}_filtered_data.xlsx')

# Save the results into an Excel file
filtered_data.to_excel(output_file_path, index=False)

print(f"Filtered data saved to {output_file_path}")
