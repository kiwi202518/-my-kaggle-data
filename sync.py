import os
import shutil
import subprocess
from datetime import datetime

# ===== 配置参数（根据实际情况修改）=====
DATA_SOURCE = "F:/CUDA/0Kaggle/KaggleData"  # .mtsd数据源目录
GIT_REPO = "C:/Users/Adminstractor/-my-kaggle-data"  # 本地Git仓库目录
GIT_BRANCH = "main"  # 远程分支（默认main，旧仓库可能是master）
# ======================================

def execute_git_cmd(cmd):
    """封装Git命令执行，捕获结果与错误（核心优化1：解决命令静默失败）"""
    try:
        # 执行命令并捕获输出/错误，超时120秒（应对网络慢）
        result = subprocess.run(
            cmd,
            cwd=GIT_REPO,  # 固定在Git仓库目录执行，避免目录切换问题
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            timeout=120
        )
        
        # 打印命令日志（便于调试）
        print(f"[Git命令] {' '.join(cmd)}")
        if result.stdout:
            print(f"[执行结果] {result.stdout.strip()}")
        if result.stderr:
            # 区分警告和错误（如"无新修改"属于警告，不中断流程）
            if "nothing to commit" in result.stderr.lower():
                print(f"[提示] {result.stderr.strip()}")
            else:
                print(f"[警告] {result.stderr.strip()}")
        
        # 命令返回非0则视为失败（抛出异常）
        result.check_returncode()
        return True
    except subprocess.TimeoutExpired:
        print(f"[错误] Git命令超时（超过120秒）：{' '.join(cmd)}")
        return False
    except subprocess.CalledProcessError:
        print(f"[错误] Git命令执行失败：{' '.join(cmd)}")
        return False
    except Exception as e:
        print(f"[未知错误] 执行Git命令时出错：{str(e)}")
        return False

def sync_to_github():
    print("="*60)
    print(f"同步开始：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # --------------------------
    # 优化1：前置路径与仓库校验（解决路径错误/非Git仓库问题）
    # --------------------------
    # 检查数据源目录是否存在
    if not os.path.exists(DATA_SOURCE):
        print(f"数据源目录不存在！路径：{DATA_SOURCE}")
        return
    # 检查Git仓库目录是否存在
    if not os.path.exists(GIT_REPO):
        print(f" Git仓库目录不存在！路径：{GIT_REPO}")
        return
    # 检查是否为合法Git仓库（是否有.git文件夹）
    if not os.path.exists(os.path.join(GIT_REPO, ".git")):
        print(f" {GIT_REPO} 不是合法Git仓库（缺少.git文件夹）")
        return

    # --------------------------
    # 原逻辑1：清空仓库（保留核心文件）
    # --------------------------
    print("\n1. 开始清空仓库（保留核心文件）...")
    keep_files = [".git", "README.md", ".gitignore", "sync.py"]
    for item in os.listdir(GIT_REPO):
        if item not in keep_files:
            item_path = os.path.join(GIT_REPO, item)
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    print(f" 删除目录：{item}")
                else:
                    os.remove(item_path)
                    print(f" 删除文件：{item}")
            except Exception as e:
                # 优化2：删除失败不中断（如文件被占用），仅提示
                print(f" 删除{item}失败：{str(e)}（跳过继续）")

    # --------------------------
    # 优化3：文件复制+完整性校验（解决复制半截/失败问题）
    # --------------------------
    print("\n2. 开始复制.mtsd文件...")
    # 筛选数据源目录下的.mtsd文件（忽略大小写，避免".MTSD"识别不到）
    mtsd_files = [f for f in os.listdir(DATA_SOURCE) if f.lower().endswith(".mtsd")]
    
    if not mtsd_files:
        print(f"数据源目录中未找到任何.mtsd文件！路径：{DATA_SOURCE}")
        return
    print(f" 找到{len(mtsd_files)}个.mtsd文件：{mtsd_files}")

    # 逐个复制并校验文件大小（确保复制完整）
    copy_failed = []
    for file in mtsd_files:
        src = os.path.join(DATA_SOURCE, file)
        dst = os.path.join(GIT_REPO, file)
        try:
            shutil.copy2(src, dst)
            # 校验：源文件与目标文件大小一致才视为成功
            if os.path.getsize(src) == os.path.getsize(dst):
                print(f" 复制成功：{file}（大小：{os.path.getsize(src)//1024}KB）")
            else:
                raise Exception("源文件与目标文件大小不一致")
        except Exception as e:
            copy_failed.append(file)
            print(f" 复制{file}失败：{str(e)}")

    # 若所有文件复制失败，终止同步
    if len(copy_failed) == len(mtsd_files):
        print(f"\n 所有.mtsd文件复制失败，同步终止")
        return
    # 若部分失败，提示但继续（避免因单个文件影响整体）
    elif copy_failed:
        print(f"\n 部分文件复制失败：{copy_failed}（继续同步其他文件）")

    # --------------------------
    # 优化4：Git提交推送+结果校验（解决推送失败无提示问题）
    # --------------------------
    print("\n3. 开始Git提交与推送...")
    # 步骤1：git add（暂存所有修改）
    if not execute_git_cmd(["git", "add", "."]):
        print(" git add执行失败，同步终止")
        return
    # 步骤2：git commit（带时间戳日志，便于追溯）
    commit_msg = f"Update MTSD data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    # 即使commit无新修改（如文件未变），也继续推送（兼容重复同步）
    execute_git_cmd(["git", "commit", "-m", commit_msg])
    # 步骤3：git push（指定分支，避免推错）
    if not execute_git_cmd(["git", "push", "origin", GIT_BRANCH]):
        print(" git push执行失败，同步终止（请检查Git凭证/网络）")
        return

    # --------------------------
    # 优化5：同步完成总结（清晰展示结果）
    # --------------------------
    print("\n" + "="*60)
    print(f"同步完成：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"统计：共{len(mtsd_files)}个.mtsd文件，成功复制{len(mtsd_files)-len(copy_failed)}个")
    print(f"查看GitHub：https://github.com/kiwi202518/-my-kaggle-data/tree/{GIT_BRANCH}")
    print("="*60)

if __name__ == "__main__":
    sync_to_github()