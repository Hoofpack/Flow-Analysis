#!/usr/bin/env python3

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from Bio import SeqIO
from difflib import get_close_matches
from datetime import datetime

# File paths
flow_data_file = 'spreadsheets/concatenated_averaged_data_20250103_0949.xlsx'  # Raw flow cytometry data
mutation_data_file = '11_25_2004_1mut.csv'  # Mutation data
snapgene_file = 'gb2004_CDS.gpt'  # GenPept file from SnapGene

# Designated folder to save the heatmap
output_folder = 'heatmap_output'
os.makedirs(output_folder, exist_ok=True)  # Create the folder if it doesn't exist

# Function to safely load a file (CSV or Excel)
def safe_load_file(file_path):
    try:
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path, encoding='ISO-8859-1', compression='infer', engine='python')
        elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            return pd.read_excel(file_path, engine='openpyxl')
        else:
            print(f"Unsupported file format for {file_path}.")
            exit(1)
    except pd.errors.ParserError:
        print(f"Error parsing {file_path}. Attempting alternative configurations...")
        try:
            if file_path.endswith('.csv'):
                return pd.read_csv(file_path, encoding='ISO-8859-1', delimiter=';', engine='python')
            else:
                print(f"Cannot apply alternative parsing to non-CSV file: {file_path}")
                exit(1)
        except Exception as e:
            print(f"Failed to load {file_path}: {e}")
            exit(1)

# Load the raw flow cytometry data
flow_data = safe_load_file(flow_data_file)
flow_data['%Gated'] = pd.to_numeric(flow_data['%Gated'], errors='coerce')  # Ensure numeric values


# Load the mutation data
mutation_data = safe_load_file(mutation_data_file)


# Parse the GenPept file to extract sequence information
genpept_record = SeqIO.read(snapgene_file, "genbank")
sequence = str(genpept_record.seq)


# Normalize the columns for matching
flow_data['Sample_Name'] = flow_data['Sample_Name'].str.strip().str.lower()
mutation_data['Name'] = mutation_data['Name'].str.strip().str.lower()

# Function to find closest matches for debugging
def find_closest_match(sample_name, mutation_names):
    matches = get_close_matches(sample_name, mutation_names, n=1, cutoff=0.6)
    return matches[0] if matches else None


# Prepare a list of all possible amino acids
amino_acids = list("ACDEFGHIKLMNPQRSTVWY") + ["null"]

# Create a DataFrame to organize the heatmap data
heatmap_data = pd.DataFrame(index=amino_acids, columns=[f"{aa}{i+1}" for i, aa in enumerate(sequence)])
heatmap_data = heatmap_data.astype(float)  # Ensure all values are floats

# Debug: Track unmatched samples
unmatched_samples = []
closest_matches = []

for _, row in flow_data.iterrows():
    sample_name = row['Sample_Name']
    try:
        flow_value = float(row['%Gated'])  # Convert to float explicitly
    except ValueError:
        flow_value = np.nan  # Assign NaN for invalid values

    # Exact matching for sample names
    matching_mutation = mutation_data[mutation_data['Name'] == sample_name]
    if not matching_mutation.empty:
        position = matching_mutation.iloc[0]['Mutated Residue']
        amino_acid = matching_mutation.iloc[0]['Mutant AA']
        if str(position).isdigit() and 1 <= int(position) <= len(sequence):
            original_aa = sequence[int(position) - 1]
            column_name = f"{original_aa}{position}"
            if column_name in heatmap_data.columns and amino_acid in heatmap_data.index:
                heatmap_data.at[amino_acid, column_name] = flow_value
    else:
        closest_match = find_closest_match(sample_name, mutation_data['Name'].tolist())
        if closest_match:
            matching_mutation = mutation_data[mutation_data['Name'] == closest_match]
            if not matching_mutation.empty:
                position = matching_mutation.iloc[0]['Mutated Residue']
                amino_acid = matching_mutation.iloc[0]['Mutant AA']
                if str(position).isdigit() and 1 <= int(position) <= len(sequence):
                    original_aa = sequence[int(position) - 1]
                    column_name = f"{original_aa}{position}"
                    if column_name in heatmap_data.columns and amino_acid in heatmap_data.index:
                        heatmap_data.at[amino_acid, column_name] = flow_value
        else:
            unmatched_samples.append(sample_name)
            closest_matches.append((sample_name, closest_match))

# Debug: Print unmatched samples and their closest matches
if unmatched_samples:
    print("Warning: The following samples were not matched:")
    for sample, match in zip(unmatched_samples, closest_matches):
        print(f"Unmatched Sample: {sample}, Closest Match: {match}")


# Ensure all amino acids are represented, even if they have no data
data_cleaned = heatmap_data.reindex(index=amino_acids, columns=heatmap_data.columns)

# Always add 'bc96_none' and 'ND' columns at the end of the x-axis
for special_column in ['bc96_none', 'ND']:
    if special_column not in data_cleaned.columns:
        data_cleaned[special_column] = np.nan  # Add missing special columns

    # Assign flow values for 'bc96_none' and 'ND' to the "null" row if they exist in flow data
    flow_value = flow_data.loc[flow_data['Sample_Name'] == special_column.lower(), '%Gated'].max()
    if not np.isnan(flow_value):
        data_cleaned.at['null', special_column] = flow_value

# Reorder columns to ensure 'bc96_none' and 'ND' are at the end
columns = [col for col in data_cleaned.columns if col not in ['bc96_none', 'ND']]
columns += ['bc96_none', 'ND']
data_cleaned = data_cleaned[columns]

# Determine vmin and vmax for the heatmap
nd_value = data_cleaned.at['null', 'ND'] if 'ND' in data_cleaned.columns else np.nan
bc96_none_value = data_cleaned.at['null', 'bc96_none'] if 'bc96_none' in data_cleaned.columns else np.nan
vmin = bc96_none_value - 1 if not np.isnan(bc96_none_value) else 0
vmax = nd_value + 1 if not np.isnan(nd_value) else 10

# Check if cleaned data is empty
if data_cleaned.empty:
    print("No valid data available for the heatmap after processing. Exiting.")
else:
   

    # Create the heatmap
    plt.figure(figsize=(25, 10))
    ax = sns.heatmap(
        data_cleaned,
        cmap="viridis",
        cbar=True,
        linewidths=0.5,
        annot=True,
        fmt=".2f",
        mask=data_cleaned.isnull(),
        vmin=vmin,
        vmax=vmax,
    )

    # Customize the plot
    plt.title("Flow Cytometry Heatmap_gb2004 rd", fontsize=16)
    plt.xlabel("Protein Sequence (Original Amino Acids)", fontsize=14)
    plt.ylabel("Mutated Amino Acids", fontsize=14)

    # Generate a unique filename using a timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file_name = f"gb2004_rd4_{timestamp}.png"
    output_file_path = os.path.join(output_folder, output_file_name)

    # Save the heatmap to the designated folder
    plt.tight_layout()
    plt.savefig(output_file_path)
    print(f"Heatmap saved to {output_file_path}")

    
