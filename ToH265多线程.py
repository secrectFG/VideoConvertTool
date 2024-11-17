import os
import subprocess
from concurrent.futures import ProcessPoolExecutor

# 定义输入和输出文件夹路径
input_folder = r'I:\同步用\待转码'
output_folder = r'I:\同步用\转码'

# 定义转码函数
def transcode_video(filename):


    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)

    # 检查文件是否为视频文件（可以根据扩展名来判断）
    
    if filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.flv')):
        print(f"正在处理: {filename}")
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_h265.mp4")
        
        # ffmpeg 命令
        command = [
            'ffmpeg',
            '-i', input_path,         # 输入文件
            '-c:v', 'libx265',        # 使用 H.265 编码
            '-preset', 'medium',      # 编码预设（可以是 ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow）
            '-crf', '22',             # 固定质量参数，越低质量越高，默认23，范围是0-51
            '-c:a', 'copy',           # 音频流直接复制
            output_path               # 输出文件
        ]
        
        # 执行 ffmpeg 命令
        subprocess.run(command)
        print(f"已完成: {filename}")

# 使用 if __name__ == '__main__' 来保护多进程代码
if __name__ == '__main__':
    # 获取输入文件夹中的所有文件

    filenames = os.listdir(input_folder)

    max_workers = 2

    # 使用 ProcessPoolExecutor 来并行处理转码，并限制最大进程数
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        executor.map(transcode_video, filenames)

    print("所有视频转码完成！")
