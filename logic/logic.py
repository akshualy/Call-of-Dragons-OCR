from dataclasses import dataclass
from time import sleep

from numpy import ndarray

import constants
from emulator.adb_integration import click
from emulator.adb_integration import get_grayscale_screen
from emulator.adb_integration import go_back
from readers.screen import Coordinate
from readers.screen import get_on_screen
from readers.screen import read_at_bounding_box


@dataclass
class AllianceInformation:
    alliance_tag: str = "Error"
    alliance_name: str = "Error"
    current_members: int = 200
    max_members: int = 200


ALLIANCE_INFORMATION = AllianceInformation()


def read_current_alliance_name(image: ndarray) -> None:
    """
    Caches the name the alliance currently has.

    Args:
        image: The image to get the name from.
    """
    full_alliance_name = read_at_bounding_box(
        image=image,
        bounding_box=constants.BoundingBoxes.ALLIANCE_NAME,
        character_whitelist=None,
    )
    if not full_alliance_name:
        print("Could not read out the alliance name. It will be shown as 'Error'.")
        return

    if "]" not in full_alliance_name:
        print(
            f"There was no ] the alliance name: {full_alliance_name}. "
            "It will be shown as 'Error'."
        )
        return

    alliance_name_split = full_alliance_name.split("]")
    ALLIANCE_INFORMATION.alliance_tag = alliance_name_split[0][1:]
    ALLIANCE_INFORMATION.alliance_name = alliance_name_split[1].replace("\n", "")


def read_current_alliance_members(image: ndarray) -> None:
    """
    Caches the amount of members the alliance currently has.

    Args:
        image: The image to get the members from.
    """
    max_members = 200
    current_members = 200

    members = read_at_bounding_box(
        image=image,
        bounding_box=constants.BoundingBoxes.ALLIANCE_MEMBERS,
        character_whitelist="0123456789/",
    )

    if members and len(member_details := members.split("/")) > 0:
        current_members = int(member_details[0])
        max_members = int(member_details[1])

    ALLIANCE_INFORMATION.current_members = current_members
    ALLIANCE_INFORMATION.max_members = max_members


def read_current_alliance_information(image: ndarray) -> None:
    """
    Caches important information about the alliance we're reading out.

    Args:
        image: The image to get the information from.
    """
    read_current_alliance_members(image=image)
    read_current_alliance_name(image=image)


def leave_rankings_interface_return_current_screen(image: ndarray):
    """
    Leaves the ranking interface if it is on the screen.
    This is done to be able to read out the alliance members.

    Args:
         image: Image of the current screen.

    Returns:
        The new screen if the ranking interface was open, otherwise the current screen.
    """
    if get_on_screen(image=image, path=constants.Images.RANKINGS_INTERFACE):
        go_back()
        sleep(0.5)
        image = get_grayscale_screen()

    return image


def go_to_rankings_interface_from_known_screens(image: ndarray) -> bool:
    """
    Performs steps to go to the alliance rankings interface from various known screens.

    Args:
        image: An image of the current screen.

    Returns:
        Whether we were on a known screen.
    """

    def click_coordinates_with_delay(click_coordinates: tuple[Coordinate] | None):
        if not click_coordinates:
            return

        for coordinate in click_coordinates:
            click(coordinate)
            sleep(1)

    known_screen_steps = {
        constants.Images.ALLIANCE_RANKINGS: None,
        constants.Images.ALLIANCE_SETTINGS: (
            constants.Coordinates.OPEN_ALLIANCE_SETTINGS,
        ),
        constants.Images.ALLIANCE: (
            constants.Coordinates.OPEN_ALLIANCE,
            constants.Coordinates.OPEN_ALLIANCE_SETTINGS,
        ),
        constants.Images.MENU: (
            constants.Coordinates.MENU_TOGGLE,
            constants.Coordinates.OPEN_ALLIANCE,
            constants.Coordinates.OPEN_ALLIANCE_SETTINGS,
        ),
    }

    for image_path, coordinates in known_screen_steps.items():
        on_screen = get_on_screen(image=image, path=image_path)
        if on_screen:
            break
    else:
        return False

    click_coordinates_with_delay(click_coordinates=coordinates)
    new_screen = get_grayscale_screen()
    read_current_alliance_information(image=new_screen)
    click(constants.Coordinates.OPEN_ALLIANCE_RANKINGS)
    return True


def search_click_info_button():
    """
    Searches for the info button on the screen and clicks it.
    This is done because the position of the button changes at the end of a list,
    and depending on officer permissions.
    """
    image = get_grayscale_screen()
    info_button = get_on_screen(image=image, path=constants.Images.INFO_BUTTON)
    if info_button:
        click(
            Coordinate(
                info_button.x + constants.Offsets.INFO_BUTTON_X,
                info_button.y + constants.Offsets.INFO_BUTTON_Y,
            )
        )
    else:
        click(constants.Coordinates.INFO_BUTTON)
