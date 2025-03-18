import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

# User inputs: Sample file (mandatory) and plate map file (optional)
sample_file = 'Spreadsheets/20250313_RFF CTC and diSc3_CB_filtered_data.xlsx'  # User-provided sample file
plate_map_file = None  # Set to None if no plate map file is provided

y_axis_column = '% Viable Cells'  # Change this to use a different y-axis value

# User-defined y-axis range
y_axis_min = 0  # Set the minimum value of the y-axis
y_axis_max = 6  # Set the maximum value of the y-axis

# Load sample data with auto-format detection
if sample_file.endswith('.csv'):
    sample_data = pd.read_csv(sample_file, encoding='ISO-8859-1', delimiter=None, engine='python')
elif sample_file.endswith('.xlsx'):
    sample_data = pd.read_excel(sample_file, sheet_name=0)  # Load first sheet
else:
    raise ValueError("Unsupported file format. Please provide a CSV or Excel file.")

# Extract R9 and R6 values for viability calculation
r9_data = sample_data[sample_data['Gate'] == 'R9'][['Sample_Name', '%Gated']].drop_duplicates()
r6_data = sample_data[sample_data['Gate'] == 'R6'][['Sample_Name', '%Gated']].drop_duplicates()

# Merge R9 and R6 data
viability_data = pd.merge(r9_data, r6_data, on='Sample_Name', suffixes=('_R9', '_R6'))

# Calculate % Viable Methanogens
viability_data[y_axis_column] = ((100 - viability_data['%Gated_R9']) / 100) * viability_data['%Gated_R6']

# Merge back with original sample data
sample_data = sample_data.merge(viability_data[['Sample_Name', y_axis_column]], on='Sample_Name', how='left').drop_duplicates()

# Assign unique markers and colors for each Sample_Name
unique_samples = sample_data['Sample_Name'].unique()
markers = ['o', 's', 'D', '^', 'v', '<', '>', 'p', 'X', '*']  # Different marker shapes
colors = sns.color_palette("husl", len(unique_samples))  # Assign unique colors

# Create figure
plt.figure(figsize=(10, 8))
ax = plt.gca()

# Plot each sample with a unique marker and color
for i, sample in enumerate(unique_samples):
    sample_subset = sample_data[sample_data['Sample_Name'] == sample]
    sns.scatterplot(
        data=sample_subset, x='Sample_Name', y=y_axis_column,
        s=100, marker=markers[i % len(markers)], color=colors[i % len(colors)], ax=ax
    )

# Calculate mean values and plot them as horizontal bars
mean_values = sample_data.groupby('Sample_Name', as_index=False)[y_axis_column].mean()
x_positions = np.arange(len(unique_samples))  # Get numeric positions of samples on x-axis
for i, sample in enumerate(unique_samples):
    mean_y = mean_values.loc[mean_values['Sample_Name'] == sample, y_axis_column].values[0]
    plt.hlines(y=mean_y, xmin=x_positions[i] - 0.3, xmax=x_positions[i] + 0.3, colors='gray', linestyles='--', lw=1.5)

# Configure plot
plt.xticks(ticks=x_positions, labels=unique_samples, rotation=45, ha='right')
plt.xlabel('')
plt.ylabel(y_axis_column)
plt.ylim(y_axis_min, y_axis_max)
plt.title('Methanogen Flow Cytometry Analysis - Metabolic Dye Pilot')

# Add gridlines
plt.grid(visible=True, which='major', axis='both', linestyle='--', linewidth=0.5, alpha=0.7)

# Save plot
output_filename = os.path.splitext(os.path.basename(sample_file))[0] + '_Methanogen_Flow.png'
output_path = os.path.join('plots', output_filename)
os.makedirs('plots', exist_ok=True)
plt.tight_layout()
plt.savefig(output_path, dpi=300)
plt.show()
