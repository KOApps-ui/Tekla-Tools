from PIL import Image
import os

def process_asm_icon():
    try:
        img = Image.open(os.path.join("assets", "asm_raw.png")).convert("RGBA")
        datas = img.getdata()

        newData = []
        for item in datas:
            # Check if pixel is white or very close to white (background)
            if item[0] > 240 and item[1] > 240 and item[2] > 240:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)

        img.putdata(newData)
        # Resize for UI usage (e.g., 32x32 for ribbon)
        img_small = img.resize((32, 32), Image.Resampling.LANCZOS)
        img_small.save(os.path.join("assets", "asm_icon.png"), "PNG")
        print("assets/asm_icon.png created with transparency.")
    except Exception as e:
        print(f"Error processing icon: {e}")

if __name__ == "__main__":
    process_asm_icon()
