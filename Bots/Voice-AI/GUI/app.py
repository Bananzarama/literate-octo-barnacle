# -*- coding: utf-8 -*-

# TODO:
# 1) fix stop buttons transition from stopping -> stopped 
# 2) fix device selection from crashing when theres multiple viable options (notes below)
# 3) fix logging
# 3.1) azure speech recognition?? 
# 4) ???
# 5) profit

from PyQt6.QtCore import Qt, QRunnable, QThreadPool
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
    QComboBox,
    QCheckBox
)
from PyQt6.QtGui import QFont, QAction
import sys
import openai
import speech_recognition as sr
import elevenlabs
import sounddevice
import soundfile
import io

openai.api_key = ""
elevenlabs.set_api_key("")

class MainWindow(QMainWindow):
    prompt = "You are a helpful assistant or something idk."
    post_prompt = "Please keep all responses to less then 3 sentences"
    prompt = prompt + post_prompt
    previous_messages = [{"role": "system", "content": prompt}]
    recording_location = "sent_recordings\\recording.wav"
    voice = "Bella"
    temp = 2
    active = False
    input_source = [sounddevice.query_devices(
        kind='input')['index'], sounddevice.query_devices(kind='input')['name']]
    output_source = [sounddevice.query_devices(
        kind='output')['index'], sounddevice.query_devices(kind='output')['name']]
    speech = False

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ryan's VoicedAI")
        self.initUI()

    def initUI(self):
        self.chat_log = QTextEdit()
        self.chat_log.setReadOnly(True)
        self.chat_log.setFont(QFont('Arial', 14))
        self.stop_button = QPushButton("Stop")
        self.stop_button.setFont(QFont('Arial', 14))
        self.stop_button.setMaximumSize(200, 100)
        self.start_button = QPushButton("Start")
        self.start_button.setFont(QFont('Arial', 14))
        self.start_button.setMaximumSize(200, 100)
        self.indicator_label = QLabel()
        self.indicator_label.setText("Active: False")
        self.indicator_label.setFont(QFont('Arial', 14))
        self.speech_checkbox = QCheckBox("voice", self)
        self.speech_checkbox.setFont(QFont('Arial', 14))
        self.speech_checkbox.toggled.connect(self.toggle_voice)

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(self.start_button)
        hbox.addWidget(self.stop_button)
        hbox.addWidget(self.speech_checkbox)
        hbox.addWidget(self.indicator_label)
        vbox.addWidget(self.chat_log)
        vbox.addLayout(hbox)

        # Set up toolbar
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)
        self.toolbar.setMovable(False)

        self.settings_action = QAction("Settings", self)
        self.toolbar.addAction(self.settings_action)
        self.settings_action.triggered.connect(self.open_settings_window)
        self.logs_action = QAction("Logs", self)
        self.toolbar.addAction(self.logs_action)
        self.logs_action.triggered.connect(self.open_log_window)
        self.help_action = QAction("Help", self)
        self.toolbar.addAction(self.help_action)
        self.help_action.triggered.connect(self.open_help_window)
        self.reset_action = QAction("Reset", self)
        self.toolbar.addAction(self.reset_action)
        self.reset_action.triggered.connect(self.reset_chat_window)

        # Set up main window layout
        central_widget = QWidget()
        central_widget.setLayout(vbox)
        self.setCentralWidget(central_widget)
        self.setWindowTitle("Chat AI")
        self.setGeometry(25, 25, 500, 400)

        self.start_button.clicked.connect(self.on_start_button_click)
        self.stop_button.clicked.connect(self.on_stop_button_click)

        # Create instance of SettingsWindow
        self.settings_window = SettingsWindow()
        # Create instance of HelpWindow
        self.help_window = HelpWindow()
        # Create instance of LogWindow
        self.log_window = LogWindow()

    def on_start_button_click(self):
        MainWindow.active = True
        self.log_window.log_window.append("Active: True")
        self.indicator_label.setText("Active: True")
        pool = QThreadPool.globalInstance()
        if pool.activeThreadCount() < 1:
            pool.reserveThread()
            pool.start(ChatLoop(1))
            print("Thread count: " + str(pool.activeThreadCount()))
            self.log_window.log_window.append("Loop running on 1 thread")
            print("Loop running on 1 thread")
        else:
            print("Thread count: " + str(pool.activeThreadCount()))
            self.log_window.log_window.append(
                "Failed: Loop already running on 1 thread")
            print("Failed: Loop already running on 1 thread")

    def on_stop_button_click(self):
        MainWindow.active = False
        self.log_window.log_window.append("Active: Stopping")
        self.indicator_label.setText("Active: Stopping")
        pool = QThreadPool.globalInstance()
        pool.releaseThread()
        self.log_window.log_window.append("Active: Stopped")
        self.indicator_label.setText("Active: Stopped")

    def reset_chat_window(self):
        self.chat_log.clear()
        MainWindow.previous_messages.clear()
        MainWindow.previous_messages.append(
            {"role": "system", "content": MainWindow.prompt})
        self.log_window.log_window.append("Chat History Cleared!")

    def open_settings_window(self):
        self.settings_window.show()
        self.log_window.log_window.append("Opened: Settings Window")

    def open_help_window(self):
        self.help_window.show()
        self.log_window.log_window.append("Opened: Help Window")

    def open_log_window(self):
        self.log_window.show()
        self.log_window.log_window.append("Opened: Log Window")

    def toggle_voice(self):
        if self.sender().isChecked() == True:
            MainWindow.speech = True
            self.log_window.log_window.append("Voice: True")
        else:
            MainWindow.speech = False
            self.log_window.log_window.append("Voice: False")

    def closeEvent(self, event):
        for window in QApplication.topLevelWidgets():
            QThreadPool.globalInstance().clear()
            window.close()


class SettingsWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.tab_widget = QTabWidget()
        self.setWindowTitle("Settings")
        self.setGeometry(0, 0, 400, 400)

        # First tab
        self.tab1 = QWidget()
        self.tab1_layout = QVBoxLayout()
        self.tab1.setLayout(self.tab1_layout)

        self.option1_layout = QHBoxLayout()
        self.option1_label = QLabel("Temperature (1-20)")
        self.option1_slider = QSlider(Qt.Orientation.Horizontal)
        self.option1_slider.setValue(MainWindow.temp)
        self.option1_slider.setMinimum(0)
        self.option1_slider.setMaximum(20)
        self.option1_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.option1_slider.setTickInterval(1)
        self.option1_slider.valueChanged[int].connect(self.sliders)
        self.option1_description = QLabel()
        self.option1_description.setText("Value: "+str(MainWindow.temp))
        self.option1_layout.addWidget(self.option1_label)
        self.option1_layout.addWidget(self.option1_slider)
        self.option1_layout.addWidget(self.option1_description)

        self.tab1_layout.addLayout(self.option1_layout)
        self.tab_widget.addTab(self.tab1, "Options")

        # Second tab
        self.tab2 = QWidget()
        self.tab2_layout = QVBoxLayout()
        self.tab2.setLayout(self.tab2_layout)
        self.tab_widget.addTab(self.tab2, "Prompt")

        self.tab2_promptbox = QTextEdit()
        self.tab2_promptbox.setReadOnly(True)
        self.tab2_promptbox.setFont(QFont('Arial', 14))
        self.tab2_promptbox.setText("Prompt: "+MainWindow.prompt)
        self.tab2_inputbox = QTextEdit()
        self.tab2_inputbox.setFont(QFont('Arial', 14))
        self.tab2_inputbox.setMaximumSize(900, 100)
        self.tab2_set_button = QPushButton("Set")
        self.tab2_set_button.setFont(QFont('Arial', 14))
        self.tab2_set_button.setMaximumSize(300, 100)

        self.tab2_layout.addWidget(self.tab2_promptbox)
        self.tab2_layout.addWidget(self.tab2_inputbox)
        self.tab2_layout.addWidget(self.tab2_set_button)

        self.tab2_set_button.clicked.connect(self.on_set_button_click)

        # Third tab
        self.tab3 = QWidget()
        self.tab3_layout = QVBoxLayout()
        self.tab3.setLayout(self.tab3_layout)

        self.input_layout = QHBoxLayout()
        self.input_title = QLabel("Input Device (microphone)")
        self.input_label = QLabel(MainWindow.input_source[1])
        self.input_dropdown = QComboBox()
        self.input_dropdown.addItems(sr.Microphone.list_microphone_names())

        self.output_layout = QHBoxLayout()
        self.output_title = QLabel("Output Device (speakers)")
        self.output_label = QLabel(MainWindow.output_source[1])
        self.output_dropdown = QComboBox()
        self.output_dropdown.addItems(
            [device['name'] for device in sounddevice.query_devices() if device['max_input_channels'] > 0])

        self.input_layout.addWidget(self.input_title)
        self.input_layout.addWidget(self.input_label)
        self.input_layout.addWidget(self.input_dropdown)
        self.output_layout.addWidget(self.output_title)
        self.output_layout.addWidget(self.output_label)
        self.output_layout.addWidget(self.output_dropdown)
        self.tab3_layout.addLayout(self.input_layout)
        self.tab3_layout.addLayout(self.output_layout)
        self.tab_widget.addTab(self.tab3, "Devices")

        self.input_dropdown.activated.connect(self.input_combovalue)
        self.output_dropdown.activated.connect(self.output_combovalue)

        # End
        self.layout.addWidget(self.tab_widget)
        self.setLayout(self.layout)

    def sliders(self):
        MainWindow.temp = self.option1_slider.value()
        self.option1_description.setText("Value: "+str(MainWindow.temp))
        self.option1_description.adjustSize()

    def on_set_button_click(self):
        MainWindow.prompt = self.tab2_inputbox.toPlainText()
        self.tab2_promptbox.setText("Prompt: "+MainWindow.prompt)
        # self.log_window.log_window.append("Promp changed to: "+MainWindow.prompt)
        self.tab2_inputbox.clear()

    # TODO Fix so this wont happen anymore (DeviceList from sounddevices' query_devices() cuts name off at 31 chars)
    # idea: compare both name and idex?
    # ValueError: Multiple input/output devices found for 'CABLE Output (VB-Audio Virtual Cable)':
    # [22] CABLE Output (VB-Audio Virtual Cable), Windows DirectSound
    # [54] CABLE Output (VB-Audio Virtual Cable), Windows WASAPI

    def input_combovalue(self):
        chosen_device_index = sr.Microphone.list_microphone_names().index(
            self.input_dropdown.currentText())
        chosen_device = sr.Microphone.list_microphone_names()[
            chosen_device_index]
        MainWindow.input_source = [chosen_device_index, chosen_device]
        self.input_label.setText(MainWindow.input_source[1])
        # self.log_window.log_window.append("Input Device Updated: " + MainWindow.input_source[1])
        print("Input Device Updated: " + MainWindow.input_source[1])

    def output_combovalue(self):
        chosen_device = sounddevice.query_devices(
            device=self.output_dropdown.currentText())
        MainWindow.output_source = [
            chosen_device['index'], chosen_device['name']]
        self.output_label.setText(MainWindow.output_source[1])
        # self.log_window.log_window.append("Output Device Updated: " + MainWindow.output_source[1])
        print("Output Device Updated: " + MainWindow.output_source[1])


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
        self.clear_action = QAction("Clear", self)
        self.toolbar.addAction(self.clear_action)
        self.clear_action.triggered.connect(self.clear_log_window)

        self.vbox.addWidget(self.toolbar)
        self.vbox.addWidget(self.log_window)
        self.setLayout(self.vbox)

    def clear_log_window(self):
        self.log_window.clear()


