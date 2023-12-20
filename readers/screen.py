"""A collection of screen helpers for reading images or areas on images."""
from dataclasses import dataclass

import cv2
from numpy import ndarray
from pytesseract import pytesseract


@dataclass
class BoundingBox:
    """
    A dataclass holding information about a bounding box,
    a rectangle of two coordinate sets.
    """

    min_x: int
    min_y: int
    max_x: int
    max_y: int

    def to_tuple(self) -> tuple[int, int, int, int]:
        """
        Converts the bounding box to a tuple.

        Returns:
            A tuple, ordered min_x, min_y, max_x, max_y.

        """
        return self.min_x, self.min_y, self.max_x, self.max_y

    def get_width(self) -> int:
        """
        Get the width of the bounding box.

        Returns:
            The width as an integer.
        """
        return self.max_x - self.min_x

    def get_height(self) -> int:
        """
        Get the height of the bounding box.

        Returns:
            The height as an integer.
        """
        return self.max_y - self.min_y


@dataclass
class Coordinate:
    """
    Class to represent a coordinate on the screen.
    """

    x: int
    y: int

    def clone(self):
        """
        Get a clone of the coordinate, safe for modification.

        Returns:
            The cloned coordinate.
        """
        return Coordinate(x=self.x, y=self.y)

    def add(self, x: int, y: int):
        """
        Add the given values to the current coordinates.

        Returns:
             The modified coordinate object.
        """
        self.x += x
        self.y += y
        return self


@dataclass
class ImageSearchResult(Coordinate):
    """
    A dataclass holding information about an image search result.
    """

    width: int
    height: int

    def get_middle(self):
        return Coordinate(self.x + (self.width // 2), self.y + (self.height // 2))


def get_on_screen(
    image: ndarray, path: str, precision: float = 0.9
) -> ImageSearchResult | None:
    """
    Check if a given image is detected on screen in a specific window's area.

    Args:
        image: The image we should look at.
        path: The relative or absolute path to the image to be found.
        precision: The precision to be used when matching the image. Defaults to 0.9.

    Returns:
        The position of the image and it's width and height or None if it wasn't found
    """
    image_to_find = cv2.imread(path, 0)
    if image_to_find is None:
        print(
            f"The image {path} does not exist on the system "
            f"or we do not have permission to read it."
        )
        return None

    search_result = cv2.matchTemplate(image, image_to_find, cv2.TM_CCOEFF_NORMED)

    _, max_precision, _, max_location = cv2.minMaxLoc(search_result)
    if max_precision < precision:
        return None

    return ImageSearchResult(
        x=max_location[0],
        y=max_location[1],
        height=image_to_find.shape[0],
        width=image_to_find.shape[1],
    )


def read_at_bounding_box(
    image: ndarray,
    bounding_box: BoundingBox,
    character_whitelist: str | None,
) -> str | None:
    """
    Read numbers off an image, in a certain boundary box on the image.

    Args:
        image: The image to look at.
        bounding_box: The bounding box to crop the image down to.
            Does not modify the original image.
        character_whitelist (optional): The chars that are allowed to be recognized.
            Defaults to 0-9.

    Returns:
        The string contained in the bounding box or None.

    """
    tesseract_config = '--oem 3 --psm 7 -c page_separator=""'
    if character_whitelist:
        tesseract_config += f" -c tessedit_char_whitelist={character_whitelist}"

    cropped_image = image[
        bounding_box.min_y : bounding_box.max_y, bounding_box.min_x : bounding_box.max_x
    ]
    return pytesseract.image_to_string(cropped_image, config=tesseract_config)


def read_numbers_at_bounding_box(image: ndarray, bounding_box: BoundingBox) -> int:
    """
    Read numbers off an image, in a certain boundary box on the image.

    Args:
        image: The image to look at.
        bounding_box: The bounding box to crop the image down to.
            Does not modify the original image.

    Returns:
        The number contained in the bounding box or 0.

    """
    return int(
        read_at_bounding_box(
            image=image, bounding_box=bounding_box, character_whitelist="0123456789"
        )
        or 0
    )
