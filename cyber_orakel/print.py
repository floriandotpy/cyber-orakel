from pathlib import Path

from escpos.printer import Usb
from PIL import Image
import textwrap
import argparse  # Für externe Parameter (CLI)

# USB-Daten des Druckers
VENDOR_ID = 0x28e9
PRODUCT_ID = 0x0289

# Pfad zu Bildern

# image_path_orakel = "/home/pablo/cyberorakel/orakel_2.jpg"
# image_path_38c3 = "/home/pablo/cyberorakel/38c3.png"

print_assets_path = Path(__file__).parent.parent / "print_assets"
image_path_orakel = print_assets_path / "orakel_2.jpg"
image_path_38c3 = print_assets_path / "38c3.png"

MAX_WIDTH = 32


def center_image(image, printer_width):
    """
    Center an image on a given width
    :param image:
    :param printer_width:
    :return:
    """
    img_width, img_height = image.size
    if img_width > printer_width:
        new_height = int((printer_width / img_width) * img_height)
        image = image.resize((printer_width, new_height), Image.Resampling.LANCZOS)
        img_width, img_height = image.size

    padding_left = (printer_width - img_width) // 2
    new_image = Image.new("1", (printer_width, img_height), 255)
    new_image.paste(image, (padding_left, 0))
    return new_image


def format_text(text, width, replace_umlaute_flag=True, center=False):
    """
    Format a text to be printed on the receipt

    :param text:  The text to be formatted
    :param width:  The width of the receipt
    :param replace_umlaute_flag: Replace umlaute with ae, oe, ue, ss
    :param center:  Center the text
    :return: The formatted text
    """
    if replace_umlaute_flag:
        umlaut_map = {
            'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss',
            'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue'
        }
        for key, value in umlaut_map.items():
            text = text.replace(key, value)

    wrapped_lines = textwrap.wrap(text, width)

    if center:
        wrapped_lines = [center_text(line, width) for line in wrapped_lines]

    return "\n".join(wrapped_lines)


def center_text(text, width):
    if len(text) >= width:
        return text
    spaces = (width - len(text)) // 2
    return " " * spaces + text


def print_receipt(message, zodiac):
    try:
        printer = Usb(VENDOR_ID, PRODUCT_ID, 0, out_ep=0x03)
        printer.profile.profile_data['media']['width']['pixel'] = 384

        # Print header image
        image = Image.open(image_path_orakel)
        image = image.convert("1")
        image = image.resize((384, int(image.height * (384 / image.width))), Image.Resampling.LANCZOS)
        printer.image(image)
        printer.text("\n")
        printer.text("\n")

        # Print intro text
        #printer.text(format_text("Grüße: " + str(zodiac) + "!", MAX_WIDTH, center=True) + "\n")
        #printer.text(format_text("Deine heutige Prophezeiung lautet:", MAX_WIDTH, center=True) + "\n")
        #printer.text("-" * MAX_WIDTH + "\n")

        # Print message
        printer.text("\n")
        printer.text(format_text(message, MAX_WIDTH, center=True) + "\n")
        printer.text("\n")

        # FOOTER
        # Print footer text
        #printer.text("-" * MAX_WIDTH + "\n")
        #footer_text = "Have a lovely congress, nerd."
        #printer.text(format_text(footer_text, MAX_WIDTH, center=True) + "\n")
        printer.text("\n")
        # Print footer image
        image = Image.open(image_path_38c3)
        image = image.resize((150, int(image.height * (150 / image.width))), Image.Resampling.LANCZOS)
        image = center_image(image, 384)
        printer.image(image)

        # Finalize print
        printer.cut()
        print("Print complete")
        printer.close()

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if printer:
            printer.close()

# Script can be run from the command line
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Druckt eine Nachricht auf den Thermodrucker.")
    parser.add_argument("message", type=str, help="Die Nachricht, die gedruckt werden soll.")

    args = parser.parse_args()
    print_receipt(args.message)
