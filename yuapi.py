import requests
import json
import re
import os
import uuid
from urllib import parse

# cookie配置
yu_cookies = {
    '_yuque_session': '',

}

# 携带cookie的get
def get_with_cookie(url, cookies):

    try:
        response = requests.get(url, cookies=cookies)
        if response.status_code == 200:
            return response.text
        else:
            return f"请求失败，状态码：{response.status_code}"
    except Exception as e:
        return f"请求发生异常: {str(e)}"

# 获取所有知识库列表
def get_all_book():
    global yu_cookies
    url = "https://www.yuque.com/api/mine/book_stacks"
    return get_with_cookie(url, yu_cookies)

# 获取知识库下的文档列表
def get_book_docs(book_id):
    global yu_cookies
    url = f"https://www.yuque.com/api/docs?book_id={book_id}"
    return get_with_cookie(url, yu_cookies)

# 获取文档的html
def get_doc_html(book_id, doc_slug):
    global yu_cookies
    url = f"https://www.yuque.com/api/docs/{doc_slug}?include_contributors=false&include_like=false&include_hits=false&merge_dynamic_data=false&book_id={book_id}"
    return get_with_cookie(url, yu_cookies)

# 获取文档的markdown
def get_doc_md(book_id, doc_slug):
    global yu_cookies
    url = f"https://www.yuque.com/api/docs/{doc_slug}?book_id={book_id}&mode=markdown"
    init_data = json.loads(get_with_cookie(url, yu_cookies))
    md_text = init_data['data']['sourcecode']
    # 匹配 <a name="*"></a>
    pattern = r'<a name="([^"]*)"></a>'
    # 使用 re.sub() 函数来删除匹配项
    md_text = re.sub(pattern, '', md_text)
    md_text = re.sub(r'<br\s*/?>', '\n', md_text)

    # 把LaTeX的链接图片转成代码公式
    pattern = r'!\[(.*?)\]\((.*__latex.*?)\)'
    matches = re.findall(pattern, md_text)

    # 遍历匹配项
    for match in matches:
        alt_text, image_url = match

        # 提取code参数的值
        code_param = parse.parse_qs(
            parse.urlparse(image_url).fragment)['code'][0]

        # 构建替换文本
        if "align" in code_param:
            replacement = f"$$ {code_param} $$"
        else:
            replacement = f"$ {code_param} $"
        # 替换Markdown文本中的匹配项
        md_text = md_text.replace(f"![{alt_text}]({image_url})", replacement)
    return md_text
