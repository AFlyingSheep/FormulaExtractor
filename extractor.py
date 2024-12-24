from bs4 import BeautifulSoup


def extract_tex_annotations(html_file):
    try:
        # 读取 HTML 文件
        with open(html_file, "r", encoding="utf-8") as file:
            html_content = file.read()

        # 解析 HTML
        soup = BeautifulSoup(html_content, "html.parser")

        # 查找所有 <annotation> 标签，属性为 encoding="application/x-tex"
        annotations = soup.find_all("annotation", encoding="application/x-tex")

        # 提取标签内容
        tex_contents = [annotation.text for annotation in annotations]
        print("Extract successfully.")
        return tex_contents
    except Exception as e:
        print(f"Error in extracting: {e}")
        return []


def extract_formulas(html_file):
    return extract_tex_annotations(html_file)
