import os
from openai import OpenAI

def get_qwen_response(messages,models):
    """
    调用千问API获取回复
    
    Args:
        messages: 消息历史列表，包含role和content
        
    Returns:
        千问API的回复内容
    """
    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"), 
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    
    completion = client.chat.completions.create(
        # model="qwen2.5-coder-32b-instruct",
        model=models,
        messages=messages
    )
    
    return completion.choices[0].message.content