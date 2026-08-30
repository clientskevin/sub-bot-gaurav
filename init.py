import os
import subprocess

folders = ["app", "utils", "service", "repository", "model", "enums", "schemas"]
for folder in folders:
    if not os.path.exists(folder):
        continue
    print(f"Creating __init__.py for {folder}")
    subprocess.run(["mkinit", folder, "-w", "--recursive", "--relative", "--nomods"])


subprocess.run(["ruff", "format", "."])
