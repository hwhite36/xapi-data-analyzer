import pandas as pd

raw_data = pd.read_csv("Chem109 PB Demo Data (Cleaned).csv")
new_data = pd.read_csv("data4-17-20(cleaned).csv")
# Get rid of all interactions that don't have emails
new_data = new_data.dropna(subset=["Email"])
class_list = set(new_data["Email"])