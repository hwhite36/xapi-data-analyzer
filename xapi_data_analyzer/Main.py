from . import GlobalData
from .Day import Day
import pandas as pd


def main():
    print("Welcome to the UW-Madison Chem 109 data analyzer!")
    print("Authors: Walt Boettge and Harrison White\n")
    print("This program will generate statistics about a range of Pressbooks chapters (AKA \"Days\", "
          "as they're called in the Chem 109 curriculum) that you select.")
    print("You will be prompted for the lower and upper bounds of the range of days (inclusive).\n")
    print("A .csv file for each day will be saved in the current directory, which can be "
          "imported into Excel for further data analysis.")
    print("A .csv of the time each student spent on each day will also be saved to the current directory.\n")
    print("IMPORTANT NOTE: if you have any .csv files of the same name (Day x.csv or StudentDurations.csv), "
          "they WILL BE OVERWRITTEN!\n")
    lower_bound = input("Please enter the lower bound: ")
    upper_bound = input("Please enter the upper bound: ")

    print("\nThe program also depends on a .csv of the xAPI data cleaned by the DoIT Learning Locker script.")
    print("It usually has a title similar to \"dataMM-DD-YY(cleaned).csv\".\n")
    data_path = input("Please enter the path to the .csv containing the data: ")

    GlobalData.set_data_vars(data_path)
    df_duration = pd.DataFrame(index=GlobalData.class_list)

    for i in range(int(lower_bound), int(upper_bound) + 1):
        day = Day(i, GlobalData.raw_data, GlobalData.class_list)
        df_duration["Day " + str(i)] = day.get_students_duration().values()
        day.get_day_dataframe().to_csv("Day " + str(i) + ".csv")

    df_duration.to_csv("StudentDurations.csv")

    print("\nAll files successfully saved!")
