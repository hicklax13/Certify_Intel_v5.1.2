import os
import sys
import importlib.util
import traceback

def check_imports(start_dir):
    print(f"[INFO] Starting Static Analysis on {start_dir}...")
    error_count = 0
    checked_count = 0
    
    # Walk through all python files
    for root, dirs, files in os.walk(start_dir):
        for file in files:
            if file.endswith(".py") and file != "verify_system.py":
                checked_count += 1
                file_path = os.path.join(root, file)
                module_name = file[:-3]
                
                try:
                    # Attempt to compile first (Syntax Check)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        source = f.read()
                    compile(source, file_path, 'exec')
                    
                    # Attempt to import (Runtime Import Check)
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[module_name] = module
                        spec.loader.exec_module(module)
                        
                    print(f"[PASS] {file} - OK")
                    
                except SyntaxError as e:
                    print(f"[FAIL] {file} - SYNTAX ERROR")
                    print(f"   Line {e.lineno}: {e.msg}")
                    error_count += 1
                except ImportError as e:
                    print(f"[FAIL] {file} - IMPORT ERROR")
                    print(f"   {e}")
                    error_count += 1
                except Exception as e:
                    print(f"[WARN] {file} - RUNTIME ERROR DURING IMPORT")
                    print(f"   {e}")
                    error_count += 1

    print("-" * 40)
    print(f"Checked {checked_count} files.")
    if error_count == 0:
        print("SUCCESS: No static, syntax, or import errors found.")
    else:
        print(f"FAILED: Found {error_count} errors.")
        sys.exit(1)

if __name__ == "__main__":
    # Add current directory to path to simulate running from backend root
    sys.path.append(os.getcwd())
    check_imports(os.getcwd())
