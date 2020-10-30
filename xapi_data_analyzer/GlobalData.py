import pandas as pd
import json
import PySimpleGUI as sg

raw_data = None
class_list = None
DayInfo = None


def set_data_vars(data_path, json_path):
    """
    Sets global data variables to be used in ``ElementCollection.py`` and ``Main.py``, including

    * raw_data: the dataframe read from the raw data's csv
    * class_list: list of unique emails from raw_data (we assume this is acceptable as a list of everyone in the class)
    * DayInfo: the JSON data imported into the program, if the user uses a JSON input

    :param data_path: path to the raw_data csv
    :param json_path: path to the JSON file, or -1 if the user isn't using a JSON file to provide H5P IDs
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

    # import data in DayElement.json (Error handling done in Main.py)
    with open(json_path) as f:
        DayInfo = json.load(f)
        # Drop data from non-student emails (using the filter emails list)
        raw_data = raw_data[~raw_data["Email"].isin(DayInfo["Filter_Emails"])]
        class_list = class_list - set(DayInfo["Filter_Emails"])
