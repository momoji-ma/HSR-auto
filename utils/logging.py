# utils/logging.py
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
        # 调用父类 FileHandler 的构造函数
        super().__init__(filename=filename, mode='r+', encoding='utf-8')
        self.open()  # 自动打开文件
        self._ensure_file_has_content()

    def _ensure_file_has_content(self):
        """确保文件不是空的，避免 JSON 解析错误"""
        # 检查文件是否为空
        self.file.seek(0)
        content = self.file.read()
        if not content.strip():
            self.file.seek(0)
            self.file.write("{}")
            self.file.flush()

    def _load_all(self):
        """从 JSON 文件中读取所有数据"""
        self.file.seek(0)
        try:
            return json.load(self.file)
        except json.JSONDecodeError:
            print("文件内容不是有效的 JSON，已重置为空数据。")
            return {}

    def save(self, key, data):
        """将指定副本的数据保存到 JSON 文件中，并记录最后选择的副本"""
        all_data = self._load_all()
        all_data[key] = data
        all_data["上次选择的副本"] = key  # 记录最后一次选择的副本

        # 写入更新后的数据
        self.file.seek(0)
        self.file.truncate()  # 清空文件
        json.dump(all_data, self.file, ensure_ascii=False, indent=4)
        self.flush()

    def load(self, key):
        """根据副本名称加载上次保存的数据"""
        all_data = self._load_all()
        return all_data.get(key, {})

    def get_last_selected(self):
        """获取上次选择的副本名称"""
        all_data = self._load_all()
        return all_data.get("_last_selected", "材料，遗器，周本")  # 默认值