from PIL import Image
import os

source_path = r"C:\Users\conno\Downloads\Certify_Health_Intelv1\Project_Intel\frontend\certify_intel_logo.png"
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

    # Create a square canvas to center the logo
    max_dim = max(img.size)
    square_size = (max_dim, max_dim)
    square_img = Image.new("RGBA", square_size, (0, 0, 0, 0))
    
    # Calculate centering position
    left = (square_size[0] - img.size[0]) // 2
    top = (square_size[1] - img.size[1]) // 2
    square_img.paste(img, (left, top))
    
    # Resize to standard size (512x512) for high res base
    base_img = square_img.resize((512, 512), Image.Resampling.LANCZOS)

    # Save as PNG
    png_path = os.path.join(dest_dir, "icon.png")
    base_img.save(png_path, "PNG")
    print(f"Saved {png_path}")

    # Save as ICO
    ico_path = os.path.join(dest_dir, "icon.ico")
    icon_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    base_img.save(ico_path, format="ICO", sizes=icon_sizes)
    print(f"Saved {ico_path}")
    
    # Also save one for the frontend/public
    frontend_icon_path = r"C:\Users\conno\Downloads\Certify_Health_Intelv1\Project_Intel\frontend\favicon.ico"
    base_img.save(frontend_icon_path, format="ICO", sizes=[(32, 32)])
    print(f"Saved frontend favicon at {frontend_icon_path}")

except Exception as e:
    print(f"An error occurred: {e}")
