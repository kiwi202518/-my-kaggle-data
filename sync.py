# sync.py - 自动同步脚本
import os, shutil, subprocess
from datetime import datetime

# ===== 需修改的配置 =====
DATA_SOURCE = "F:\CUDA\0Computer316\CuData\FiveM-MODE\15%"      # 替换为您的数据文件夹路径（如"C:/Users/Name/data"）
GIT_REPO = "C:\Users\Adminstractor\-my-kaggle-data"        # 替换为GitHub仓库本地路径（如"C:/my-kaggle-data"）
# ======================

def sync_to_github():
    print("🔄 开始同步数据到GitHub...")
    
    # 1. 清空仓库（保留.git和README.md）
    for item in os.listdir(GIT_REPO):
        if item not in ['.git', 'README.md', '.gitignore', 'sync.py']:
            path = os.path.join(GIT_REPO, item)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
    
    # 2. 复制新数据到仓库
    for file in os.listdir(DATA_SOURCE):
        src = os.path.join(DATA_SOURCE, file)
        dst = os.path.join(GIT_REPO, file)
        if os.path.isfile(src):  # 只复制文件，忽略子目录
            shutil.copy2(src, dst)
    
    # 3. 提交到GitHub
    os.chdir(GIT_REPO)
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", f"Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
    subprocess.run(["git", "push"])
    
    print("✅ 同步完成！")

if __name__ == "__main__":
    sync_to_github()
