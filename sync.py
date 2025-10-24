# sync.py - 自动同步脚本
import os, shutil, subprocess
from datetime import datetime

# ===== 配置参数 =====
DATA_SOURCE = "F:/CUDA/0Kaggle/KaggleData"  # 您的.mtsd数据文件夹
GIT_REPO = "C:/Users/Adminstractor/-my-kaggle-data"  # GitHub仓库路径
# ======================

def sync_to_github():
    print("🔄 开始同步.mtsd数据到GitHub...")
    
    # 1. 清空仓库（保留必要文件）
    for item in os.listdir(GIT_REPO):
        if item not in ['.git', 'README.md', '.gitignore', 'sync.py']:
            path = os.path.join(GIT_REPO, item)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
    
    # 2. 复制所有.mtsd文件到仓库
    mtsd_files = [f for f in os.listdir(DATA_SOURCE) if f.endswith('.mtsd')]
    print(f"📁 找到 {len(mtsd_files)} 个.mtsd文件")
    
    for file in mtsd_files:
        src = os.path.join(DATA_SOURCE, file)
        dst = os.path.join(GIT_REPO, file)
        shutil.copy2(src, dst)
        print(f"✅ 已复制: {file}")
    
    # 3. 提交到GitHub
    os.chdir(GIT_REPO)
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", f"Update MTSD data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
    subprocess.run(["git", "push"])
    
    print("✅ .mtsd数据同步完成！")

if __name__ == "__main__":
    sync_to_github()