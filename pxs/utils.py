import os
import shutil

def copy_files(files):
    """输入复制文件路径数组，可以使用通配符,格式为：[{'src':'','dst':''}]"""
    for file in files:
        src = file['src']
        dst = file['dst']
        if os.path.isfile(src):
            # 处理文件复制
            if os.path.isdir(dst):
                # 目标是目录，将文件复制到目录下
                dst_file = os.path.join(dst, os.path.basename(src))
                # 确保目标目录存在
                os.makedirs(dst, exist_ok=True)
                shutil.copy2(src, dst_file)
            else:
                # 目标是文件，确保父目录存在
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
        elif os.path.isdir(src):
            # 处理目录复制，确保目标目录存在
            os.makedirs(dst, exist_ok=True)
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            print(f"路径 {src} 不存在")