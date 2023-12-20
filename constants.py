from readers.screen import BoundingBox
from readers.screen import Coordinate


class Images:
    MENU = "images/menu.png"
    ALLIANCE = "images/menu_alliance.png"
    ALLIANCE_SETTINGS = "images/menu_alliance_settings.png"
    ALLIANCE_RANKINGS = "images/menu_alliance_rankings.png"
    COPY_NAME = "images/copy_name.png"
    RANKINGS_INTERFACE = "images/rankings.png"
    INFO_BUTTON = "images/info_top_right.png"
    OWN_POSITION = "images/rankings_own_entry.png"


class BoundingBoxes:
    POWER = BoundingBox(min_x=115, min_y=560, max_x=355, max_y=590)
    MERIT = BoundingBox(min_x=800, min_y=560, max_x=1020, max_y=590)
    LORD_ID = BoundingBox(min_x=910, min_y=268, max_x=1019, max_y=288)
    ALLIANCE_MEMBERS = BoundingBox(min_x=360, min_y=610, max_x=455, max_y=635)
    ALLIANCE_NAME = BoundingBox(min_x=120, min_y=450, max_x=450, max_y=485)
    OWN_POSITION = BoundingBox(min_x=0, min_y=0, max_x=69, max_y=69)


class Coordinates:
    MENU_TOGGLE = Coordinate(1237, 660)
    OPEN_ALLIANCE = Coordinate(983, 667)
    OPEN_ALLIANCE_SETTINGS = Coordinate(992, 73)
    OPEN_ALLIANCE_RANKINGS = Coordinate(945, 225)
    LIST_ENTRY = Coordinate(500, 350)
    INFO_BUTTON = Coordinate(478, 415)
    LIST_ENTRY_MIDDLE = Coordinate(800, 351)
    LIST_ENTRY_MIDDLE_UP = Coordinate(800, 260)


class Offsets:
    ENTRY_DISTANCE = 75
    INFO_BUTTON_X = 90
    INFO_BUTTON_Y = 30


def increase_list_entry_constants_by_one_entry() -> None:
    """
    Increases constants where the y position is a specific entry position in the
    rankings list by one entry.
    This is needed to skip the own entry and to reach entries at the bottom of the list.
    """
    Coordinates.LIST_ENTRY.y += Offsets.ENTRY_DISTANCE
    Coordinates.INFO_BUTTON.y += Offsets.ENTRY_DISTANCE
    Coordinates.LIST_ENTRY_MIDDLE.y += Offsets.ENTRY_DISTANCE
    Coordinates.LIST_ENTRY_MIDDLE_UP.y += Offsets.ENTRY_DISTANCE
