from snps import SNPs
import os

file_path = r"D:\Building\beeja\Beeja_Genetic\raw_data\genome_James_Jones_v5_Full_20230726173828\genome_James_Jones_v5_Full_20230726173828.txt"
print(f"Checking file: {file_path}")
if os.path.exists(file_path):
    print("File exists. Loading...")
    s = SNPs(file_path)
    print(f"Loaded successfully. Source: {s.source}")
else:
    print("File does not exist.")
