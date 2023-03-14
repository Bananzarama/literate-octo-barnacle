import os
import sys
import openai
import json
from collections import deque
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QToolBar,
    QMainWindow,
    QLabel,
    QSlider,
    QTabWidget,
    QComboBox
)
from PyQt6.QtGui import QFont, QAction
from dotenv import load_dotenv
load_dotenv()


class ChatWindow(QMainWindow):
    model = "text-davinci-003"
    prompt = "You are a normal human."
    temp = 5
    top_p = 1
    max_tokens = 500
    n = 1
    best_of = 1
    presence_penalty = 5
    frequency_penalty = 5
    count = 1

    def __init__(self):
        super().__init__()
        self.previous_messages = deque(maxlen=10)
        self.initUI()

    def initUI(self):
        self.previous_messages.append(ChatWindow.prompt)
        self.chat_log = QTextEdit()
        self.chat_log.setReadOnly(True)
        self.chat_log.setFont(QFont('Arial', 14))
        self.input_field = QTextEdit()
        self.input_field.setFont(QFont('Arial', 14))
        self.input_field.setMaximumSize(800, 100)
        self.send_button = QPushButton("Send")
        self.send_button.setFont(QFont('Arial', 14))
        self.send_button.setMaximumSize(200, 100)

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(self.input_field)
        hbox.addWidget(self.send_button)
        vbox.addWidget(self.chat_log)
        vbox.addLayout(hbox)

        # Set up toolbar
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)
        self.toolbar.setMovable(False)

        self.reset_action = QAction("Reset", self)
        self.toolbar.addAction(self.reset_action)
        self.reset_action.triggered.connect(self.reset_chat_window)
        self.settings_action = QAction("Settings", self)
        self.toolbar.addAction(self.settings_action)
        self.settings_action.triggered.connect(self.open_settings_window)
        self.help_action = QAction("Help", self)
        self.toolbar.addAction(self.help_action)
        self.help_action.triggered.connect(self.open_help_window)
        self.logs_action = QAction("Logs", self)
        self.toolbar.addAction(self.logs_action)
        self.logs_action.triggered.connect(self.open_log_window)

        # Set up main window layout
        central_widget = QWidget()
        central_widget.setLayout(vbox)
        self.setCentralWidget(central_widget)
        self.setWindowTitle("Chat AI")
        self.setGeometry(25, 25, 1000, 800)

        self.send_button.clicked.connect(self.on_send_button_click)

        # Create instance of SettingsWindow
        self.settings_window = SettingsWindow()
        # Create instance of HelpWindow
        self.help_window = HelpWindow()
        # Create instance of LogWindow
        self.log_window = LogWindow()

    def on_send_button_click(self):
        message = self.input_field.toPlainText()
        self.chat_log.append(f"You: {message}")
        self.previous_messages.append(f"{message}")
        response = get_response_from_openai(self.previous_messages)
        response_text = response.choices[0].text.strip()
        self.chat_log.append(f"Bot: {response_text}")
        context = "\n".join(self.previous_messages)
        self.previous_messages.append(f"{response_text}")
        sent_parameters = {
            "model": ChatWindow.model,
            "prompt": context,
            "temperature": ChatWindow.temp/10,
            "top_p": ChatWindow.top_p,
            "max_tokens": ChatWindow.max_tokens,
            "n": ChatWindow.n,
            "best_of": ChatWindow.best_of,
            "presence_penalty": ChatWindow.presence_penalty/10,
            "frequency_penalty": ChatWindow.frequency_penalty/10,
        }
        self.log_window.log_window.append(
            f"Sent#{ChatWindow.count}: {json.dumps(sent_parameters, indent=4)}")
        self.log_window.log_window.append(
            f"Response#{ChatWindow.count}: {response}")
        ChatWindow.count += 1
        self.input_field.clear()

    def open_settings_window(self):
        self.settings_window.show()

    def reset_chat_window(self):
        self.chat_log.clear()
        self.previous_messages.clear()
        self.previous_messages.append(ChatWindow.prompt)
        ChatWindow.count = 1

    def open_help_window(self):
        self.help_window.show()

    def open_log_window(self):
        self.log_window.show()

    def closeEvent(self, event):
        for window in QApplication.topLevelWidgets():
            window.close()


class SettingsWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.tab_widget = QTabWidget()
        self.setWindowTitle("Settings")
        self.setGeometry(0, 0, 600, 400)

        # First tab
        self.tab1 = QWidget()
        self.tab1_layout = QVBoxLayout()
        self.tab1.setLayout(self.tab1_layout)

        self.option1_layout = QHBoxLayout()
        self.option1_label = QLabel("Temperature (1-20)")
        self.option1_slider = QSlider(Qt.Orientation.Horizontal)
        self.option1_slider.setValue(ChatWindow.temp)
        self.option1_slider.setMinimum(0)
        self.option1_slider.setMaximum(20)
        self.option1_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.option1_slider.setTickInterval(1)
        self.option1_slider.valueChanged[int].connect(self.display)
        self.option1_description = QLabel()
        self.option1_description.setText("Value: "+str(ChatWindow.temp))
        self.option1_layout.addWidget(self.option1_label)
        self.option1_layout.addWidget(self.option1_slider)
        self.option1_layout.addWidget(self.option1_description)
        self.tab1_layout.addLayout(self.option1_layout)

        self.option2_layout = QHBoxLayout()
        self.option2_label = QLabel("Presence Penalty (-20-20)")
        self.option2_slider = QSlider(Qt.Orientation.Horizontal)
        self.option2_slider.setValue(ChatWindow.presence_penalty)
        self.option2_slider.setMinimum(-20)
        self.option2_slider.setMaximum(20)
        self.option2_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.option2_slider.setTickInterval(1)
        self.option2_slider.valueChanged[int].connect(self.display)
        self.option2_description = QLabel()
        self.option2_description.setText(
            "Value: "+str(ChatWindow.presence_penalty))
        self.option2_layout.addWidget(self.option2_label)
        self.option2_layout.addWidget(self.option2_slider)
        self.option2_layout.addWidget(self.option2_description)
        self.tab1_layout.addLayout(self.option2_layout)

        self.option3_layout = QHBoxLayout()
        self.option3_label = QLabel("Frequency Penalty (-20-20)")
        self.option3_slider = QSlider(Qt.Orientation.Horizontal)
        self.option3_slider.setValue(ChatWindow.frequency_penalty)
        self.option3_slider.setMinimum(-20)
        self.option3_slider.setMaximum(20)
        self.option3_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.option3_slider.setTickInterval(1)
        self.option3_slider.valueChanged[int].connect(self.display)
        self.option3_description = QLabel()
        self.option3_description.setText(
            "Value: "+str(ChatWindow.frequency_penalty))
        self.option3_layout.addWidget(self.option3_label)
        self.option3_layout.addWidget(self.option3_slider)
        self.option3_layout.addWidget(self.option3_description)
        self.tab1_layout.addLayout(self.option3_layout)

        # Add more options here...

        self.tab_widget.addTab(self.tab1, "Options")

        # Second tab
        self.tab2 = QWidget()
        self.tab2_layout = QVBoxLayout()
        self.tab2.setLayout(self.tab2_layout)

        self.tab2_promptbox = QTextEdit()
        self.tab2_promptbox.setReadOnly(True)
        self.tab2_promptbox.setFont(QFont('Arial', 14))
        self.tab2_promptbox.setText("Prompt: "+ChatWindow.prompt)
        self.tab2_inputbox = QTextEdit()
        self.tab2_inputbox.setFont(QFont('Arial', 14))
        self.tab2_inputbox.setMaximumSize(800, 100)
        self.tab2_set_button = QPushButton("Set")
        self.tab2_set_button.setFont(QFont('Arial', 14))
        self.tab2_set_button.setMaximumSize(300, 100)

        self.tab2_layout.addWidget(self.tab2_promptbox)
        self.tab2_layout.addWidget(self.tab2_inputbox)
        self.tab2_layout.addWidget(self.tab2_set_button)
        self.tab_widget.addTab(self.tab2, "Prompt")

        self.tab2_set_button.clicked.connect(self.on_set_button_click)

        # Third tab
        self.tab3 = QWidget()
        self.tab3_layout = QVBoxLayout()
        self.tab3.setLayout(self.tab3_layout)

        self.tab3_combobox = QComboBox()
        self.tab3_combobox.addItems([
            "text-davinci-003",
            "text-curie-001",
            "text-babbage-001",
            "text-ada-001",
            "code-davinci-002",
            "code-cushman-001",
        ])
        self.tab3_combobox.currentTextChanged.connect(self.model_changed)
        self.tab3_layout.addWidget(self.tab3_combobox)

        self.tokens_layout = QHBoxLayout()
        self.tokens_label = QLabel("Max Tokens")
        self.tokens_slider = QSlider(Qt.Orientation.Horizontal)
        self.tokens_slider.setValue(ChatWindow.max_tokens)
        self.tokens_slider.setMinimum(50)
        self.tokens_slider.setMaximum(3500)
        self.tokens_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.tokens_slider.setTickInterval(50)
        self.tokens_slider.valueChanged.connect(self.display)
        self.tokens_description = QLabel()
        self.tokens_description.setText("Value: "+str(ChatWindow.max_tokens))
        self.tokens_layout.addWidget(self.tokens_label)
        self.tokens_layout.addWidget(self.tokens_slider)
        self.tokens_layout.addWidget(self.tokens_description)
        self.tab3_layout.addLayout(self.tokens_layout)

        self.tab_widget.addTab(self.tab3, "Models")

        # End
        self.layout.addWidget(self.tab_widget)
        self.setLayout(self.layout)

    def display(self):
        ChatWindow.temp = self.option1_slider.value()
        ChatWindow.presence_penalty = self.option2_slider.value()
        ChatWindow.frequency_penalty = self.option3_slider.value()
        ChatWindow.max_tokens = self.tokens_slider.value()

        self.option1_description.setText("Value: "+str(ChatWindow.temp))
        self.option1_description.adjustSize()
        self.option2_description.setText(
            "Value: "+str(ChatWindow.presence_penalty))
        self.option2_description.adjustSize()
        self.option3_description.setText(
            "Value: "+str(ChatWindow.frequency_penalty))
        self.option3_description.adjustSize()
        self.tokens_description.setText(
            "Value: "+str(ChatWindow.max_tokens))
        self.tokens_description.adjustSize()

    def on_set_button_click(self):
        ChatWindow.prompt = self.tab2_inputbox.toPlainText()
        self.tab2_promptbox.setText("Prompt: "+ChatWindow.prompt)
        self.tab2_inputbox.clear()

    def model_changed(self):
        ChatWindow.model = self.tab3_combobox.currentText()


class HelpWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(50, 50, 200, 100)
        self.setWindowTitle("(:")
        self.label = QLabel("This is the help menu. \n Go fuck yourself")
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.label)
        self.setLayout(self.vbox)


class LogWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(0, 0, 500, 300)
        self.setWindowTitle("Logs")
        self.vbox = QVBoxLayout()

        self.log_window = QTextEdit()
        self.log_window.setReadOnly(True)

        # Set up toolbar
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setFixedHeight(20)
        self.reset_action = QAction("Reset", self)
        self.toolbar.addAction(self.reset_action)
        self.reset_action.triggered.connect(self.reset_log_window)

        self.vbox.addWidget(self.toolbar)
        self.vbox.addWidget(self.log_window)
        self.setLayout(self.vbox)

    def reset_log_window(self):
        self.log_window.clear()


def get_response_from_openai(previous_messages):
    # Set up OpenAI API authentication
    openai.api_key = os.environ.get("open-ai-token")
    # models = openai.Model.list()["data"]
    # list = []
    # for i in range(0,len(models)):
    #    list.append(models[i]["id"])
    # print(list)

    # Combine previous messages into prompt
    context = "\n".join(previous_messages)

    # Call OpenAI API to get response
    response = openai.Completion.create(
        model=ChatWindow.model,
        prompt=context,
        temperature=ChatWindow.temp/10,
        top_p=ChatWindow.top_p,
        max_tokens=ChatWindow.max_tokens,
        n=ChatWindow.n,
        best_of=ChatWindow.best_of,
        presence_penalty=ChatWindow.presence_penalty/10,
        frequency_penalty=ChatWindow.frequency_penalty/10,
    )

    return response


if __name__ == '__main__':
    app = QApplication(sys.argv)
    chat_window = ChatWindow()
    chat_window.show()
    sys.exit(app.exec())
