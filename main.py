import tkinter as tk
from chat import ChatApp

API_KEY = "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"
ORG_ID = ""

def main():
    root = tk.Tk()
    root.title("BuuGPT")
    ChatApp(root, API_KEY)  # Replace with your actual API key and organization ID
    root.mainloop()

if __name__ == "__main__":
    main()
