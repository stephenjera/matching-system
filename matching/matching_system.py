import os
import os.path
from subprocess import Popen, CREATE_NEW_CONSOLE
import pandas as pd
from class_matching_system import MatchingSystem


if __name__ == "__main__":
    data = pd.read_excel("../Matching_System_TestData.xlsx", sheet_name="Sheet1")

    # Get sum of null values
    null_values = data.isna().sum()

    # Drop columns with only null values
    for index_name in data.isna().sum().index:
        if null_values[index_name] == len(data):
            data.drop(columns=index_name, axis=0, inplace=True)

    # Rename columns
    rename_cols = {
        "Start time": "start_time",
        "Completion time": "completion_time",
        "Name": "name",
        "Email": "email",
        "In which part of Harman group do you work? (select one only)": "department",
        "What’s your preferred meeting method? (select one only)": "meeting_method",
        "Which office are you able to access for an in-person meeting? (select one only)": "office_location",
    }
    data.rename(columns=rename_cols, inplace=True)

    # Drop unused columns
    data.drop(
        columns=["start_time", "completion_time", "ID", "name"], axis=0, inplace=True
    )

    # Run matching system
    matching_system = MatchingSystem()

    if os.path.exists("past_matches.csv"):
        matching_system.load_past_matches("past_matches.csv")

    match1 = matching_system.match(
        df=data, criteria=["meeting_method", "office_location"]
    )
    matching_system.unique_matched(match1)

    match2 = matching_system.match(df=data, criteria=["meeting_method"])
    matching_system.unique_matched(match2)

    match3 = matching_system.match(df=data, criteria=["office_location"])
    matching_system.unique_matched(match3)

    match4 = matching_system.match(
        df=data, criteria=["meeting_method", "office_location"], diff_department=False
    )
    matching_system.unique_matched(match4)

    match5 = matching_system.match(
        df=data, criteria=["meeting_method"], diff_department=False
    )
    matching_system.unique_matched(match5)

    matching_system.save_matches("past_matches.csv")

    Popen(
        "python -m smtpd -c DebuggingServer -n localhost:1025",
        creationflags=CREATE_NEW_CONSOLE,
    )

    people_matched = matching_system.get_matches()
    for emails in people_matched:
        split_emails = emails.split("&")
        matching_system.send_match_email(split_emails[0], split_emails[1])
        matching_system.send_match_email(split_emails[1], split_emails[0])
