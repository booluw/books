"""Run every example's unit tests. Usage: python3 run_all_tests.py"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).parent
failed = []
for folder in sorted(p for p in ROOT.iterdir() if p.is_dir() and any(p.glob("test_*.py"))):
    print(f"== {folder.name}")
    result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", ".", "-p", "test_*.py"],
                            cwd=folder)
    if result.returncode:
        failed.append(folder.name)
print("\nFAILED: " + ", ".join(failed) if failed else "\nAll example tests passed.")
sys.exit(1 if failed else 0)
