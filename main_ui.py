import tkinter as tk
from tkinter import ttk
import sys
from utils import autoclick
from utils import logging


#sys.stdout = logging.Logger("log.txt")

def validate_int(input):
    """验证函数，确保输入是整数"""
    if input.isdigit() or input == "":
        return True
    else:
        return False


def on_invalid(*args):
    """当输入无效时的回调函数，发出提示声"""
    root.bell()


def update(*args):
    """根据选择是否显示技能施放顺序的输入框、挂机时长标签和一次使用的体力药输入框"""
    selected_option = option_var.get()

    # 移除所有可变组件
    jnsf_label.grid_remove()
    jnsf_entry.grid_remove()
    tly_count_label.grid_remove()
    tly_count_entry.grid_remove()

    # 重置当前行索引
    global current_row
    current_row = 4  # 固定起始行为4，前面有副本、刷取次数、是否使用体力药三个固定行

    # 控制一次使用的体力药输入框的可见性
    if tly_var.get():
        tly_count_label.grid(row=current_row, column=0, pady=5, sticky=tk.E)
        tly_count_entry.grid(row=current_row, column=1, pady=5, padx=20, sticky=tk.W)
        current_row += 1  # 更新当前行索引

    # 根据选择更新输入框可见性
    if selected_option == "内圈":
        jnsf_label.grid(row=current_row, column=0, pady=5, sticky=tk.E)
        jnsf_entry.grid(row=current_row, column=1, pady=5, padx=20, sticky=tk.W)
        current_row += 1  # 更新当前行索引

    # 调整提交按钮的位置
    submit_button.grid(row=current_row, column=1, pady=10)


def load_lastdata():
    """加载上次数据并填充到界面中"""
    saver = logging.LastDataSaver(filename="lastdata.json")

    def update_ui(data):
        option_var.set(data.get("选择的选项", "请选择副本"))
        runs_entry.delete(0, 'end')
        runs_entry.insert(0, str(data.get("刷取次数", 8)))
        tly_var.set(data.get("是否使用体力药", False))
        if tly_var.get():
            tly_count_entry.delete(0, 'end')
            tly_count_entry.insert(0, str(data.get("每次使用的体力药数量", "")))
        if option_var.get() == "内圈":
            jnsf_entry.delete(0, 'end')
            jnsf_entry.insert(0, data.get("人物技能施放顺序", ""))
        update()  # 调用 update 函数以正确显示或隐藏组件

    # 切换副本时的加载逻辑
    def on_option_change(*args):
        selected = option_var.get()
        data = saver.load(selected)
        if data:
            update_ui(data)
        else:
            update()

    # 启动时读取“上次选择的副本”
    last_selected = saver.get_last_selected()
    option_var.set(last_selected)  # 设置下拉框为上次选择的副本

    # 加载该副本的数据
    data = saver.load(last_selected)
    if data:
        update_ui(data)
    else:
        update()  # 没有数据时也调用 update 确保布局正确

    # 监听副本变化
    option_var.trace_add('write', on_option_change)


def get_data():
    # 获取用户选择和输入的数据
    selected_fb = option_var.get()
    jn_input = jnsf_entry.get() if selected_fb == "内圈" else ""
    try:
        count = int(runs_entry.get())
    except ValueError:
        print("请输入有效的整数")
        return

    use_tly = tly_var.get()
    tly_count = None
    if use_tly:
        try:
            tly_count = int(tly_count_entry.get())
        except ValueError:
            print("请输入有效的体力药数量")
            return

    data_to_log = {
        "选择的选项": selected_fb,
        "刷取次数": count,
        "是否使用体力药": use_tly,
        "每次使用的体力药数量": tly_count if use_tly else "",
        "人物技能施放顺序": jn_input if selected_fb == "内圈" else ""
    }

    # 保存数据，key 为副本名称，并更新 _last_selected
    saver = logging.LastDataSaver(filename="lastdata.json")
    saver.save(selected_fb, data_to_log)  # 这里会自动更新 _last_selected

    print(f"选择的选项: {selected_fb}\n刷取次数: {count}")
    if jn_input:
        print(f"人物技能施放顺序：{jn_input}")
    print(f"是否使用体力药: {'是' if use_tly else '否'}")
    if use_tly and tly_count is not None:
        print(f"每次使用的体力药数量: {tly_count}")
    print()
    root.destroy()
    if selected_fb == "材料，遗器，周本":
        autoclick.richang(count, tly_count)
    else:
        autoclick.neiqvan(count, jn_input, tly_count)
    sys.exit(0)


