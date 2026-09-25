import os
import random
import string
from pathlib import Path

import barcode
from barcode.errors import BarcodeError, IllegalCharacterError
from barcode.writer import ImageWriter


def generate_random_item_id(prefix: str = "ITEM") -> str:
    """
    Generates a random, ASCII-safe identifier suitable for Code128, e.g.
    'ITEM-4821-QXZ'. Uses 4 random digits + 3 random uppercase letters,
    which gives ~26 million combinations per prefix - plenty to avoid
    collisions for a library catalog, without needing external state.

    :param prefix: Prefix to prepend to the random portion.
    :return: A random identifier string like 'ITEM-4821-QXZ'.
    """
    digits = "".join(random.choices(string.digits, k=4))
    letters = "".join(random.choices(string.ascii_uppercase, k=3))
    return f"{prefix}-{digits}-{letters}"


def create_code128_barcode(
    data_string: str,
    output_filename: str,
    overwrite: bool = False,
) -> str:
    """
    Generates a Code 128 barcode as a high-resolution PNG image.

    :param data_string: The string/content to encode. Must be ASCII
        (Code128 does not support non-ASCII characters).
    :param output_filename: File path to save the image to, WITH or
        WITHOUT the .png extension.
    :param overwrite: If False (default), raises FileExistsError instead
        of silently overwriting an existing file.
    :return: The full path to the saved PNG file.
    :raises ValueError: if data_string is empty or contains characters
        Code128 cannot encode.
    :raises FileExistsError: if the target file already exists and
        overwrite=False.
    """
    if not data_string:
        raise ValueError("data_string cannot be empty")

    # Code128 only supports ASCII (specifically Latin-1 / code points 0-127
    # for the standard character sets). Fail loudly and early instead of
    # letting the barcode library raise a less obvious error deep inside.
    try:
        data_string.encode("ascii")
    except UnicodeEncodeError as e:
        raise ValueError(
            f"data_string must be ASCII-only for Code128; found non-ASCII "
            f"character(s): {e}"
        ) from e

    # Normalize output path and check for collisions BEFORE generating,
    # since the barcode library appends .png automatically on save.
    target_path = Path(output_filename)
    if target_path.suffix.lower() != ".png":
        target_path = target_path.with_suffix(target_path.suffix + ".png")

    if target_path.exists() and not overwrite:
        raise FileExistsError(
            f"'{target_path}' already exists. Pass overwrite=True to replace it."
        )

    options = {
        "module_width": 0.3,    # X-dimension size in millimeters
        "module_height": 15.0,  # Height of the barcode bars
        "font_size": 10,        # Human-readable text size
        "text_distance": 5.0,   # Distance between bars and text
        "quiet_zone": 6.5,      # Margin width (crucial for scanners)
        "background": "white",
        "foreground": "black",
    }

    try:
        code128_class = barcode.get_barcode_class("code128")
        my_barcode = code128_class(data_string, writer=ImageWriter())

        # save() wants the filename WITHOUT extension (it appends .png itself)
        save_stem = str(target_path.with_suffix(""))
        saved_path = my_barcode.save(save_stem, options=options)
        return saved_path

    except IllegalCharacterError as e:
        # A character survived the ASCII check but Code128 still rejects it
        # (e.g. control characters). Re-raise with a clearer message.
        raise ValueError(f"'{data_string}' contains a character Code128 can't encode: {e}") from e
    except BarcodeError as e:
        # Any other barcode-library-specific failure
        raise RuntimeError(f"Failed to generate barcode for '{data_string}': {e}") from e


if __name__ == "__main__":
    # A new random ID (and matching filename) is generated every time
    # this script runs, so re-running it never collides with a previous
    # barcode and never needs overwrite=True.
    sample_data = generate_random_item_id()
    output_file = f"code128_{sample_data}"

    try:
        path = create_code128_barcode(sample_data, output_file)
        print(f"Generated ID: {sample_data}")
        print(f"Barcode successfully generated and saved at: {path}")
    except (ValueError, FileExistsError, RuntimeError) as e:
        print(f"Error generating barcode: {e}")