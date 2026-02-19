import requests
import re
import sys

# 1. 定义官方源地址
url = "https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/config/ACL4SSR_Online_Full_MultiMode.ini"

# 2. 下载文件 (增加超时与异常处理)
print("正在下载官方配置...")
try:
    # 设置 10 秒超时，避免网络问题导致脚本无限挂起
    r = requests.get(url, timeout=10)
    r.raise_for_status() # 如果状态码不是 200，主动抛出异常
    content = r.text
except requests.RequestException as e:
    print(f"❌ 下载失败，网络请求异常: {e}")
    sys.exit(1)

print("✅ 下载成功，开始修改配置...")

# ===============================================================
# 3. 定义你要添加的策略组
# ===============================================================

new_groups_def = """
; === 自定义新增策略组 Start ===
custom_proxy_group=自定义香港高级BGP负载均衡`load-balance`(香港 高级中继)`http://www.gstatic.com/generate_204`300,,50
custom_proxy_group=自定义香港IEPL负载均衡`load-balance`(香港 IEPL)`http://www.gstatic.com/generate_204`300,,50
custom_proxy_group=自定义日常工作`url-test`[]自定义香港IEPL负载均衡`[]自定义香港高级BGP负载均衡`[]♻️ 自动选择`http://www.gstatic.com/generate_204`300,,50
; === 自定义新增策略组 End ===
"""

# ===============================================================
# 4. 执行自动化修改逻辑
# ===============================================================

# 【修改操作 A】插入新策略组定义 (仅替换第一处标志位)
if ";设置分组标志位" in content:
    content = content.replace(";设置分组标志位", ";设置分组标志位\n" + new_groups_def, 1)
else:
    content = content.replace("[custom]", "[custom]\n" + new_groups_def)
print("✅ 已创建 3 个自定义策略组")


# 【修改操作 B】修改 "🚀 节点选择" 
# 替换 `select`[] 确保准确插入到第一个选项位置
content = content.replace(
    "custom_proxy_group=🚀 节点选择`select`[]", 
    "custom_proxy_group=🚀 节点选择`select`[]自定义日常工作`[]",
    1
)
print("✅ 已将 [自定义日常工作] 加入到节点选择首位")


# 【修改操作 C】重写 "💬 Ai平台"
new_ai_group = "custom_proxy_group=💬 Ai平台`select`(GPT|Gemini|Ai)"
content = re.sub(
    r"^custom_proxy_group=💬 Ai平台.*", 
    new_ai_group, 
    content, 
    flags=re.MULTILINE
)
print("✅ 已修改 [💬 Ai平台] 为仅筛选 GPT/Gemini/Ai")


# 【修改操作 D】添加“临时测试”分组 (优化插入位置)
new_test_group = "custom_proxy_group=临时测试`select`.*\n"
last_marker = ";设置分组标志位"
last_idx = content.rfind(last_marker) # 查找文件中最后一个标志位的位置

if last_idx != -1 and last_idx != content.find(last_marker):
    # 找到了文件末尾的那个闭合标志位，将新分组插在它正上方
    content = content[:last_idx] + new_test_group + content[last_idx:]
    print("✅ 已在分组列表末尾安全添加 [临时测试] 分组")
else:
    # 备用方案：如果没找到第二个标志位，则插在 enable_rule_generator 参数前
    content = content.replace("enable_rule_generator=true", new_test_group + "enable_rule_generator=true")
    print("✅ 已通过备用方案添加 [临时测试] 分组")


# ===============================================================
# 5. 保存为新文件
# ===============================================================
filename = "ACL4SSR_Custom.ini"
with open(filename, "w", encoding="utf-8") as f:
    f.write(content)

print(f"🎉 成功更新并保存为 {filename}")
