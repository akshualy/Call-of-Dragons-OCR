import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from exporters import AbstractExporter
from logic.logic import ALLIANCE_INFORMATION

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class GoogleSheetsExporter(AbstractExporter):
    def export(self, user_data: dict[int, dict[str, int | str]]):
        """
        Exports given user data to Google Sheets.
        Currently, does not support creating sheets, but will support it in the future.
        """
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open("token.json", "w") as token:
                token.write(creds.to_json())

        spreadsheet_id = os.getenv("GOOGLE_SPREADSHEET_ID")
        try:
            service = build("sheets", "v4", credentials=creds)
            spreadsheet_service = service.spreadsheets()

            spreadsheet = spreadsheet_service.get(
                spreadsheetId=spreadsheet_id
            ).execute()
            for sheet in spreadsheet["sheets"]:
                if sheet["properties"]["title"] == ALLIANCE_INFORMATION.alliance_name:
                    alliance_sheet_max_range = sheet["properties"]["gridProperties"][
                        "columnCount"
                    ]
                    break
            else:
                print(
                    "There is no sheet for the alliance yet, it will be created. "
                    "In case of an alliance rename, abort (CTRL + C) "
                    "and rename the sheet online first."
                )
                alliance_sheet_max_range = 26

            spreadsheet_values = (
                spreadsheet_service.values()
                .get(
                    spreadsheetId=spreadsheet_id,
                    range=(
                        f"{ALLIANCE_INFORMATION.alliance_name}!"
                        f"A2:{column_count_to_column_letter(alliance_sheet_max_range)}"
                    ),
                    valueRenderOption="UNFORMATTED_VALUE",
                )
                .execute()
            )
            existing_values = spreadsheet_values.get("values")

            new_values = []

            if not existing_values:
                # TODO Append all to new values
                return

            last_column = len(max(existing_values, key=len))
            for row in existing_values:
                filled_row = [
                    row[cell_idx] if len(row) - 1 >= cell_idx and row[cell_idx] else 0
                    for cell_idx in range(last_column)
                ]

                lord_id: int = row[0]
                given_user = user_data.pop(lord_id, {})
                power = given_user.get("power", 0)
                merit = given_user.get("merit", 0)

                if given_user.get("name"):
                    filled_row[1] = given_user["name"]

                filled_row.extend(
                    [
                        power,
                        merit,
                        power - filled_row[-4],
                        merit - filled_row[-3],
                    ]
                )
                new_values.append(filled_row)

            for lord_id, given_user in user_data.items():
                filled_row = [0] * last_column
                filled_row[0] = lord_id
                filled_row[1] = given_user["name"]
                filled_row.extend(
                    [
                        given_user["power"],
                        given_user["merit"],
                        0,
                        0,
                    ]
                )
                new_values.append(filled_row)

            spreadsheet_service.values().update(
                spreadsheetId=spreadsheet_id,
                range=(
                    f"{ALLIANCE_INFORMATION.alliance_name}!"
                    f"A2:{column_count_to_column_letter(alliance_sheet_max_range + 4)}"
                ),
                body={"values": new_values},
                valueInputOption="USER_ENTERED",
            ).execute()

        except HttpError as err:
            print(err)


def column_count_to_column_letter(column_count: int):
    """
    Calculates the letter associated to the given column index/count.

    Args:
        column_count: The amount of columns in the sheet.

    Returns:
        The letter associated to that column "index", e.g. "A" for 0, "AA" for 27, etc.
    """
    result = []

    while column_count:
        column_count, remainder = divmod(column_count - 1, 26)
        result.append(chr(ord("A") + remainder))

    return "".join(reversed(result))
