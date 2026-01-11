#!python 3 select_assemblies.py
import tkinter as tk
from tkinter import ttk, filedialog
import threading
import time
import clr
import sys
import os
import math
import webbrowser
import json
import traceback

def get_res(filename):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    # Check if file exists in base_path (for PyInstaller flattened structure)
    path = os.path.join(base_path, filename)
    if os.path.exists(path):
        return path
        
    # Check in assets folder (for development structure)
    path = os.path.join(base_path, "assets", filename)
    if os.path.exists(path):
        return path
        
    return os.path.join(base_path, filename) # Fallback

# --- LOCALIZATION ---
CURRENT_LANG = "EN" # Default: EN or TR
TRANSLATIONS = {
    "EN": {
        "app_title": "TEKLA TOOLS",
        "connect_success": "Tekla Connected Successfully!",
        "connect_fail": "Could not connect to Tekla Structures!",
        "waiting": "WAITING FOR TEKLA...",
        "ready": "READY",
        "tools": "TOOLS",
        "asm": "  Assembly  ",
        "asm_hint": "Select Assembly & Find Similar",
        "part": "  Part  ",
        "part_hint": "Select Single Part & Find Similar",
        "bolt": "  Bolt  ",
        "bolt_hint": "Count & Select Bolt Groups",
        "inq": "Inquire",
        "inq_hint": "Inquire Object Data",
        "analyze": "Analyze",
        "analyze_hint": "Check Assembly Consistency",
        "check": "Model Check",
        "check_hint": "Scan for Missing Drawings",
        "support": " ❤  SUPPORT ",
        "support_hint": "Support Development",
        "close_hint": "Close Application",
        "min_hint": "Minimize / Restore",
        "restore_hint": "Restore Window",
        "developer": "Software by KO|Apps",
        "contact": "Contact Developer",
        "manual_select": "📁 SELECT TEKLASTRUCTURES.EXE",
        "manual_desc": "Solves 2024/2025 path issues",
        "manual_title": "Select TeklaStructures.exe",
        "manual_info": "Please select the folder where Tekla is installed.",
        "success": "Success",
        "error": "Error",
        "minimized_title": "TEKLA TOOLS",
        
        # --- TUTORIAL EN ---
        "tut_title": "HOW TO USE",
        "tut_desc": "Quick guide to Tekla Tools functions",
        "t_asm": "Selects an Assembly in model and finds/selects all similar assemblies.",
        "t_part": "Selects a Single Part and finds/selects all identical parts.",
        "t_bolt": "Selects and counts Bolt Groups, showing quantities.",
        "t_inq": "Shows comprehensive raw data (properties) of any selected object.",
        "t_analyze": "Compares two or more assemblies to check for consistency errors.",
        "t_check": "Scans the entire model for parts without drawings (Missing Drawings).",
        "tekla_not_found": "Tekla Structures not found!\nPlease open Tekla and load a model first.",
    },
    "TR": {
        "app_title": "TEKLA ARAÇLARI",
        "connect_success": "Tekla Başarıyla Bağlandı!",
        "connect_fail": "Tekla Structures'a bağlanılamadı!",
        "waiting": "TEKLA BEKLENİYOR...",
        "ready": "HAZIR",
        "tools": "ARAÇLAR",
        "asm": "  Montaj  ",
        "asm_hint": "Montaj Seç & Benzerleri Bul",
        "part": "  Parça  ",
        "part_hint": "Tekil Parça Seç & Benzerleri Bul",
        "bolt": "  Civata  ",
        "bolt_hint": "Civata Gruplarını Say & Seç",
        "inq": "Sorgula",
        "inq_hint": "Nesne Verilerini Sorgula",
        "analyze": " Analiz ",
        "analyze_hint": "Montaj Tutarlılığını Analiz Et",
        "check": "Model Kontrol",
        "check_hint": "Eksik Çizimleri Tara",
        "support": " ❤  DESTEK ",
        "support_hint": "Geliştirmeyi Destekle",
        "close_hint": "Uygulamayı Kapat",
        "min_hint": "Küçült / Geri Yükle",
        "restore_hint": "Pencereyi Göster",
        "developer": "KO|Apps Yazılım",
        "contact": "Geliştirici İletişim",
        "manual_select": "📁 TEKLASTRUCTURES.EXE SEÇ",
        "manual_desc": "2024/2025 yol sorunlarını çözer",
        "manual_title": "TeklaStructures.exe Seçin",
        "manual_info": "Lütfen Tekla'nın kurulu olduğu klasörü seçin.",
        "success": "Başarılı",
        "error": "Hata",
        "minimized_title": "TEKLA ARAÇLARI",

        # --- TUTORIAL TR ---
        "tut_title": "NASIL KULLANILIR?",
        "tut_desc": "Tekla Araçları fonksiyon rehberi",
        "t_asm": "Modeldeki bir Montajı seçer ve benzerlerini bulup listeler.",
        "t_part": "Tekil bir Parçayı seçer ve modeldeki tüm kopyalarını (benzerlerini) bulur.",
        "t_bolt": "Civata gruplarını seçer, sayar ve adet bilgisini gösterir.",
        "t_inq": "Seçilen nesneye ait tüm ham verileri (property) detaylıca döker.",
        "t_analyze": "İki veya daha fazla montajı kıyaslayıp tutarsızlıkları raporlar.",
        "t_check": "Tüm modeli tarayarak imalat çizimi olmayan (eksik) parçaları bulur.",
        "tekla_not_found": "Tekla Structures bulunamadı!\nLütfen önce Tekla'yı açın ve bir model yükleyin.",
    }
}

def T(key):
    # Single, consolidated localization helper
    lang_data = TRANSLATIONS.get(CURRENT_LANG, TRANSLATIONS["EN"])
    return lang_data.get(key, key)

# Global Tekla Objects (Dummies by default)
TEKLA_AVAILABLE = False
CONNECTED_VERSION = "Unknown"

# Define Dummies first
class Model: pass
class Assembly: pass
class Part: pass
class BoltGroup: pass
class Connection: pass
class Beam: pass
class ReferenceModelObject: pass
class ReferenceModel: pass
class ModelObject: pass
class Operation:
    @staticmethod
    def RunCommand(c): pass

class ModelObjectSelector: pass
class Picker: pass
class Point: pass
class ArrayList: pass
class TS_Op: pass
class DrawingHandler: pass
class AssemblyDrawing: pass
class SinglePartDrawing: pass
class Drawing: pass
class DrawingSelector: pass

t_msg = "Waiting for connection..."

def try_connect(manual_path=None):
    global TEKLA_AVAILABLE, CONNECTED_VERSION, t_msg
    global Model, Assembly, Part, BoltGroup, Connection, Beam, ReferenceModelObject, ReferenceModel, ModelObject
    global Operation, ModelObjectSelector, Picker, Point, ArrayList, TS_Op
    global DrawingHandler, AssemblyDrawing, SinglePartDrawing, Drawing, DrawingSelector
    
    try:
        from tekla_env import connect_tekla
        ok, result = connect_tekla(manual_path)
        
        if ok:
            # result is api_bin path
            bin_path = result
            # Try to guess version from path
            try:
                parts = bin_path.split(os.sep)
                for i, part in enumerate(parts):
                    if part.lower() in ["nt", "bin"] and i > 0:
                        prev = parts[i-1]
                        if prev.startswith("20"):
                            CONNECTED_VERSION = prev
                            break
            except: pass
            
            # NOW IMPORT REAL OBJECTS
            from Tekla.Structures.Model import Model as rModel, Assembly as rAssembly, Part as rPart, BoltGroup as rBoltGroup, Connection as rConnection, Beam as rBeam, ReferenceModelObject as rReferenceModelObject, ReferenceModel as rReferenceModel, ModelObject as rModelObject
            from Tekla.Structures.Model.Operations import Operation as rOperation
            from Tekla.Structures.Model.UI import ModelObjectSelector as rModelObjectSelector, Picker as rPicker
            from Tekla.Structures.Geometry3d import Point as rPoint
            from System.Collections import ArrayList as rArrayList
            import Tekla.Structures.Model.Operations as rTS_Op
            
            # Update global references
            Model, Assembly, Part, BoltGroup, Connection, Beam = rModel, rAssembly, rPart, rBoltGroup, rConnection, rBeam
            ReferenceModelObject, ReferenceModel, ModelObject = rReferenceModelObject, rReferenceModel, rModelObject
            Operation, ModelObjectSelector, Picker, Point = rOperation, rModelObjectSelector, rPicker, rPoint
            ArrayList, TS_Op = rArrayList, rTS_Op
            
            try:
                clr.AddReference("Tekla.Structures.Drawing")
                from Tekla.Structures.Drawing import DrawingHandler as rDH, AssemblyDrawing as rAD, SinglePartDrawing as rSPD, Drawing as rD, DrawingItem as rDI
                from Tekla.Structures.Drawing.UI import DrawingSelector as rDS
                DrawingHandler, AssemblyDrawing, SinglePartDrawing, Drawing, DrawingSelector, DrawingItem = rDH, rAD, rSPD, rD, rDS, rDI
            except: pass
            
            TEKLA_AVAILABLE = True
            t_msg = "Connected"
            return True
        else:
            t_msg = result
            if t_msg == "TEKLA_EXE_NOT_FOUND":
                t_msg = "Please select TeklaStructures.exe"
            elif t_msg == "API_DLLS_NOT_FOUND":
                t_msg = "API DLLs not found in folder"
            return False
    except Exception as e:
        t_msg = str(e)
        return False

# Initial attempt
try_connect()

# Drawing API
try:
    clr.AddReference("Tekla.Structures.Drawing")
    from Tekla.Structures.Drawing import DrawingHandler, AssemblyDrawing, SinglePartDrawing, Drawing
    from Tekla.Structures.Drawing.UI import DrawingSelector
except:
    # Dummy Drawing Classes
    class DrawingHandler: pass
    class AssemblyDrawing: pass
    class SinglePartDrawing: pass
    class Drawing: pass
    class DrawingSelector: pass
    class DrawingItem: # Dummy for enum access
        class DrawingTypeEnum:
            ASSEMBLY_DRAWING = 0
            SINGLE_PART_DRAWING = 1

    # Dummy class placeholder if not connected yet
    pass

