import os
import shutil

def copy_files(files):
    """输入复制文件路径数组，可以使用通配符,格式为：[{'src':'','dst':''}],src可以是文件或目录，dst必须是目录"""
    for file in files:
        src = file['src']
        dst = file['dst']
        if not os.path.exists(dst):
            os.makedirs(dst)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
        elif os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            print(f"路径 {src} 不存在")