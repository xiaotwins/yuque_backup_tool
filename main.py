from yuapi import *
from datetime import datetime

# 获取当前时间的时间字符串
current_time = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')

# 备份路径
backup_path = f"./语雀备份/{current_time}"

# 当前时间的备份路径
if not os.path.exists(backup_path):
    os.makedirs(backup_path)
    print(f"创建备份目录:  {os.path.abspath(backup_path)}")

# 获取所有知识库列表
all_book_json = get_all_book()
all_book_data = json.loads(all_book_json)['data'][0]['books']
all_book_arr = []


# 简化知识库列表
for i in all_book_data:
    book_dic = {}
    book_dic['id'] = i['id']
    book_dic['slug'] = i['slug']
    book_dic['name'] = i['name']
    book_dic['items_count'] = i['items_count']
    book_path = f"{backup_path}/{book_dic['name']}"
    # 知识库路径
    if not os.path.exists(book_path):
        os.makedirs(book_path)
        print(f"创建知识库【{book_dic['name']}】目录:  {book_path}")
    book_dic['book_path'] = book_path
    all_book_arr += [book_dic]

# 保存知识库json
all_book_arr_json_data = json.dumps(all_book_arr, ensure_ascii=False)
books_json_path = f"{backup_path}/books.json"
with open(books_json_path, 'w', encoding='utf-8') as json_file:
    json_file.write(all_book_arr_json_data)

all_docs_arr=[]
# 遍历所有知识库
for book in all_book_arr:
    # 获取知识库下所有文档
    docs_json = get_book_docs(book['id'])
    docs_data = json.loads(docs_json)['data']
    docs_arr = []
    for k in docs_data:
        doc_dic = {}
        doc_dic['book_id'] = k['book_id']
        doc_dic['slug'] = k['slug']
        doc_dic['title'] = k['title'].replace("*", "_").replace("|", "_").replace("/", "_")
        doc_path = f"{book['book_path']}/{doc_dic['title']}".replace("*", "_").replace("|", "_")
        doc_dic['doc_path'] = doc_path

        # 文档路径
        if not os.path.exists(doc_path):
            os.makedirs(doc_path)
            print(f"创建文档【{doc_dic['title']}】目录:  {doc_path}")
        docs_arr += [doc_dic]
    # 保存知识库下的文档json
    docs_arr_json_data = json.dumps(docs_arr, ensure_ascii=False)
    docs_json_path = f"{book['book_path']}/docs.json"
    with open(docs_json_path, 'w', encoding='utf-8') as json_file:
        json_file.write(docs_arr_json_data)
    all_docs_arr+=[docs_arr]

#遍历所有知识库下的所有文档
for docs in all_docs_arr:
    for doc in docs:
        
        print(f"正在备份文档【{doc['title']}】")
        md_text=get_doc_md(int(doc['book_id']), doc['slug'])
        # print(md_text)
        # 定义正则表达式匹配Markdown中的图片链接
        image_link_pattern = r'!\[(.*?)\]\((?:(?!__latex).)*\)'
        # 使用正则表达式查找所有图片链接
        matches = re.finditer(image_link_pattern, md_text)

        # 定义本地目录路径-图片
        local_directory = f"{doc['doc_path']}/resources/img"

        # 如果本地目录不存在，创建它
        if not os.path.exists(local_directory):
            os.makedirs(local_directory)

        # 遍历匹配的图片链接
        for match in matches:
            full_match = match.group(0)
            alt_text = match.group(1)

            # 提取图片链接
            image_url = re.search(r'\!\[.*\]\((.*?)\)', full_match).group(1)
            if "cdn.nlark.com" not in image_url:
                continue
            # 生成随机UUID
            random_uuid = str(uuid.uuid4())
            image_filename = random_uuid

            # 提取文件名的后缀
            file_extension = os.path.splitext(image_url.split("#")[0])[1]
            if "?" in file_extension:
                file_extension=file_extension.split('?')[0]
            local_image_path = os.path.join(local_directory, image_filename+file_extension).replace("\\", "/")
            md_image_path = os.path.join("./resources/img", image_filename+file_extension).replace("\\", "/")
            # 下载图片到本地
            response = requests.get(image_url)
            if response.status_code == 200:
                with open(local_image_path, 'wb') as image_file:
                    image_file.write(response.content)

                # 替换Markdown中的图片链接为本地路径
                md_text = md_text.replace(full_match, f'![{alt_text}]({md_image_path})')

        # 将更新后的Markdown内容写回文件
        with open(f"{doc['doc_path']}/{doc['title']}.md", 'w', encoding='utf-8') as file:
            file.write(md_text)
