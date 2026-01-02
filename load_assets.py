import urllib.request
import tarfile
import os
import shutil

def download_monaco():
    print("📦 Downloading Monaco Editor...")
    url = "https://registry.npmjs.org/monaco-editor/-/monaco-editor-0.34.0.tgz"
    file_name = "monaco.tgz"
    urllib.request.urlretrieve(url, file_name)

    print("Extracting Monaco...")
    with tarfile.open(file_name, "r:gz") as tar:
        tar.extractall()

    target_dir = "app/static/vs"
    source_dir = "package/min/vs"

    if os.path.exists(target_dir): shutil.rmtree(target_dir)
    shutil.move(source_dir, target_dir)
    
    os.remove(file_name)
    shutil.rmtree("package")

def download_marked():
    print("📝 Downloading Marked.js (Markdown Engine)...")
    url = "https://cdn.jsdelivr.net/npm/marked/marked.min.js"
    os.makedirs("app/static/lib", exist_ok=True)
    urllib.request.urlretrieve(url, "app/static/lib/marked.min.js")

if __name__ == "__main__":
    os.makedirs("app/static", exist_ok=True)
    download_monaco()
    download_marked()
    print("✅ All Assets Ready!")