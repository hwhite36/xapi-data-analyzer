import GlobalData
from ElementCollection import ElementCollection
import pandas as pd
import PySimpleGUI as sg
from datetime import datetime
import pytz
import matplotlib.pyplot as plt
from pathlib import Path
import os
import json
import webbrowser
import jsonschema
import traceback


def create_main_window():
    """
    Creates the main window layout.

    :return: a PySimpleGUI Window object for the main window
    """
    layout = [
        [sg.Text("UW-Madison xAPI Data Analyzer", font="Any 15 bold")],
        [sg.Text("Please select the non-cleaned xAPI data .csv file from the DoIT Learning Locker "
                 "(usually called something like dataMM-DD-YY.csv):")],
        [sg.In(), sg.FileBrowse(key="FILEIN")],
        [sg.Text("Please select the DayElement.json file, which contains info on the timedelta and which H5P IDs "
                 "correspond to which days:")],
        [sg.In(), sg.FileBrowse(key="JSONIN")],
        [sg.HorizontalSeparator(color="black")],
        [sg.Text("This program has two modes: it can either get data for certain days (chapters) or for specific H5P "
                 "IDs. Please choose a method and only fill in one of the following text boxes.")],
        [sg.Text()],
        [sg.Text("Please enter a comma-separated list of days you would like to get data on, or enter \"all\" to "
                 "have all days with data from the spreadsheet analyzed.")],
        [sg.InputText(size=(20, 1), key="DAYLIST")],
        [sg.Text("OR", font="Any 12 bold")],
        [sg.Text("if you know the exact H5P elements you want data on, please enter a comma-separated list of "
                 "their ID numbers in the box below (leave blank if using above method).")],
        [sg.InputText(size=(20, 1), key="IDLIST")],
        [sg.HorizontalSeparator(color="black")],
        [sg.Text("The data will be saved to the current directory under the folder 'xAPI-Data-Analyzer_$TIMESTAMP/'",
                 font="Any 10 bold")],
        [sg.Button("Go", size=(4, 1), button_color=("white", "green"))],
        [sg.HorizontalSeparator(color="black")],
        [sg.Text("Need help or want to learn more? Check out our GitHub page for an in-depth explanation of the tool:")],
        [sg.Text("README", font="Any 12 underline bold", text_color="blue", enable_events=True, tooltip="Follow link")]
    ]
    return sg.Window("xAPI Data Analyzer", layout, element_justification="center")


def use_id_list(id_list, timestamp):
    """
    Controls dataframe creation and data-saving if the user chooses to enter a list of H5P IDs, as opposed to providing
    a JSON file that lists all IDs.

    :param id_list: the list of H5P IDs
    :param timestamp: timestamp string for file-naming purposes
    """
    # Create folder we want to save everything to
    save_folder = Path("xAPI-Data-Analyzer_" + timestamp + "/")
    os.mkdir(save_folder)

    # Create ElementCollection object + dataframe
    element_collection = ElementCollection(id_list, GlobalData.raw_data, GlobalData.class_list)
    elements_df = element_collection.get_dataframe()
    elements_df.to_csv(save_folder / "ElementCollection.csv")

    # create student durations dataframe
    df_students = pd.DataFrame.from_dict(element_collection.get_students_duration(GlobalData.delta_max), orient='index')
    df_students.to_csv(save_folder / "StudentDurations.csv")

    # Generate graphs
    generate_graphs(elements_df, df_students, save_folder)

    sg.Popup("All files successfully saved!", title="Success!")


def use_json(timestamp, day_dict_list):
    """
    Controls dataframe creation if the user provides a JSON file. Creates a dataframe and graphs for every day that has
    data, and outputs it into a day-specific folder within the base folder.

    :param timestamp: timestamp string for file-naming purposes
    :param day_dict_list: a list of the day dictionary objects (from JSON file) that we're analyzing
    """
    base_folder = Path("xAPI-Data-Analyzer_" + timestamp + "/")
    os.mkdir(base_folder)

    students_master = pd.DataFrame(index=GlobalData.class_list)
    units = []

    for i, day in enumerate(day_dict_list, 1):
        sg.OneLineProgressMeter("Progress", i, len(day_dict_list), orientation="h")
        # Get info from JSON file
        day_num = day['DayNumber']
        day_ids = day['Elements']
        unit_name = "Unit" + str(day['Unit'])

        # Check that data for the given Day exists
        element_collection = ElementCollection(day_ids, GlobalData.raw_data, GlobalData.class_list)
        if not element_collection.data.empty:
            # Create where we want to store the csvs and graphs
            day_folder = base_folder / ("Day" + str(day_num))
            os.mkdir(day_folder)

            # Create ElementCollection object and dataframe
            day_df = element_collection.get_dataframe()
            # Uncomment below to print the number of bytes the dataframe takes in memory
            # print("Day " + str(day_num) + ": " + str(day_df.memory_usage(index=True, deep=True).sum()))
            day_df.to_csv(day_folder / ("Day" + str(day_num) + ".csv"))

            # create student durations dataframe
            students_dict = element_collection.get_students_duration(GlobalData.delta_max)
            df_students = pd.DataFrame.from_dict(students_dict, orient='index')
            if not df_students.empty:
                df_students.to_csv(day_folder / ("StudentDurations_Day" + str(day_num) + ".csv"))
            else:
                with open(day_folder / ("StudentDurations_Day" + str(day_num) + ".txt"), "w") as text_file:
                    text_file.write("No student durations data to report for Day " + str(day_num) +
                                    ". Because of this, the student durations CSV and histogram were not generated.")

            # Update aggregated students df
            students_master["Day" + str(day_num)] = pd.Series(students_dict)
            if unit_name in students_master.columns:
                students_master[unit_name] = students_master[unit_name].add(pd.Series(students_dict), fill_value=0)
            else:
                students_master[unit_name] = pd.Series(students_dict)
                units.append(unit_name)

            # Generate and save graphs
            generate_graphs(day_df, df_students, day_folder)

    # Finish processing students_master
    # Rearrange columns
    cols = list(students_master.columns)
    for unit in units:
        cols.append(cols.pop(cols.index(unit)))
    students_master = students_master[cols]

    # Compute a totals column
    students_master['Total'] = students_master[units].sum(axis=1)
    students_master.to_csv(base_folder / "TotalDurations.csv")

    sg.Popup("All files successfully saved!", title="Success!")


