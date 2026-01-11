import os
import sys
import clr
import subprocess

# ================= CONFIG =================
APP_NAME = "KOIApps"
CONFIG_FILE = "tekla_path.txt"

# Updated for Tekla 2025 - Geometry3d has "Compatibility" suffix
REQUIRED_DLLS = {
    "Tekla.Structures.Model.dll",
}

# Optional DLLs - try both old and new names
GEOMETRY_DLL_VARIANTS = [
    "Tekla.Structures.Geometry3d.dll",
    "Tekla.Structures.Geometry3d.Compatibility.dll"
]

# ================= PERSISTENCE =================
def _config_file():
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    root = os.path.join(base, APP_NAME)
    os.makedirs(root, exist_ok=True)
    return os.path.join(root, CONFIG_FILE)

def save_exe(path):
    try:
        with open(_config_file(), "w", encoding="utf-8") as f:
            f.write(path.strip())
    except: pass

def load_exe():
    try:
        p = open(_config_file(), "r", encoding="utf-8").read().strip()
        return p if os.path.exists(p) else None
    except: return None

# ================= ENHANCED API SEEKER =================
def find_api_root(exe_path):
    """
    Find API DLLs with support for Tekla 2025's renamed Geometry3d DLL
    """
    if not exe_path or not os.path.exists(exe_path): 
        return None
    
    exe_path = os.path.abspath(exe_path)
    exe_dir = os.path.dirname(exe_path)
    version_root = os.path.dirname(exe_dir)
    product_root = os.path.dirname(version_root)
    
    # TIER 1: Check explicit known locations
    candidates = [
        os.path.join(version_root, "nt", "bin", "plugins"),
        os.path.join(version_root, "nt", "bin"),
        os.path.join(version_root, "bin", "plugins"),
        os.path.join(exe_dir, "plugins"),
        exe_dir,
    ]
    
    for candidate in candidates:
        if os.path.isdir(candidate):
            try:
                files_in_dir = set(os.listdir(candidate))
                # Check if Model.dll is present
                if REQUIRED_DLLS.issubset(files_in_dir):
                    # Check if any variant of Geometry3d is present
                    has_geometry = any(variant in files_in_dir for variant in GEOMETRY_DLL_VARIANTS)
                    if has_geometry:
                        return candidate
            except: pass
    
    # TIER 2: Deep recursive search
    search_roots = [version_root, product_root, exe_dir]
    seen = set()
    
    for start_node in search_roots:
        if not os.path.isdir(start_node): continue
        start_node = os.path.normpath(start_node)
        if start_node in seen: continue
        seen.add(start_node)
        
        for root, dirs, files in os.walk(start_node):
            files_set = set(files)
            # Check Model.dll + any Geometry variant
            if REQUIRED_DLLS.issubset(files_set):
                has_geometry = any(variant in files_set for variant in GEOMETRY_DLL_VARIANTS)
                if has_geometry:
                    return root
            
            # Only skip system folders
            lname = os.path.basename(root).lower()
            if lname in {"$recycle.bin", "system volume information"}:
                dirs.clear()
                continue
            
            # Depth limit
            if root.count(os.sep) - start_node.count(os.sep) > 8:
                dirs.clear()
    
    return None

# ================= AUTO-DETECTION =================
def find_running_tekla():
    try:
        out = subprocess.check_output(
            'wmic process where "name=\'TeklaStructures.exe\'" get ExecutablePath',
            shell=True
        ).decode(errors="ignore")
        for l in out.splitlines():
            l = l.strip()
            if l.lower().endswith("teklastructures.exe") and os.path.exists(l):
                return l
    except: pass
    return None

# ================= MASTER CONNECT =================
def connect_tekla(manual_exe=None):
    exe = manual_exe or load_exe() or find_running_tekla()
    
    if not exe:
        return False, "TEKLA_EXE_NOT_FOUND"

    api_root = find_api_root(exe)
    
    if not api_root:
        return False, "API_DLLS_NOT_FOUND"

    save_exe(exe)

    if api_root not in sys.path:
        sys.path.insert(0, api_root)
    
    os.environ["PATH"] = api_root + ";" + os.environ.get("PATH", "")

    try:
        # Load Model.dll
        clr.AddReference(os.path.join(api_root, "Tekla.Structures.Model.dll"))
        
        # Try to load Geometry3d - check both variants
        geometry_loaded = False
        for variant in GEOMETRY_DLL_VARIANTS:
            dll_path = os.path.join(api_root, variant)
            if os.path.exists(dll_path):
                try:
                    clr.AddReference(dll_path)
                    geometry_loaded = True
                    break
                except: pass
        
        if not geometry_loaded:
            return False, "GEOMETRY_DLL_LOAD_FAILED"
            
        return True, api_root
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    ok, info = connect_tekla()
    print(f"STATUS: {ok}, INFO: {info}")
