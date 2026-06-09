import pandas as pd

df = pd.read_csv("oulad_ready_for_training.csv")

print(df.head())  #first 5 rows 
print("\nColumns:")   #columns name
print(df.columns) 
print("\nShape:")   #(rows,column)
print(df.shape)   