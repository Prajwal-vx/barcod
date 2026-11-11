import secrets
import string
from pathlib import Path
from typing import Final

try:
    import barcode
    from barcode.writer import ImageWriter
except ImportError:
    print("Missing dependency: python-barcode")
    print("Install it with:")
    print("  py -m pip install python-barcode pillow")
    raise SystemExit(1)


OUTPUT_DIR: Final[Path] = Path(__file__).resolve().parent / "generated_barcodes"


def generate_random_code(length: int = 12) -> str:
    """Generate a random numeric barcode value."""
    if length <= 0:
        raise ValueError("Barcode length must be greater than zero.")

    return "".join(secrets.choice(string.digits) for _ in range(length))


def create_barcode(value: str) -> Path:
    """Create and save a Code 128 barcode as a PNG."""
    if not value:
        raise ValueError("Barcode value must not be empty.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
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


def main() -> None:
    value = generate_random_code(12)
    path = create_barcode(value)

    print("=== Random Barcode Generator ===")
    print(f"Barcode value : {value}")
    print(f"Saved to      : {path.resolve()}")


if __name__ == "__main__":
    main()
