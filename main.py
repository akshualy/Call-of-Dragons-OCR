from datetime import datetime
import os
from time import sleep

import dotenv
from pytesseract import pytesseract

import constants
from emulator.adb_integration import ADB
from emulator.adb_integration import click
from emulator.adb_integration import get_clipboard
from emulator.adb_integration import get_grayscale_screen
from emulator.adb_integration import go_back
from emulator.adb_integration import scroll_low_level
from logic.logic import ALLIANCE_INFORMATION
from logic.logic import go_to_rankings_interface_from_known_screens
from logic.logic import leave_rankings_interface_return_current_screen
from logic.logic import search_click_info_button
from readers.screen import get_on_screen
from readers.screen import read_numbers_at_bounding_box


def main():
    data = {}

    image = get_grayscale_screen()

    image = leave_rankings_interface_return_current_screen(image=image)
    if not go_to_rankings_interface_from_known_screens(image=image):
        print(
            "You are not on a screen the program supports yet. "
            "Please try starting from somewhere else (Base, Alliance Overview, ...)"
        )
        return

    sleep(0.5)

    print(
        "Reading rankings leaderboard of "
        f"[{ALLIANCE_INFORMATION.alliance_tag}] "
        f"{ALLIANCE_INFORMATION.alliance_name} (Members: "
        f"{ALLIANCE_INFORMATION.current_members}/{ALLIANCE_INFORMATION.max_members})"
    )

    image = get_grayscale_screen()
    own_position = 0
    own_entry_coordinates = get_on_screen(
        image=image, path=constants.Images.OWN_POSITION
    )
    if own_entry_coordinates:
        constants.BoundingBoxes.OWN_POSITION.min_x += own_entry_coordinates.x
        constants.BoundingBoxes.OWN_POSITION.max_x += own_entry_coordinates.x
        constants.BoundingBoxes.OWN_POSITION.min_y += own_entry_coordinates.y
        constants.BoundingBoxes.OWN_POSITION.max_y += own_entry_coordinates.y
        own_position = read_numbers_at_bounding_box(
            image=image, bounding_box=constants.BoundingBoxes.OWN_POSITION
        )
        print(f"Position in the rankings of the current account is {own_position}.")

    if own_position == 0:
        own_position = int(
            input(
                "Could not read the current rank of the account. " "Please enter it: "
            )
        )

    last = own_position >= ALLIANCE_INFORMATION.current_members - 5

    repeated_fail_count = 0
    current_rank = 1
    while current_rank <= ALLIANCE_INFORMATION.current_members:
        bottom_of_list = current_rank >= ALLIANCE_INFORMATION.current_members - (
            3 if last else 4
        )

        if current_rank == own_position:
            current_rank += 1
            constants.increase_list_entry_constants_by_one_entry()
            continue

        if bottom_of_list and repeated_fail_count == 0:
            constants.increase_list_entry_constants_by_one_entry()

        click(constants.Coordinates.LIST_ENTRY)
        sleep(1)

        if bottom_of_list:
            search_click_info_button()
        else:
            click(constants.Coordinates.INFO_BUTTON)
        sleep(1)

        image = get_grayscale_screen()

        copy_name_position = get_on_screen(image, path=constants.Images.COPY_NAME)
        if not copy_name_position:
            # TODO Make more effort to re-jump into the rankings,
            #   depending on INFO button or profile on screen.
            if repeated_fail_count == 5:
                print(f"Failed to read rank {current_rank} 5 times, exiting.")
                break

            print(
                f"Could not read the name of the user at rank {current_rank}. Retrying."
            )
            repeated_fail_count += 1
            continue

        repeated_fail_count = 0
        click(copy_name_position.get_middle())
        name = get_clipboard()

        power = read_numbers_at_bounding_box(image, constants.BoundingBoxes.POWER)
        merit = read_numbers_at_bounding_box(image, constants.BoundingBoxes.MERIT)
        lord_id = read_numbers_at_bounding_box(image, constants.BoundingBoxes.LORD_ID)

        go_back()
        data[lord_id] = {"name": name, "power": power, "merit": merit}
        sleep(0.1)

        if bottom_of_list:
            current_rank += 1
            continue

        # It seems that the scrolling gets put off slowly over time.
        # Subtracting 1 from LIST_ENTRY_MIDDLE_UP did not fix it, so we "subtract" 0.1.
        if current_rank % 100 == 0:
            scroll_low_level(
                constants.Coordinates.LIST_ENTRY_MIDDLE,
                constants.Coordinates.LIST_ENTRY_MIDDLE_UP.clone().add(0, 10),
            )
            current_rank += 1
            continue

        scroll_low_level(
            constants.Coordinates.LIST_ENTRY_MIDDLE,
            constants.Coordinates.LIST_ENTRY_MIDDLE_UP,
        )
        current_rank += 1

    file_name = (
        f"{datetime.now().strftime('%Y-%m-%d_%H-%M')}_"
        f"{ALLIANCE_INFORMATION.alliance_name.replace(' ', '-')}"
    )
    with open(file_name + ".csv", "w", encoding="utf-8") as csv:
        csv.write("Lord ID,Name,Power,Merit\n")
        for lord_id, name_power_merit in data.items():
            csv.write(
                f"{lord_id},"
                f"{name_power_merit['name']},"
                f"{name_power_merit['power']},"
                f"{name_power_merit['merit']}\n"
            )


if __name__ == "__main__":
    dotenv.load_dotenv(".env")

    pytesseract.tesseract_cmd = os.getenv("TESSERACT_BINARY")

    ADB.adb_path = os.getenv("ADB_BINARY")
    ADB.device_name = os.getenv("ADB_DEVICE_NAME", "emulator-5554")
    ADB.shell = f"{ADB.adb_path} -s {ADB.device_name} shell"

    if not os.path.isfile(pytesseract.tesseract_cmd):
        print("The environment variable TESSERACT_BINARY is not set. Exiting.")
        exit(0)

    if not os.path.isfile(ADB.adb_path):
        print("The environment variable TESSERACT_BINARY is not set. Exiting.")
        exit(0)

    main()
