import pandas as pd
#to understand dataset structure 
# number of rows and columns, column names, data types, missing values ,distribution of the target column

# read the dataset
df = pd.read_csv("oulad_ready_for_training.csv")

# basic information
print("Shape of dataset:")
print(df.shape)

print("\nColumn names:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isnull().sum())

print("\nFirst 5 rows:")
print(df.head())

# check target column distribution
if "final_result" in df.columns:
    print("\nFinal result distribution:")
    print(df["final_result"].value_counts())
