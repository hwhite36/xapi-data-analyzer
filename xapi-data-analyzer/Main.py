import GlobalData
from Day import Day
import pandas as pd

print("Welcome to the UW-Madison Chem 109 data analyzer!")
print("Authors: Walt Boettge and Harrison White\n")
print("This program will generate statistics about a range of Pressbooks chapters that you select.")
print("You will be prompted for the lower and upper bounds of the range of days (inclusive).\n")
print("A .csv file for each day will be saved in the current directory, which can be "
      "imported into Excel for further data analysis.")
print("A .csv of the time each student spent on each day will also be saved to the current directory.\n")
print("IMPORTANT NOTE: if you have any .csv files of the same name (Day x.csv or StudentDurations.csv), "
      "they WILL BE OVERWRITTEN!\n")
lowerBound = input("Please enter the lower bound: ")
upperBound = input("Please enter the upper bound: ")

print("\nThe program also depends on a .csv of the xAPI data cleaned by the DoIT Learning Locker script.")
print("It usually has a title similar to \"dataMM-DD-YY(cleaned).csv\".\n")
data_path = input("Please enter the path to the .csv containing the data: ")

GlobalData.set_data_vars(data_path)
dfDuration = pd.DataFrame(index=GlobalData.class_list)

for i in range(int(lowerBound), int(upperBound) + 1):
    day = Day(i, GlobalData.raw_data, GlobalData.class_list)
    dfDuration["Day " + str(i)] = day.get_students_duration().values()
    day.get_day_dataframe().to_csv("Day " + str(i) + ".csv")

dfDuration.to_csv("StudentDurations.csv")

print("\nAll files successfully saved!")
