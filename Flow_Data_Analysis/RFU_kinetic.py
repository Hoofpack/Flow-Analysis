import pandas as pd
import matplotlib.pyplot as plt
import os

# Load the Excel file
file_path = "20250307_T7 for MK.xlsx"  # Replace with the actual file path
sheet_name = "Sheet1"  # Modify if needed

# Read the Excel file
df = pd.read_excel(file_path, sheet_name=sheet_name)

# Convert "Time" column to string if needed, then parse to timedelta
df["Time"] = pd.to_timedelta(df["Time"].astype(str))

# Extract the RFU columns
rfu_columns = ["gb2826", "gb2827", "gb2829", "gb2829", "gb2830", "gb2830", "gb2831", "gb2832"]  # Excluding "ND" since it's all zeros

# Plot the data
plt.figure(figsize=(12, 6))
plt.ylim(0, 8000)

for column in rfu_columns:
    plt.plot(df["Time"].dt.total_seconds() / 3600, df[column], marker="o", linestyle="-", label=column)  # Convert time to minutes

# Formatting
plt.xlabel("Time (hours)")
plt.ylabel("RFU")
plt.title("GFP Expression Over Time - 30C")
plt.legend()
plt.grid(True)

# Save the plot
output_filename = os.path.splitext(os.path.basename(file_path))[0] + '_RFU_Kinetic.png'
output_path = os.path.join('plots', output_filename)
os.makedirs('plots', exist_ok=True)
plt.tight_layout()
plt.savefig(output_path, dpi=300)
plt.show()

