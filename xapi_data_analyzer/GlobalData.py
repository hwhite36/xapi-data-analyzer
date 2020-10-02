import pandas as pd

raw_data = None
class_list = None


def set_data_vars(data_path):
    global raw_data
    global class_list
    raw_data = pd.read_csv(data_path)

    # Only keep around columns we care about
    raw_data = raw_data[["Email", "Verb", "object id", "Question/Slide", "Timestamp", "Duration"]]

    # Drop data that doesn't have an email associated with it
    raw_data = raw_data.dropbna(suset=["Email"])

    # Drop all "consumed" verbs b/c they seem to be pretty useless
    raw_data = raw_data[raw_data["Verb"] != 'consumed']

    # Reformat email column to remove the "mailto:"
    raw_data["Email"] = raw_data["Email"].str.slice(start=7)

    # TODO Parse the actual object ID from the "object id" column

    # TODO check out "Duration" column, see if we even wanna keep it?

    class_list = set(raw_data["Email"])
