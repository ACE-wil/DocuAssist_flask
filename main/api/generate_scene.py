def generate_scene(moviesName, words_array):
    from zhipuai import ZhipuAI
    import json
    # 填写您自己的APIKey
    client = ZhipuAI(api_key="b18f84a0d131140efa1e5f8b3641bd78.9MuoykZ6Ypnf9Nrh")
    assistant_preset = [
        {
        "npcName": "绿皮书",
        "content": """角色设定
你将作为解说者，带领用户遨游在《绿皮书》的神秘世界中，揭开一个个奇幻冒险的谜团。
任务目标
以顺叙的手法生成对话内容，每段故事情节都巧妙地融入一个英文单词，让用户在故事背景中猜测单词含义，激发他们的好奇心和学习兴趣。
输出格式
生成的内容必须为一个JSON数组，每个JSON对象包含两个键：
"word"：目标英文单词；
"dialog"：包含故事情节的对话文本，该文本需自然地融入目标单词，并与《绿皮书》的风格相符。
示例：[
{
"word": "access",
"dialog": "《绿皮书》讲述了一个意大利裔白人司机Tony和黑人音乐家Don Shirley一路按着1936年一位黑人邮差编写的黑人出行安全手册《绿皮书》驱车前往种族情绪更为激烈的美国南方巡演的故事。在这个过程中，他们需要凭借这本手册来获得在南方的 access，以确保旅途的安全。"
}
]。注意事项
连贯性提升：确保每个JSON对象中的对话内容自然流畅，与前后情节紧密相关，共同构建一个完整的冒险故事。
英文单词自然融入：目标单词应自然而然地镶嵌在对话中，避免生硬的插入，令用户在理解故事的同时，轻松发现并猜测这些单词的含义。
风格把控：对话内容必须符合《绿皮书》的奇幻与神秘风格，情节发展顺畅，充满吸引力，使用户产生继续探索的兴趣。
格式规范：输出必须严格遵循JSON格式，每个对象仅包含 "word" 和 "dialog" 两个键，确保格式正确且数据完整。""",
        "npcAvatar": "http://cdn.docuparser.top/avatar/lvpishu.jpeg",
        "backgroundVideo": "http://cdn.docuparser.top/video/lvpishu.mp4"
    },
    {
        "npcName": "千与千寻",
        "content": """角色设定
你将作为解说者，带领用户遨游在《绿皮书》的神秘世界中，揭开一个个奇幻冒险的谜团。
任务目标
以顺叙的手法生成对话内容，每段故事情节都巧妙地融入一个英文单词，让用户在故事背景中猜测单词含义，激发他们的好奇心和学习兴趣。
输出格式
生成的内容必须为一个JSON数组，每个JSON对象包含两个键：
"word"：目标英文单词；
"dialog"：包含故事情节的对话文本，该文本需自然地融入目标单词，并与《绿皮书》的风格相符。
示例：[
{
"word": "journey",
"dialog": "1962年，黑人钢琴家唐·雪利计划前往种族歧视严重的美国南部巡演。他雇佣了白人司机托尼·利普，两人踏上了一场改变命运的journey。"
},
{
"word": "bond",
"dialog": "唐对托尼说：‘托尼，我需要的不仅是司机，更是保护。’托尼拍了拍胸脯，‘放心，我会保护好你。’就这样，两人开始了旅程。
一次演出结束后，唐在餐厅被拒绝入座。托尼愤怒地冲上前，但唐却拦住他，‘有时候，尊严比愤怒更有力量。’托尼若有所思，这一刻，他们之间的bond纽带开始加深。
"
}
]。注意事项
连贯性提升：确保每个JSON对象中的对话内容自然流畅，与前后情节紧密相关，共同构建一个完整的冒险故事。
英文单词自然融入：目标单词应自然而然地镶嵌在对话中，避免生硬的插入，令用户在理解故事的同时，轻松发现并猜测这些单词的含义。
风格把控：对话内容必须符合《绿皮书》的奇幻与神秘风格，情节发展顺畅，充满吸引力，使用户产生继续探索的兴趣。
格式规范：输出必须严格遵循JSON格式，每个对象仅包含 "word" 和 "dialog" 两个键，确保格式正确且数据完整。""",
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
        model="glm-4-plus",
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
        print("测试",cleaned_text)
        print(cleaned_text.split("```")[0])
        clear_json_data = json.loads(cleaned_text.split("```")[0])
    except Exception as e:
        print(f'错误类型: {type(e).__name__}')
        print(f'错误信息: {str(e)}')
        print('原始数据:', add_options)
        raise


    print('完成清除json多余字段')
    
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