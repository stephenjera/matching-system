import smtplib
import pandas as pd


class MatchingSystem:
    """A matching system to match people based on a specified criteria"""

    def __init__(self) -> None:
        self._matched_people = []
        self._past_matches = []
        self._matches = []
        self.operations = None
        self.support = None
        self.matched_df = None

    def match(
        self, df: pd.DataFrame, criteria: list[str], diff_department=True
    ) -> pd.DataFrame:
        """Match a dataframe on specified criteria.

        Args:
            df (pd.DataFrame): Dataframe to match
            criteria (list[str]): Criteria to match dataframe
            diff_department (bool, optional): used to match different departments. Defaults to True.

        Returns:
            pd.DataFrame: Returns the matched dataframe
        """
        if diff_department:
            self.operations, self.support = self._prep_data(df)
            self.matched_df = self.operations.merge(self.support, on=criteria)
            return self.matched_df

        _, self.support = self._prep_data(df)
        self.matched_df = self.support.merge(self.support, on=criteria)
        return self.matched_df

    def _prep_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Sort data into different departments

        Args:
            df (pd.DataFrame): Dataframe to be sorted into departments

        Returns:
            pd.DataFrame: returns the sorted dataframes
        """
        self.operations = df[df["department"] == "operations"]
        self.support = df[
            (df["department"] == "support")
            | (df["department"] == "Neither of the above")
        ]
        return self.operations, self.support

    def unique_matched(self, matched_df: pd.DataFrame):
        """Ensures a match is unique and not repeated

        Args:
            matched_df (pd.DataFrame): A dataframe with all the possible matches
        """
        for _, row in matched_df.iterrows():
            if (
                (row["email_x"] not in self._matched_people)
                and (row["email_y"] not in self._matched_people)
                and (row["email_x"] != row["email_y"])
                and row["email_x"] + "&" + row["email_y"] not in self._past_matches
            ):

                self._matches.append(row["email_x"] + "&" + row["email_y"])
                self._matched_people.append(row["email_x"])
                self._matched_people.append(row["email_y"])

    def get_matches(self) -> list:
        """Returns all the matches

        Returns:
            list: list of the matches
        """
        return self._matches

    def get_past_matches(self) -> list:
        """Returns all past matches

        Returns:
            list: a list of past matches
        """
        return self._past_matches

    def save_matches(self, file_name: str):
        """Save the matches to a CSV file

        Args:
            file_name (str): Name of file to save as
        """
        pd.DataFrame(self._matches).to_csv(file_name, mode="a")

    def load_past_matches(self, file_name: str):
        """Loads past matches into a dataframe

        Args:
            file_name (str): name of file to load
        """
        self._past_matches = pd.read_csv(file_name).values

    def get_unmatched(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get the people without a match

        Args:
            df (pd.DataFrame): Original unmodified dataframe

        Returns:
            pd.DataFrame: Dataframe of unmatched people
        """
        return df[~df.email.isin(self._matched_people)]

    def send_match_email(self, recipient: str, match: str):

        SERVER = "localhost"
        PORT = 1025

        FROM = "MatchingSystem@matching.com"
        TO = [recipient]

        SUBJECT = "Your new match"

        TEXT = f"Your new match is {match} give them an email to setup the meeting"

        message = """\
        From: %s
        To: %s
        Subject: %s

        %s
        """ % (
            FROM,
            ",".join(TO),
            SUBJECT,
            TEXT,
        )

        server = smtplib.SMTP(SERVER, PORT)
        server.sendmail(FROM, TO, message)
        server.quit()
