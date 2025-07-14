import tkinter as tk
from tkinter import ttk, messagebox
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from extractor import extract_formulas  # 假设之前写好的公式提取函数
from downloader import download


class FormulaExtractorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Formula Extractor")
        self.root.geometry("600x600")
        self.create_widgets()

    def create_widgets(self):
        # 设置整体背景颜色
        self.root.configure(bg="#f9f9f9")

        # 主框架
        main_frame = tk.Frame(self.root, bg="#f9f9f9")
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # URL 输入框
        tk.Label(main_frame, text="Input URL:", bg="#f9f9f9").pack(pady=5, anchor="w")
        self.url_entry = tk.Entry(main_frame, width=80)
        self.url_entry.pack(pady=5)

        # 转换按钮
        tk.Button(main_frame, text="Transform Now!", command=self.on_convert).pack(
            pady=10
        )

        # 分隔线
        ttk.Separator(main_frame, orient="horizontal").pack(fill=tk.X, pady=10)

        # 日志输出框
        tk.Label(main_frame, text="Log output:", bg="#f9f9f9").pack(pady=5, anchor="w")
        self.log_text = tk.Text(
            main_frame,
            height=8,
            width=80,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#f7f7f7",
            relief=tk.SUNKEN,
            bd=1,
        )
        self.log_text.pack(pady=5)

        # 分隔线
        ttk.Separator(main_frame, orient="horizontal").pack(fill=tk.X, pady=10)

        # 创建公式显示框
        tk.Label(main_frame, text="Extract result", bg="#f9f9f9").pack(
            pady=5, anchor="w"
        )

        self.result_frame = tk.Frame(main_frame, bg="#f9f9f9", relief=tk.GROOVE, bd=2)
        self.result_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # 创建滚动条
        self.scrollbar = tk.Scrollbar(self.result_frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 创建公式列表框
        self.canvas = tk.Canvas(
            self.result_frame,
            yscrollcommand=self.scrollbar.set,
            bg="#ffffff",
            relief=tk.FLAT,
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.canvas.yview)

        # 内部框架
        self.inner_frame = tk.Frame(self.canvas, bg="#ffffff")
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.inner_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        # 添加滚动条绑定到鼠标滚轮
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    # 添加滚轮处理方法
    def _on_mousewheel(self, event):
        """处理鼠标滚轮事件"""
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def on_convert(self):
        """点击转换按钮后启动提取任务"""
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please input URL!")
            return

        # 清空日志框和公式框
        self.log_text.delete(1.0, tk.END)
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        # 后台线程处理公式提取
        thread = threading.Thread(target=self.convert_task, args=(url,))
        thread.start()

    def convert_task(self, url):
        """提取公式并渲染到窗口中"""
        try:
            self.update_log("Extracting...\n")
            hash_value = hash(url) & 0xFFFFFFFF
            save_file_name = f"./.cache/{hash_value}.html"
            download(url, save_file_name)
            formulas = extract_formulas(save_file_name)
            print(formulas)
            if not formulas or formulas[0].startswith("Error:"):
                self.update_log(
                    f"Extract error: {formulas[0] if formulas else 'Unknown Error.'}\n"
                )
            else:
                self.update_log("Extract successfully.\n")
                self.root.after(0, self.render_formulas, formulas)
        except Exception as e:
            self.update_log(f"Extract error: {e}\n")

    def update_log(self, message):
        """更新日志框内容"""
        self.root.after(0, self.log_text.insert, tk.END, message)
        self.root.after(0, self.log_text.yview, tk.END)

    def render_formulas(self, formulas):
        """在窗口中渲染公式"""
        for idx, formula in enumerate(formulas):
            # 显示公式编号，左对齐
            label = tk.Label(
                self.inner_frame, text=f"Formula {idx + 1}:", anchor="w", bg="#ffffff"
            )
            label.pack(fill=tk.X, padx=5, pady=5)

            # 使用 matplotlib 渲染公式
            fig = plt.figure(figsize=(5, 0.8))
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, f"${formula}$", fontsize=14, va="center", ha="center")
            ax.axis("off")  # 隐藏坐标轴

            # 将 matplotlib 图像嵌入到 tkinter 中
            canvas = FigureCanvasTkAgg(fig, self.inner_frame)
            widget = canvas.get_tk_widget()

            # 设置 widget 居中
            widget.pack(padx=5, pady=10, anchor="center")

            canvas.draw()

            # 为每个公式绑定点击事件
            widget.bind("<Button-1>", lambda e, f=formula: self.copy_to_clipboard(f))

    def copy_to_clipboard(self, formula):
        """将公式复制到剪贴板"""
        self.root.clipboard_clear()
        self.root.clipboard_append(formula)
        self.root.update()  # 刷新剪贴板内容
        messagebox.showinfo("Copy successfully!", f"The formula has been copied to the clipboard:\n{formula}")

    def run(self):
        self.root.mainloop()
