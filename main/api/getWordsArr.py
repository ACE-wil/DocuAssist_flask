

def get_words_arr(file_url):
    import requests
    from openai import OpenAI
    from dotenv import load_dotenv
    from pathlib import Path
    import os
    import json
    load_dotenv()

    client = OpenAI(
        api_key='sk-LjTqTa7tIVwLQInDmRILGchIP9X1vXG3mARWqFMbKxNRKgVn',  # 请确保在环境变量中设置了 API_KEY
        base_url="https://api.moonshot.cn/v1",
    )

    # 上传文件并获取内容
    file_object = client.files.create(file=Path(file_url), purpose="file-extract")
    file_content = client.files.content(file_id=file_object.id).text

    # 把文件内容通过系统提示词 system prompt 放进请求中
    messages = [
        {
            "role": "system",
            "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。"
        },
        {
            "role": "system",
            "content": file_content
        },
{"role": "user", "content": """提取文件中的前60个单词（只要英文，无需音标），返回4个单词数组，每个数组包含15个单词,返回json给我，格式如下：array1:1. afraid 2. able 3. about 4. above 5. absence 6. absolute 7. abstract 8. absolute 9. absolute 10. absolute 11. absolute 12. absolute 13. absolute 14. absolute 15. absolute。 不要回复多余内容，我要对单词进行切分"""},
    ]

    # 然后调用 chat-completion, 获取 Kimi 的回答
    completion = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=messages,
        temperature=0.3,
    )

    word_Array = completion.choices[0].message.content
    print(word_Array)

    # 解析返回的 JSON 数据
    word_Array_json = json.loads(word_Array)
    word_all = [word_Array_json[f'array{i+1}'] for i in range(len(word_Array_json))]
    print(word_all)

    return word_all