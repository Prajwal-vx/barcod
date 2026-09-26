import random
import string
from pathlib import Path

try:
    import barcode
    from barcode.writer import ImageWriter
except ImportError:
    print("Missing dependency: python-barcode")
    print("Install it with:")
    print("  py -m pip install python-barcode pillow")
    raise SystemExit(1)


OUTPUT_DIR = Path("generated_barcodes")
OUTPUT_DIR.mkdir(exist_ok=True)


def generate_random_code(length=12):
    """Generate a random numeric barcode value."""
    return "".join(random.choices(string.digits, k=length))


def create_barcode(value):
    """Create and save a Code 128 barcode as a PNG."""
    filename = OUTPUT_DIR / f"barcode_{value}"

    code128 = barcode.get(
        "code128",
        value,
        writer=ImageWriter(),
    )

    saved_path = code128.save(
        str(filename),
        options={
            "module_width": 0.35,
            "module_height": 18,
            "font_size": 10,
            "text_distance": 5,
            "quiet_zone": 6,
        },
    )

    return Path(saved_path)


def main():
    # No user input required.
    # A new random barcode is generated automatically every time the program runs.
    value = generate_random_code(12)
    path = create_barcode(value)

    print("=== Random Barcode Generator ===")
    print(f"Barcode value : {value}")
    print(f"Saved to      : {path.resolve()}")


if __name__ == "__main__":
    main()