class TeklaEngine:
    def __init__(self):
        try: self.model = Model()
        except: self.model = None
        
        try: self.selector = ModelObjectSelector()
        except: self.selector = None
        
        try: self.picker = Picker()
        except: self.picker = None
        
        try: self.dh = DrawingHandler()
        except: self.dh = None

    def get_p(self, obj, prop, p_type="double"):
        if p_type == "double":
            val = 0.0
            ok, val = obj.GetReportProperty(prop, val)
            return round(val, 2) if ok else 0.0
        else:
            val = ""
            ok, val = obj.GetReportProperty(prop, val)
            return str(val).strip() if ok else ""

    def get_robust_cog(self, obj):
        try:
            p = obj.GetCenterOfGravity()
            return (p.X, p.Y, p.Z)
        except:
            x = self.get_p(obj, "COG_X")
            y = self.get_p(obj, "COG_Y")
            z = self.get_p(obj, "COG_Z")
            return (x, y, z)

    def calc_dist(self, p1, p2):
        return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)

    def get_assembly_dna(self, assembly):
        try:
            w = self.get_p(assembly, "WEIGHT_NET")
            n = self.get_p(assembly, "NUMBER_OF_PARTS")
            ass_cog = self.get_robust_cog(assembly)
            mp = assembly.GetMainPart()
            if not mp: return "ERR"
            mp_cog = self.get_robust_cog(mp)
            shift = self.calc_dist(ass_cog, mp_cog)
            return f"W:{w}|N:{int(n)}|S:{round(shift, 1)}"
        except: return "ERR"

    def safe_run_command(self, cmd_name):
        try:
            if hasattr(TS_Op.Operation, "RunCommand"):
                TS_Op.Operation.RunCommand(cmd_name)
                return True
            if hasattr(Operation, "RunCommand"):
                Operation.RunCommand(cmd_name)
                return True
            print(f"[WARN] RunCommand('{cmd_name}') is not supported in this Tekla version.")
            return False
        except Exception as e:
            print(f"[ERR] Command {cmd_name} failed: {e}")
            return False

    def safe_numbering(self):
        try:
            print("[LOG] Attempting numbering...")
            # Try Native API (Newer versions)
            if hasattr(self.model, "GetNumberingHandler"):
                nh = self.model.GetNumberingHandler()
                nh.NumberSelectedObjects()
                print("[LOG] Numbering triggered via Handler.")
                return True
            # Try Classic Command
            return self.safe_run_command("PerformNumberingSelection")
        except Exception as e:
            print(f"[ERR] Numbering failed: {e}")
            return False

    def set_selection_mode(self, mode):
        if mode == "asm": self.safe_run_command("SetSelectionType_Assembly")
        elif mode == "part": self.safe_run_command("SetSelectionType_Component")
        elif mode == "bolt": self.safe_run_command("SetSelectionType_Bolt")

    def get_detailed_map(self, assembly):
        mp = assembly.GetMainPart()
        if not mp: return {}
        m_cog = self.get_robust_cog(mp)
        data_map = {}
        secs = assembly.GetSecondaries()
        enum = secs.GetEnumerator()
        while enum.MoveNext():
            child = enum.Current
            if isinstance(child, Part):
                p_prof = self.get_p(child, "PROFILE", "string")
                c_cog = self.get_robust_cog(child)
                dist = self.calc_dist(c_cog, m_cog)
                if p_prof not in data_map: data_map[p_prof] = []
                data_map[p_prof].append({"dist": round(dist, 1), "obj": child})
        for k in data_map: data_map[k].sort(key=lambda x: x["dist"])
        return data_map

    def normalize_mark(self, s):
        if not s: return ""
        s = str(s).upper()
        # Aggressive normalization: Strip all separators and brackets
        for char in ["[", "]", ".", "/", " ", "_", "(", ")", "-", "*"]:
            s = s.replace(char, "")
        return s.strip()

    def get_drawing(self, obj):
        try:
            dh = DrawingHandler()
            enum = dh.GetDrawings()
            
            # IDs to look for
            target_id = obj.Identifier.ID
            
            # Position Matching
            target_pos = ""
            if isinstance(obj, Assembly):
                target_pos = self.get_p(obj, "ASSEMBLY_POS", "string")
            elif isinstance(obj, Part):
                target_pos = self.get_p(obj, "PART_POS", "string")
            
            clean_target = self.normalize_mark(target_pos)
            
            # Helper to check match
            def check_match(drw, t_id, t_mark):
                # 1. STRICT TYPE CHECK FIRST
                if isinstance(obj, Assembly) and not isinstance(drw, AssemblyDrawing): return False
                if isinstance(obj, Part) and not isinstance(drw, SinglePartDrawing): return False

                # 2. Check ID Match
                try:
                    if isinstance(obj, Assembly) and isinstance(drw, AssemblyDrawing):
                        if drw.AssemblyIdentifier.ID == t_id: return True
                    elif isinstance(obj, Part) and isinstance(drw, SinglePartDrawing):
                        if drw.PartIdentifier.ID == t_id: return True
                except: pass
                
                # 3. Check Mark Match
                if hasattr(drw, "Mark"):
                    d_mark = self.normalize_mark(drw.Mark)
                    if d_mark == t_mark and t_mark:
                        return True
                return False

            # Check for Direct Match
            while enum.MoveNext():
                drw = enum.Current
                if check_match(drw, target_id, clean_target):
                    return drw
            
            return None
        except Exception as e:
            # print(f"DrawErr: {e}")
            return None

    def open_drawing(self, obj):
        # print(f"[DEBUG] Opening drawing for object: {obj}")
        try:
            self.dh = DrawingHandler()
            enum = self.dh.GetDrawings()
            
            target_pos = ""
            if isinstance(obj, Assembly):
                target_pos = self.get_p(obj, "ASSEMBLY_POS", "string")
            elif isinstance(obj, Part):
                target_pos = self.get_p(obj, "PART_POS", "string")
            
            target_pos_clean = self.normalize_mark(target_pos)
            target_id = str(obj.Identifier.ID)

            while enum.MoveNext():
                dwg = enum.Current
                
                # DERİN ANALİZ: Tip Kontrolü Eklendi
                # Seçilen nesne Montaj ise ve çizim Tekil Parça resmi ise pas geç.
                if isinstance(obj, Assembly) and not isinstance(dwg, AssemblyDrawing):
                    continue
                # Seçilen nesne Parça ise ve çizim Montaj resmi ise pas geç.
                if isinstance(obj, Part) and not isinstance(dwg, SinglePartDrawing):
                    continue

                dwg_mark = ""
                dwg_id = 0
                try:
                    if hasattr(dwg, "Mark"):
                        dwg_mark = self.normalize_mark(dwg.Mark)
                    
                    if isinstance(dwg, AssemblyDrawing):
                        dwg_id = dwg.AssemblyIdentifier.ID
                    elif isinstance(dwg, SinglePartDrawing):
                        dwg_id = dwg.PartIdentifier.ID
                except: pass
                
                matched = False
                # 1. ID eşleşmesi (En güvenli yol)
                if dwg_id != 0 and str(dwg_id) == target_id:
                    matched = True
                # 2. Poz No eşleşmesi (Yedek yol)
                elif dwg_mark and dwg_mark == target_pos_clean:
                    matched = True
                    
                if matched:
                    # print(f"[DEBUG] Doğru tip ve poz bulundu! Açılıyor...")
                    self.dh.SetActiveDrawing(dwg, True)
                    return True
            
            import tkinter.messagebox
            tk.messagebox.showwarning("Tekla Tools", f"Çizim bulunamadı: {target_pos}")
            return False
        except Exception as e:
            # print(f"[DEBUG] Error: {e}")
            import tkinter.messagebox
            tk.messagebox.showerror("Açılış Hatası", str(e))
            return False

    def select_drawing(self, obj):

        try:
            drw = self.get_drawing(obj)
            if drw:
                # 1. Bring DocMan to front first
                Operation.RunCommand("DocumentManager")
                
                # 2. Select
                ds = DrawingSelector()
                
                # UNSELECT ALL first to ensure visibility of change
                dummy = ArrayList()
                ds.SelectDrawings(dummy, False) 
                
                # Now Select target
                temp_list = ArrayList()
                temp_list.Add(drw)
                ds.SelectDrawings(temp_list, False) 
                
                # Highlight in list
                return True
            return False
        except: return False

    def create_drawing(self, obj):
        try:
            # 1. SELECT IT
            list_sel = ArrayList()
            list_sel.Add(obj)
            self.selector.Select(list_sel)
            
            # 2. NUMBER IT
            self.safe_numbering()
            self.model.CommitChanges()
            time.sleep(0.5)
            
            # 3. RE-SELECT
            self.selector.Select(list_sel)
            
            # 4. DRAWING CREATION (MULTI-STRATEGY)
            dh = DrawingHandler()
            new_drw = None
            
            # Strategy A: Factory Method
            if hasattr(dh, "CreateDrawing"):
                try: 
                    new_drw = dh.CreateDrawing(obj)
                    if new_drw:
                        dh.Save()
                        return True, "Drawing created (Factory)."
                except: pass
            
            # Strategy B: Manual Insert
            try:
                if isinstance(obj, Assembly):
                    new_drw = AssemblyDrawing(obj.Identifier)
                elif isinstance(obj, Part):
                    new_drw = SinglePartDrawing(obj.Identifier)
                
                if new_drw and new_drw.Insert():
                    dh.Save()
                    return True, "Drawing created (Direct)."
            except:
                # Try fallback constructor
                try:
                    if isinstance(obj, Assembly): new_drw = AssemblyDrawing(obj.Identifier, "standard")
                    else: new_drw = SinglePartDrawing(obj.Identifier, "standard")
                    if new_drw and new_drw.Insert():
                        dh.Save()
                        return True, "Drawing created (Direct Std)."
                except: pass
            
            # Strategy C: UI Command
            if self.safe_run_command("CreateFabricationDrawing"):
                return True, "Drawing created (Macro/Cmd)."
            
            return False, "No creation strategy worked."
        except Exception as e: 
            print(f"[CRITICAL ERR] Create Drawing Failed: {e}")
            return False, f"Err: {str(e)}"

    def get_missing_drawings(self):
        missing_asms = []
        missing_parts = []
        
        # DEBUG: Create log file
        try:
            debug_file = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "drawing_check_debug.txt")
            with open(debug_file, "w", encoding="utf-8") as f:
                f.write("=== DRAWING CHECK DEBUG ===\n\n")
        except: pass
        
        def debug_log(msg):
            try:
                with open(debug_file, "a", encoding="utf-8") as f:
                    f.write(msg + "\n")
            except: pass
        
        # Helper to extract drawing mark from multiple possible properties
        def get_drawing_mark(drw):
            """Try multiple properties to get the drawing identifier"""
            # Try Mark first
            if hasattr(drw, "Mark") and drw.Mark:
                return drw.Mark
            # Try Name
            if hasattr(drw, "Name") and drw.Name:
                return drw.Name
            # Try Title
            if hasattr(drw, "Title") and drw.Title:
                return drw.Title
            return None
        
        # 1. Map existing DRAWING MARKS (Position-based)
        dh = DrawingHandler()
        enum_drw = dh.GetDrawings()
        existing_asm_marks = set()
        existing_part_marks = set()
        
        debug_log("--- EXISTING DRAWINGS ---")
        while enum_drw.MoveNext():
            d = enum_drw.Current
            mark = get_drawing_mark(d)
            if mark:
                clean_m = self.normalize_mark(mark)
                if isinstance(d, AssemblyDrawing):
                    existing_asm_marks.add(clean_m)
                    debug_log(f"Assembly Drawing: Mark='{mark}' -> Normalized='{clean_m}'")
                elif isinstance(d, SinglePartDrawing):
                    existing_part_marks.add(clean_m)
                    debug_log(f"Part Drawing: Mark='{mark}' -> Normalized='{clean_m}'")
        
        debug_log(f"\nTotal Assembly Drawings: {len(existing_asm_marks)}")
        debug_log(f"Total Part Drawings: {len(existing_part_marks)}")
        debug_log(f"\nAssembly Marks: {sorted(existing_asm_marks)}")
        debug_log(f"Part Marks: {sorted(existing_part_marks)}")
        
        # 2. Track processed missing marks to avoid duplicates
        found_missing_asm_marks = set()
        found_missing_part_marks = set()

        # 3. Scan Model
        debug_log("\n--- SCANNING MODEL ---")
        enum_obj = self.model.GetModelObjectSelector().GetAllObjects()
        asm_count = 0
        part_count = 0
        
        while enum_obj.MoveNext():
            obj = enum_obj.Current
            if isinstance(obj, Assembly):
                asm_count += 1
                pos = self.get_p(obj, "ASSEMBLY_POS", "string")
                clean_pos = self.normalize_mark(pos)
                if clean_pos and clean_pos not in existing_asm_marks:
                    if clean_pos not in found_missing_asm_marks:
                        missing_asms.append(obj)
                        found_missing_asm_marks.add(clean_pos)
                        debug_log(f"MISSING Assembly: '{pos}' -> '{clean_pos}'")
                else:
                    if clean_pos:
                        debug_log(f"FOUND Assembly: '{pos}' -> '{clean_pos}'")
            elif isinstance(obj, Part):
                part_count += 1
                pos = self.get_p(obj, "PART_POS", "string")
                clean_pos = self.normalize_mark(pos)
                if clean_pos and clean_pos not in existing_part_marks:
                    if clean_pos not in found_missing_part_marks:
                        missing_parts.append(obj)
                        found_missing_part_marks.add(clean_pos)
                        debug_log(f"MISSING Part: '{pos}' -> '{clean_pos}'")
                else:
                    if clean_pos:
                        debug_log(f"FOUND Part: '{pos}' -> '{clean_pos}'")
        
        debug_log(f"\nTotal Assemblies in Model: {asm_count}")
        debug_log(f"Total Parts in Model: {part_count}")
        debug_log(f"Missing Assemblies: {len(missing_asms)}")
        debug_log(f"Missing Parts: {len(missing_parts)}")
        
        return missing_asms, missing_parts

    def create_bulk_drawings(self, objects, dwg_type, progress_cb=None):
        if not objects:
            print("[LOG] No objects to process.")
            return 0
            
        print(f"[LOG] STARTING BULK DRAWING for {len(objects)} objects...")
        try:
            # 1. SELECT OBJECTS
            print("[LOG] Step 1: Selecting objects in model...")
            list_for_sel = ArrayList()
            for o in objects: list_for_sel.Add(o)
            self.selector.Select(list_for_sel)
            
            # 2. PERFORM NUMBERING
            print("[LOG] Step 2: Numbering...")
            self.safe_numbering()
            self.model.CommitChanges()
            time.sleep(1.0) 
            
            # 3. RE-SELECT
            self.selector.Select(list_for_sel)
            time.sleep(0.5)
            
            # 4. DRAWING LOOP
            print("[LOG] Step 3: Drawing Loop...")
            dh = DrawingHandler()
            success_count = 0
            for i, obj in enumerate(objects):
                try:
                    if progress_cb: progress_cb(i + 1, len(objects))
                    
                    inserted = False
                    if hasattr(dh, "CreateDrawing"):
                        try:
                            if dh.CreateDrawing(obj): inserted = True
                        except: pass
                    
                    if not inserted:
                        try:
                            new_dwg = None
                            if dwg_type == "asm": new_dwg = AssemblyDrawing(obj.Identifier)
                            else: new_dwg = SinglePartDrawing(obj.Identifier)
                            if new_dwg and new_dwg.Insert(): inserted = True
                        except:
                            try:
                                if dwg_type == "asm": new_dwg = AssemblyDrawing(obj.Identifier, "standard")
                                else: new_dwg = SinglePartDrawing(obj.Identifier, "standard")
                                if new_dwg and new_dwg.Insert(): inserted = True
                            except: pass
                    
                    if inserted:
                        print(f"  -> [{i+1}/{len(objects)}] OK")
                        success_count += 1
                    else:
                        print(f"  -> [{i+1}/{len(objects)}] UPDATE REQUIRED")
                        if progress_cb: progress_cb(i + 1, len(objects))
                except: continue
            
            # Final Attempt: Command
            if success_count == 0:
                print("[LOG] API failed, attempting UI Command...")
                self.safe_run_command("CreateFabricationDrawing")
                success_count = len(objects)
            
            if success_count > 0:
                print(f"[LOG] BULK FINISHED. Created: {success_count} drawings.")
                # No dh.Save() needed here, .Insert() is permanent in Tekla Drawing DB
                
            return success_count
        except Exception as e:
            print(f"[CRITICAL ERROR] Bulk Drawing Failed: {str(e)}")
            return 0

    def find_similar_assemblies(self, ref_asm):
        ref_dna = self.get_assembly_dna(ref_asm)
        ref_pos = self.get_p(ref_asm, "ASSEMBLY_POS", "string")
        
        matches = ArrayList()
        enum = self.model.GetModelObjectSelector().GetAllObjects()
        while enum.MoveNext():
            obj = enum.Current
            if isinstance(obj, Assembly):
                if self.get_assembly_dna(obj) == ref_dna:
                    # DNA matches, now check position if exists
                    curr_pos = self.get_p(obj, "ASSEMBLY_POS", "string")
                    if ref_pos and curr_pos and ref_pos != curr_pos:
                        continue
                    matches.Add(obj)
                    
        self.selector.Select(matches)
        summary = (f"• Position: {ref_pos or '?'}\n"
                   f"• DNA: {ref_dna}\n"
                   f"• Found: {matches.Count} Identical Assemblies")
        return matches.Count, summary

    def find_similar_parts(self, ref_part):
        prof = self.get_p(ref_part, "PROFILE", "string")
        mat = self.get_p(ref_part, "MATERIAL", "string")
        length = self.get_p(ref_part, "LENGTH")
        weight = self.get_p(ref_part, "WEIGHT_NET")
        pos = self.get_p(ref_part, "PART_POS", "string")
        
        matches = ArrayList()
        enum = self.model.GetModelObjectSelector().GetAllObjects()
        while enum.MoveNext():
            obj = enum.Current
            if isinstance(obj, Part):
                # STRICT COMPARISON
                if (self.get_p(obj, "PROFILE", "string") == prof and 
                    self.get_p(obj, "MATERIAL", "string") == mat and
                    abs(self.get_p(obj, "LENGTH") - length) < 0.1 and
                    abs(self.get_p(obj, "WEIGHT_NET") - weight) < 0.05):
                    
                    # If both have positions, they must match
                    curr_pos = self.get_p(obj, "PART_POS", "string")
                    if pos and curr_pos and pos != curr_pos:
                        continue
                        
                    matches.Add(obj)
                    
        self.selector.Select(matches)
        summary = (f"• Profile: {prof} | L: {length}\n"
                   f"• Pos: {pos or '?'}\n"
                   f"• Found: {matches.Count} Identical Parts")
        return matches.Count, summary

    def find_similar_bolts(self, ref_bolt):
        size = str(ref_bolt.BoltSize)
        std = ref_bolt.BoltStandard
        
        l_v = 0.0; _, l_v = ref_bolt.GetReportProperty("LENGTH", l_v)
        length = l_v
        
        # Use reliable API property instead of Report Property
        ref_type = str(ref_bolt.BoltType) # "SITE" or "WORKSHOP" (String Enum)
        
        total_pcs = 0
        matches = ArrayList()
        enum = self.model.GetModelObjectSelector().GetAllObjects()
        while enum.MoveNext():
            obj = enum.Current
            if isinstance(obj, BoltGroup):
                c_l = 0.0; _, c_l = obj.GetReportProperty("LENGTH", c_l)
                
                # Check properties match
                if (str(obj.BoltSize) == size and 
                    obj.BoltStandard == std and
                    abs(c_l - length) < 0.1 and
                    str(obj.BoltType) == ref_type):
                    
                    matches.Add(obj)
                    
                    # Count Bolts
                    c_n = 0.0
                    try: 
                        if obj.BoltPositions: c_n = float(obj.BoltPositions.Count)
                    except: pass
                    
                    if not c_n:
                         ok, c_n = obj.GetReportProperty("BOLT_COUNTER", 0.0)
                         if not ok or not c_n: _, c_n = obj.GetReportProperty("NUMBER", 0.0)
                    
                    total_pcs += int(c_n)
                        
        self.selector.Select(matches)
        
        # Format Size
        disp_size = str(size)
        if disp_size.endswith(".0"): disp_size = disp_size[:-2]
        
        sw_label = "Site" if "SITE" in str(ref_type).upper() else "Shop"
        summary = (f"• Selected: M{disp_size} x {int(length)} ({std})\n"
                   f"• Type: {sw_label}\n"
                   f"• Found: {matches.Count} Groups ({total_pcs} Bolts)")
        return matches.Count, summary

    def normalize_mark(self, mark):
        if not mark: return ""
        s = str(mark).upper()
        # Aggressive normalization: Strip all separators and brackets (MUST MATCH TeklaEngine version!)
        for char in ["[", "]", ".", "/", " ", "_", "(", ")", "-", "*"]:
            s = s.replace(char, "")
        return s.strip()





    def create_drawing(self, obj):
        try:
            objs = ArrayList(); objs.Add(obj)
            try: self.model.GetNumberingHandler().Number(objs)
            except: pass
            
            dwg = None
            if isinstance(obj, Assembly): dwg = AssemblyDrawing(obj.Identifier)
            elif isinstance(obj, Part): dwg = SinglePartDrawing(obj.Identifier)
            
            if dwg and dwg.Insert(): return True, "Created manually"
            return False, "Creation Failed"
            
        except Exception as e: 
            import tkinter.messagebox
            tk.messagebox.showerror("Creation Error", str(e))
            return False, str(e)

    def get_full_data(self, obj):
        if isinstance(obj, BoltGroup):
            # FIXED: Direct property access
            b_size = str(obj.BoltSize)
            if b_size.endswith(".0"): b_size = b_size[:-2]
            
            dc = 0.0; ok, dc = obj.GetReportProperty("BOLT_COUNTER", dc)
            if not ok or dc == 0: _, dc = obj.GetReportProperty("NUMBER", dc)
            
            sw = 0.0; _, sw = obj.GetReportProperty("SITE_WORKSHOP", sw)
            # Retrieve Class/Phase with fallbacks
            # CLASS removed for Bolt as requested
            
            # Robust Phase Retrieval for Bolt
            p_phase = "-"
            try:
                # 1. Report Property
                success, dp = obj.GetReportProperty("PHASE", 0)
                if success and dp != 0: p_phase = str(dp)
                else:
                     # Try PART_PHASE
                     success, dp = obj.GetReportProperty("PART_PHASE", 0)
                     if success and dp != 0: p_phase = str(dp)
                     else:
                         # 2. Main Part of Bolt (PartToBeBolted)
                         p_items = None
                         try:
                             if hasattr(obj, "PartToBeBolted"): p_items = obj.PartToBeBolted
                             elif hasattr(obj, "GetPartToBeBolted"): p_items = obj.GetPartToBeBolted()
                         except: pass
                         if p_items and hasattr(p_items, "Count") and p_items.Count > 0:
                             ph = p_items[0].GetPhase(self.model.GetNumberingHandler())
                             if ph: p_phase = str(ph.PhaseNumber)
                         
                         # 3. PartToBoltTo (Backup)
                         if p_phase == "-" and hasattr(obj, "PartToBoltTo") and obj.PartToBoltTo:
                             ph = obj.PartToBoltTo.GetPhase(self.model.GetNumberingHandler())
                             if ph: p_phase = str(ph.PhaseNumber)
                     
                     # 3. Check PartToBeBolted
                     if p_phase == "-" and hasattr(obj, "PartToBeBolted"):
                          parts = obj.PartToBeBolted
                          if parts and parts.Count > 0:
                              first_part = parts[0]
                              ph = first_part.GetPhase(self.model.GetNumberingHandler())
                              if ph: p_phase = str(ph.PhaseNumber)

                     # 4. Check Father Component (System components sometimes hold phase)
                     if p_phase == "-":
                         try:
                             dad = obj.GetFatherComponent()
                             if dad:
                                 _, dp = dad.GetReportProperty("PHASE", 0.0)
                                 if dp and int(dp) != 0: p_phase = str(int(dp))
                         except: pass
            except: pass
            
            tl = 0.0; _, tl = obj.GetReportProperty("THREAD_LENGTH", tl)
            bl = 0.0; _, bl = obj.GetReportProperty("LENGTH", bl)
            
            # Robust Count Fallback
            bolt_qty = 0
            try: 
                if hasattr(obj, "BoltPositions") and obj.BoltPositions: 
                    bolt_qty = int(obj.BoltPositions.Count)
            except: pass
            
            if not bolt_qty:
                # Direct report property check with value capture
                v_q = 0.0; ok_q, v_q = obj.GetReportProperty("BOLT_COUNTER", v_q)
                if not ok_q or not v_q: _, v_q = obj.GetReportProperty("NUMBER", v_q)
                bolt_qty = int(v_q)
            
            # If still 0, try to count via model selection as a last resort
            if not bolt_qty and hasattr(obj, "BoltPositions"):
                try: bolt_qty = len(list(obj.BoltPositions))
                except: pass
            
            info_list = [
                f"GUID: {obj.Identifier.GUID}",
                f"NAME: {self.get_p(obj,'NAME','string')}",
                f"BOLT STANDARD: {obj.BoltStandard}",
                f"SIZE: M{b_size}",
                f"LENGTH: {bl}",
                f"THREAD LENGTH: {tl}",
                f"WEIGHT: {self.get_p(obj,'WEIGHT','double')}",
                f"EDGE DISTANCE: {self.get_p(obj,'EDGE_DISTANCE','double')}",
                # HOLE TOLERANCE is safer via Report Property or specific prop check
                f"HOLE TOLERANCE: {self.get_p(obj,'HOLE_TOLERANCE','double')}",
                f"ASSEMBLY TYPE: {'Site' if 'SITE' in str(obj.BoltType).upper() else 'Workshop'}",
                f"BOLT QTY: {bolt_qty}",
                f"PHASE: {p_phase}"
            ]
            ass = None
            try: ass = obj.GetAssembly()
            except: pass
            drw = self.get_drawing(ass) if ass else None
            drw_status = f"DRAWING: {'YES' if drw else 'NO'}"
            info_list.insert(0, drw_status)
            return "\n".join(info_list)
        
        props = []
        if isinstance(obj, Assembly):
            props = [("GUID","GUID","string"), ("ASSEMBLY POS","ASSEMBLY_POS","string"), ("PHASE","PHASE","string"), ("MAIN PART PROF","MAINPART.PROFILE","string"), ("WIDTH","WIDTH","double"), ("HEIGHT","HEIGHT","double"), ("LENGTH","LENGTH","double"), ("PAINTING AREA","AREA_PAINT","double"), ("NET WEIGHT","WEIGHT_NET","double"), ("GROSS WEIGHT","WEIGHT_GROSS","double"), ("TOP LEVEL","TOP_LEVEL","string"), ("BOTTOM LEVEL","BOTTOM_LEVEL","string"), ("GLOBAL TOP","TOP_LEVEL_GLOBAL","string"), ("GLOBAL BOT","BOTTOM_LEVEL_GLOBAL","string"), ("COG X","COG_X","double"), ("COG Y","COG_Y","double"), ("COG Z","COG_Z","double"), ("NUM OF PARTS","NUMBER_OF_PARTS","double")]
        else: # Part
            props = [("GUID","GUID","string"), ("NAME","NAME","string"), ("PROFILE","PROFILE","string"), ("MATERIAL","MATERIAL","string"), ("FINISH","FINISH","string"), ("ASSEMBLY POS","ASSEMBLY_POS","string"), ("PART POS","PART_POS","string"), ("CLASS","CLASS","string"), ("PHASE","PHASE","string"), ("NET LENGTH","LENGTH","double"), ("GROSS LENGTH","LENGTH_GROSS","double"), ("WIDTH","WIDTH","double"), ("HEIGHT","HEIGHT","double"), ("NET WEIGHT","WEIGHT_NET","double"), ("GROSS WEIGHT","WEIGHT_GROSS","double"), ("VOLUME","VOLUME","double"), ("AREA","AREA","double"), ("TOP LEVEL","TOP_LEVEL","string"), ("BOTTOM LEVEL","BOTTOM_LEVEL","string"), ("COG X","COG_X","double"), ("COG Y","COG_Y","double"), ("COG Z","COG_Z","double")]
        
        data = [f"DRAWING: {'YES' if self.get_drawing(obj) else 'NO'}"]
        for l, p, t in props:
            v = self.get_p(obj, p, t)
            # Direct Property Access Override
            if p == "CLASS":
                try: 
                    if hasattr(obj, "Class"): 
                        val = str(obj.Class)
                        if val and val != "0": v = val
                except: pass
            
            if p == "PHASE":
                try:
                    target = obj
                    if isinstance(obj, Assembly): target = obj.GetMainPart()
                    
                    if target:
                        # Try Integer Overload (Preferred for Phase)
                        ival = 0
                        ok, ival = target.GetReportProperty("PHASE", ival)
                        if ok and ival != 0: v = str(ival)
                        else:
                             # Try alternates
                             ok, ival = target.GetReportProperty("PART_PHASE", ival)
                             if ok and ival != 0: v = str(ival)
                             else:
                                 # Try String Overload
                                 sval = ""
                                 ok, sval = target.GetReportProperty("PHASE", sval)
                                 if ok and sval: v = sval
                except: pass

            # --- SPECIAL HANDLING FOR PAINTING AREA ---
            if p == "AREA_PAINT":
                if v == 0.0 or v == "0.0":
                    v = self.get_p(obj, "AREA_NET", "double")
                    if v == 0.0:
                        v = self.get_p(obj, "AREA", "double")
                
                # Convert to m2 (Tekla usually returns mm2 or just raw area unit)
                try:
                    m2 = round(float(v) / 1000000.0, 3)
                    v = f"{v} (≈ {m2} m²)"
                except: pass

            # --- SPECIAL HANDLING FOR NUM OF PARTS ---
            if p == "NUMBER_OF_PARTS":
                if isinstance(obj, Assembly):
                    # Robust count: Main Part (1) + Secondaries
                    try:
                        secs = obj.GetSecondaries()
                        count = 1 + (secs.Count if hasattr(secs, "Count") else 0)
                        v = float(count)
                    except: pass
                
                # Add marker for the UI to inject the [List] button
                if isinstance(obj, Assembly):
                    data.append(f"{l}_BTN_LIST: {v}")
                    continue

            data.append(f"{l}: {v}")
        return "\n".join(data)



