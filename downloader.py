from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os


def download_rendered_page_edge(url, output_file, driver_path):
    # 配置 Edge 浏览器
    options = webdriver.EdgeOptions()
    options.add_argument("--headless")  # 无界面模式
    options.add_argument("--disable-gpu")  # 禁用 GPU 加速（可选）

    # 初始化 EdgeDriver
    if driver_path:
        service = Service(driver_path)
        driver = webdriver.Edge(service=service, options=options)
    else:
        driver = webdriver.Edge(options=options)

    try:
        # 打开页面
        driver.get(url)

        # 使用 WebDriverWait 等待 KaTeX 渲染完成
        wait = WebDriverWait(driver, 15)  # 最多等待 15 秒

        # 检查页面加载完成
        wait.until(
            lambda driver: driver.execute_script("return document.readyState")
            == "complete"
        )

        # 等待 .katex 元素加载
        wait.until(
            lambda driver: driver.execute_script(
                "return document.querySelectorAll('.katex').length > 0"
            )
        )

        # 获取渲染后的 HTML
        rendered_html = driver.page_source

        # 保存到文件
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(rendered_html)
        print(f"渲染后的页面已保存到 {output_file}")
    finally:
        # 关闭 WebDriver
        driver.quit()


def download(url, output_file, driver_path=None):
    # 检测是否存在 .cache 文件夹
    if not os.path.exists(".cache"):
        os.makedirs(".cache")
    download_rendered_page_edge(url, output_file, driver_path)
