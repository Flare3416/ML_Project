import os
import shutil
import kagglehub

# Create target folder
target_dir = "UECFOOD256"
os.makedirs(target_dir, exist_ok=True)

# Download dataset
path = kagglehub.dataset_download("rkuo2000/uecfood256")

print("Downloaded to:", path)

# Move contents into UECFOOD256/
for item in os.listdir(path):
    src = os.path.join(path, item)
    dst = os.path.join(target_dir, item)

    if os.path.isdir(src):
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        shutil.copy2(src, dst)

print("Dataset moved to ./UECFOOD256/")