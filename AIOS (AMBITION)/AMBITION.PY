import os
import subprocess
import psutil
import time
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from transformers import pipeline, GPT2LMHeadModel, GPT2Tokenizer
import speech_recognition as sr
import pyttsx3
import json
from flask import Flask, render_template

# Flask app initialization
app = Flask(__name__)

# FileManager class handles file operations
class FileManager:
    def __init__(self, root_directory):
        self.root_directory = root_directory

    def list_files(self):
        try:
            files = os.listdir(self.root_directory)
            return files
        except Exception as e:
            return f"Error: {str(e)}"

    def create_file(self, file_name, content=""):
        try:
            with open(os.path.join(self.root_directory, file_name), 'w') as file:
                file.write(content)
            return f"File '{file_name}' created successfully."
        except Exception as e:
            return f"Error: {str(e)}"

    def read_file(self, file_name):
        try:
            with open(os.path.join(self.root_directory, file_name), 'r') as file:
                return file.read()
        except Exception as e:
            return f"Error: {str(e)}"

    def delete_file(self, file_name):
        try:
            os.remove(os.path.join(self.root_directory, file_name))
            return f"File '{file_name}' deleted successfully."
        except Exception as e:
            return f"Error: {str(e)}"

# Function to launch applications
def launch_app(app_name):
    try:
        if app_name.lower() == "notepad":
            subprocess.Popen('notepad.exe')
        elif app_name.lower() == "calculator":
            subprocess.Popen('calc.exe')
        else:
            print(f"Application '{app_name}' not found.")
    except Exception as e:
        print(f"Error launching application: {str(e)}")

# Function to display system information
def get_system_info():
    try:
        cpu_usage = psutil.cpu_percent()
        mem_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        return f"CPU Usage: {cpu_usage}%\nMemory Usage: {mem_usage}%\nDisk Usage: {disk_usage}%"
    except Exception as e:
        return f"Error retrieving system info: {str(e)}"

# Function to respond to user input using NLP
def chatbot_response(user_input):
    try:
        chatbot = pipeline('conversational', model='facebook/blenderbot-400M-distill')
        response = chatbot(user_input)
        return response[0]['generated_text']
    except Exception as e:
        return f"Error in chatbot response: {str(e)}"

# Function to handle voice commands
def voice_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print(f"Recognized: {command}")
            process_voice_command(command)
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")

def process_voice_command(command):
    if "notepad" in command.lower():
        launch_app("notepad")
    elif "calculator" in command.lower():
        launch_app("calculator")
    elif "system information" in command.lower():
        print(get_system_info())
    else:
        print("Command not recognized.")

# Function to monitor system performance
def monitor_system():
    while True:
        cpu_usage = psutil.cpu_percent(interval=1)
        mem_usage = psutil.virtual_memory().percent
        if cpu_usage > 90:
            print("Warning: High CPU Usage!")
        if mem_usage > 90:
            print("Warning: High Memory Usage!")
        time.sleep(10)

# GUI Application using Tkinter
def gui_main():
    def launch_app_gui():
        app_name = app_entry.get()
        launch_app(app_name)

    def show_system_info_gui():
        info = get_system_info()
        messagebox.showinfo("System Information", info)

    def manage_windows_gui():
        messagebox.showinfo("Manage Windows", "This feature is under development.")

    def process_file_operations():
        operation = file_operation.get()
        file_name = file_name_entry.get()
        content = file_content_entry.get()

        if operation == "Create":
            result = 'file_manager'.create_file(file_name, content)
        elif operation == "Read":
            result = 'file_manager'.read_file(file_name)
        elif operation == "Delete":
            result = 'file_manager'.delete_file(file_name)
        else:
            result = "Invalid operation."

        messagebox.showinfo("File Operation Result", result)

    def voice_command_gui():
        voice_command()

    root = tk.Tk()
    root.title("AIOS GUI")

    tk.Label(root, text="Application Name:").pack()
    app_entry = tk.Entry(root)
    app_entry.pack()

    tk.Button(root, text="Launch Application", command=launch_app_gui).pack()
    tk.Button(root, text="Show System Info", command=show_system_info_gui).pack()
    tk.Button(root, text="Manage Windows", command=manage_windows_gui).pack()
    tk.Button(root, text="Voice Command", command=voice_command_gui).pack()

    tk.Label(root, text="File Operation:").pack()
    file_operation = tk.StringVar(value="Create")
    tk.OptionMenu(root, file_operation, "Create", "Read", "Delete").pack()

    tk.Label(root, text="File Name:").pack()
    file_name_entry = tk.Entry(root)
    file_name_entry.pack()

    tk.Label(root, text="Content (for Create):").pack()
    file_content_entry = tk.Entry(root)
    file_content_entry.pack()

    tk.Button(root, text="Execute File Operation", command=process_file_operations).pack()

    root.mainloop()

# Voice Command class with Text-to-Speech (TTS) integration
class VoiceCommand:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.tts = pyttsx3.init()

    def listen(self):
        with sr.Microphone() as source:
            print("Listening...")
            audio = self.recognizer.listen(source)
            try:
                command = self.recognizer.recognize_google(audio)
                print(f"User said: {command}")
                return command
            except sr.UnknownValueError:
                self.tts.say("Sorry, I did not understand that.")
                self.tts.runAndWait()
                return None

    def respond(self, response):
        self.tts.say(response)
        self.tts.runAndWait()

# AI Model using GPT-2 for generating responses
class SmartAI:
    def __init__(self):
        self.model = GPT2LMHeadModel.from_pretrained('gpt2')
        self.tokenizer = GPT2Tokenizer.from_pretrained('gpt2')

    def generate_response(self, prompt):
        inputs = self.tokenizer.encode(prompt, return_tensors="pt")
        outputs = self.model.generate(inputs, max_length=100, num_return_sequences=1)
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response

# Main AIOS Class combining all features
class AIOS:
    def __init__(self):
        self.voice_command = VoiceCommand()
        self.smart_ai = SmartAI()
        self.file_manager = FileManager(root_directory="aios_files")

    def start(self):
        while True:
            command = self.voice_command.listen()
            if command:
                ai_response = self.smart_ai.generate_response(command)
                print(f"AI: {ai_response}")
                self.voice_command.respond(ai_response)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == "__main__":
    # Start the system monitor in a separate thread
    threading.Thread(target=monitor_system, daemon=True).start()
    # Launch the GUI application
    threading.Thread(target=gui_main).start()

    # Start the Flask app
    app.run(debug=True, use_reloader=False)
    
    # Start the AIOS main loop
    aios = AIOS()
    aios.start()
