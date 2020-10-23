import pandas as pd
import collections
import datetime


class ElementCollection:
    """
    Contains information about the range of user-provided H5P elements, including:
    - the H5P ID
    - the H5P element name
    - A list of students who interacted with the element
    - The percent of the class that interacted with the element
    - The time spent on the element
    """

    def __init__(self, id_list, data, class_list):
        self.id_list = id_list
        self.data = data[data["object id"].isin(self.id_list)]  # Now data can be trimmed
        self.class_list = class_list
        self.class_size = len(class_list)

        # Below are vars that are expensive time-wise to calculate, so we make em instance vars and calculate only once
        self.question_name_dict = None
        self.interacted_dict = None

    def set_expensive_instance_vars(self):
        """
        This function is meant to be called ONLY ONCE per class instance. It condenses down expensive operations so we
        only need to run them once. All variables that depend on these expensive operations are defined as instance
        variables, rather than a local variable returned by the function. This is so they can be accessed without
        re-calling the expensive function.
        """
        question_name_dict = dict.fromkeys(self.id_list)
        interacted_dict = {k: [] for k in self.id_list}

        for index, row in self.data.iterrows():
            # Question name dict stuff
            if pd.notna(row["Question/Slide"]):
                question_name_dict[row["object id"]] = row["Question/Slide"]
            # Interacted dict stuff
            if not (row["Email"] in interacted_dict[row["object id"]]):
                interacted_dict[row["object id"]].append(row["Email"])

        question_name_dict = collections.OrderedDict(sorted(question_name_dict.items()))

        self.question_name_dict = question_name_dict
        self.interacted_dict = interacted_dict

    def get_question_name_dict(self):
        """
        Iterates over the raw data. If "Question/Slide" for a row is populated, it adds it to a dictionary.

        :param: none
        :return: a dictionary with keys = H5P ID and values = Question/Slide
        """
        question_name_dict = dict.fromkeys(self.id_list)
        for index, row in self.data.iterrows():
            if pd.notna(row["Question/Slide"]):
                question_name_dict[row["object id"]] = row["Question/Slide"]

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
            if not (row["Email"] in interacted_dict[row["object id"]]):
                interacted_dict[row["object id"]].append(row["Email"])

        return interacted_dict

    def get_percent_interacted(self):
        """
        Iterates over the dictionary returned by get_interacted_dict to calculate the percent of users who interacted
        with each H5P element.

        :param: none
        :return: a dict with keys = H5P ID and values = % of users who interacted
        """
        percent_interacted_dict = dict.fromkeys(self.id_list)
        interacted_dict = self.interacted_dict
        for key in interacted_dict:
            num_interacted = len(interacted_dict[key])
            percent_interacted_dict[key] = num_interacted / self.class_size * 100

        return percent_interacted_dict

    def get_students_duration(self):
        """
        Calculates each student's time spent on the range of

        :param: none
        :return: a dictionary mapping students to their duration
        """
        durations = {}
        delta_max = datetime.timedelta(minutes=10)
        for student in self.class_list:
            student_df = self.data[self.data['Email'] == student].reset_index()
            duration = datetime.timedelta()
            for index in range(0, len(student_df) - 1):
                delta = student_df.iloc[index]['Timestamp'] - student_df.iloc[index + 1]['Timestamp']
                if delta < delta_max:
                    duration += delta
                durations[student] = duration.total_seconds() / 60
        return durations

    def get_dataframe(self):
        """
        Puts everything together into a dataframe specific for the range of H5P IDs.

        :param: none
        :return: a complete dataframe containing all we want to know from the raw data regarding specific elements
        """
        self.set_expensive_instance_vars()

        df = pd.DataFrame(index=self.id_list)
        df["object id"] = self.id_list
        df["Element Name"] = self.question_name_dict.values()
        interacted_dict_values = self.interacted_dict.values()
        df["List of users who interacted"] = interacted_dict_values
        df["Number of users who interacted"] = [len(val) for val in interacted_dict_values]
        df["% of users who interacted"] = self.get_percent_interacted().values()
        return df
