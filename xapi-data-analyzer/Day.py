import pandas as pd
import collections
import re


class Day:
    """
    Contains information about a Pressbooks chapter, including:
    - Day Number/title
    - the H5P elements in the chapter
    - Students who interacted with H5P elements within the day
    """

    def __init__(self, day_number, data, class_list):
        self.day_number = day_number
        self.data = data  # Needed so generate_id_list has some data
        self.id_list = self.generate_id_list()
        self.data = data[data["H5P ID"].isin(self.id_list)]  # Now data can be trimmed
        self.class_list = class_list
        self.class_size = len(class_list)

    def generate_id_list(self):
        """
        :return: a list of H5P id's corresponding with the day
        """
        id_list = set([])
        pattern = re.compile("D0?" + str(self.day_number) + "|" + "Day0?" + str(self.day_number))

        for index, row in self.data.iterrows():
            if re.match(pattern, str(row["Question/Slide"])):
                id_list.add(row["H5P ID"])
        return sorted(id_list)

    def get_question_name_dict(self):
        """
        Iterates over the raw data. If "Question/Slide" for a row is populated, it adds it to a dictionary.
        :param: none
        :return: a dictionary with keys = H5P ID and values = Question/Slide
        """
        question_name_dict = {}
        for index, row in self.data.iterrows():
            if pd.notna(row["Question/Slide"]):
                question_name_dict[row["H5P ID"]] = row["Question/Slide"]

        # Sorts the dictionary by key, but preserves dictionary type
        question_name_dict = collections.OrderedDict(sorted(question_name_dict.items()))
        return question_name_dict

    def get_interacted_dict(self):
        """
        Iterates over the raw data. Adds a user to a dictionary if they interacted with an element (defined by
        certain verbs in xAPI).
        :param: none
        :return: a dict with keys = H5P ID and values = lists of users who interacted
        """
        interacted_dict = {k: [] for k in self.id_list}
        for index, row in self.data.iterrows():
            if (row["Verb"] == "interacted" or row["Verb"] == "attempted" or row["Verb"] == "progressed"
                    or row["Verb"] == "completed" or row["Verb"] == "experienced") and pd.notna(row["Email"]):
                if not (row["Email"] in interacted_dict[row["H5P ID"]]):
                    interacted_dict[row["H5P ID"]].append(row["Email"])

        return interacted_dict

    def get_percent_interacted(self):
        """
        Iterates over the dictionary returned by get_interacted_dict to calculate the percent of users who interacted with
        each H5P element.
        :param: none
        :return: a dict with keys = H5P ID and values = % of users who interacted
        """
        percent_interacted_dict = dict.fromkeys(self.id_list)
        interacted_dict = self.get_interacted_dict()
        for key in interacted_dict:
            num_interacted = len(interacted_dict[key])
            percent_interacted_dict[key] = num_interacted / self.class_size * 100

        return percent_interacted_dict

    def get_duration(self):
        """
        Calculates approximate time spent.

        This looks in the "duration" column of the raw data and calculates the average of any values there for each
        element. Not perfect, but if the data in the duration column is actually representative of time taken,
        it should give a ballpark number.
        :param: none
        :return: a dict with keys = H5P ID and values = average time spent
        """
        duration_dict = {k: [] for k in self.id_list}
        for index, row in self.data.iterrows():
            if pd.notna(row["Duration"]):
                duration_dict[row["H5P ID"]].append(row["Duration"])

        average_duration_dict = dict.fromkeys(self.id_list)
        for key in duration_dict:
            num_elements = len(duration_dict[key])
            try:
                average_duration_dict[key] = sum(duration_dict[key]) / num_elements
            except ZeroDivisionError:
                average_duration_dict[key] = "N/A"

        return average_duration_dict

    def get_students_duration(self):
        """
        :param: none
        :return: a dictionary mapping students to their duration on the day
        """
        students_duration_dict = {k: [0] for k in self.class_list}
        for index, row in self.data.iterrows():
            if pd.notna(row["Email"]) and pd.notna(row["Duration"]):
                students_duration_dict[row["Email"]].append(row["Duration"])

        for student in self.class_list:
            students_duration_dict[student] = max(students_duration_dict[student])

        return students_duration_dict

    def get_day_dataframe(self):
        """
        Puts everything together into a dataframe specific for the day.
        :param: none
        :return: a complete dataframe containing all we want to know from the raw data regarding specific elements
        """
        df = pd.DataFrame(index=self.id_list)
        df["H5P ID"] = self.id_list
        df["Element Name"] = self.get_question_name_dict().values()
        df["List of users who interacted"] = self.get_interacted_dict().values()
        df["% of users who interacted"] = self.get_percent_interacted().values()
        df["Average duration (sec)"] = self.get_duration().values()
        return df
