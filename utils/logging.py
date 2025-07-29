# utils/logging.py
import os
import sys
import json
import datetime

class FileHandler:
    def __init__(self, filename, mode='w', encoding='utf-8'):
        self.filename = filename
        self.mode = mode
        self.encoding = encoding
        self.file = None

    def open(self):
        """打开文件"""
        if self.file is None or self.file.closed:
            self.file = open(self.filename, self.mode, encoding=self.encoding)

    def write(self, message):
        """写入内容"""
        if self.file and not self.file.closed:
            self.file.write(message)

    def flush(self):
        """刷新缓冲区"""
        if self.file and not self.file.closed:
            self.file.flush()

    def close(self):
        """关闭文件"""
        if self.file and not self.file.closed:
            self.file.close()
            self.file = None

    @property
    def _encoding(self):
        return self.encoding


class Logger(FileHandler):
    def __init__(self, filename="log.txt"):
        super().__init__(filename=filename, mode='w', encoding='utf-8')  # 使用追加模式
        self.terminal = sys.stdout
        self.open()
        self.write(f"\n=== 记录时间：{datetime.datetime.now()} ===\n")

    def write(self, message):
        """同时写入终端和日志文件"""
        self.terminal.write(message)
        super().write(message)
        self.flush()  # 每次写入后都刷新缓冲区

    def flush(self):
        """刷新终端和文件"""
        self.terminal.flush()
        super().flush()

    def close(self):
        """关闭文件"""
        super().close()


class LastDataSaver(FileHandler):
    def __init__(self, filename="lastdata.json"):
        # 1. 如果文件不存在，创建一个空的 JSON 文件
        if not os.path.exists(filename):
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=4)
            print(f"已创建新文件: {filename}")

        # 2. 使用 'r+' 模式初始化父类（可读可写，不覆盖原有内容）
        super().__init__(filename=filename, mode='r+', encoding='utf-8')
        self.open()  # 打开文件
        self._ensure_file_has_content()  # 确保内容有效

    def _ensure_file_has_content(self):
        """确保文件不是空的，避免 JSON 解析错误"""
        self.file.seek(0)
        content = self.file.read()
        if not content.strip():
            # 文件为空或只有空白字符
            self.file.seek(0)
            self.file.truncate()  # 清空
            json.dump({}, self.file, ensure_ascii=False, indent=4)
            self.file.flush()
            print("文件为空，已初始化为 {}")

    def _load_all(self):
        """从 JSON 文件中读取所有数据"""
        self.file.seek(0)
        content = self.file.read()
        if not content.strip():
            return {}  # 空内容返回空字典

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"JSON 解析错误: {e}，已重置为空数据。")
            return {}

    def save(self, key, data):
        """
        将指定副本的数据保存到 JSON 文件中
        并记录“上次选择的副本”
        """
        all_data = self._load_all()
        all_data[key] = data
        all_data["上次选择的副本"] = key

        # 写入更新后的数据
        self.file.seek(0)
        self.file.truncate()  # 清空原内容
        json.dump(all_data, self.file, ensure_ascii=False, indent=4)
        self.flush()

    def load(self, key):
        """根据副本名称加载上次保存的数据"""
        all_data = self._load_all()
        return all_data.get(key, {})

    def get_last_selected(self):
        """获取上次选择的副本名称"""
        all_data = self._load_all()
        # ✅ 使用相同的中文键名，并设置默认值
        return all_data.get("上次选择的副本", "材料，遗器，周本")