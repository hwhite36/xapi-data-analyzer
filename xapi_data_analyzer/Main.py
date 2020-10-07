import GlobalData
from ElementCollection import ElementCollection
import pandas as pd
import PySimpleGUI as sg
from datetime import datetime
import pytz
import matplotlib.pyplot as plt


def create_main_window():
    layout = [
        [sg.Text("UW-Madison xAPI Data Analyzer", font="Any 15 bold")],
        [sg.Text("Please select the cleaned xAPI data .csv file from the DoIT Learning Locker "
                 "(usually called dataMM-DD-YY(cleaned).csv)")],
        [sg.FileBrowse(key="FILEIN")],
        [sg.Text("Next, please enter a comma-separated list of the H5P element ID numbers you would like to be "
                 "included in the box below.")],
        [sg.Text("If the field is left blank, all data will be analyzed and organized based on Day")],
        [sg.InputText(size=(20, 1), key="IDLIST")],
        [sg.Text("Two files will be saved to the current directory:")],
        [sg.Text("xAPI-Data-Analyzer_$TIMESTAMP.csv and StudentDurations_$TIMESTAMP.csv", font="Any 10 bold")],
        [sg.Button("Go", size=(4, 1)), sg.Exit()]
    ]
    return sg.Window("xAPI Data Analyzer", layout, element_justification="center")


def use_id_list(id_list):
    try:
        # Generate a CST timestamp + ElementCollection object
        timestamp = str(datetime.now(pytz.timezone("America/Chicago")))
        element_collection = ElementCollection(id_list, GlobalData.raw_data, GlobalData.class_list)

        # Make the timestamp a little prettier
        timestamp = timestamp.replace(" ", "_")
        timestamp = timestamp.replace(":", "-")
        timestamp = timestamp[:timestamp.rindex(".")]

        elements_df = element_collection.get_dataframe()
        elements_df.to_csv("xAPI-Data-Analyzer_" + str(timestamp) + ".csv")

        df_students = pd.DataFrame.from_dict(element_collection.get_students_duration(), orient='index')
        df_students.to_csv("StudentDurations_" + str(timestamp) + ".csv")

        sg.Popup("All files successfully saved!", title="Success!")

    except KeyError as e:
        sg.Popup("ERROR: The following H5P element was not found: " + str(e.args[0]), title="Error")
    except FileNotFoundError:
        sg.Popup("ERROR: Data file not found! Please double-check the path to the data file and try again.",
                 title="Error")
    except ValueError:
        sg.Popup("ERROR: The items entered in the H5P ID list were not valid integers! Please try again.",
                 title="Error")

    # Generate graphs window
    graphs_window = create_graphs_window()
    while True:
        event, values = graphs_window.read()

        if event is None:
            break

        if event == "Student % Interacted Graph":
            elements_df.plot(x="object id", y="% of users who interacted", kind="bar")
            plt.xlabel("H5P ID")
            plt.ylabel("Percent")
            plt.ylim(0, 100)
            plt.show()

        if event == "Student Count Interacted Graph":
            elements_df.plot(x="object id", y="Number of users who interacted", kind="bar")
            plt.xlabel("H5P ID")
            plt.ylim(0, len(GlobalData.class_list))
            plt.show()

        if event == "Student Duration Graph":
            df_students.hist()
            plt.xlabel("Duration (min)")
            plt.ylabel("Number of Students")
            plt.title("Student Durations")
            plt.show()

    graphs_window.close()

def use_json():
    days = GlobalData.DayInfo['Days']
    timestamp = datetime.now(pytz.timezone("America/Chicago"))

    for day in days.values():
        day_num = day['DayNumber']
        day_ids = day['Elements']

        element_collection = ElementCollection(day_ids, GlobalData.raw_data, GlobalData.class_list)
        element_collection.get_dataframe().to_csv("Day" + str(day_num) + "_" + str(timestamp) + ".csv")

        df_students = pd.DataFrame.from_dict(element_collection.get_students_duration(), orient='index')
        df_students.to_csv("StudentDurations_Day" + str(day_num) + str(timestamp) + ".csv")

def create_graphs_window():
    layout = [
        [sg.Text("Generate Graphs", font="Any 15 bold")],
        [sg.Text("All files have been successfully saved into the current directory!")],
        [sg.Text("If you would like, you can generate some graphs now, or use the files to make your own.")],
        [sg.Text("Generate:")],
        [sg.Button("Student % Interacted Graph", button_color=("white", "green"), size=(30, 1))],
        [sg.Button("Student Count Interacted Graph", button_color=("white", "green"), size=(30, 1))],
        [sg.Button("Student Duration Graph", button_color=("white", "green"), size=(30, 1))]
    ]
    return sg.Window("Generate Graphs", layout, element_justification="center")


def main():
    sg.theme("SystemDefault")

    main_window = create_main_window()
    while True:
        event, values = main_window.read()

        if event in ("Exit", None):
            break

        if event == "Go":
            try:
                GlobalData.set_data_vars(values["FILEIN"])
            except KeyError as e:
                sg.Popup("ERROR: The following H5P element was not found: " + str(e.args[0]), title="Error")

            # Parse the ID list
            id_list = values["IDLIST"]

            # If the user entered IDs, use those. Otherwise, use the json data
            if id_list:
                id_list = [int(item.strip()) for item in id_list.split(",")]
                use_id_list(id_list)
            else:
                use_json()

    main_window.close()

main()
