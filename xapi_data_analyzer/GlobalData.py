import pandas as pd

raw_data = None
class_list = None


def set_data_vars(data_path):
    global raw_data
    global class_list
    raw_data = pd.read_csv(data_path)
    raw_data = raw_data.dropna(subset=["Name"])
    raw_data = raw_data[raw_data["Verb"] != 'consumed']
    class_list = set(raw_data["Name"])
