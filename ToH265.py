import os
import ffmpeg
from datetime import datetime
import subprocess

# 定义输入和输出文件夹路径
input_folder = r'Z:\照片\2018'
output_folder = r'H:\转码'
processed_file = 'processed_files.txt'

processes = [] 

# 确保输出文件夹存在
os.makedirs(output_folder, exist_ok=True)

def set_creation_date(output_path, creation_date, rel_path):
    try:
        process = subprocess.Popen(
            ['exiftool', '-overwrite_original', f'-createdate={creation_date}', output_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        # 不等待进程完成，立即返回
        print(f"开始设置文件 {rel_path} 的创建日期为 {creation_date}")
        return process
    except Exception as e:
        print(f"启动设置文件 {rel_path} 创建日期的进程时发生异常: {e}")
        return None

# 读取已处理的文件列表
processed_files = set()
if os.path.exists(processed_file):
    with open(processed_file, 'r') as f:
        processed_files = set(f.read().splitlines())

filelist = []
# 遍历input_folder及其所有子目录
for root, dirs, files in os.walk(input_folder):
    for filename in files:
        if filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.flv', '.mts')):
            full_path = os.path.join(root, filename)
            if full_path not in processed_files:
                filelist.append(full_path)
                print(f"待处理文件: {full_path}")

count = 0
# 遍历所有待处理的文件
for input_path in filelist:
    rel_path = os.path.relpath(input_path, input_folder)
    output_rel_path = os.path.splitext(rel_path)[0] + "_hevc_amf.mp4"
    output_path = os.path.join(output_folder, output_rel_path)


    #如果输出文件已经存在,重命名
    duplicate_count = 1
    while os.path.exists(output_path): 
        output_path = os.path.splitext(output_path)[0] + f"_{duplicate_count}.mp4"
        duplicate_count += 1
    print(f"输出文件: {output_path}")
    
    # 确保输出文件的目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 使用 ffmpeg-python 获取原视频的创建日期
    try:
        probe = ffmpeg.probe(input_path, v='error', select_streams='v:0', show_entries='format_tags=creation_time')
        creation_date = probe.get('format', {}).get('tags', {}).get('creation_time', None)
        
        if creation_date:
            try:
                if 'T' in creation_date and 'Z' in creation_date:
                    creation_timestamp = datetime.strptime(creation_date, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
                else:
                    creation_timestamp = datetime.strptime(creation_date, "%Y-%m-%d %H:%M:%S").timestamp()
            except ValueError as ve:
                print(f"时间格式错误: {ve}")
                creation_timestamp = None
    
    except ffmpeg.Error as e:
        print(f"获取文件 {rel_path} 元数据时发生错误: {e}")
        creation_timestamp = None
    
    # 使用 ffmpeg-python 转码视频
    try:
        ffmpeg.input(input_path).output(output_path, vcodec='hevc_amf', crf=22, acodec='aac', audio_bitrate='576k', ar='44100', ac=2).run()
        print(f"视频 {rel_path} 转码完成！")
    except ffmpeg.Error as e:
        print(f"转码文件 {rel_path} 时发生错误: {e}")
        continue

    if not creation_date:
        try:
            creation_date = datetime.fromtimestamp(os.path.getmtime(input_path)).strftime('%Y-%m-%d %H:%M:%S')
        except OSError as e:
            print(f"获取文件 {rel_path} 修改日期时发生错误: {e}")

    if creation_date:
        process = set_creation_date(output_path, creation_date, rel_path)
        if process:
            processes.append((process, rel_path))
    else:
        print(f"未能设置文件 {rel_path} 的创建日期，因为无法提取原文件的创建日期。")

    for i in range(len(processes) - 1, -1, -1):
        process, rel_path = processes[i]
        if process.returncode == 0:
            del processes[i]
            print(f"成功设置文件 {rel_path} 的创建日期")

    # 将处理完的文件添加到已处理列表
    with open(processed_file, 'a') as f:
        f.write(input_path + '\n')

    count += 1
    print(f"============================ 视频 {rel_path} 转码完成，并尝试设置了创建日期！进度：{count}/{len(filelist)} ============================")



for process, rel_path in processes:
    stdout, stderr = process.communicate()
    if process.returncode == 0:
        print(f"成功设置文件 {rel_path} 的创建日期")
    else:
        print(f"设置文件 {rel_path} 创建日期时发生错误: {stderr.decode()}")

if processes:
    print(f"有 {len(processes)} 个文件的创建日期设置失败:")
    for process, rel_path in processes:
        print(f"- {rel_path}")

print("所有视频转码完成！")
