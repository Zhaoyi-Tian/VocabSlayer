from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QTextCursor, QColor, QTextCharFormat, QTextBlockFormat
from openai import OpenAI
from qfluentwidgets import PushButton, SwitchButton, TextEdit, TextBrowser, RoundMenu, FluentIcon, Action
import json
import os
import time

from AI import Ui_ai

HISTORY_DIR = "chat_history"


class ChatTextEdit(TextBrowser):
    # 保持你原有的ChatTextEdit实现不变
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QTextBrowser {
                background: #f5f7fb;
                border: none;
                padding: 10px;
            }
        """)
        self.document().setDefaultStyleSheet("hr { border: 0; border-top: 1px solid #cccccc; margin: 5px 0; }")
        self.ai_format = self.create_text_format(QColor("#2d2d2d"))
        self.user_format = self.create_text_format(QColor("#0078D4"))

    def create_text_format(self, color):
        char_format = QTextCharFormat()
        char_format.setForeground(color)
        return char_format

    def append_message(self, text, is_ai=True):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)

        if not self.document().isEmpty():
            cursor.insertText("\n")
            time_format = QTextCharFormat()
            time_format.setFontPointSize(8)
            time_format.setForeground(QColor("#666666"))

            block_format = QTextBlockFormat()
            block_format.setAlignment(Qt.AlignLeft)
            cursor.mergeBlockFormat(block_format)

            current_time = QtCore.QDateTime.currentDateTime().toString("HH:mm:ss")
            cursor.insertText(f"{current_time}\n")

        block_format = QTextBlockFormat()
        alignment = Qt.AlignLeft if is_ai else Qt.AlignRight
        block_format.setAlignment(alignment)
        cursor.mergeBlockFormat(block_format)

        char_format = self.ai_format if is_ai else self.user_format
        cursor.setCharFormat(char_format)
        cursor.insertText(text + "\n")
        self.setTextCursor(cursor)
        self.ensureCursorVisible()
        return cursor.position()

    def append_temp_message(self, text, is_ai=True):
        """ 插入临时消息并返回起始位置 """
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        start = cursor.position()
        self.append_message(text, is_ai)
        return start

    def replace_temp_message(self, start_pos, new_text):
        """ 替换临时消息 """
        cursor = self.textCursor()
        cursor.setPosition(start_pos)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
        self.append_message(new_text, is_ai=True)


class AiWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, client, messages,model):
        super().__init__()
        self.client = client
        self.messages = messages
        self.model = model
    def run(self):
        max_retries = 3
        retry_delay = 5

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    stream=False,
                    timeout=100
                )
                reply = response.choices[0].message.content
                self.finished.emit(reply)
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    self.error.emit(f"请求失败: {str(e)}")


class Ai_Widget(QtWidgets.QWidget):
    def __init__(self, cfg,User,tab_id=0):
        super().__init__()
        self.Username = User
        self.cfg = cfg
        self.client =OpenAI(api_key=cfg.API.value, base_url="https://api.deepseek.com")
        self.tab_id = tab_id
        self.messages = []
        self.history_file = os.path.join(HISTORY_DIR, f"../../user/{User}/chat_history.json")
        self.Prompt_words_English="""你是一位专业的英语学习助手。当我输入一个英文单词时，请提供以下信息：
1.  ​**核心中文释义：​** 给出最常用、最核心的1-2个中文意思。​**核心日语释义：​** 给出最常用、最核心的1-2个日语意思。
2.  ​**词性：​** 标明单词的词性（如 n.名词, v.动词, adj.形容词, adv.副词 等）。
3.  ​**简明英文释义：​** 用简单易懂的英文解释单词。
4.  ​**典型例句：​** 提供一个能清晰展示单词用法的英文例句，并附带中文翻译。
5.  ​**发音提示：​** 提供音标（IPA或KK音标，请明确标注）或音节划分。
6.  ​**记忆技巧（可选）：​** 提供一个简短、有效的记忆联想或词根词缀分析（如果适用）。
7.  ​**常见搭配/短语（可选）：​** 列出1-2个最常用的搭配或短语（如果适用）。
8.  ​**易混词提示（可选）：​** 如果该词容易与其他词混淆，给出简短提示（如果适用）。
        """
        self.Prompt_words_Chinese = """你是一位专业的中文学习助手。当我输入一个中文词语（简体字）时，请提供以下信息：
1.  ​**核心英文释义：​** 给出最常用、最核心的1-2个英文意思。​**核心日语释义：​** 给出最常用、最核心的1-2个日语意思。
2.  ​**词性：​** 标明词语的词性（如 名词, 动词, 形容词, 副词 等）。
3.  ​**简明中文释义：​** 用简单易懂的中文解释词语（可选，对非母语者或复杂词很有用）。
4.  ​**典型例句：​** 提供一个能清晰展示词语用法的中文例句，并附带英文翻译。
5.  ​**拼音：​** 提供词语的标准拼音（带声调）。
6.  ​**部首/结构（可选）：​** 对于汉字，可以简要说明其部首或结构特点（对识字有帮助）。
7.  ​**常见搭配/用法（可选）：​** 列出1-2个最常用的搭配或说明其典型用法（如果适用）。
8.  ​**近义词/反义词提示（可选）：​** 如果该词有常用近义词或反义词，给出简短提示（如果适用）。
                """
        self.Prompt_words_Japanese = """你是一位专业的日语学习助手。当我输入一个日语单词（可以是汉字、假名或混合）时，请提供以下信息：
