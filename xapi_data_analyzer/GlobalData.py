import pandas as pd
import json
import PySimpleGUI as sg

raw_data = None
class_list = None
DayInfo = None


def set_data_vars(data_path, json_path):
    """
    TODO fill in

    :param data_path:
    :param json_path:
    :return:
    """
    global raw_data
    global class_list
    global DayInfo

    raw_data = pd.read_csv(data_path)

    # Only keep around columns we care about
    raw_data = raw_data[["Email", "Verb", "object id", "Question/Slide", "Timestamp", "Duration"]]

    # Drop data that doesn't have an email associated with it
    raw_data = raw_data.dropna(subset=["Email"])

    # Drop all "consumed" verbs b/c they seem to be pretty useless
    raw_data = raw_data[raw_data["Verb"] != 'consumed']

    # Reformat email column to remove the "mailto:"
    raw_data["Email"] = raw_data["Email"].str.slice(start=7)

    # Convert the Timestamp column to datetime objects
    raw_data["Timestamp"] = pd.to_datetime(raw_data["Timestamp"])

    # Parse the actual object ID from the "object id" column
    url_list = raw_data["object id"].to_list()
    id_list = [int(s[s.index("id=") + 3: len(s) if s.find("?", s.index("id=")) == -1 else s.find("?", s.index("id="))])
               for s in url_list]
    raw_data["object id"] = id_list

    class_list = set(raw_data["Email"])

    # import data in DayElement.json
    if json_path != -1:
        try:
            with open(json_path) as f:
                DayInfo = json.load(f)

        except json.JSONDecodeError:
            sg.Popup("ERROR: DayElement.json could could not be read", title="Error")

        except FileNotFoundError:
            sg.Popup("ERROR: DayElement.json could could not be found", title="Error")