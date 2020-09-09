import GlobalData
from Day import Day
import pandas as pd
import PySimpleGUI as sg


def create_main_window():
    layout = [
        [sg.Text("UW-Madison xAPI Data Analyzer", font="Any 15")],
        [sg.Text("Please select the cleaned xAPI data .csv file from the DoIT Learning Locker "
                 "(usually called dataMM-DD-YY(cleaned).csv)")],
        [sg.FileBrowse(key="FILEIN")],
        [sg.Text("Next, please enter the lower and upper bounds of the range of chapters (inclusive).")],
        [sg.Text("Lower:"), sg.InputText(size=(3, 1), key="LOWERBOUND"), sg.Text("Upper:"),
         sg.InputText(size=(3, 1), key="UPPERBOUND")],
        [sg.Text("A .csv file for each chapter will be saved in the current directory, which can be imported into Excel"
                 " for further data analysis.")],
        [sg.Text("A .csv of the time each student spent on each chapter will also be saved to the current directory.")],
        [sg.Text("If you have any .csv files of the same name (Day x.csv or StudentDurations.csv), THEY WILL BE "
                 "OVERWRITTEN!", text_color="red")],
        [sg.Button("Go", size=(4, 1)), sg.Exit()]
    ]
    return sg.Window("xAPI Data Analyzer", layout, element_justification="center")


def main():
    sg.theme("SystemDefault")

    main_window = create_main_window()
    while True:
        event, values = main_window.read()

        if event in ("Exit", None):
            break

        if event == "Go":
            try:
                # Make sure the chapter numbers are legal
                lower_bound = int(values["LOWERBOUND"])
                upper_bound = int(values["UPPERBOUND"])
                if lower_bound > upper_bound:
                    raise ValueError()
                if lower_bound <= 0:
                    raise ValueError()

                GlobalData.set_data_vars(values["FILEIN"])
                df_duration = pd.DataFrame(index=GlobalData.class_list)

                # Crank out CSVs for each day and save em to the current directory
                for i in range(int(lower_bound), int(upper_bound) + 1):
                    day = Day(i, GlobalData.raw_data, GlobalData.class_list)
                    df_duration["Chapter " + str(i)] = day.get_students_duration().values()
                    day.get_day_dataframe().to_csv("Chapter " + str(i) + ".csv")

                df_duration.to_csv("StudentDurations.csv")

                sg.Popup("All files successfully saved!", title="Success!")

            except ValueError:
                sg.Popup("ERROR: invalid input. Please enter only positive integers, and make sure the lower bound is "
                         "less than or equal to the upper bound.", title="Error")
            except FileNotFoundError:
                sg.Popup("ERROR: Data file not found! Please double-check the path to the data file and try again.",
                         title="Error")

    main_window.close()


main()
