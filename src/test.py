# Import necessary library
import os

# Define the file path
file_path = 'data/raw/AMZN-10k-08.txt'

# Extract the file name without extension
file_name_without_extension = os.path.splitext(os.path.basename(file_path))[0]

# Print the file name without extension
print("File name without extension:", file_name_without_extension)