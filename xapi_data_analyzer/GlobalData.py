import pandas as pd
import json
from jsonschema import validate
from os import path
import sys
import PySimpleGUI as sg


raw_data = None
class_list = None
DayInfo = None
delta_max = None


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
    global delta_max

    raw_data = pd.read_csv(data_path)

    # Uncomment below to print the number of bytes the dataframe takes in memory
    # print("raw data: " + str(raw_data.memory_usage(index=True, deep=True).sum()))

    # Only keep around columns we care about
    raw_data = raw_data[["Email", "Verb", "object id", "Question/Slide", "Timestamp", "Duration"]]

    # Convert the Timestamp column to datetime objects
    raw_data["Timestamp"] = pd.to_datetime(raw_data["Timestamp"], errors='coerce')
    # Drop all rows where the datetime conversion failed or where email doesn't exist, b/c that means they're bad data
    rows_count = len(raw_data.index)
    raw_data = raw_data.dropna(subset=["Timestamp"])
    rows_dropped_timestamp = rows_count - len(raw_data.index)

    # Drop all columns with an NaN email, b/c that's bad data
    rows_count = len(raw_data.index)
    raw_data = raw_data.dropna(subset=["Email"])
    rows_dropped_email_nan = rows_count - len(raw_data.index)

    # Drop all columns that don't have a valid email URL, b/c that means they're bad data
    rows_count = len(raw_data.index)
    raw_data = raw_data[raw_data["Email"].str.slice(start=0, stop=7).str.fullmatch("mailto:", case=False)]
    rows_dropped_bad_email = rows_count - len(raw_data.index)

    # Reformat email column to remove the "mailto:"
    raw_data["Email"] = raw_data["Email"].str.slice(start=7)

    # Give notice popup about dropped rows
    if rows_dropped_timestamp != 0 or rows_dropped_email_nan != 0 or rows_dropped_bad_email != 0:
        sg.Popup("Some data was dropped because of improper formatting:\nBad timestamp: " + str(rows_dropped_timestamp)
                 + " entries\nNo email associated: " + str(rows_dropped_email_nan) + " entries\nBad email value: " +
                 str(rows_dropped_bad_email) + " entries", title="Info: Data dropped")

    # Drop all "consumed" verbs b/c they seem to be pretty useless
    raw_data = raw_data[raw_data["Verb"] != 'consumed']

    # Parse the actual object ID from the "object id" column
    url_list = raw_data["object id"].to_list()
    id_list = [int(s[s.index("id=") + 3: len(s) if s.find("?", s.index("id=")) == -1 else s.find("?", s.index("id="))])
               for s in url_list]
    raw_data["object id"] = id_list

    class_list = set(raw_data["Email"])

    # import data in DayElement.json (Error handling done in Main.py)
    with open(json_path) as f:
        DayInfo = json.load(f)
        # Find path to DayElementSchema
        bundle_dir = getattr(sys, '_MEIPASS', path.abspath(path.dirname(__file__)))
        validation_path = path.abspath(path.join(bundle_dir, 'DayElementSchema.json'))
        with open(validation_path) as v:
            schema = json.load(v)
            # Perform Validation
            validate(instance=DayInfo, schema=schema)

        # Drop data from non-student emails (using the filter emails list)
        raw_data = raw_data[~raw_data["Email"].isin(DayInfo["Filter_Emails"])]
        class_list = class_list - set(DayInfo["Filter_Emails"])
        delta_max = DayInfo["Time_Delta"]
