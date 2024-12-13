import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# User inputs: Sample file and plate map file
sample_file = '20241205_RFF OG3_plt2_CB.csv'  # User-provided sample file
plate_map_file = '20241205_OP3_RF + TXTL plate map 2.csv'  # User-provided plate map file

# Load datasets
sample_data = pd.read_csv(sample_file, encoding='ISO-8859-1')
plate_map_data = pd.read_csv(plate_map_file, encoding='ISO-8859-1')

# Function to create a mapping from the plate map dataframe
def create_plate_map_mapping(df):
    mapping = {}
    for row in df.itertuples():
        for col in range(1, len(df.columns)):
            cell_label = f"{row[1]}{col}"  # e.g., "A1", "B2", etc.
            mapping[cell_label] = row[col + 1]
    return mapping

# Apply plate map to sample data to enrich it
def apply_plate_map(sample_data, plate_map):
    # Creating a mapping from the plate map
    plate_mapping = create_plate_map_mapping(plate_map)
    
    # Add a "Mapped Sample" column to the sample data
    sample_data['Mapped Sample'] = sample_data['Sample'].map(plate_mapping)
    return sample_data

# Enrich the sample data
enriched_sample_data = apply_plate_map(sample_data, plate_map_data)

# Filter data based on specific criteria
filtered_data = enriched_sample_data[
    (enriched_sample_data['Gate'] == 'R6') & 
    (enriched_sample_data['Y Parameter'].str.contains('methanogen', case=False, na=False))
].copy()

# Clean up and format the data
filtered_data['Sample Info'] = filtered_data['Sample'].apply(lambda x: str(x).split('.')[0])
filtered_data['Mapped Sample'] = filtered_data['Mapped Sample'].apply(lambda x: str(x).split('.')[0])

# Create a "Category" column for plotting
filtered_data['Category'] = filtered_data['Mapped Sample']

# Filter out rows with NaN or invalid categories
filtered_data = filtered_data[~filtered_data['Category'].isna()]

# Calculate mean '%Gated' values for each category
mean_gated_values = filtered_data.groupby('Category')['%Gated'].mean().reset_index()

# Sort categories for consistent plotting
sorted_categories = sorted(filtered_data['Category'].unique())
filtered_data['Category'] = pd.Categorical(filtered_data['Category'], categories=sorted_categories, ordered=True)

# Plotting
plt.figure(figsize=(15, 8))

# Scatter plot for individual data points
sns.scatterplot(
    data=filtered_data, 
    x='Category', 
    y='%Gated', 
    hue='Mapped Sample', 
    s=100, 
    style='Mapped Sample', 
    legend=None
)

# Draw horizontal lines for mean values
for _, row in mean_gated_values.iterrows():
    category_index = sorted_categories.index(row['Category'])
    plt.hlines(y=row['%Gated'], xmin=category_index - 0.2, xmax=category_index + 0.2, colors='gray', linestyles='--', lw=2)

# Customize plot
plt.xlabel('', fontsize=14)
plt.ylabel('% Methanogens', fontsize=14)
plt.title('Methanogen Flow Cytometry Analysis - Oligo Pool_1892 rd2', fontsize=16)
plt.xticks(rotation=45, fontsize=12, ha='right')
plt.yticks(fontsize=12)
plt.ylim(0, 8)

# Save the plot
output_filename = os.path.splitext(os.path.basename(sample_file))[0] + '_Methanogen_Flow.png'
output_path = os.path.join('plots', output_filename)
os.makedirs('plots', exist_ok=True)
plt.tight_layout()
plt.savefig(output_path, dpi=300)
plt.show()
