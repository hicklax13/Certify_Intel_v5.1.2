from PIL import Image
import os

source_path = r"C:\Users\conno\Downloads\Certify_Health_Intelv1\Project_Intel\desktop and browser icon.jpg"
dest_dir = r"C:\Users\conno\Downloads\Certify_Health_Intelv1\Project_Intel\desktop-app\resources\icons"

if not os.path.exists(source_path):
    print(f"Error: Source file not found at {source_path}")
    exit(1)

if not os.path.exists(dest_dir):
    print(f"Error: Destination directory not found at {dest_dir}")
    exit(1)

try:
    img = Image.open(source_path)
    print(f"Opened source image: {img.format} {img.size} {img.mode}")

    # Convert to RGBA for transparency support (though jpg doesn't have it, good practice)
    img = img.convert("RGBA")

    # Save as PNG
    png_path = os.path.join(dest_dir, "icon.png")
    # Resize to standard size if needed, e.g., 512x512
    img_png = img.resize((512, 512), Image.Resampling.LANCZOS)
    img_png.save(png_path, "PNG")
    print(f"Saved {png_path}")

    # Save as ICO
    ico_path = os.path.join(dest_dir, "icon.ico")
    # Windows icons usually include multiple sizes
    icon_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    img.save(ico_path, format="ICO", sizes=icon_sizes)
    print(f"Saved {ico_path}")
    
    # Also save one for the frontend/public just in case
    frontend_icon_path = r"C:\Users\conno\Downloads\Certify_Health_Intelv1\Project_Intel\frontend\favicon.ico"
    img.save(frontend_icon_path, format="ICO", sizes=[(32, 32)])
    print(f"Saved frontend favicon at {frontend_icon_path}")

except Exception as e:
    print(f"An error occurred: {e}")
