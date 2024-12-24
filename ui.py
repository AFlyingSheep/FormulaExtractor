import tkinter as tk
from tkinter import messagebox
import threading
import sys
from downloader import download
from extractor import extract_formulas


class RedirectText:
    """重定向 stdout 和 stderr 到 tkinter Text 控件"""

    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        """将消息写入 Text 控件"""
        self.text_widget.insert(tk.END, message)
        self.text_widget.yview(tk.END)  # 自动滚动到最新输出

    def flush(self):
        """flush 方法必须实现，但在此不做任何操作"""
        pass


class FormulaExtractorApp:
    def __init__(self):
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("Formula Extractor")
        self.root.geometry("600x600")

        # 创建 UI 元素
        self.create_widgets()

        # 重定向 stdout 和 stderr 到日志框
        sys.stdout = RedirectText(self.output_text)
        sys.stderr = RedirectText(self.output_text)

    def create_widgets(self):
        # 创建一个框架，将界面分成不同部分
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # 创建 URL 输入框
        tk.Label(frame, text="Input URL:").pack(pady=5)
        self.url_entry = tk.Entry(frame, width=80)
        self.url_entry.pack(pady=5)

        # 转换按钮
        tk.Button(frame, text="Transform Now!", command=self.on_convert).pack(pady=10)

        # 创建一个框架用于显示日志
        log_frame = tk.Frame(frame)
        log_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # 日志输出框
        tk.Label(log_frame, text="Log output:").pack(pady=5)
        self.output_text = tk.Text(log_frame, height=4, width=80, wrap=tk.WORD)
        self.output_text.pack(pady=5)

        # 创建一个框架用于显示提取的结果
        result_frame = tk.Frame(frame)
        result_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # 结果输出框
        tk.Label(result_frame, text="Extract result").pack(pady=5)
        self.result_text = tk.Text(result_frame, height=20, width=80, wrap=tk.WORD)
        self.result_text.pack(pady=5)

        # 输出框设置为只读，用户不能编辑
        self.output_text.config(state=tk.DISABLED)
        self.result_text.config(state=tk.DISABLED)

    def on_convert(self):
        """点击转换按钮后的回调"""
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please input URL!")
            return

        # 清空输出框并显示加载信息
        self.output_text.config(state=tk.NORMAL)  # 允许编辑
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Extracting...\n")
        self.output_text.config(state=tk.DISABLED)  # 禁止编辑

        # 清空结果框
        self.result_text.config(state=tk.NORMAL)  # 允许编辑
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)  # 禁止编辑

        # 启动新线程执行公式提取，避免阻塞 UI
        thread = threading.Thread(target=self.convert_task, args=(url,))
        thread.start()

    def convert_task(self, url):
        """后台任务：提取公式并更新 UI"""
        try:
            print("Start to extract...")  # 会显示在日志框中
            hash_value = hash(url) & 0xFFFFFFFF
            save_file_name = f"./.cache/{hash_value}.html"
            download(url, save_file_name)
            formulas = extract_formulas(save_file_name)
            print(formulas)

            if formulas and formulas[0].startswith("Error:"):
                self.update_log_output(formulas[0])  # 显示错误信息
            else:
                self.update_log_output("Successful!\n")
                self.update_result_output("\n".join(formulas))  # 显示提取的公式
        except Exception as e:
            self.update_log_output(f"Extract error: {e}")

    def update_log_output(self, text):
        """在主线程中更新日志框"""
        self.output_text.config(state=tk.NORMAL)  # 允许编辑
        self.output_text.insert(tk.END, text)
        self.output_text.config(state=tk.DISABLED)  # 禁止编辑

    def update_result_output(self, text):
        """在主线程中更新结果框"""
        self.result_text.config(state=tk.NORMAL)  # 允许编辑
        self.result_text.insert(tk.END, text)
        self.result_text.config(state=tk.DISABLED)  # 禁止编辑

    def run(self):
        self.root.mainloop()
