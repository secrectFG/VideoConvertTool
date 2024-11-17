import os
import subprocess

# 定义输入和输出文件夹路径
input_folder = r'I:\同步用\待转码'
output_folder = r'I:\同步用\转码'

# 确保输出文件夹存在
os.makedirs(output_folder, exist_ok=True)

# 遍历输入文件夹中的所有文件
for filename in os.listdir(input_folder):
    # 检查文件是否为视频文件（可以根据扩展名来判断）
    if filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.flv','.mts',)):
        print(f"正在处理文件: {filename}")
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_hevc_amf.mp4")

        # ffmpeg 命令
        command = [
            'ffmpeg',
            '-i', input_path,         # 输入文件
            '-c:v', 'hevc_amf',        # 使用 H.265 编码(hevc_amf不支持copy音频流)
            # '-preset', 'medium',      # 编码预设（可以是ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow）
            '-crf', '22',             # 固定质量参数，越低质量越高，默认23，范围是0-51
            '-c:a', 'aac',           
            '-b:a', '576k',           # 音频比特率
            '-ar', '44100',             # 音频采样率
            '-ac', '2',               # 音频通道数
            output_path               # 输出文件
        ]

        # 执行 ffmpeg 命令
        subprocess.run(command)

print("视频转码完成！")
