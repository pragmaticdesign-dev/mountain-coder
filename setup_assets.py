# Save as download_assets.py and run it: python download_assets.py
import urllib.request
import tarfile
import os
import shutil

print("Downloading Monaco Editor...")
url = "https://registry.npmjs.org/monaco-editor/-/monaco-editor-0.34.0.tgz"
file_name = "monaco.tgz"
urllib.request.urlretrieve(url, file_name)

print("Extracting...")
with tarfile.open(file_name, "r:gz") as tar:
    tar.extractall()

# Move the 'vs' folder to app/static/vs
target_dir = "app/static/vs"
source_dir = "package/min/vs"

os.makedirs("app/static", exist_ok=True)
if os.path.exists(target_dir):
    shutil.rmtree(target_dir)

shutil.move(source_dir, target_dir)

# Cleanup
os.remove(file_name)
shutil.rmtree("package")
print("✅ Assets ready in app/static/vs")