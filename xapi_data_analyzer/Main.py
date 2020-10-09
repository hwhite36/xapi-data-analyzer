import GlobalData
from ElementCollection import ElementCollection
import pandas as pd
import PySimpleGUI as sg
from datetime import datetime
import pytz
import matplotlib.pyplot as plt
from pathlib import Path
import os


def create_main_window():  # TODO add browse button for json file, add more text describing options
    """
    TODO fill in

    :return:
    """
    layout = [
        [sg.Text("UW-Madison xAPI Data Analyzer", font="Any 15 bold")],
        [sg.Text("Please select the xAPI data .csv file from the DoIT Learning Locker "
                 "(usually called something like dataMM-DD-YY.csv)")],
        [sg.FileBrowse(key="FILEIN")],
        [sg.Text("If you would like the data to be automatically organized by Day (recommended), please select "
                 "the DayElement.json file")],
        [sg.FileBrowse(key="JSONIN")],
        [sg.Text("Or, if you know the exact H5P elements you want data on, please enter a comma-separated list of "
                 "their ID numbers in the box below (leave blank if using the JSON file).")],
        [sg.InputText(size=(20, 1), key="IDLIST")],
        [sg.Text("Two files will be saved to the current directory:")],
        [sg.Text("xAPI-Data-Analyzer_$TIMESTAMP.csv and StudentDurations_$TIMESTAMP.csv", font="Any 10 bold")],
        [sg.Button("Go", size=(4, 1)), sg.Exit()]
    ]
    return sg.Window("xAPI Data Analyzer", layout, element_justification="center")


def use_id_list(id_list, timestamp):
    """
    TODO Fill in

    :param id_list:
    :param timestamp:
    :return:
    """
    # Create folder we want to save everything to
    save_folder = Path("xAPI-Data-Analyzer_" + timestamp + "/")
    os.mkdir(save_folder)

    # Create ElementCollection object + dataframe
    element_collection = ElementCollection(id_list, GlobalData.raw_data, GlobalData.class_list)
    elements_df = element_collection.get_dataframe()
    elements_df.to_csv(save_folder / "ElementCollection.csv")

    # create student durations dataframe
    df_students = pd.DataFrame.from_dict(element_collection.get_students_duration(), orient='index')
    df_students.to_csv(save_folder / "StudentDurations.csv")

    # Generate graphs
    generate_graphs(elements_df, df_students, save_folder)

    sg.Popup("All files successfully saved!", title="Success!")


def use_json(timestamp):
    """
    TODO fill in

    :param timestamp:
    :return:
    """
    days = GlobalData.DayInfo['Days']
    base_folder = Path("xAPI-Data-Analyzer_" + timestamp + "/")
    os.mkdir(base_folder)

    for day in days.values():
        # Get info from JSON file
        day_num = day['DayNumber']
        day_ids = day['Elements']

        # Create where we want to store the csvs and graphs
        day_folder = base_folder / ("Day" + str(day_num))
        os.mkdir(day_folder)

        # Create ElementCollection object and dataframe
        element_collection = ElementCollection(day_ids, GlobalData.raw_data, GlobalData.class_list)
        day_df = element_collection.get_dataframe()
        day_df.to_csv(day_folder / ("Day" + str(day_num) + ".csv"))

        # create student durations dataframe
        df_students = pd.DataFrame.from_dict(element_collection.get_students_duration(), orient='index')
        df_students.to_csv(day_folder / ("StudentDurations_Day" + str(day_num) + ".csv"))

        # Generate and save graphs
        generate_graphs(day_df, df_students, day_folder)


def generate_graphs(element_df, duration_df, folder):
    """
    TODO fill in

    :param element_df:
    :param duration_df:
    :param folder:
    :return:
    """
    # Generate student % interacted graph, save to png
    element_df.plot(x="object id", y="% of users who interacted", kind="bar")
    plt.xlabel("H5P ID")
    plt.ylabel("Percent")
    plt.ylim(0, 100)
    plt.title("Students % Interacted")
    plt.savefig(folder / "student_percent_interacted.png")

    # Generate student count interacted graph, save to png
    element_df.plot(x="object id", y="Number of users who interacted", kind="bar")
    plt.xlabel("H5P ID")
    plt.ylim(0, len(GlobalData.class_list))
    plt.title("Student Interacted Count")
    plt.savefig(folder / "student_count_interacted.png")

    # Generate student duration histogram, save to png
    duration_df.hist()
    plt.xlabel("Duration (min)")
    plt.ylabel("Number of Students")
    plt.title("Student Durations")
    plt.savefig(folder / "student_durations.png")


def generate_timestamp():
    """
    TODO fill in

    :return:
    """
    # Generate a CST timestamp
    timestamp = str(datetime.now(pytz.timezone("America/Chicago")))
    # Make the string a little prettier
    timestamp = timestamp.replace(" ", "_")
    timestamp = timestamp.replace(":", "-")
    timestamp = timestamp[:timestamp.rindex(".")]
    return timestamp


def main():
    sg.theme("SystemDefault")

    main_window = create_main_window()
    while True:
        event, values = main_window.read()

        if event in ("Exit", None):
            break

        if event == "Go":
            try:
                GlobalData.set_data_vars(values["FILEIN"], values["JSONIN"])
            except KeyError as e:
                sg.Popup("ERROR: The following H5P element was not found: " + str(e.args[0]), title="Error")
                continue
            except FileNotFoundError:
                sg.Popup("ERROR: Data file not found! Please double-check the path to the data file and try again.",
                         title="Error")
                continue

            # Parse the ID list
            id_list = values["IDLIST"]

            # Generate a timestamp for naming the files
            timestamp = generate_timestamp()

            # If the user entered IDs, use those. Otherwise, use the json data
            if id_list:
                try:
                    id_list = [int(item.strip()) for item in id_list.split(",")]
                    use_id_list(id_list, timestamp)
                except ValueError:
                    sg.Popup("ERROR: The items entered in the H5P ID list were not valid integers! Please try again.",
                             title="Error")
                    continue
            else:
                use_json(timestamp)

    main_window.close()


main()