def generate_graphs(element_df, duration_df, folder):
    """
    Creates graphs of the following, and saves them as a png in ``folder``:

    * % of students who interacted with each given element
    * # of students who interacted with each given element
    * Histogram of the durations that students spent on all elements in ``element_df``

    :param element_df: dataframe for an ElementCollection object
    :param duration_df: dataframe containing students' durations for the same ElementCollection object
    :param folder: Path object of the folder to save the graphs in
    """
    # Generate student % interacted graph, save to png
    element_df.plot(x="object id", y="% of users who interacted", kind="bar")
    plt.xlabel("H5P ID")
    plt.ylabel("Percent")
    plt.ylim(0, 100)
    plt.title("Students % Interacted")
    plt.savefig(folder / "student_percent_interacted.png")
    plt.close()

    # Generate student count interacted graph, save to png
    element_df.plot(x="object id", y="Number of users who interacted", kind="bar")
    plt.xlabel("H5P ID")
    plt.ylim(0, len(GlobalData.class_list))
    plt.title("Student Interacted Count")
    plt.savefig(folder / "student_count_interacted.png")
    plt.close()

    # Generate student duration histogram, save to png
    if not duration_df.empty:  # Make sure student_durations isn't empty, bc that makes the histogram a n g e r y
        duration_df.hist()
        plt.xlabel("Duration (min)")
        plt.ylabel("Number of Students")
        plt.title("Student Durations")
        plt.savefig(folder / "student_durations.png")
        plt.close()


def generate_timestamp():
    """
    Generates a timestamp string for the current time in CST to be used for file-naming.

    :return: a nicely-formatted string of the timestamp
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

        if event == "README":
            webbrowser.open("https://github.com/HBlanco36/xapi-data-analyzer")

        if event == "Go":
            # Load in the data and JSON files
            try:
                GlobalData.set_data_vars(values["FILEIN"], values["JSONIN"])
            except KeyError as e:
                sg.Popup("ERROR: The following H5P element was not found: " + str(e.args[0]), title="Error")
                continue
            except FileNotFoundError:
                sg.Popup("ERROR: A provided file was not found! Please double-check the path to the data and JSON files"
                         " and try again.", title="Error")
                continue
            except json.JSONDecodeError:
                sg.Popup("ERROR: The provided JSON file could not be read. Please ensure its formatting is correct.",
                         title="Error")
                continue
            except jsonschema.exceptions.ValidationError as e:
                message = str(e.message).replace("^Day_\\\\d{1,2}$", "Day_XX")
                sg.Popup("ERROR: The DayElement.json file is invalid, please check the Schema to ensure validity. \n"
                         + message, title="Error")
                continue

            # Generate a timestamp for naming the files
            timestamp = generate_timestamp()

            # Parse the ID list and Days list
            id_list = values["IDLIST"]
            day_num_list = values["DAYLIST"]

            # Check the "Days" list first
            if day_num_list:
                if str(day_num_list).lower().strip() == "all":  # Send in the full list of days from the JSON
                    use_json(timestamp, GlobalData.DayInfo['Days'].values())
                else:  # Parse the list of only the days the user wants and send that in instead
                    try:
                        day_num_list = [int(item.strip()) for item in day_num_list.split(",")]
                    except ValueError:
                        sg.Popup(
                            "ERROR: The items entered in the Days list were not valid integers! Please try again.",
                            title="Error")
                        continue

                    day_dict_list = []
                    for day in GlobalData.DayInfo["Days"].values():
                        if day["DayNumber"] in day_num_list:
                            day_dict_list.append(day)
                            day_num_list.remove(day["DayNumber"])

                    # If there's ints that the user entered that aren't days in JSON, let them know
                    if day_num_list:
                        sg.Popup("INFO: The following day numbers entered were not found in the JSON file. These "
                                 "values will be ignored.\n" + str(day_num_list), title="Info")

                    use_json(timestamp, day_dict_list)

            elif id_list:  # Ok, then check if the user entered IDs, and use those if so
                try:
                    id_list = [int(item.strip()) for item in id_list.split(",")]
                except ValueError:
                    sg.Popup("ERROR: The items entered in the H5P ID list were not valid integers! Please try again.",
                             title="Error")
                    continue
                use_id_list(id_list, timestamp)

            else:  # The user must've not entered anything in either input
                sg.Popup("Error: no method selected! Please read the instructions and enter appropriate values into "
                         "one of the text boxes above", title="Error")

    main_window.close()


# Kinda bad practice to have such a broad exception clause but it works well in our use case so the program exits
# gracefully and we can easily debug
try:
    main()
except Exception:
    sg.Popup("An unexpected error occurred that caused the program to crash. An error log text file was created in "
             "the current directory called 'xAPI-Data-Analyzer-ERROR-LOG.txt'. Please consider filing a bug report on "
             "our GitHub page with this file.", title="Fatal Error")
    with open("xAPI-Data-Analyzer-ERROR-LOG.txt", "a") as error_file:
        traceback.print_exc(file=error_file)