from tkinter import filedialog, messagebox

class CreateToolTip(object):
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     # miliseconds
        self.wraplength = 180   # pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.attributes("-topmost", True) # Ensure tooltip is above everything
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background="#2c3e50", fg="white", relief='solid', borderwidth=0,
                       font=("Segoe UI", "8", "normal"), padx=5, pady=2)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()

class RibbonToolbar:
    def __init__(self):
        self.root = tk.Tk()
        
        # --- SMART STARTUP CHECK ---
        # 1. Check if we even have the path/DLLs
        import tekla_env
        path_found = tekla_env.load_exe() is not None
        
        if not path_found:
            # First time setup - Need to find Tekla DLLs
            self.manual_connect() # This will ask for folder and exit
            return

        # 2. Path exists, but is Tekla RUNNING?
        if not TEKLA_AVAILABLE:
            messagebox.showwarning("Tekla Tools", T("tekla_not_found"))
            self.root.destroy()
            os._exit(0)
            
        self.engine = TeklaEngine()
        self.is_minimized = False
        self.active_popup = None
        self.monitor_popup = None
        self.tut_win = None
        self.ribbon_bg = "#f3f3f3"
        self.ribbon_blue = "#0078d7"
        self.text_color = "#333333"
        
        # UI Style for Progressbar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TProgressbar", thickness=15, troughcolor='#f1f1f1', background=self.ribbon_blue, bordercolor='#f1f1f1', lightcolor=self.ribbon_blue, darkcolor=self.ribbon_blue)

        self.root.title(T("app_title"))
        
        # Set Icon
        try:
            icon_path = get_res("logo.png")
            if os.path.exists(icon_path):
                 self.win_icon = tk.PhotoImage(file=icon_path)
                 self.root.iconphoto(False, self.win_icon)
        except: pass
        
        # CENTER TOP POSITIONING
        w = 560
        h = 110
        sw = self.root.winfo_screenwidth()
        x = (sw - w) // 2
        y = int(h * 1.5) # Position: Height + Half Height from top
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=self.ribbon_bg)
        self.setup_ui()

    def manual_connect(self):
        msg = (
            "We could not automatically locate Tekla Structures.\n\n"
            "Please select the folder where Tekla is installed.\n"
            "Example: C:\\Program Files\\Tekla Structures\\2024.0"
        )
        messagebox.showinfo("Manual Connection", msg)
        
        # Default start dir
        start_dir = "C:\\Program Files\\Tekla Structures"
        if not os.path.exists(start_dir):
            start_dir = "C:\\"
            
        path = filedialog.askdirectory(initialdir=start_dir, title="Select Tekla Folder (Any Version)")
        if path:
            # Smart Check: If user picked parent folder (e.g. 2024.0) instead of bin
            # ... (rest of logic is fine, just fixing the text and start dir)
            if not os.path.exists(os.path.join(path, "Tekla.Structures.dll")):
                potential_bin = os.path.join(path, "bin")
                if os.path.exists(os.path.join(potential_bin, "Tekla.Structures.dll")):
                    path = potential_bin
            
            # Validate
            if os.path.exists(os.path.join(path, "Tekla.Structures.dll")):
                try:
                    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
                    with open(os.path.join(base_dir, "tekla_path.txt"), "w") as f:
                        f.write(path)
                    messagebox.showinfo("Success", f"Path saved!\n{path}\n\nPlease RESTART this application now.")
                    self.root.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Could not save config: {e}")
            else:
                messagebox.showerror("Invalid Path", f"The selected folder does not contain 'Tekla.Structures.dll'.\nChecked: {path}\n\nPlease try again and make sure to select the 'bin' folder.")

    def log(self, text, color="#0078d7"):
        try:
            if hasattr(self, 'footer_status') and self.footer_status.winfo_exists():
                self.footer_status.config(text=text.upper(), fg=color)
                self.root.after(3000, lambda: self.footer_status.config(text="TOOLS", fg="#888888") if self.footer_status.winfo_exists() else None)
            print(f"[UI LOG] {text}")
        except: pass

    def open_mail(self): webbrowser.open("mailto:koaqqs@gmail.com")
    def open_support(self): 
        webbrowser.open("https://donate.bynogame.com/koapps")
        webbrowser.open("https://github.com/sponsors/KOApps-ui")

    def create_ribbon_button(self, parent, icon, text, cmd, icon_color=None, hint=None):
        btn_frame = tk.Frame(parent, bg=self.ribbon_bg, cursor="hand2", width=80, height=75, highlightthickness=1, highlightbackground=self.ribbon_bg)
        btn_frame.pack(side='left', padx=1, pady=5)
        btn_frame.pack_propagate(False)
        f_color = icon_color if icon_color else self.text_color
        is_crane = "🏗" in icon 
        i_relx = 0.65 if is_crane else 0.5
        i_size = 24 if is_crane else 22
        
        icon_widgets = [] # To store widgets that need their background changed on hover
        
        if icon == "ASM_ICON":
            try:
                from PIL import Image, ImageTk
                asm_path = get_res("asm_icon.png")
                if os.path.exists(asm_path):
                    asm_img = Image.open(asm_path).convert("RGBA")
                    asm_img = asm_img.resize((32, 32), Image.Resampling.LANCZOS)
                    # Use a unique name to prevent garbage collection
                    if not hasattr(self, 'asm_photos'): self.asm_photos = {}
                    photo = ImageTk.PhotoImage(asm_img)
                    self.asm_photos[text] = photo 
                    icon_label = tk.Label(btn_frame, image=photo, bg=self.ribbon_bg, bd=0)
                    icon_label.place(relx=0.5, y=28, anchor='center')
                    icon_widgets.append(icon_label)
                else:
                    raise FileNotFoundError
            except:
                icon_label = tk.Label(btn_frame, text="🧩", font=('Segoe UI', i_size), bg=self.ribbon_bg, fg=f_color, bd=0, padx=0, pady=0)
                icon_label.place(relx=i_relx, y=28, anchor='center')
                icon_widgets.append(icon_label)
        else:
            icon_label = tk.Label(btn_frame, text=icon, font=('Segoe UI', i_size), bg=self.ribbon_bg, fg=f_color, bd=0, padx=0, pady=0)
            icon_label.place(relx=i_relx, y=28, anchor='center')
            icon_widgets.append(icon_label)
        
        text_label = tk.Label(btn_frame, text=text, font=('Segoe UI', 8, 'bold'), bg=self.ribbon_bg, fg=self.text_color, bd=0, padx=0, pady=0)
        text_label.place(relx=0.5, y=58, anchor='center')
        
        def on_enter(e):
            if not self.is_minimized:
                bg = "#e8e8e8" # Slightly darker for better visibility
                btn_frame.config(bg=bg, highlightthickness=1, highlightbackground="#0078d7")
                text_label.config(bg=bg)
                for w in icon_widgets:
                    w.config(bg=bg)
        def on_leave(e):
            bg = self.ribbon_bg
            btn_frame.config(bg=bg, highlightthickness=1, highlightbackground=bg)
            text_label.config(bg=bg)
            for w in icon_widgets:
                w.config(bg=bg)
        
        btn_frame.bind("<Enter>", on_enter); btn_frame.bind("<Leave>", on_leave)
        text_label.bind("<Enter>", on_enter); text_label.bind("<Leave>", on_leave)
        for w in icon_widgets:
            w.bind("<Enter>", on_enter); w.bind("<Leave>", on_leave)
        
        # Bind command to all relevant widgets
        btn_frame.bind("<Button-1>", lambda e: cmd())
        text_label.bind("<Button-1>", lambda e: cmd())
        for w in icon_widgets:
            w.bind("<Button-1>", lambda e: cmd())

        if hint: CreateToolTip(btn_frame, hint)
        return btn_frame

    def setup_ui(self):
        # Clear existing widgets for refresh (Language switch / Min-Max)
        for widget in self.root.winfo_children():
            widget.destroy()

        self.tab_frame = tk.Frame(self.root, bg=self.ribbon_bg, cursor="arrow") # Default arrow for bar
        self.tab_frame.pack(fill='x')
        # Movement bindings removed from frame to restrict to GREEN BOX (spacer)
        
        def on_dbl_click(e): self.toggle_min()
        self.tab_frame.bind("<Double-Button-1>", on_dbl_click)
        # REMOVED: tab_frame tooltip to prevent overlap

        # Logo icon
        try:
            from PIL import Image, ImageTk
            logo_path = get_res("logo.png")
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((20, 20), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = tk.Label(self.tab_frame, image=self.logo_photo, bg=self.ribbon_bg, cursor="hand2")
                logo_label.pack(side='left', padx=(5, 0))
                logo_label.bind("<Double-Button-1>", on_dbl_click)
                logo_label.bind("<Button-1>", lambda e: self.show_credits())
        except: pass

        title_text = T("minimized_title") if self.is_minimized else T("app_title")
        lbl_title = tk.Label(self.tab_frame, text=title_text, font=('Segoe UI', 8, 'bold'), bg=self.ribbon_bg, fg=self.ribbon_blue, cursor="hand2")
        lbl_title.pack(side='left', pady=2, padx=(5, 2)) # Reduced right padding
        lbl_title.bind("<Button-1>", on_dbl_click) # Single click to minimize as per request
        
        # GREEN BOX: Dedicated Move/Draggable spacer
        if not self.is_minimized:
            spacer_move = tk.Frame(self.tab_frame, bg=self.ribbon_bg, cursor="fleur", width=160) # Increased width
            spacer_move.pack(side='left', fill='y', expand=True)
            spacer_move.bind("<Button-1>", self.start_move)
            spacer_move.bind("<B1-Motion>", self.do_move)
            CreateToolTip(spacer_move, T("min_hint")) # Hint for the move area

        # Buttons Right Side
        btn_close = tk.Button(self.tab_frame, text="✕", command=self.root.destroy, bg=self.ribbon_bg, fg="#e74c3c", bd=0, font=('Arial', 8), width=3)
        btn_close.pack(side='right', padx=2)
        CreateToolTip(btn_close, T("close_hint"))
        
        # Maximize/Restore Button (IMPROVED VISIBILITY)
        min_icon = "❐" if self.is_minimized else "−"
        min_font_size = 9 if self.is_minimized else 11
        min_hint = T("restore_hint") if self.is_minimized else T("min_hint")
        
        self.btn_min = tk.Button(self.tab_frame, text=min_icon, command=self.toggle_min, bg=self.ribbon_bg, fg=self.text_color, bd=0, font=('Arial', min_font_size, 'bold'), width=3)
        self.btn_min.pack(side='right', padx=2)
        CreateToolTip(self.btn_min, min_hint)

        if not self.is_minimized:
            # Language Toggle
            lang_label = "TR" if CURRENT_LANG == "EN" else "EN"
            btn_lang = tk.Button(self.tab_frame, text=lang_label, command=self.toggle_lang, bg=self.ribbon_bg, fg="#555", bd=0, font=('Segoe UI', 7, 'bold'), width=3)
            btn_lang.pack(side='right', padx=2)
            CreateToolTip(btn_lang, "Dil Değiştir / Switch Language")

            # Info Button
            btn_info = tk.Button(self.tab_frame, text="ℹ", command=self.show_tutorial, bg=self.ribbon_bg, fg="#0078d7", bd=0, font=('Segoe UI', 9, 'bold'), width=3)
            btn_info.pack(side='right', padx=0)
            CreateToolTip(btn_info, T("tut_desc"))
        
            self.btn_support = tk.Label(self.tab_frame, text=T("support"), font=('Segoe UI', 7, 'bold'), bg="#ffffff", fg="#d95e86", cursor="hand2", padx=8, highlightthickness=1, highlightbackground="#d95e86")
            self.btn_support.pack(side='right', padx=10, pady=2)
            self.btn_support.bind("<Button-1>", lambda e: self.open_support())
            CreateToolTip(self.btn_support, T("support_hint"))
            
            self.brand_frame = tk.Frame(self.tab_frame, bg=self.ribbon_bg, highlightthickness=1, highlightbackground="#0078d7", padx=8, pady=1)
            if not self.is_minimized: # Only place brand if not minimized
                self.brand_frame.place(relx=0.5, rely=0.5, anchor='center')
            self.brand_frame.bind("<Double-Button-1>", on_dbl_click)
            # REMOVED: brand_frame tooltip to prevent double hint

            self.brand = tk.Label(self.brand_frame, text="By KO|Apps", font=('Segoe UI', 9, 'bold'), bg=self.ribbon_bg, fg=self.ribbon_blue, cursor="hand2")
            self.brand.pack()
            self.brand.bind("<Button-1>", lambda e: self.open_mail())
            self.brand.bind("<Double-Button-1>", on_dbl_click)
            CreateToolTip(self.brand, T("contact"))

            self.line = tk.Frame(self.root, bg=self.ribbon_blue, height=2)
            self.line.pack(fill='x')
            
        self.content_frame = tk.Frame(self.root, bg=self.ribbon_bg)
        if not self.is_minimized:
            self.content_frame.pack(fill='both', expand=True, padx=5)

        
        # --- DYNAMIC UI CONTENT ---
        # Since we check at startup, TEKLA_AVAILABLE is always True here
        self.group_sim = tk.Frame(self.content_frame, bg=self.ribbon_bg)
        self.group_sim.pack(side='left', fill='y')
        # Assembly gets the composite '4-puzzle' icon
        self.create_ribbon_button(self.group_sim, "ASM_ICON", T("asm"), lambda: self.action("asm"), "#2980b9", hint=T("asm_hint"))
        self.create_ribbon_button(self.group_sim, "🧩", T("part"), lambda: self.action("part"), "#27ae60", hint=T("part_hint"))
        self.create_ribbon_button(self.group_sim, "🔩", T("bolt"), lambda: self.action("bolt"), "#d35400", hint=T("bolt_hint"))
        
        tk.Frame(self.content_frame, bg="#cccccc", width=1).pack(side='left', fill='y', padx=10, pady=10)
        
        self.group_tools = tk.Frame(self.content_frame, bg=self.ribbon_bg)
        self.group_tools.pack(side='left', fill='y')
        self.create_ribbon_button(self.group_tools, "❓", T("inq"), lambda: self.action("inq"), "#8e44ad", hint=T("inq_hint"))
        self.create_ribbon_button(self.group_tools, "🔍", T("analyze"), lambda: self.action("analyze"), "#16a085", hint=T("analyze_hint"))
        self.create_ribbon_button(self.group_tools, "📊", T("check"), lambda: self.action("model_scan"), "#2c3e50", hint=T("check_hint"))

        # Footer (Only show if not minimized)
        if not self.is_minimized:
            self.footer = tk.Frame(self.root, bg="#e9e9e9", height=15)
            self.footer.pack(fill='x', side='bottom')
            f_container = tk.Frame(self.footer, bg="#e9e9e9")
            f_container.pack(expand=True)
            
            status_text = T("ready") if TEKLA_AVAILABLE else T("waiting")
            tk.Label(f_container, text=status_text, font=('Segoe UI', 6, 'bold'), bg="#e9e9e9", fg="#888888").pack(side='left', padx=(0, 60))
            self.footer_status = tk.Label(f_container, text=T("tools"), font=('Segoe UI', 6, 'bold'), bg="#e9e9e9", fg="#888888")
            self.footer_status.pack(side='left', padx=(20,0))

    def manual_find_exe(self):
        file_path = filedialog.askopenfilename(
            title="Select TeklaStructures.exe",
            filetypes=[("Executable", "TeklaStructures.exe"), ("All Files", "*.*")]
        )
        try:
            if file_path:
                if try_connect(file_path):
                    return
                else:
                    # FRIENDLY MESSAGE: No Tekla found
                    tk.messagebox.showwarning(T("tut_title"), T("tekla_not_found"))
                    self.root.destroy()
                    os._exit(0)
            else:
                # FRIENDLY MESSAGE: No exe or connection
                tk.messagebox.showwarning(T("tut_title"), T("tekla_not_found"))
                self.root.destroy()
                os._exit(0)
        except Exception:
            # Silently exit or show minimal warning instead of huge traceback
            os._exit(0)
        # Re-initialize UI
        self.root.title(T("app_title"))
        self.setup_ui()

    def toggle_lang(self):
        global CURRENT_LANG
        CURRENT_LANG = "TR" if CURRENT_LANG == "EN" else "EN"
        # Re-initialize UI
        self.root.title(T("app_title"))
        self.setup_ui()

    def show_tutorial(self):
        if self.tut_win and self.tut_win.winfo_exists():
            self.tut_win.lift()
            return
            
        t = tk.Toplevel(self.root)
        self.tut_win = t
        t.title(T("tut_title"))
        # Optimized height to end right after content
        # Balanced width/height
        w, h = 380, 440
        sw = t.winfo_screenwidth()
        sh = t.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        t.geometry(f"{w}x{h}+{x}+{y}")
        t.configure(bg="#ffffff")
        t.resizable(False, False)
        t.attributes("-topmost", True)
        
        try: 
            logo_path = get_res("logo.png")
            if os.path.exists(logo_path):
                 img = tk.PhotoImage(file=logo_path)
                 t.iconphoto(False, img)
        except: pass

        # Header - Lifted up to the top
        tk.Label(t, text=T("tut_title"), font=('Segoe UI', 13, 'bold'), bg="#ffffff", fg="#0078d7").pack(pady=(5, 0))
        tk.Label(t, text=T("tut_desc"), font=('Segoe UI', 8), bg="#ffffff", fg="#777777").pack(pady=(0, 5))
        
        row_frame = tk.Frame(t, bg="#ffffff", padx=15)
        row_frame.pack(fill='both', expand=True)
        
        def add_row(icon, title_key, desc_key, color, i_size=22):
            f = tk.Frame(row_frame, bg="#ffffff", pady=4)
            f.pack(fill='x')
            
            # Match the Ribbon's centering logic
            i_container = tk.Frame(f, bg="#ffffff", width=45, height=45)
            i_container.pack(side='left', anchor='n')
            i_container.pack_propagate(False)
            
            if icon == "ASM_ICON":
                try:
                    from PIL import Image, ImageTk
                    asm_path = get_res("asm_icon.png")
                    if os.path.exists(asm_path):
                        asm_img = Image.open(asm_path).convert("RGBA")
                        asm_img = asm_img.resize((32, 32), Image.Resampling.LANCZOS)
                        if not hasattr(self, 'tut_photos'): self.tut_photos = {}
                        photo = ImageTk.PhotoImage(asm_img)
                        self.tut_photos[title_key] = photo
                        tk.Label(i_container, image=photo, bg="#ffffff").place(relx=0.5, rely=0.5, anchor='center')
                    else: raise Exception
                except:
                    tk.Label(i_container, text="🧩", font=('Segoe UI', i_size), fg="#2980b9", bg="#ffffff").place(relx=0.5, rely=0.5, anchor='center')
            else:
                tk.Label(i_container, text=icon, font=('Segoe UI', i_size), fg=color, bg="#ffffff").place(relx=0.5, rely=0.5, anchor='center')
            
            txt_f = tk.Frame(f, bg="#ffffff")
            txt_f.pack(side='left', fill='x', expand=True, padx=(8, 0))
            tk.Label(txt_f, text=T(title_key).strip(), font=('Segoe UI', 9, 'bold'), bg="#ffffff", fg="#333333", anchor='w').pack(fill='x')
            tk.Label(txt_f, text=T(desc_key), font=('Segoe UI', 8), bg="#ffffff", fg="#666666", anchor='w', wraplength=270, justify='left').pack(fill='x')

        # Integrated Assembly icon (4-puzzle composite)
        add_row("ASM_ICON", "asm", "t_asm", "#2980b9", 22)
        add_row("🧩", "part", "t_part", "#27ae60", 22)
        add_row("🔩", "bolt", "t_bolt", "#d35400", 22)
        
        tk.Frame(row_frame, bg="#f0f0f0", height=1).pack(fill='x', pady=6)
        
        add_row("❓", "inq", "t_inq", "#8e44ad", 22)
        add_row("🔍", "analyze", "t_analyze", "#16a085", 22)
        add_row("📊", "check", "t_check", "#2c3e50", 22)




    def show_credits(self):
        if hasattr(self, 'credits_win') and self.credits_win and self.credits_win.winfo_exists():
            self.credits_win.lift()
            return

        c = tk.Toplevel(self.root)
        self.credits_win = c
        c.overrideredirect(True)
        c.attributes("-topmost", True)
        
        # Transparent hack for Windows
        bg_color = '#abcdef' # A color unlikely to be in the logo
        c.configure(bg=bg_color)
        c.attributes("-transparentcolor", bg_color)
        
        size = (375, 375)
        sw, sh = c.winfo_screenwidth(), c.winfo_screenheight()
        c.geometry(f"{size[0]}x{size[1]}+{(sw-size[0])//2}+{(sh-size[1])//2}")

        try:
            from PIL import Image, ImageTk
            logo_path = get_res("logo.png")
            if os.path.exists(logo_path):
                img = Image.open(logo_path).convert("RGBA")
                img = img.resize(size, Image.Resampling.LANCZOS)
                self.credit_photo = ImageTk.PhotoImage(img)
                lbl = tk.Label(c, image=self.credit_photo, bg=bg_color, bd=0)
                lbl.pack(expand=True, fill='both')
                lbl.bind("<Button-1>", lambda e: c.destroy())
        except: 
            c.destroy()
            return
            
        c.bind("<FocusOut>", lambda e: c.destroy())
        c.focus_set()

    def toggle_min(self):
        self.is_minimized = not self.is_minimized
        if self.is_minimized:
            self.root.geometry("220x25") # Compact width for [Logo + TEKLA TOOLS + Icons]
        else:
            self.root.geometry("560x110")
        self.setup_ui()

    def start_move(self, event): self.x, self.y = event.x, event.y
    def do_move(self, event):
        x = self.root.winfo_x() + (event.x - self.x)
        y = self.root.winfo_y() + (event.y - self.y)
        self.root.geometry(f"+{x}+{y}")

    def show_popup(self, title, msg, color="#0078d7", target_obj=None):
        if self.active_popup and self.active_popup.winfo_exists():
            try: self.active_popup.destroy()
            except: pass
        
        pop = tk.Toplevel(self.root)
        self.active_popup = pop
        pop.overrideredirect(True)
        pop.attributes("-topmost", True)
        pop.configure(bg='#f5f7fa', highlightthickness=1, highlightbackground=color)
        
        
        # Dynamic geometry (Start small, let it grow)
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x_pos = (screen_w - 480) // 2
        y_pos = (screen_h - 400) // 2
        pop.geometry(f"480x100+{x_pos}+{y_pos}") # Small initial height
        
        # Modern Header (Draggable)
        header = tk.Frame(pop, bg=color, height=50)
        header.pack(fill='x', side='top')
        header.pack_propagate(False)
        
        # Make popup draggable
        def start_drag(e): pop._drag_x, pop._drag_y = e.x, e.y
        def do_drag(e): pop.geometry(f"+{pop.winfo_x()+(e.x-pop._drag_x)}+{pop.winfo_y()+(e.y-pop._drag_y)}")
        header.bind("<Button-1>", start_drag)
        header.bind("<B1-Motion>", do_drag)
        
        tk.Label(header, text=title, bg=color, fg='white', font=('Segoe UI', 11, 'bold')).pack(side='left', padx=20, pady=12)
        
        close_btn = tk.Label(header, text="✕", bg=color, fg="white", font=('Segoe UI', 14), cursor="hand2", padx=10)
        close_btn.pack(side='right', padx=10)
        close_btn.bind("<Button-1>", lambda e: pop.destroy())
        
        # Main Content Area (No Scroll)
        main_frame = tk.Frame(pop, bg="#f5f7fa")
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        section_frame = None
        
        for line in msg.split("\n"):
            line = line.strip()
            if not line: continue
            
            # --- 1. Section Headers ---
            if line.startswith("---") and line.endswith("---"):
                section_name = line.replace("-", "").strip()
                if section_name:
                    section_card = tk.Frame(main_frame, bg="white", highlightthickness=1, highlightbackground="#e0e6ed")
                    section_card.pack(fill='x', padx=8, pady=2)
                    
                    section_header = tk.Frame(section_card, bg="#f8f9fa", height=32)
                    section_header.pack(fill='x')
                    section_header.pack_propagate(False)
                    
                    icon_map = {"SELECTION": "🎯", "DETAILS": "📋", "SMART ACTIONS": "⚡", "ERROR": "⚠️"}
                    icon = icon_map.get(section_name, "📌")
                    
                    tk.Label(section_header, text=f"{icon} {section_name}", 
                            font=('Segoe UI', 9, 'bold'), bg="#f8f9fa", fg="#2c3e50").pack(side='left', padx=12, pady=6)
                    
                    section_frame = tk.Frame(section_card, bg="white", padx=12, pady=8)
                    section_frame.pack(fill='x')
                continue
            
            # --- 2. Ensure Container Exists ---
            if not section_frame:
                # Create a default "Message" card if none exists (for plain errors/messages)
                section_card = tk.Frame(main_frame, bg="white", highlightthickness=1, highlightbackground="#e0e6ed")
                section_card.pack(fill='x', padx=8, pady=2)
                section_frame = tk.Frame(section_card, bg="white", padx=15, pady=15)
                section_frame.pack(fill='x')

            # --- 3. Render Content ---
            # A) Property Row (Key: Value)
            if ":" in line:
                parts = line.split(":", 1)
                key = parts[0].strip()
                val = parts[1].strip() if len(parts) > 1 else ""
                
                # Special: Drawing Status Badge
                if key.upper() == "DRAWING" and isinstance(target_obj, (Assembly, Part)):
                    status_frame = tk.Frame(section_frame, bg="white")
                    status_frame.pack(fill='x', pady=4)
                    tk.Label(status_frame, text="Drawing Status:", font=('Segoe UI', 9), bg="white", fg="#5a6c7d").pack(side='left')
                    badge_color = "#27ae60" if val.upper() == "YES" else "#e74c3c"
                    badge_text = "✓ EXISTS" if val.upper() == "YES" else "✗ MISSING"
                    tk.Label(status_frame, text=badge_text, font=('Segoe UI', 8, 'bold'), bg=badge_color, fg="white", padx=10, pady=3).pack(side='right')
                    continue
                
                # Standard Property
                prop_row = tk.Frame(section_frame, bg="white")
                prop_row.pack(fill='x', pady=0)
                
                # Check for List Button Marker
                has_list_btn = False
                if key.endswith("_BTN_LIST"):
                    key = key.replace("_BTN_LIST", "")
                    has_list_btn = True

                tk.Label(prop_row, text=key, font=('Segoe UI', 8), bg="white", fg="#5a6c7d", width=22, anchor='w').pack(side='left')
                
                val_color = "#2c3e50"
                val_font = ('Segoe UI', 8)
                try: # Highlight numbers
                    float(val.replace(",", ""))
                    val_color = "#3498db"
                    val_font = ('Segoe UI', 8, 'bold')
                except: pass
                
                val_label = tk.Label(prop_row, text=val, font=val_font, bg="white", fg=val_color, anchor='w', justify='left')
                val_label.pack(side='left', fill='x', expand=True)

                if has_list_btn and isinstance(target_obj, Assembly):
                    # Prominent orange styling for the LIST button
                    btn_list = tk.Button(prop_row, text=" LIST ", font=('Segoe UI', 7, 'bold'), 
                                       bg="#e67e22", fg="white", activebackground="#d35400", activeforeground="white",
                                       bd=0, padx=6, pady=1, cursor="hand2", 
                                       command=lambda: self.show_parts_popup(target_obj))
                    btn_list.pack(side='right', padx=2)
                    CreateToolTip(btn_list, "Show all parts in this assembly")
            
            # B) Plain Text (Paragraphs)
            else:
                tk.Label(section_frame, text=line, bg="white", fg="#34495e", font=('Segoe UI', 10), anchor='w', justify='left', wraplength=420).pack(fill='x', pady=2)
        
        # Smart Actions
        if target_obj and isinstance(target_obj, (Assembly, Part)):
            # Reparent to 'pop' to stick to bottom without gap from main content
            # Width alignment: Main frame has pad 10, cards have pad 8. Total 18.
            actions_card = tk.Frame(pop, bg="white", highlightthickness=1, highlightbackground="#e0e6ed")
            actions_card.pack(side='bottom', fill='x', padx=18, pady=(0, 10))
            
            actions_header = tk.Frame(actions_card, bg="#f8f9fa", height=32)
            actions_header.pack(fill='x')
            actions_header.pack_propagate(False)
            tk.Label(actions_header, text="⚡ SMART ACTIONS", font=('Segoe UI', 9, 'bold'), bg="#f8f9fa", fg="#2c3e50").pack(side='left', padx=12, pady=6)
            
            actions_content = tk.Frame(actions_card, bg="white", padx=12, pady=12)
            actions_content.pack(fill='x')
            
            def cmd_open():
                if self.engine.open_drawing(target_obj): self.log("Drawing Opened", "#27ae60")
                else: self.log("Failed to Open", "#e74c3c")

            def cmd_create():
                ok, msg_text = self.engine.create_drawing(target_obj)
                if ok:
                    self.log("Drawing Created!", "#27ae60")
                    self.show_popup(title, self.engine.get_full_data(target_obj), color, target_obj)
                else: self.log(msg_text, "#e74c3c")
            
            btn_text = "ASSEMBLY" if isinstance(target_obj, Assembly) else "PART"
            
            # SIMPLIFIED LAYOUT: [OPEN] [CREATE]
            btn_row = tk.Frame(actions_content, bg="white")
            btn_row.pack(fill='x')
            
            # Open Button (Left)
            tk.Button(btn_row, text=f"🖼 OPEN {btn_text} DWG", font=('Segoe UI', 9, 'bold'), bg="#3498db", fg="white", bd=0, pady=12, cursor="hand2", command=cmd_open).pack(side='left', fill='x', expand=True, padx=(0, 5))
            
            # Create Button (Right)
            tk.Button(btn_row, text=f"🏗 CREATE {btn_text} DWG", font=('Segoe UI', 9, 'bold'), bg="#2c3e50", fg="white", bd=0, pady=12, cursor="hand2", command=cmd_create).pack(side='left', fill='x', expand=True, padx=(5, 0))
        

        
        # CRITICAL FIX: Calculate TOTAL height including the bottom actions card
        pop.update_idletasks()
        try:
            content_h = main_frame.winfo_reqheight()
            actions_h = actions_card.winfo_reqheight() if 'actions_card' in locals() else 0
            header_h = 50
            
            # Total needed height + buffer
            total_req = content_h + actions_h + header_h + 30
            
            screen_h = self.root.winfo_screenheight()
            screen_w = self.root.winfo_screenwidth()
            
            final_h = min(total_req, screen_h - 100)
            
            # Re-center with correct height
            x_pos = (screen_w - 480) // 2
            y_pos = (screen_h - final_h) // 2
            
            pop.geometry(f"480x{final_h}+{x_pos}+{y_pos}")
        except: pass

    def show_parts_popup(self, assembly):
        if not assembly: return
        
        p_pop = tk.Toplevel(self.root)
        p_pop.title("Parts List")
        p_pop.overrideredirect(True)
        p_pop.attributes("-topmost", True)
        p_pop.configure(bg='white', highlightthickness=1, highlightbackground="#2980b9")
        
        # Center relative to current popup
        try:
            px = self.active_popup.winfo_x() + 50
            py = self.active_popup.winfo_y() + 100
            p_pop.geometry(f"450x400+{px}+{py}") # Wider and taller for table
        except:
            p_pop.geometry("450x400")

        header = tk.Frame(p_pop, bg="#2980b9", height=30)
        header.pack(fill='x')
        
        # Dragging logic
        def start_pop_drag(e): p_pop._px, p_pop._py = e.x, e.y
        def do_pop_drag(e): p_pop.geometry(f"+{p_pop.winfo_x()+(e.x-p_pop._px)}+{p_pop.winfo_y()+(e.y-p_pop._py)}")
        header.bind("<Button-1>", start_pop_drag)
        header.bind("<B1-Motion>", do_pop_drag)

        tk.Label(header, text="ASSEMBLY PARTS", font=('Segoe UI', 9, 'bold'), bg="#2980b9", fg="white").pack(side='left', padx=10)
        
        close_btn = tk.Label(header, text="✕", font=('Segoe UI', 10), bg="#2980b9", fg="white", cursor="hand2", padx=10)
        close_btn.pack(side='right')
        close_btn.bind("<Button-1>", lambda e: p_pop.destroy())

        body = tk.Frame(p_pop, bg="white", padx=15, pady=10)
        body.pack(fill='both', expand=True)
        
        # Get Data
        try:
            parts_data = {} # (pos, prof, mat) -> qty
            raw_bolts = {} # ID -> (std, size, qty)

            def log_bolt(b):
                if not b: return
                try:
                    # Capture unique bolts by ID
                    bid = b.Identifier.ID
                    if bid in raw_bolts: return
                    
                    b_type = str(b.BoltType).upper()
                    # We will show the bolt regardless of type if it's connected to our assembly
                    # since the user wants to see "everything belonging to the assembly"
                    
                    b_size = b.BoltSize
                    # Robust length check
                    b_len = 0.0; ok_l, b_len = b.GetReportProperty("LENGTH", b_len)
                    if not ok_l: b_len = 0.0 
                    
                    size_str = f"{b_size}x{int(b_len)}"
                    std_str = b.BoltStandard
                    
                    b_qty = 0
                    try:
                        if hasattr(b, "BoltPositions") and b.BoltPositions:
                            b_qty = b.BoltPositions.Count
                    except: pass
                    
                    if b_qty == 0:
                        ok, val = b.GetReportProperty("NUMBER", 0.0)
                        b_qty = int(val) if ok else 0
                    
                    if b_qty > 0:
                        raw_bolts[bid] = (std_str, size_str, b_qty)
                except: pass

            # 1. Collect Parts
            scan_parts = []
            mp = assembly.GetMainPart()
            if mp: scan_parts.append(mp)
            
            secs = assembly.GetSecondaries()
            enum_s = secs.GetEnumerator()
            while enum_s.MoveNext():
                item = enum_s.Current
                if isinstance(item, Part):
                    scan_parts.append(item)
            
            # 2. Collect Bolts: Strategy A - Assembly Level
            try:
                be_a = assembly.GetBolts()
                while be_a.MoveNext():
                    log_bolt(be_a.Current)
            except: pass
            
            # 3. Collect Bolts: Strategy B - Part Level (Catch Site Bolts too)
            for p in scan_parts:
                try:
                    be_p = p.GetBolts()
                    while be_p.MoveNext():
                        log_bolt(be_p.Current)
                except: pass

            # 4. Process Parts (For listing)
            for p in scan_parts:
                pos = self.engine.get_p(p, "PART_POS", "string") or "?"
                prof = self.engine.get_p(p, "PROFILE", "string") or "?"
                mat = self.engine.get_p(p, "MATERIAL", "string") or "?"
                key = (pos, prof, mat)
                parts_data[key] = parts_data.get(key, 0) + 1

            # 3. Finalize Bolt Tally (Summing up same types)
            final_bolts = {} # (std, size) -> total_qty
            for bid in raw_bolts:
                std, sz, q = raw_bolts[bid]
                k = (std, sz)
                final_bolts[k] = final_bolts.get(k, 0) + q

            # --- RENDER PARTS ---
            tk.Label(body, text="PARTS", font=('Segoe UI', 9, 'bold'), bg="white", fg="#2c3e50").pack(anchor='w', pady=(0, 5))
            
            h_frame = tk.Frame(body, bg="#f8f9fa")
            h_frame.pack(fill='x')
            cols = [("QTY", 5), ("POS", 10), ("PROFILE", 15), ("MATERIAL", 12)]
            for t, w in cols:
                tk.Label(h_frame, text=t, font=('Segoe UI', 7, 'bold'), bg="#f8f9fa", fg="#7f8c8d", width=w, anchor='w').pack(side='left')
            
            tk.Frame(body, bg="#e0e0e0", height=1).pack(fill='x', pady=2)
            
            for (pos, prof, mat), qty in sorted(parts_data.items()):
                row = tk.Frame(body, bg="white")
                row.pack(fill='x')
                tk.Label(row, text=str(qty), font=('Segoe UI', 8), bg="white", width=5, anchor='w').pack(side='left')
                tk.Label(row, text=pos, font=('Segoe UI', 8, 'bold'), bg="white", fg="#e67e22", width=10, anchor='w').pack(side='left')
                tk.Label(row, text=prof, font=('Segoe UI', 8), bg="white", width=15, anchor='w').pack(side='left')
                tk.Label(row, text=mat, font=('Segoe UI', 8), bg="white", width=12, anchor='w').pack(side='left')

            # --- RENDER BOLTS ---
            if final_bolts:
                tk.Frame(body, bg="white", height=15).pack()
                tk.Label(body, text="BOLTS", font=('Segoe UI', 9, 'bold'), bg="white", fg="#2c3e50").pack(anchor='w', pady=(0, 5))
                
                bh_frame = tk.Frame(body, bg="#f8f9fa")
                bh_frame.pack(fill='x')
                bcols = [("QTY", 5), ("GRADE", 10), ("SIZE", 20)]
                for t, w in bcols:
                    tk.Label(bh_frame, text=t, font=('Segoe UI', 7, 'bold'), bg="#f8f9fa", fg="#7f8c8d", width=w, anchor='w').pack(side='left')
                
                tk.Frame(body, bg="#e0e0e0", height=1).pack(fill='x', pady=2)
                
                for (std, size), qty in sorted(final_bolts.items()):
                    row = tk.Frame(body, bg="white")
                    row.pack(fill='x')
                    tk.Label(row, text=str(qty), font=('Segoe UI', 8), bg="white", width=5, anchor='w').pack(side='left')
                    tk.Label(row, text=std, font=('Segoe UI', 8), bg="white", width=10, anchor='w').pack(side='left')
                    tk.Label(row, text=size, font=('Segoe UI', 8, 'bold'), bg="white", fg="#2980b9", width=20, anchor='w').pack(side='left')

        except Exception as e:
            tk.Label(body, text=f"Error: {e}", bg="white", fg="red", font=('Segoe UI', 8)).pack()

        # Simple click outside or anywhere to close - DISABLED for better stability
        # p_pop.bind("<FocusOut>", lambda e: p_pop.destroy())
        # p_pop.focus_set()

    def action(self, t): 
        if not TEKLA_AVAILABLE:
            self.show_popup("CONNECTION ERROR", T("tekla_not_found"), "red")
            return
        threading.Thread(target=self.worker, args=(t,), daemon=True).start()
    def worker(self, t):
        try:
            # 1. Global Tasks (No Selection Needed)
            if t == "model_scan":
                self.log("Scanning Model...", "#2c3e50")
                asms, parts = self.engine.get_missing_drawings()
                self.show_missing_popup(asms, parts)
                return

            # 2. Selection-Based Tasks
            self.engine.set_selection_mode(t)
            
            p = self.engine.picker.PickObject(Picker.PickObjectEnum.PICK_ONE_OBJECT, "Select Object")
            if not p: return
            
            info = self.engine.get_full_data(p)
            if t == "asm":
                # Force to Assembly if it's a part
                if not isinstance(p, Assembly):
                    try: p = p.GetAssembly()
                    except: pass
                if not isinstance(p, Assembly): 
                    self.show_popup("ERROR", "Please select an Assembly object!", "red")
                    return
                info = self.engine.get_full_data(p)
                c, m = self.engine.find_similar_assemblies(p)
                self.show_popup("ASSEMBLY DETAILS", f"--- SELECTION --- \n{m}\n\n--- DETAILS ---\n{info}", "#2980b9", p)
            elif t == "part":
                # Ensure we have the Part object, not the Assembly
                if not isinstance(p, Part):
                    # If picker returned assembly, get main part as representative
                    try: p = p.GetMainPart()
                    except: pass
                if not isinstance(p, Part):
                    self.show_popup("ERROR", "Please select a Part object!", "red")
                    return
                info = self.engine.get_full_data(p)
                c, m = self.engine.find_similar_parts(p)
                self.show_popup("PART DETAILS", f"--- SELECTION --- \n{m}\n\n--- DETAILS ---\n{info}", "#27ae60", p)
            elif t == "bolt":
                if isinstance(p, BoltGroup):
                    c, m = self.engine.find_similar_bolts(p)
                    info = self.engine.get_full_data(p)
                    self.show_popup("BOLT DETAILS", f"--- SELECTION --- \n{m}\n\n--- DETAILS ---\n{info}", "#d35400", p)
            elif t == "inq": 
                # Format the info properly for Inquire
                self.show_popup("INQUIRE", f"--- SELECTION ---\n{info}", "#8e44ad", p)
            elif t == "analyze":
                # Safe check for GetAssembly
                if not hasattr(p, "GetAssembly"):
                     self.show_popup("ERROR", "Selected object type cannot be analyzed (No Assembly).", "red")
                     return
                
                if not isinstance(p, Assembly): 
                    try: p = p.GetAssembly()
                    except: pass
                ref_dna = self.engine.get_assembly_dna(p); ref_map = self.engine.get_detailed_map(p)
                reports = []
                enum = self.engine.model.GetModelObjectSelector().GetAllObjects()
                while enum.MoveNext():
                    obj = enum.Current
                    if isinstance(obj, Assembly) and obj.Identifier.ID != p.Identifier.ID:
                        if self.engine.get_assembly_dna(obj) != ref_dna:
                            w = self.engine.get_p(obj, "WEIGHT_NET"); n = self.engine.get_p(obj, "NUMBER_OF_PARTS")
                            if abs(w - self.engine.get_p(p, "WEIGHT_NET")) < 0.1 and int(n) == int(self.engine.get_p(p, "NUMBER_OF_PARTS")):
                                curr_map = self.engine.get_detailed_map(obj); obj_name = self.engine.get_p(obj, "ASSEMBLY_POS", "string") or f"ID:{obj.Identifier.ID}"
                                for prof, ref_list in ref_map.items():
                                    if prof in curr_map:
                                        for i, r_item in enumerate(ref_list):
                                            if i < len(curr_map[prof]) and abs(r_item["dist"] - curr_map[prof][i]["dist"]) > 3:
                                                reports.append(f"{obj_name}: {prof} position error!"); curr_map[prof][i]["obj"].Class = "2"; curr_map[prof][i]["obj"].Modify()
                self.engine.model.CommitChanges()
                # Format results properly
                result_text = "\n".join(reports) if reports else "All assemblies are compatible!"
                self.show_popup("ANALYSIS RESULT", f"--- FINDINGS ---\n{result_text}", "#16a085")
        except Exception as e:
            err_str = str(e).lower()
            # Filter common Tekla connection/COM errors
            if "connection" in err_str or "remoting" in err_str or "nullreference" in err_str or "com" in err_str:
                self.show_popup("CONNECTION ERROR", T("tekla_not_found"), "red")
                # Force status update
                global TEKLA_AVAILABLE
                TEKLA_AVAILABLE = False
            elif "interrupt" not in err_str: 
                self.show_popup("ERROR", f"--- ERROR ---\n{T('tekla_not_found')}\n\nTechnical Details:\n{str(e)}", "red")

    def show_missing_popup(self, asms, parts):
        if self.monitor_popup and self.monitor_popup.winfo_exists():
            self.monitor_popup.lift()
            self.monitor_popup.focus_force()
            return

        pop = tk.Toplevel(self.root)
        self.monitor_popup = pop
        pop.title("System Monitor"); 
        # Taller window to fit the terminal below cards
        bw, bh = 500, 380 # Start compact
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        bx = (sw - bw) // 2
        by = (sh - bh) // 2
        pop.geometry(f"{bw}x{bh}+{bx}+{by}") 
        pop.overrideredirect(True); pop.attributes("-topmost", True)
        pop.configure(bg='#f8f9fa', highlightthickness=1, highlightbackground="#ced4da")

        def start_m(e): pop._x, pop._y = e.x, e.y
        def do_m(e): pop.geometry(f"+{pop.winfo_x()+(e.x-pop._x)}+{pop.winfo_y()+(e.y-pop._y)}")

        header = tk.Frame(pop, bg="#1a1a1a", height=50); header.pack(fill='x')
        header.bind("<Button-1>", start_m); header.bind("<B1-Motion>", do_m)
        tk.Label(header, text="🛡️ MISSION CONTROL", bg="#1a1a1a", fg="#ffffff", font=('Segoe UI', 10, 'bold')).pack(side='left', padx=15, pady=12)
        tk.Button(header, text="✕", command=pop.destroy, bg="#1a1a1a", fg="#95a5a6", bd=0, font=('Segoe UI', 12), cursor="hand2").pack(side='right', padx=10)

        # Container for Cards
        mon_main = tk.Frame(pop, bg="#f8f9fa", padx=25, pady=15)
        mon_main.pack(fill='x')
        
        # Container for Terminal (Bottom Space)
        term_container = tk.Frame(pop, bg="#f8f9fa", padx=25, pady=0)
        term_container.pack(fill='both', expand=True, pady=(0, 25))
        
        def start_creation(objs, dtype, btn_ref):
            # Disable button
            btn_ref.config(state='disabled', text="⏳ INITIALIZING...", bg="#95a5a6")
            
            # Prepare Terminal Area
            # Clear previous terminal if any (though likely only one run per session)
            for widget in term_container.winfo_children(): widget.destroy()
            
            term_frame = tk.Frame(term_container, bg="white", highlightthickness=1, highlightbackground="#dcdcdc")
            term_frame.pack(fill='both', expand=True)
            
            # Terminal Header
            t_head = tk.Frame(term_frame, bg="#2c3e50", height=30)
            t_head.pack(fill='x'); t_head.pack_propagate(False)
            tk.Label(t_head, text="🚀 LIVE EXECUTION LOG", font=('Consolas', 9, 'bold'), bg="#2c3e50", fg="white").pack(side='left', padx=10)
            
            # Progress Bar
            p_frame = tk.Frame(term_frame, bg="white", padx=10, pady=5)
            p_frame.pack(fill='x')
            pb = ttk.Progressbar(p_frame, mode='determinate')
            pb.pack(fill='x')
            
            # Console Output
            log_box = tk.Text(term_frame, bg="#1e1e1e", fg="#ecf0f1", font=('Consolas', 8), bd=0, height=8, state='disabled')
            log_box.pack(fill='both', expand=True, padx=1, pady=1)
            
            status_lbl = tk.Label(term_frame, text="Waiting for Tekla API...", font=('Segoe UI', 8), bg="white", fg="#7f8c8d")
            status_lbl.pack(fill='x', pady=2)

            def safe_log(txt):
                log_box.config(state='normal')
                log_box.insert('end', f" {txt}\n")
                log_box.see('end')
                log_box.config(state='disabled')

            def task():
                # EXPAND UI ON START
                pop.after(0, lambda: pop.geometry("500x750"))
                
                self.batch_req_update = False
                
                def on_progress(cur, total):
                    p = int((cur/total)*100)
                    obj = objs[cur-1]
                    if dtype == "asm":
                        mark = self.engine.get_p(obj, "ASSEMBLY_POS", "string")
                        prefix = "ASM"
                    else:
                        mark = self.engine.get_p(obj, "PART_POS", "string")
                        prefix = "PRT"
                    
                    mark_display = mark if mark else 'ID:'+str(obj.Identifier.ID)
                    
                    status_suffix = ""
                    if "(?)" in mark_display:
                        status_suffix = " -> UPDATE REQUIRED"
                        self.batch_req_update = True
                        
                    display_text = f"[{cur}/{total}] {prefix}: {mark_display}{status_suffix}"
                    
                    pop.after(0, lambda: [
                        pb.config(value=p),
                        status_lbl.config(text=f"PROCESSING: {p}% ({cur}/{total})"),
                        safe_log(display_text),
                        self.footer_status.config(text=f"CREATING: {p}%", fg="#f39c12")
                    ])
                
                try:
                    count = self.engine.create_bulk_drawings(objs, dtype, on_progress)
                    
                    final_msg = f"✅ SUCCESS: {count} DRAWINGS CREATED"
                    final_bg = "#27ae60"
                    
                    if self.batch_req_update:
                        final_msg = "⚠ NUMBERING UPDATE REQUIRED"
                        final_bg = "#e74c3c" # Red warning
                    
                    pop.after(0, lambda: [
                        status_lbl.config(text=final_msg, fg=final_bg, font=('Segoe UI', 9, 'bold')),
                        btn_ref.config(state='normal', text="✓ COMPLETED" if not self.batch_req_update else "⚠ REVIEW", bg=final_bg),
                        safe_log("--- OPERATION FINISHED ---")
                    ])
                    self.log(final_msg, final_bg)
                except Exception as ex:
                    pop.after(0, lambda: [
                        safe_log(f"ERROR: {str(ex)}"),
                        btn_ref.config(state='normal', text="RETRY", bg="#e74c3c")
                    ])
                    self.log(f"BATCH FAILED", "#e74c3c")

            threading.Thread(target=task, daemon=True).start()

        def create_card(parent, title, icon, count, color, objs, dtype):
            card = tk.Frame(parent, bg="white", highlightthickness=1, highlightbackground="#e9ecef", padx=15, pady=15)
            card.pack(fill='x', pady=8)
            t_line = tk.Frame(card, bg="white"); t_line.pack(fill='x')
            tk.Label(t_line, text=f"{icon} {title}", font=('Segoe UI', 10, 'bold'), bg="white", fg="#2c3e50").pack(side='left')
            tag = tk.Label(t_line, text=f"{count} MISSING", font=('Segoe UI', 7, 'bold'), bg=color, fg="white", padx=8, pady=2)
            tag.pack(side='right')
            
            btn = tk.Button(card, text="START AUTO-GENERATION", bg=color, fg="white", font=('Segoe UI', 9, 'bold'), bd=0, pady=12, cursor="hand2")
            if count == 0: 
                btn.config(state='disabled', bg='#f1f1f1', fg='#bdc3c7', text="UP TO DATE")
            else:
                btn.config(command=lambda: start_creation(objs, dtype, btn))
            btn.pack(fill='x', pady=(15, 0))

        create_card(mon_main, "ASSEMBLY DRAWINGS", "🏗️", len(asms), "#2980b9", asms, "asm")
        create_card(mon_main, "PART DRAWINGS", "🧩", len(parts), "#27ae60", parts, "part")

if __name__ == "__main__":
    app = RibbonToolbar()
    app.root.mainloop()
