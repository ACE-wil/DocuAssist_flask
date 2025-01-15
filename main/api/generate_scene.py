def generate_scene(moviesName, words_array):
    from zhipuai import ZhipuAI
    import json
    # 填写您自己的APIKey
    client = ZhipuAI(api_key="b18f84a0d131140efa1e5f8b3641bd78.9MuoykZ6Ypnf9Nrh")

    assistant_preset = [
        {
            "npcName": "绿皮书",
            "content": """你是月光仙子，你现在需要带领用户遨游在绿皮书世界，接受用户单词的同时高效地教会用户单词。
            拿《绿皮书》电影来说，而不是一直切换电影，并以json形式储存,示例:
            [{"word":"access","dialog":"在《千与千寻》中，千寻意外地进入了一个神秘的世界，她需要找到通往这个世界的access以返回现实。"},
            {"word":"accessory","dialog":"电影中的无脸男可以被视为千寻冒险中的一个accessory，因为他在某些情况下帮助了她。"}]；
            注意：对话主要为中文，夹杂唯一的一个英文单词，不要有中文提示，不理解可以看我示例里面的dialog""",
            "npcAvatar": "http://cdn.docuparser.top/avatar/lvpishu.jpeg",
            "backgroundVideo": "http://cdn.docuparser.top/video/lvpishu.mp4"
        },
        {
            "npcName": "千与千寻",
            "content": """你是月光仙子，你现在需要带领用户遨游在宫崎骏笔下的千与千寻的世界，接受用户单词的同时高效地教会用户单词。
            可以拿具体某一部电影来说，而不是一直切换电影，并以json形式储存,示例:
            [{"word":"access","dialog":"在《千与千寻》中，千寻意外地进入了一个神秘的世界，她需要找到通往这个世界的access以返回现实。"},
            {"word":"accessory","dialog":"电影中的无脸男可以被视为千寻冒险中的一个accessory，因为他在某些情况下帮助了她。"}]；
            注意：对话主要为中文，夹杂唯一的一个英文单词，不要有中文提示，不理解可以看我示例里面的dialog""",
            "npcAvatar": "http://cdn.docuparser.top/avatar/gongqijun.jpg",
            "backgroundVideo": "http://cdn.docuparser.top/video/qianyuqianxun.mp4"
        }
    ]

    # 使用列表解析查找npcName为moviesName的内容
    npc_content = next((item["content"] for item in assistant_preset if item["npcName"] == moviesName), None)

    messages_preset = []
    if npc_content:
        messages_preset.append({
            "role": "assistant",
            "content": str(npc_content)
        })

    messages_preset.append({
        "role": "user",
        "content": str(words_array)
    })

    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=messages_preset
    )
    print('开始生成带单词句子')
    word_sentence = response.choices[0].message.content
    # print(word_sentence)
    print('带单词句子生成完成')
    messages_preset.append({
    "role": "assistant",
    "content": f"{word_sentence}"
})
    messages_preset.append({
        "role": "user",
        "content": "基于这个json进行将每个对话丰富一下情感和故事性"
    })
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=messages_preset
    )
    print('开始生成更长的句子')
    word_long_sentence = response.choices[0].message.content
    # print(word_long_sentence)
    print('更长句子生成完成')

    messages_preset.append({
        "role": "assistant",
        "content": f"{word_long_sentence}"
    })
    messages_preset.append({
        "role": "user",
        "content": """
        基于这个json进行给每个小json加选项，2个混淆翻译和1个正确翻译，正确翻译要符合语境，而不是脱离语境的翻译，options格式如下：options: [
            { text: "入口", isCorrect: True },
            { text: "通道", isCorrect: False  },
            { text: "接近", isCorrect: False  },
            ],
            """
    })
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=messages_preset
    )

    print('开始给每个内容加选项')
    add_options = response.choices[0].message.content
    # print(add_options)
    print('给每个内容加选项完成')

    print('开始清除json多余字段')
    try:
        if not add_options or add_options.isspace():
            raise ValueError("add_options 为空或只包含空白字符")
        
        # 更严格的 JSON 清理
        cleaned_text = add_options
        
        # 移除 markdown 代码块标记
        if "```json" in cleaned_text:
            cleaned_text = cleaned_text.split("```json")[1]
        elif "```" in cleaned_text:
            cleaned_text = cleaned_text.split("```")[0]
        cleaned_text = cleaned_text.strip()
        
        # 修复 JSON 格式问题
        import re
        
        # 修复属性名的引号问题
        cleaned_text = re.sub(r'(\s*)(\w+)(:)', r'\1"\2"\3', cleaned_text)
        
        # 修复布尔值和其他常见问题
        replacements = {
            "'": "\"",          # 单引号替换为双引号
            "True": "true",     # Python布尔值替换为JSON布尔值
            "False": "false",
            "None": "null",
            ",]": "]",         # 移除数组最后多余的逗号
            ",}": "}"          # 移除对象最后多余的逗号
        }
        
        for old, new in replacements.items():
            cleaned_text = cleaned_text.replace(old, new)
        
        try:
            clear_json_data = json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            print(f"JSON 解析错误位置: 行 {e.lineno}, 列 {e.colno}")
            print(f"错误信息: {e.msg}")
            print("问题字符附近的内容:")
            lines = cleaned_text.split('\n')
            if e.lineno <= len(lines):
                problem_line = lines[e.lineno-1]
                print(f"第 {e.lineno} 行: {problem_line}")
                print(" " * (e.colno-1) + "^")
                print("\n完整的清理后文本:")
                print(cleaned_text)
            raise
        
        if not isinstance(clear_json_data, list):
            raise ValueError("解析后的数据不是列表格式")
            
        print('成功清除json多余字段')
        
    except Exception as e:
        print(f'错误类型: {type(e).__name__}')
        print(f'错误信息: {str(e)}')
        print('原始数据:', add_options)
        raise
    
    print('开始选项随机操作')
    import random

    # 为每个条目的options列表随机打乱顺序
    for item in clear_json_data:
        random.shuffle(item["options"])

    # 打印结果以验证
    # for item in clear_json_data:
    #     print(f"Word: {item['word']}")
    #     for option in item['options']:
    #         print(f"Translation: {option['text']}, Correct: {option['isCorrect']}")
    #     print("-" * 50)

    random_json_data = clear_json_data
    print('完成选项随机操作')
    # print(random_json_data)
    print('开始添加下个场景字段')
    # 为每个条目的options列表添加nextScene
    i = 1
    for item in random_json_data:
        for option in item['options']:
            if option['isCorrect']:
                option['nextScene'] = i
                i += 1
            else:
                option['nextScene'] = -1

    # 打印结果以验证
    for item in random_json_data:
        print(f"Word: {item['word']}")
        for option in item['options']:
            print(f"Translation: {option['text']}, Correct: {option['isCorrect']}, NextScene: {option.get('nextScene', 'N/A')}")
        print("-" * 50)
    next_scene_json_data = random_json_data
    print('在json中添加npcName字段')

    # 为每个条目添加npcName字段
    for item in next_scene_json_data:
        item['npcName'] = moviesName  # 添加npcName字段

    # 打印结果以验证
    for item in next_scene_json_data:
        print(f"Word: {item['word']}, NPC Name: {item['npcName']}")
        for option in item['options']:
            print(f"Translation: {option['text']}, Correct: {option['isCorrect']}, NextScene: {option.get('nextScene', 'N/A')}")
        print("-" * 50)
    npc_name_json_data = next_scene_json_data
    print('在json中添加npcName字段完成')

    print('在json中添加npcAvatar字段')
    # 为每个条目添加npcAvatar字段
    for item in npc_name_json_data:
        item['npcAvatar'] = next((item["npcAvatar"] for item in assistant_preset if item["npcName"] == moviesName), None)  # 添加npcAvatar字段

    # 打印结果以验证
    for item in npc_name_json_data:
        print(f"Word: {item['word']}, NPC Name: {item['npcName']}, NPC Avatar: {item['npcAvatar']}")
        for option in item['options']:
            print(f"Translation: {option['text']}, Correct: {option['isCorrect']}, NextScene: {option.get('nextScene', 'N/A')}")
        print("-" * 50)
    npc_avatar_json_data = npc_name_json_data
    print('在json中添加npcName和npcAvatar字段完成')

    print('在json中添加backgroundVideo字段')
    # 为每个条目添加backgroundVideo字段
    for item in npc_avatar_json_data:
        item['backgroundVideo'] = next((item["backgroundVideo"] for item in assistant_preset if item["npcName"] == moviesName), None)  # 添加backgroundVideo字段

    # 打印结果以验证
    for item in npc_avatar_json_data:
        print(f"Word: {item['word']}, NPC Name: {item['npcName']}, NPC Avatar: {item['npcAvatar']}, Background Video: {item['backgroundVideo']}")
        for option in item['options']:
            print(f"Translation: {option['text']}, Correct: {option['isCorrect']}, NextScene: {option.get('nextScene', 'N/A')}")
        print("-" * 50)
    background_video_json_data = npc_avatar_json_data
    print('在json中添加npcName、npcAvatar和backgroundVideo字段完成')

    print(background_video_json_data)

    background_video_json_data.append({
        "word": "none",
        "dialog": "恭喜你完成了游戏的所有关卡，点击重玩游戏，重新开始游戏",
        "options": [
            { "text": "重玩游戏", "isCorrect": "true", "nextScene": 0 },
        ],
        "npcName": moviesName,
        "npcAvatar": next((item["npcAvatar"] for item in assistant_preset if item["npcName"] == moviesName), None),
        "backgroundVideo": next((item["backgroundVideo"] for item in assistant_preset if item["npcName"] == moviesName), None),
    })

    # 将options中的True和False改为小写字符串
    for item in background_video_json_data:
        for option in item['options']:
            option['isCorrect'] = 'true' if option['isCorrect'] else 'false'

    # 打印结果以验证
    for item in background_video_json_data:
        print(f"Word: {item['word']}, NPC Name: {item['npcName']}, NPC Avatar: {item['npcAvatar']}, Background Video: {item['backgroundVideo']}")
        for option in item['options']:
            print(f"Translation: {option['text']}, Correct: {option['isCorrect']}, NextScene: {option.get('nextScene', 'N/A')}")
        print("-" * 50)
    print('添加下个场景字段完成')
    return background_video_json_data 