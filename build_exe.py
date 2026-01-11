import PyInstaller.__main__
import os
import shutil
import sys

def build():
    print("Cleaning old build files...")
    # Explicitly remove build and dist to force a fresh icon/cache
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            try: 
                shutil.rmtree(folder)
                print(f"Removed {folder} folder.")
            except Exception as e:
                print(f"Warning: Could not remove {folder}. Maybe a file is in use? Error: {e}")
            
    print("Building Tekla Tools Exe...")
    
    # 1. Force recreate ICO from latest premium PNG
    logo_png = os.path.join("assets", "logo.png")
    logo_ico = os.path.join("assets", "logo.ico")
    
    if os.path.exists(logo_png):
        try:
            from PIL import Image
            img = Image.open(logo_png)
            # Create a high quality ICO with multiple sizes for better Windows display
            icon_sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
            img.save(logo_ico, format='ICO', sizes=icon_sizes)
            print(f"Successfully refreshed {logo_ico} with new premium logo.")
        except Exception as e:
            print(f"Icon conversion failed: {e}")
    
    # OS specific path separator for --add-data
    sep = os.pathsep

    # 2. Build Arguments
    # RENAMED to force Windows Explorer to refresh its icon cache
    exe_name = "TeklaTools.v1.0.1.1" 
    
    args = [
        'select_assemblies.py',
        f'--name={exe_name}', 
        '--onefile',
        '--noconsole',
        '--hidden-import=clr', 
        '--hidden-import=tekla_env',
        '--hidden-import=psutil',
        '--hidden-import=requests', 
        '--clean',
        f'--add-data=assets/logo.png{sep}.', 
        f'--add-data=assets/asm_icon.png{sep}.',
    ]
    
    # Use logo.ico for the EXE icon if created
    if os.path.exists(logo_ico):
        args.append(f'--icon={logo_ico}')
        args.append(f'--add-data=assets/logo.ico{sep}.')

    PyInstaller.__main__.run(args)
    
    print("\n" + "="*40)
    print("BUILD COMPLETE!")
    print(f"EXE Location: {os.path.abspath(f'dist/{exe_name}.exe')}")
    print("="*40)

if __name__ == "__main__":
    build()
