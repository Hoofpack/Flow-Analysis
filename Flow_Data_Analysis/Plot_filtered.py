import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import re
from natsort import natsorted, ns

# Function to extract the alphabetical and numerical components of a sample name
def split_alpha_num(name):
    match = re.match(r"([A-Za-z]+)(\d*)", str(name))  # Extracts letters + optional number
    if match:
        alpha_part = match.group(1)  # Alphabetical part
        num_part = int(match.group(2)) if match.group(2) else 0  # Convert number part
        return (alpha_part, num_part)
    return (name, 0)  # Default if no match

# Function to load and process the data
def load_and_process_data(excel_file):
    # Read Excel into a pandas DataFrame
    data = pd.read_excel(excel_file)
    
    # Filter for R6 gate data
    filtered_data = data[data['Gate'] == 'R9']
    
    # Apply alphabetical + numerical sorting using a DataFrame helper column
    filtered_data = filtered_data.copy()
    filtered_data['AlphaPart'] = filtered_data['Sample_Name'].apply(lambda x: split_alpha_num(x)[0])
    filtered_data['NumPart'] = filtered_data['Sample_Name'].apply(lambda x: split_alpha_num(x)[1])

    # Sort first alphabetically, then numerically
    filtered_data = filtered_data.sort_values(by=['AlphaPart', 'NumPart'], ascending=[True, True])

    # Drop the helper columns after sorting
    filtered_data = filtered_data.drop(columns=['AlphaPart', 'NumPart'])

    # Calculate the mean '%Gated' for each 'Sample_Name'
    mean_gated_values = filtered_data.groupby('Sample_Name')['%Gated'].mean().reset_index()

    return filtered_data, mean_gated_values

# (Rest of the code remains unchanged)


def plot_data(filtered_data, mean_gated_values, excel_file, save_path=None):
    plt.figure(figsize=(17, 8))  # Adjust width (14) to create more space
    
    sns.scatterplot(data=filtered_data, 
                    x='Sample_Name', 
                    y='%Gated', 
                    hue='Sample_Name', 
                    style='Sample_Name', 
                    s=100, 
                    palette='bright', 
                    markers=True, 
                    legend=False)
    
    unique_samples = filtered_data['Sample_Name'].unique()
    sample_position = {sample: i for i, sample in enumerate(unique_samples)}
    
    for _, row in mean_gated_values.iterrows():
        sample_name = row['Sample_Name']
        sample_x_pos = sample_position[sample_name]
        plt.hlines(y=row['%Gated'], xmin=sample_x_pos - 0.2, xmax=sample_x_pos + 0.2, 
                   colors='gray', linestyles='-', lw=2)
    
    plt.xlabel('', fontsize=14)
    plt.ylabel('% Dead Methanogens', fontsize=14)
    plt.title('Methanogen Flow Cytometry Analysis - Metabolic Dye Pilot - R9', fontsize=16)
    plt.xticks(ticks=range(len(unique_samples)), labels=unique_samples, rotation=50, fontsize=12, ha='right')
    plt.subplots_adjust(bottom=0.5)
    plt.yticks(fontsize=12)
    plt.ylim(0, 7)

    # Add gridlines
    plt.grid(visible=True, which='major', axis='both', linestyle='--', linewidth=0.5, alpha=0.7)
    
    plt.tight_layout()

    if save_path:
        os.makedirs(save_path, exist_ok=True)
        file_name = os.path.splitext(os.path.basename(excel_file))[0]
        file_path = os.path.join(save_path, f'{file_name}_R9_plot.png')
        plt.savefig(file_path, bbox_inches='tight', dpi=300)
        print(f"Plot saved to {file_path}")
    
    plt.show()

# Main function to load data and generate plot
def main(excel_file, save_path=None):
    # Load and process the data
    filtered_data, mean_gated_values = load_and_process_data(excel_file)
    
    # Plot the data and save to file if save_path is provided
    plot_data(filtered_data, mean_gated_values, excel_file, save_path)
    
    # Print confirmation that the plot is complete
    print("Plot has been generated and displayed.")

# Example usage
excel_file = 'Spreadsheets/20250313_RFF CTC and diSc3_CB_filtered_data.xlsx'  # Use the correct path to your Excel file
save_path = 'plots'  # Folder where the plot will be saved
main(excel_file, save_path)
