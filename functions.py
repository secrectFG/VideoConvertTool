from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import threading


def set_and_monitor_creation_date(output_path, 
                                  creation_date, 
                                  input_path, 
                                  logging, 
                                  processed_file,
                                  progressdata):
    try:
        progressdata['count'] += 1
        total = progressdata['total']
        count = progressdata['count']
        logging.info(f"开始处理文件日期 {output_path}")
        process = subprocess.Popen(
            ['exiftool', '-overwrite_original', f'-createdate={creation_date}', output_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        logging.info(f"开始设置文件 {output_path} 的创建日期为 {creation_date}")
        
        process.wait()
        
        if process.returncode == 0:
            logging.info(f"成功设置文件 {output_path} 的创建日期")
            # 将处理完的文件添加到已处理列表
            with threading.Lock():
                with open(processed_file, encoding='utf-8', mode='a') as f:
                    f.write(input_path + '\n')
            logging.info(f"已完成文件: {input_path} 进度: {count}/{total} 百分比： {round(count/total*100, 2)}%")
            return True
        else:
            logging.error(f"设置文件 {output_path} 创建日期时发生错误")
            return False
    except Exception as e:
        logging.error(f"处理文件 {output_path} 创建日期时发生异常: {e}")
        return False