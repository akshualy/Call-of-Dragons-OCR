from dataclasses import dataclass
import re
import subprocess
from time import sleep

import cv2
import numpy
from numpy import ndarray

from readers.screen import Coordinate


@dataclass
class ADB:
    adb_path: str = ""
    device_name: str = ""
    shell: str = ""


ADB = ADB()


def get_grayscale_screen() -> ndarray:
    """
    Gets a ndarray which contains the values of the gray-scaled pixels
    currently on the screen, through ADB.

    Returns:
        The ndarray containing the gray-scaled pixels.
    """
    with subprocess.Popen(
        f"{ADB.shell} screencap -p",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        shell=True,
    ) as adb_shell:
        image_bytes_str = adb_shell.stdout.read().replace(b"\r\n", b"\n")

    raw_image = numpy.frombuffer(image_bytes_str, dtype=numpy.uint8)
    return cv2.imdecode(raw_image, cv2.IMREAD_GRAYSCALE)


def click(coordinate: Coordinate):
    """
    Tap a specific coordinate through ADB.

    Args:
        coordinate: The coordinate where to tap/click.
    """
    subprocess.check_output(f"{ADB.shell} input tap {coordinate.x} {coordinate.y}")


def go_back():
    """
    Utility method to fulfill the action which goes back one screen,
    however the current app might interpret that.
    """
    subprocess.check_output(f"{ADB.shell} input keyevent KEYCODE_BACK")


def scroll_low_level(
    coordinate_from: Coordinate, coordinate_to: Coordinate, steps: int = 5
):
    """
    Swipe from a given coordinate to a given coordinate within a given duration.
    This takes a low level approach and sends raw input events.
    Enables us to hold before releasing and disables the game's "smooth scroll".

    Args:
        coordinate_from: The coordinate from where to begin swiping.
        coordinate_to: The coordinate where to stop swiping.
        steps: The steps taken to go from one to the other.
    """
    subprocess.run(f"{ADB.shell} sendevent /dev/input/event2 3 53 {coordinate_from.x}")
    subprocess.run(f"{ADB.shell} sendevent /dev/input/event2 3 54 {coordinate_from.y}")
    subprocess.run(f"{ADB.shell} sendevent /dev/input/event2 1 330 1")
    subprocess.run(f"{ADB.shell} sendevent /dev/input/event2 0 0 0")

    y_per_step = abs(coordinate_from.y - coordinate_to.y) // steps
    for i in range(1, steps):
        subprocess.run(
            f"{ADB.shell} sendevent /dev/input/event2 3 54 "
            f"{coordinate_from.y - (y_per_step * i)}"
        )
        subprocess.run(f"{ADB.shell} sendevent /dev/input/event2 0 0 0")

    subprocess.run(f"{ADB.shell} sendevent /dev/input/event2 3 54 {coordinate_to.y}")
    subprocess.run(f"{ADB.shell} sendevent /dev/input/event2 0 0 0")

    sleep(1)
    subprocess.run(f"{ADB.shell} sendevent /dev/input/event2 1 330 0")
    subprocess.run(f"{ADB.shell} sendevent /dev/input/event2 0 0 0")


class ClipBoardResponse(object):
    status = None
    data = None


data_matcher = re.compile('data="(.*)"')


def get_clipboard() -> str:
    """
    Reads the clipboard through ADB.
    It was not possible to read it from the emulator I was using, so I had to rely on
    adb install AdbClipboard-2.0_3-release.apk (only works until Android 9)

    Response example from the app:
    Broadcasting: Intent { flg=0x400000 cmp=ch.pete.adbclipboard/.ReadReceiver }
    Broadcast completed: result=-1, data="Clipboard Content"

    Returns:
        The content of the clipboard or an empty string.
    """
    clipboard_response = subprocess.check_output(
        f"{ADB.shell} am broadcast -n ch.pete.adbclipboard/.ReadReceiver"
    ).decode("UTF-8")
    content = ""
    if "result=-1" in clipboard_response:
        data_match = data_matcher.search(clipboard_response)
        if data_match and len(data_match.groups()) > 0:
            content = data_match.group(1)
    return content