# 生成界面
root = tk.Tk()
root.title("告诉迷迷你想要什么")
root.geometry("800x400")  # 宽*高

default_font = ("TkDefaultFont", 12)  # 设置字体

# 使用 grid 布局管理器
for i in range(3):  # 设置三列的最小宽度
    root.grid_columnconfigure(i, minsize=200)

# 初始化当前行索引
current_row = 0

# row(行),column(列),pady(x轴方向间距),sticky(对齐方式)tk.E(右对齐)
tk.Label(root, text="副本：", font=default_font).grid(row=current_row, column=0, pady=5, sticky=tk.E)
option_var = tk.StringVar(value="请选择副本")
# values：选项， state：设置框的状态，'readonly'则只能选择下拉列表的值，width：宽度
fb_menu = ttk.Combobox(root, textvariable=option_var, values=["材料，遗器，周本", "内圈"],
                       state='readonly', font=default_font, width=20)
fb_menu.grid(row=current_row, column=1, pady=5, sticky=tk.W)
current_row += 1  # 更新当前行索引

# 创建一个整数验证器, 注册验证函数和错误处理函数，与Tkinter的事件处理系统“挂钩”
# ‘%P’：输入框当前的内容
vcmd = (root.register(validate_int), '%P')
invalid_cmd = root.register(on_invalid)

# 添加新输入框 - 刷取次数
tk.Label(root, text="请输入要刷取的次数或体力使用次数：", font=default_font).grid(row=current_row, column=0, pady=5, sticky=tk.E)
runs_entry = ttk.Entry(root, font=default_font, validate='key', validatecommand=vcmd, invalidcommand=invalid_cmd)
runs_entry.grid(row=current_row, column=1, pady=5, padx=20, sticky=tk.W)
current_row += 1  # 更新当前行索引

# 新增部分：是否使用体力药的选择
tk.Label(root, text="是否使用体力药：", font=default_font).grid(row=current_row, column=0, pady=5, sticky=tk.E)
tly_var = tk.BooleanVar(value=False)
yes_radio = ttk.Radiobutton(root, text="是", variable=tly_var, value=True, command=lambda: update())
no_radio = ttk.Radiobutton(root, text="否", variable=tly_var, value=False, command=lambda: update())
yes_radio.grid(row=current_row, column=1, pady=5, sticky=tk.W)
no_radio.grid(row=current_row, column=2, pady=5, sticky=tk.W)
current_row += 1  # 更新当前行索引

# 初始化人物技能释放顺序号输入框及其标签为不可见
jnsf_label = tk.Label(root, text="释放技能的人物顺序号(例：123)：", font=default_font)
jnsf_entry = ttk.Entry(root, font=default_font, validate='key', validatecommand=vcmd, invalidcommand=invalid_cmd)
jnsf_label.grid_remove()  # 初始状态下隐藏标签
jnsf_entry.grid_remove()  # 初始状态下隐藏输入框

# 初始化一次使用的体力药输入框
tly_count_label = tk.Label(root, text="每次使用的体力药量：", font=default_font)
tly_count_entry = ttk.Entry(root, font=default_font, validate='key', validatecommand=vcmd, invalidcommand=invalid_cmd)
tly_count_label.grid_remove()  # 初始状态下隐藏标签
tly_count_entry.grid_remove()  # 初始状态下隐藏输入框

# 监听副本选择变化并更新输入框可见性和标签文本
option_var.trace_add('write', update)

# 监听是否使用体力药的变化并更新输入框可见性和标签文本
tly_var.trace_add('write', lambda *args: update())

# 生成”提交“按钮，点击时执行get_data函数
submit_button = tk.Button(root, text="提交", command=get_data, font=default_font, width=10)

# 最后放置提交按钮
submit_button.grid(row=current_row, column=1, pady=10)

# 自动加载上次数据
load_lastdata()

try:
    root.mainloop()
except Exception as e:
    print(f"程序异常退出: {e}")
finally:
    sys.stdout.close()  # 确保在任何情况下都能关闭日志文件