import requests

# 1. 定义官方源地址
url = "https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/config/ACL4SSR_Online_Full_MultiMode.ini"

# 2. 下载文件
print("正在下载官方配置...")
r = requests.get(url)
content = r.text

if r.status_code != 200:
    print("下载失败")
    exit(1)

# ---------------------------------------------------------------
# 3. 这里是【核心修改区】，你想改什么都在这里写
# ---------------------------------------------------------------

# 【示例1：简单的文字替换】
# 比如把规则里的 "Netflix" 组全部替换成 "奈飞视频"
content = content.replace("filter_name=Netflix", "filter_name=奈飞视频")

# 【示例2：插入自定义规则到前面】
# 在文件开头加入一段你的自定义规则
custom_rules = """
# ==================
# 这里的规则会优先匹配
# ==================
"""
# 这一行是把你的规则加到内容最前面 (或者你可以找[Rule]位置插进去，这里简单处理)
# 注意：ini文件结构比较严格，简单的追加建议用 Sub-Store 等工具，
# 如果只是改组名或简单替换，replace足够了。

# ---------------------------------------------------------------

# 4. 保存为新文件
filename = "ACL4SSR_Custom.ini"
with open(filename, "w", encoding="utf-8") as f:
    f.write(content)

print(f"成功更新并保存为 {filename}")
