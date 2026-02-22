import requests
import re
import sys

# 1. 定义官方源地址
url = "https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/config/ACL4SSR_Online_Full_MultiMode.ini"

# 2. 下载文件
print("正在下载官方配置...")
try:
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    content = r.text
except requests.RequestException as e:
    print(f"❌ 下载失败，网络请求异常: {e}")
    sys.exit(1)

print("✅ 下载成功，开始修改配置...")

# ===============================================================
# 3. 定义你要添加的策略组（行内 health-check 将以反引号字段形式追加）
#    health-check 行内格式：`health-check`<url>`<interval>`<tolerance>
#    例如：`health-check`https://www.gstatic.com/generate_204`60`2
# ===============================================================
new_groups_def = """
; === 自定义新增策略组 Start ===
custom_proxy_group=自定义香港高级BGP负载均衡`load-balance`(香港 高级中继)`http://www.gstatic.com/generate_204`300,,50`health-check`https://www.gstatic.com/generate_204`60`2
custom_proxy_group=自定义香港IEPL负载均衡`load-balance`(香港 IEPL)`http://www.gstatic.com/generate_204`300,,50`health-check`https://www.gstatic.com/generate_204`60`2
custom_proxy_group=自定义日常工作`fallback`[]自定义香港IEPL负载均衡`[]自定义香港高级BGP负载均衡`[]♻️ 自动选择`http://www.gstatic.com/generate_204`300,,50
; === 自定义新增策略组 End ===
"""

# ===============================================================
# 4. 执行自动化修改逻辑（插入新策略组定义）
# ===============================================================
# 【修改操作 A】插入新策略组定义
if ";设置分组标志位" in content:
    content = content.replace(";设置分组标志位", ";设置分组标志位\n" + new_groups_def, 1)
else:
    content = content.replace("[custom]", "[custom]\n" + new_groups_def)
print("✅ 已创建 3 个自定义策略组（其中两个已包含行内 health-check 字段）")

# 【修改操作 B】修改 "🚀 节点选择" 
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

# ===============================================================
# 5. 确保 ♻️ 自动选择 行内追加 health-check（若尚未存在）
#    使用与上面相同的行内字段格式：`health-check`https://www.gstatic.com/generate_204`60`2
# ===============================================================
auto_pattern = r"(^custom_proxy_group=♻️ 自动选择[^\n]*)"
m_auto = re.search(auto_pattern, content, flags=re.MULTILINE)
if m_auto:
    auto_line = m_auto.group(1)
    if "health-check" in auto_line:
        print("ℹ️ [♻️ 自动选择] 已包含 health-check，跳过追加。")
    else:
        new_auto_line = auto_line + "`health-check`https://www.gstatic.com/generate_204`60`2"
        content = content.replace(auto_line, new_auto_line, 1)
        print("✅ 已在 [♻️ 自动选择] 行追加行内 health-check 字段。")
else:
    print("⚠️ 未找到 [♻️ 自动选择] 行，无法追加行内 health-check（请确认原始文件结构）。")

# ===============================================================
# 6. 动态提取所有分组，并生成“临时测试” （保持原逻辑）
# ===============================================================
# 1. 使用正则抓取当前 content 中所有的策略组名称
all_group_names = re.findall(r"^custom_proxy_group=([^`\n]+)`", content, flags=re.MULTILINE)

# 2. 去重（保持原有的顺序）
unique_groups = []
seen = set()
for name in all_group_names:
    if name not in seen:
        seen.add(name)
        unique_groups.append(name)

# 3. 将所有分组名称拼接成 subconverter 支持的格式: `[]分组1`[]分组2...
groups_str = "".join([f"`[]{g}" for g in unique_groups])

# 4. 组装“临时测试” (顺序：REJECT -> DIRECT -> 所有分组 -> .*所有单节点)
new_test_group = f"custom_proxy_group=临时测试`select`[]REJECT`[]DIRECT{groups_str}`.*\n"

# 5. 插入到文件末尾的安全位置
last_marker = ";设置分组标志位"
last_idx = content.rfind(last_marker)

if last_idx != -1 and last_idx != content.find(last_marker):
    content = content[:last_idx] + new_test_group + content[last_idx:]
    print("✅ 已动态抓取所有分组，并在末尾添加 [临时测试] 分组")
else:
    content = content.replace("enable_rule_generator=true", new_test_group + "enable_rule_generator=true")
    print("✅ 已通过备用方案添加 [临时测试] 分组")

# ===============================================================
# 7. 保存为新文件
# ===============================================================
filename = "ACL4SSR_Custom.ini"
try:
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"🎉 成功更新并保存为 {filename}")
except OSError as e:
    print(f"❌ 保存文件失败: {e}")
    sys.exit(1)
