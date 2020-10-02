import pandas as pd
import json
import PySimpleGUI as sg

raw_data = None
class_list = None
DayInfo = None


def set_data_vars(data_path):
    global raw_data
    global class_list
    global DayInfo
    raw_data = pd.read_csv(data_path, parse_dates=[['Date', 'Time']])
    # raw_data = pd.read_csv(data_path)
    raw_data = raw_data.dropna(subset=["Email"])
    # We drop all "consumed" verbs here b/c they seem to be pretty useless
    raw_data = raw_data[raw_data["Verb"] != 'consumed']

    class_list = set(raw_data["Email"])

    # import data in DayElement.json
    try:
        with open('DayElement.json') as f:
            DayInfo = json.load(f)

    except json.JSONDecodeError:
        sg.Popup("ERROR: DayElement.json could could not be read", title="Error")

    except FileNotFoundError:
        sg.Popup("ERROR: DayElement.json could could not be found", title="Error")
