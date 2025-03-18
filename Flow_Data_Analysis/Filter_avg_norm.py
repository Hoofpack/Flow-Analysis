import os
import pandas as pd
import datetime

# Define the directories containing sample files and plate map files
sample_dir = 'Flow_Files'
platemap_dir = 'Plate_Maps'

# Specify the output directory and file
output_dir = 'spreadsheets'
os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist

# Generate a unique filename based on the current timestamp
current_time = datetime.datetime.now().strftime('%Y%m%d_%H%M')
output_file_path = os.path.join(output_dir, f'concatenated_averaged_data_{current_time}.xlsx')

# Initialize an empty list to hold the processed DataFrames
all_data = []

# Iterate over all sample files in the directory
for sample_file in os.listdir(sample_dir):
    if sample_file.endswith('.csv'):
        # Construct the full path to the sample file
        sample_file_path = os.path.join(sample_dir, sample_file)

        # Extract the base name of the sample file (without the extension)
        base_name = os.path.splitext(sample_file)[0]

        # Construct the corresponding plate map file path
        platemap_file_path = os.path.join(platemap_dir, f'{base_name}_plate_map.csv')

        # Check if the plate map file exists
        if not os.path.exists(platemap_file_path):
            print(f"Plate map file for {sample_file} not found. Skipping.")
            continue

        # Read the sample file into a DataFrame
        sample_df = pd.read_csv(sample_file_path)

        # Read the plate map file into a DataFrame
        platemap_df = pd.read_csv(platemap_file_path, encoding='ISO-8859-1')  # or 'latin1'

        # Reshape the platemap DataFrame to get well names in format 'A1', 'B2', etc.
        platemap_df_melted = platemap_df.melt(id_vars=['Unnamed: 0'], var_name='Column', value_name='Sample_Name')
        platemap_df_melted['Well'] = platemap_df_melted['Unnamed: 0'] + platemap_df_melted['Column'].astype(str)

        # Merge the sample information with the platemap based on well positions
        df = sample_df.merge(platemap_df_melted[['Well', 'Sample_Name']], left_on='Sample', right_on='Well', how='left')

        # Drop unnecessary columns after merging
        df = df.drop(columns=['Well'])

        # Filter df for 'Gate' == 'R6' and 'Y Parameter' containing 'methanogen'
        filtered_df1 = df[(df['Gate'] == 'R6') & (df['Y Parameter'].str.contains('methanogen', case=False, na=False))]

        # Select only the required columns
        selected_columns = ['Plate', 'Sample_Name', 'Gate', 'Y Parameter', '%Gated']
        filtered_data = filtered_df1[selected_columns]

        # Group by 'Sample_Name' and calculate the mean for numeric columns
        averaged_data = filtered_data.groupby(['Sample_Name', 'Plate', 'Gate', 'Y Parameter'], as_index=False).mean()

        # Append the processed DataFrame to the list
        all_data.append(averaged_data)

# Concatenate all processed DataFrames into a single DataFrame
if all_data:
    concatenated_data = pd.concat(all_data, ignore_index=True)

    # Calculate averaged ND and bc96_none values from the concatenated data
    ND_data = concatenated_data[concatenated_data['Sample_Name'] == 'ND']
    ND_value = ND_data['%Gated'].mean()

    bc96_none_data = concatenated_data[concatenated_data['Sample_Name'] == 'gb2004']
    bc96_none_value = bc96_none_data['%Gated'].mean()

    # Normalize %Gated values for each row using the calculated ND and bc96_none values
    concatenated_data['Normalized %Gated'] = concatenated_data['%Gated'].apply(
        lambda x: (ND_value - x) / (ND_value - bc96_none_value)
    )

    # Save the concatenated data into an Excel file
    concatenated_data.to_excel(output_file_path, index=False)
    print(f"Concatenated averaged data saved to {output_file_path}")
else:
    print("No data to concatenate. Ensure sample and plate map files are correctly paired.")
