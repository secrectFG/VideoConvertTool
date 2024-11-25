from concurrent.futures import ThreadPoolExecutor, as_completed
from logging.handlers import RotatingFileHandler
import os
import ffmpeg
from datetime import datetime
import logging
import functions

# 定义输入和输出文件夹路径
input_folder = r'Z:\照片\2023'
# input_folder = r'C:\MyDat\videos'
output_folder = r'H:\转码'
processed_file = 'processed_files.txt'

# 确保日志目录存在
log_directory = 'logs'
os.makedirs(log_directory, exist_ok=True)

# 创建日志文件路径
log_file = os.path.join(log_directory, 'video_processing.log')

# 设置日志格式
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 创建RotatingFileHandler
file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8')
file_handler.setFormatter(log_formatter)

# 创建StreamHandler用于控制台输出
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

# 配置根日志记录器
logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])

# 获取根日志记录器
logger = logging.getLogger()



# 确保输出文件夹存在
os.makedirs(output_folder, exist_ok=True)


# 读取已处理的文件列表
processed_files = set()
if os.path.exists(processed_file):
    with open(processed_file,encoding='utf-8', mode='r') as f:
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

logger.info(f"待处理文件总数: {len(filelist)}")


def process_files(executor: ThreadPoolExecutor,future_to_path):
    progressdata = {"count":0, "total":len(filelist)}
    # 遍历所有待处理的文件
    for input_path in filelist:
        rel_path = os.path.relpath(input_path, input_folder)
        output_rel_path = os.path.splitext(rel_path)[0] + "_hevc_amf.mp4"
        output_path = os.path.join(output_folder, output_rel_path)

        # 如果输出文件已经存在,重命名
        duplicate_count = 1
        while os.path.exists(output_path): 
            output_path = os.path.splitext(output_path)[0] + f"_{duplicate_count}.mp4"
            duplicate_count += 1
        logging.info(f"输出文件: {output_path}")
        
        # 确保输出文件的目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 使用 ffmpeg-python 获取原视频的创建日期
        try:
            probe = ffmpeg.probe(input_path, v='error', select_streams='v:0', show_entries='format_tags=creation_time')
            creation_date = probe.get('format', {}).get('tags', {}).get('creation_time', None)
        except ffmpeg.Error as e:
            logging.warning(f"获取文件 {rel_path} 元数据时发生错误: {e}")
        
        # 使用 ffmpeg-python 转码视频
        try:
            ffmpeg.input(input_path).output(output_path, vcodec='hevc_amf', crf=22, acodec='aac', audio_bitrate='576k', ar='44100', ac=2).run()
            logging.info(f"视频 {rel_path} 转码完成！")
        except ffmpeg.Error as e:
            logging.error(f"转码文件 {rel_path} 时发生错误: {e}")
            continue

        if not creation_date:
            try:
                creation_date = datetime.fromtimestamp(os.path.getmtime(input_path)).strftime('%Y-%m-%d %H:%M:%S')
            except OSError as e:
                logging.error(f"获取文件 {rel_path} 修改日期时发生错误: {e}")

        if creation_date:
            print(f"设置文件 {rel_path} 的创建日期为 {creation_date}")
            future = executor.submit(functions.set_and_monitor_creation_date, 
                output_path, 
                creation_date,
                input_path, logging, 
                processed_file,
                progressdata)
            future_to_path[future] = input_path
        else:
            logging.warning(f"未能设置文件 {rel_path} 的创建日期，因为无法提取原文件的创建日期。")


        
        logging.info(f"视频 {rel_path} 转码完成")


def main():
    future_to_path = {}
    with ThreadPoolExecutor(max_workers=2) as executor: # 使用线程池并发处理
        process_files(executor, future_to_path)

     # 等待所有任务完成并处理结果
    for future in as_completed(future_to_path):
        input_path = future_to_path[future]
        try:
            success = future.result()
            if not success:
                logging.warning(f"文件 {input_path} 的创建日期设置失败")
        except Exception as e:
            logging.error(f"处理文件 {input_path} 时发生异常: {e}")

    logging.info("所有视频转码完成！")
    print("所有视频转码完成！")


if __name__ == "__main__":
    main()