class ChatLoop(QRunnable):

    def __init__(self, n):
        super().__init__()
        self.n = n

    def run(self):
        print("voice: "+ str(MainWindow.speech))
        while MainWindow.active == True:
            if MainWindow.speech == True:
                self.say(self.digest_voice(MainWindow.previous_messages))
            else:
                self.digest_voice(MainWindow.previous_messages)

    def say(self, text):
        print("Attempting to speak")
        # self.log_window.log_window.append("Attempting to speak")
        audio = elevenlabs.generate(
            text=text,
            voice=MainWindow.voice,
            model="eleven_monolingual_v1",
        )
        sounddevice.play(*soundfile.read(io.BytesIO(audio)),
                         device=MainWindow.output_source[0])
        sounddevice.wait()
        print("Finished talking")
        # self.log_window.log_window.append("Finished talking")

    def get_response_from_openai(self, previous_messages):
        print("ChatGPT digesting")
        # self.log_window.log_window.append("ChatGPT digesting")
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=previous_messages,
                temperature=MainWindow.temp/10,
                max_tokens=3500,
            )
            print("ChatGPT response: ",
                  response["choices"][0]["message"]["content"])
            # self.log_window.log_window.append("ChatGPT response: " + response["choices"][0]["message"]["content"])
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            print("Unknown OpenAI ChatGPT Error: " + str(e))
            # self.log_window.log_window.append("Unknown OpenAI ChatGPT Error: " + str(e))
            return "Unknown OpenAI ChatGPT Error: " + str(e)

    def get_transcript_from_audio(self, file_name):
        print("Whisper digesting")
        # self.log_window.log_window.append("Whisper digesting")
        try:
            wavfile = open(file_name, "rb")
            transcription = openai.Audio.transcribe(
                "whisper-1", wavfile)["text"]
            print("Voice Input: ", transcription)
            # self.log_window.log_window.append("Voice Input: " + transcription)
            return transcription
        except Exception as e:
            print("Unknown OpenAI Whisper Error: " + str(e))
            # self.log_window.log_window.append("Unknown OpenAI Whisper Error: " + str(e))
            return "Unknown OpenAI Whisper Error: " + str(e)

    def record_audio(self, file_output):
        r = sr.Recognizer()
        print("start talking now")
        # self.log_window.log_window.append("start talking now")
        try:
            with sr.Microphone(device_index=MainWindow.input_source[0]) as source:
                r.adjust_for_ambient_noise(source, duration=0.25)
                audio = r.listen(source)
            with open(file_output, 'wb') as file:
                wav_data = audio.get_wav_data()
                file.write(wav_data)
        except Exception as e:
            print("Recording Error: " + str(e))
            # self.log_window.log_window.append("Recording Error: " + str(e))

    def digest_voice(self, previous_messages):
        try:
            self.record_audio(MainWindow.recording_location)
            user_response = self.get_transcript_from_audio(
                MainWindow.recording_location)
            previous_messages.append(
                {"role": "user", "content": user_response})
            main_window.chat_log.append("User: " + user_response)
            response_text = self.get_response_from_openai(previous_messages)
            previous_messages.append(
                {"role": "assistant", "content": response_text})
            main_window.chat_log.append("Bot: " + response_text)
            return response_text
        except Exception as e:
            print("Voice Digestion Error: " + str(e))
            # self.log_window.log_window.append("Voice Digestion Error: " + str(e))
            return "Voice Digestion Error: " + str(e)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