1.  ​**核心中文释义：​** 给出最常用、最核心的1-2个中文意思。
2.  ​**核心英文释义：​** 给出最常用、最核心的1-2个英文意思。
3.  ​**词性：​** 标明单词的词性（如 名詞, 動詞, 形容詞, 副詞 等）。
4.  ​**假名标注：​** 为输入的单词标注平假名（ひらがな）或片假名（カタカナ）读音（如果输入的是汉字，必须标注；如果是假名，可省略或重复）。
5.  ​**罗马音：​** 提供单词的罗马字拼音。
6.  ​**典型例句：​** 提供一个能清晰展示单词用法的日文例句，并附带中文翻译。
7.  ​**汉字说明（如果适用）：​** 如果单词包含汉字，解释该汉字的音读（おんよみ）和训读（くんよみ）（如果该单词使用了训读）。
8.  ​**礼貌形/变形提示（如果适用）：​** 如果是动词或形容词，给出其基本形（辞書形）和礼貌形（ます形/です形）或常用变形（如果适用）。
9.  ​**常见搭配/用法（可选）：​** 列出1-2个最常用的搭配或说明其典型用法（如果适用）
                """
        self.Prompt={
            "English":self.Prompt_words_English,
            "Chinese":self.Prompt_words_Chinese,
            "Japanese":self.Prompt_words_Japanese
        }
        history_dir = os.path.dirname(self.history_file)
        if not os.path.exists(history_dir):
            os.makedirs(history_dir)

        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w') as f:
                f.write('[]')  # 写入空数组
        # 初始化UI
        self.ui = Ui_ai()
        self.ui.setupUi(self)
        self.ui.TextEdit_2.setPlaceholderText("请输入你的问题")
        # 替换原有TextEdit为自定义聊天框
        self.ui.TextEdit = ChatTextEdit(self)
        self.ui.TextEdit.setGeometry(QtCore.QRect(0, 0, 811, 548))
        # 连接信号
        self.ui.PushButton.clicked.connect(self.send_message)
        self.current_model = "deepseek-chat"
        self.ui.SwitchButton.checkedChanged.connect(self.on_model_changed)
        # 初始化历史记录
        self.load_history()

        menu = RoundMenu(parent=self.ui.DropDownToolButton)
        menu.addAction(Action(FluentIcon.LANGUAGE,'English', triggered=lambda:self.write_prompt_words('English')))
        menu.addAction(Action( FluentIcon.LANGUAGE,'Chinese', triggered=lambda :self.write_prompt_words('Chinese')))
        menu.addAction(Action( FluentIcon.LANGUAGE,'Japanese', triggered=lambda: self.write_prompt_words('Japanese')))
        self.ui.DropDownToolButton.setMenu(menu)
        self.ui.PushButton.setIcon(FluentIcon.SEND)
    def on_model_changed(self, is_checked: bool):
        """ SwitchButton状态变化处理 """
        if is_checked:
            self.current_model = "deepseek-reasoner"  # 开启时使用大模型
            print("[DEBUG] 切换到深度模式")
        else:
            self.current_model = "deepseek-chat"  # 关闭时使用标准模型
            print("[DEBUG] 切换到标准模式")

    def send_message(self):
        user_input = self.ui.TextEdit_2.toPlainText().strip()
        if not user_input:
            return

        # 添加用户消息
        self.messages.append({"role": "user", "content": user_input})
        self.ui.TextEdit.append_message(user_input, is_ai=False)
        self.ui.TextEdit_2.clear()
        thinking_text = "正在深度思考..." if self.current_model == "deepseek-reasoner" else "正在思考..."
        self.temp_msg_pos = self.ui.TextEdit.append_temp_message(thinking_text, is_ai=True)
        # 禁用发送按钮
        self.ui.PushButton.setEnabled(False)

        # 创建并启动工作线程
        self.worker = AiWorker(self.client, self.messages,self.current_model)
        self.worker.finished.connect(self.handle_response)
        self.worker.error.connect(self.handle_error)
        self.worker.start()

    def handle_response(self, reply):
        self.ui.TextEdit.replace_temp_message(self.temp_msg_pos, reply)
        self.messages.append({"role": "assistant", "content": reply})
        self.ui.PushButton.setEnabled(True)
        self.save_history()

    def handle_error(self, error_msg):
        self.ui.TextEdit.replace_temp_message(self.temp_msg_pos, error_msg)
        QtWidgets.QMessageBox.critical(self, "错误", error_msg)
        self.ui.PushButton.setEnabled(True)

    def load_history(self):
        try:
            with open(self.history_file, "r") as f:
                self.messages = json.load(f)
                for msg in self.messages:
                    if msg["role"] == "user":
                        self.ui.TextEdit.append_message(msg["content"], is_ai=False)
                    elif msg["role"] == "assistant":
                        self.ui.TextEdit.append_message(msg["content"], is_ai=True)
        except (FileNotFoundError, json.JSONDecodeError):
            self.messages = [{"role": "system", "content": "You are a helpful assistant."}]

    def save_history(self):
        os.makedirs(HISTORY_DIR, exist_ok=True)
        with open(self.history_file, "w") as f:
            json.dump(self.messages, f)
    def write_prompt_words(self,language,word=""):
        self.ui.TextEdit_2.clear()
        self.ui.TextEdit_2.setText(self.Prompt[language]+str(word))