#!/usr/bin/env python3
"""
Test script to print the footer logo with different conversion methods.
Run this to find the best settings for your logo.
"""

from pathlib import Path
from escpos.printer import Usb
from PIL import Image, ImageEnhance

# USB-Daten des Druckers
VENDOR_ID = 0x28e9
PRODUCT_ID = 0x0289

# Pfad zum Logo
print_assets_path = Path(__file__).parent / "print_assets"
image_path = print_assets_path / "39c3.png"


def center_image(image, printer_width):
    """Center an image on a given width"""
    img_width, img_height = image.size
    if img_width > printer_width:
        new_height = int((printer_width / img_width) * img_height)
        image = image.resize((printer_width, new_height), Image.Resampling.LANCZOS)
        img_width, img_height = image.size

    padding_left = (printer_width - img_width) // 2
    new_image = Image.new("1", (printer_width, img_height), 255)
    new_image.paste(image, (padding_left, 0))
    return new_image


def test_variant_1(printer):
    """Original method - direct convert to 1-bit (BROKEN - for comparison)"""
    print("\n=== VARIANT 1: Direct convert to 1-bit (BROKEN) ===")
    printer.text("\n--- VARIANT 1: Direct 1-bit (BROKEN) ---\n")

    image = Image.open(image_path)
    image = image.convert("1")
    image = image.resize((165, int(image.height * (165 / image.width))), Image.Resampling.LANCZOS)
    image = center_image(image, 384)
    printer.image(image)
    printer.text("\n")


def test_variant_2(printer):
    """Remove transparency with WHITE background"""
    print("\n=== VARIANT 2: White background + Dithering ===")
    printer.text("\n--- VARIANT 2: White BG ---\n")

    image = Image.open(image_path)

    # Handle transparency by adding WHITE background
    if image.mode == 'RGBA':
        background = Image.new('RGB', image.size, (255, 255, 255))  # White background
        background.paste(image, mask=image.split()[3])  # Use alpha channel as mask
        image = background

    image = image.convert("L")
    image = image.resize((165, int(image.height * (165 / image.width))), Image.Resampling.LANCZOS)
    image = image.convert("1", dither=Image.Dither.FLOYDSTEINBERG)
    image = center_image(image, 384)
    printer.image(image)
    printer.text("\n")


def test_variant_3(printer):
    """White background + Brightness + Contrast"""
    print("\n=== VARIANT 3: White BG + Brightness +20%, Contrast +30% ===")
    printer.text("\n--- VARIANT 3: White BG + Enhance ---\n")

    image = Image.open(image_path)

    # Handle transparency with WHITE background
    if image.mode == 'RGBA':
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3])
        image = background

    image = image.convert("L")

    # Increase brightness and contrast
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1.2)  # 20% brighter
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.3)  # 30% more contrast

    image = image.resize((165, int(image.height * (165 / image.width))), Image.Resampling.LANCZOS)
    image = image.convert("1", dither=Image.Dither.FLOYDSTEINBERG)
    image = center_image(image, 384)
    printer.image(image)
    printer.text("\n")


def test_variant_4(printer):
    """White background + Higher brightness"""
    print("\n=== VARIANT 4: White BG + Brightness +50%, Contrast +50% ===")
    printer.text("\n--- VARIANT 4: White BG + Extra Bright ---\n")

    image = Image.open(image_path)

    # Handle transparency with WHITE background
    if image.mode == 'RGBA':
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3])
        image = background

    image = image.convert("L")

    # More aggressive enhancement
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1.5)  # 50% brighter
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.5)  # 50% more contrast

    image = image.resize((165, int(image.height * (165 / image.width))), Image.Resampling.LANCZOS)
    image = image.convert("1", dither=Image.Dither.FLOYDSTEINBERG)
    image = center_image(image, 384)
    printer.image(image)
    printer.text("\n")


def test_variant_5(printer):
    """White background + No dithering (pure threshold)"""
    print("\n=== VARIANT 5: White BG + No Dithering (threshold) ===")
    printer.text("\n--- VARIANT 5: White BG + Threshold ---\n")

    image = Image.open(image_path)

    # Handle transparency with WHITE background
    if image.mode == 'RGBA':
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3])
        image = background

    image = image.convert("L")
    image = image.resize((165, int(image.height * (165 / image.width))), Image.Resampling.LANCZOS)

    # Convert to 1-bit WITHOUT dithering (pure threshold at 128)
    image = image.point(lambda x: 0 if x < 128 else 255, '1')

    image = center_image(image, 384)
    printer.image(image)
    printer.text("\n")


def main():
    printer = None
    try:
        print("Connecting to printer...")
        printer = Usb(VENDOR_ID, PRODUCT_ID, {}, out_ep=0x03)
        
        # Set printer width
        if 'media' not in printer.profile.profile_data:
            printer.profile.profile_data['media'] = {}
        if 'width' not in printer.profile.profile_data['media']:
            printer.profile.profile_data['media']['width'] = {}
        printer.profile.profile_data['media']['width']['pixel'] = 384
        
        print(f"Testing logo: {image_path}")
        printer.text("\n=== LOGO PRINT TEST ===\n")
        printer.text(f"File: {image_path.name}\n")
        
        # Run all test variants
        test_variant_1(printer)
        test_variant_2(printer)
        test_variant_3(printer)
        test_variant_4(printer)
        test_variant_5(printer)
        
        # Cut the paper
        printer.text("\n=== END OF TEST ===\n\n")
        printer.cut()
        
        print("\n✅ Test complete! Check the printed output.")
        print("Choose the variant that looks best and update print.py accordingly.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if printer and printer.device:
            printer.close()


if __name__ == "__main__":
    main()

