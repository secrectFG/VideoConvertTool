import os
import ffmpeg
from datetime import datetime
import subprocess

# 定义输入和输出文件夹路径
input_folder = r'H:\导出\视频'
output_folder = r'F:\转码'

# 确保输出文件夹存在
os.makedirs(output_folder, exist_ok=True)



filelist = []
for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.flv', '.mts')):
        filelist.append(filename)

count = 0
# 遍历输入文件夹中的所有文件
for filename in filelist:
        
    input_path = os.path.join(input_folder, filename)
    output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_hevc_amf.mp4")
    
    # 使用 ffmpeg-python 获取原视频的创建日期
    try:
        # 获取视频的元数据
        probe = ffmpeg.probe(input_path, v='error', select_streams='v:0', show_entries='format_tags=creation_time')
        
        # 检查 'tags' 是否存在，避免 KeyError
        creation_date = probe.get('format', {}).get('tags', {}).get('creation_time', None)
        
        if creation_date:
            try:
                # 如果日期包含 'T' 和 'Z'，则使用以下格式
                if 'T' in creation_date and 'Z' in creation_date:
                    creation_timestamp = datetime.strptime(creation_date, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
                else:
                    # 否则使用没有 'T' 和 'Z' 的格式
                    creation_timestamp = datetime.strptime(creation_date, "%Y-%m-%d %H:%M:%S").timestamp()
            except ValueError as ve:
                print(f"时间格式错误: {ve}")
                creation_timestamp = None

    
    except ffmpeg.Error as e:
        print(f"获取文件 {filename} 元数据时发生错误: {e}")
        creation_timestamp = None
    
    # 使用 ffmpeg-python 转码视频
    try:
        ffmpeg.input(input_path).output(output_path, vcodec='hevc_amf', crf=22, acodec='aac', audio_bitrate='576k', ar='44100', ac=2).run()
        print(f"视频 {filename} 转码完成！")
    except ffmpeg.Error as e:
        print(f"转码文件 {filename} 时发生错误: {e}")

    if not creation_date:
        #获取修改日期
        try:
            creation_date = datetime.fromtimestamp(os.path.getmtime(input_path)).strftime('%Y-%m-%d %H:%M:%S')
        except OSError as e:
            print(f"获取文件 {filename} 修改日期时发生错误: {e}")

    # 如果成功提取到创建日期，使用 exiftool 设置创建日期
    if creation_date:
        try:
            # 使用 exiftool 设置创建日期
            subprocess.run(['exiftool','-overwrite_original', '-createdate={}'.format(creation_date), output_path], check=True)
            print(f"设置文件 {filename} 的创建日期为 {creation_date}")
            
        except subprocess.CalledProcessError as e:
            print(f"设置文件 {filename} 创建日期时发生错误: {e}")
            break
    else:
        print(f"未能设置文件 {filename} 的创建日期，因为无法提取原文件的创建日期。")

    count += 1
    print(f"============================ 视频 {filename} 转码完成，并尝试设置了创建日期！进度：{count}/{len(filelist)} ============================")

print("所有视频转码完成！")
