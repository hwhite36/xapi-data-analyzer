from . import GlobalData
from .Day import Day
import pandas as pd
import os


def clear():
    # Windows
    if os.name == "nt":
        os.system("cls")

    # Unix-based OSes
    else:
        os.system("clear")


def main():
    clear()
    print("Welcome to the UW-Madison Chem 109 data analyzer!")
    print("Authors: Walt Boettge and Harrison White\n")

    view_help = input("Would you like to view instructions? [y/N] ")
    if view_help == "y" or view_help == "Y" or view_help == "Yes" or view_help == "yes":
        clear()
        print("This program will generate statistics about a range of Pressbooks chapters (AKA \"Days\", "
              "as they're called in the Chem 109 curriculum) that you select.")
        print("You will be prompted for the lower and upper bounds of the range of days (inclusive).\n")
        print("The program also depends on a .csv of the xAPI data cleaned by the DoIT Learning Locker script.")
        print("It usually has a title similar to \"dataMM-DD-YY(cleaned).csv\".")
        print("You will be prompted to enter the path to this data file on your computer.\n")
        print("A .csv file for each day will be saved in the current directory, which can be "
              "imported into Excel for further data analysis.")
        print("A .csv of the time each student spent on each day will also be saved to the current directory.\n")
        print("IMPORTANT NOTE: if you have any .csv files of the same name (Day x.csv or StudentDurations.csv), "
              "they WILL BE OVERWRITTEN!\n")
    else:
        clear()

    lower_bound = None
    upper_bound = None
    input_incorrect = True
    while input_incorrect:
        lower_bound = input("Please enter the lower bound: ")
        upper_bound = input("Please enter the upper bound: ")
        try:
            lower_bound = int(lower_bound)
            upper_bound = int(upper_bound)
            if lower_bound > upper_bound:
                raise ValueError()
            if lower_bound <= 0:
                raise ValueError()
            input_incorrect = False
        except ValueError:
            print("ERROR: invalid input. Please enter only positive integers, and make sure the lower bound is "
                  "less than or equal to the upper bound.\n")

    input_incorrect = True
    while input_incorrect:
        data_path = input("Please enter the path to the .csv containing the data: ")
        try:
            GlobalData.set_data_vars(data_path)
            df_duration = pd.DataFrame(index=GlobalData.class_list)

            for i in range(int(lower_bound), int(upper_bound) + 1):
                day = Day(i, GlobalData.raw_data, GlobalData.class_list)
                df_duration["Day " + str(i)] = day.get_students_duration().values()
                day.get_day_dataframe().to_csv("Day " + str(i) + ".csv")

            df_duration.to_csv("StudentDurations.csv")
            clear()
            input_incorrect = False
        except FileNotFoundError:
            print("\nERROR: Data file not found! Please double-check the path to the data file and try again.\n")

    print("All files successfully saved!")
