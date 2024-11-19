import os
import ffmpeg
import tkinter as tk
from tkinter import filedialog, messagebox
import json

# 加载上次保存的路径
def load_paths():
    if os.path.exists('paths.json'):
        with open('paths.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'input_folder': '', 'output_folder': ''}

# 保存当前路径
def save_paths(input_folder, output_folder):
    with open('paths.json', 'w', encoding='utf-8') as f:
        json.dump({'input_folder': input_folder, 'output_folder': output_folder}, f)

# 视频转码函数
def convert_video(input_file, output_file):
    try:
        # 使用 ffmpeg 进行视频转码
        ffmpeg.input(input_file).output(output_file).run()
    except ffmpeg.Error as e:
        print(f"转码失败: {e}")
        messagebox.showerror("错误", f"转码失败: {e}")

# 创建GUI界面
class VideoConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("视频转码工具")
        self.root.geometry("500x250")

        # 加载上次的路径
        paths = load_paths()
        self.input_folder = paths['input_folder']
        self.output_folder = paths['output_folder']

        # 输入文件夹选择
        self.input_label = tk.Label(root, text="输入文件夹:")
        self.input_label.grid(row=0, column=0, padx=10, pady=5, sticky='e')

        self.input_var = tk.StringVar()
        self.input_var.set(self.input_folder)
        self.input_entry = tk.Entry(root, width=30, textvariable=self.input_var)
        self.input_entry.grid(row=0, column=1, padx=10, pady=5)

        self.input_button = tk.Button(root, text="选择文件夹", command=self.select_input_folder)
        self.input_button.grid(row=0, column=2, padx=10, pady=5)

        # 输出文件夹选择
        self.output_label = tk.Label(root, text="输出文件夹:")
        self.output_label.grid(row=1, column=0, padx=10, pady=5, sticky='e')

        self.output_var = tk.StringVar()
        self.output_var.set(self.output_folder)
        self.output_entry = tk.Entry(root, width=30, textvariable=self.output_var)
        self.output_entry.grid(row=1, column=1, padx=10, pady=5)

        self.output_button = tk.Button(root, text="选择文件夹", command=self.select_output_folder)
        self.output_button.grid(row=1, column=2, padx=10, pady=5)

        # 开始转码按钮
        self.start_button = tk.Button(root, text="开始转码", command=self.start_conversion)
        self.start_button.grid(row=2, column=0, columnspan=3, pady=20)

        # 进度显示
        self.progress_label = tk.Label(root, text="准备开始转码...")
        self.progress_label.grid(row=3, column=0, columnspan=3, pady=5)

    def select_input_folder(self):
        folder = filedialog.askdirectory(initialdir=self.input_folder)
        if folder:
            self.input_folder = folder
            self.input_var.set(self.input_folder)
            save_paths(self.input_folder, self.output_folder)

    def select_output_folder(self):
        folder = filedialog.askdirectory(initialdir=self.output_folder)
        if folder:
            self.output_folder = folder
            self.output_var.set(self.output_folder)
            save_paths(self.input_folder, self.output_folder)

    def start_conversion(self):
        input_folder = self.input_folder
        output_folder = self.output_folder

        if not input_folder or not output_folder:
            messagebox.showerror("错误", "请输入有效的文件夹路径！")
            return

        self.progress_label.config(text="开始转码...")

        # 获取文件夹中的视频文件
        video_files = [f for f in os.listdir(input_folder) if f.endswith(('.mp4', '.avi', '.mov'))]

        if not video_files:
            messagebox.showwarning("提示", "没有找到视频文件！")
            return

        # 遍历视频文件并转码
        for video_file in video_files:
            input_file = os.path.join(input_folder, video_file)
            output_file = os.path.join(output_folder, f"converted_{video_file}")
            convert_video(input_file, output_file)

        self.progress_label.config(text="转码完成！")
        messagebox.showinfo("完成", "所有视频转码完成！")

# 启动应用
if __name__ == "__main__":
    root = tk.Tk()
    app = VideoConverterApp(root)
    root.mainloop()
