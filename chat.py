import tkinter as tk
import requests
import threading
import pyperclip  # You might need to install this package


class ChatApp:
    def __init__(self, root, api_key, organization_id=None):
        self.root = root
        self.api_key = api_key
        self.organization_id = organization_id
        
        self.dark_mode = True  # Define the dark_mode attribute
        self.previous_messages = []  # Initialize the previous_messages attribute

        # Set window size to 80% of screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        
        # Calculate x and y coordinates for the Tk root window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # Set the window size and position it at the center
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')

        # Make the window not resizable
        self.root.resizable(False, False)

        self.setup_ui()

    def setup_ui(self):
        self.root.bind("<Configure>", self.update_wraplength)

        self.custom_font = ("Arial", 12)
        self.set_theme()

        # Main frame
        frame = tk.Frame(self.root, bg=self.bg_color)
        frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Chat history container with a scrollbar
        self.chat_container = tk.Canvas(frame, bg=self.bg_color)
        self.chat_scrollbar = tk.Scrollbar(frame, orient="vertical", command=self.chat_container.yview)
        self.chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_container.pack(fill=tk.BOTH, expand=True)  # Changed to default stacking
        self.chat_container.configure(yscrollcommand=self.chat_scrollbar.set)

        # Frame to hold chat messages inside the Canvas
        self.messages_frame = tk.Frame(self.chat_container, bg=self.bg_color)
        self.messages_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        self.messages_frame.bind("<Configure>", self.on_frame_configure)

        # Create the window for the messages_frame inside the chat_container
        self.messages_frame_window = self.chat_container.create_window((0, 0), window=self.messages_frame, anchor="nw")

        # Update the window width when the canvas is resized
        self.chat_container.bind("<Configure>", self.on_canvas_resize)
        
        # Input and button frame
        input_frame = tk.Frame(frame, bg=self.bg_color)
        input_frame.pack(padx=10, pady=10, fill=tk.X)  # Changed to default stacking

        # Input text area
        self.text_input = tk.Text(input_frame, height=1, width=40, font=self.custom_font, fg=self.text_color, bg=self.user_msg_bg, wrap=tk.WORD)
        self.text_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text_input.bind("<KeyRelease>", self.update_ui)
        self.text_input.bind("<Return>", self.on_enter_key)
        
        self.text_input.focus_set()

        # Submit button
        self.submit_button = tk.Button(input_frame, text="Start Chat", command=self.on_submit, font=self.custom_font, fg=self.text_color, bg=self.button_color, state="disabled")
        self.submit_button.pack(side=tk.RIGHT, padx=5)
        
    def on_canvas_resize(self, event=None):
        # Set the width of the messages_frame_window to match the canvas width
        self.chat_container.itemconfig(self.messages_frame_window, width=event.width - 5)

        # Update the scroll region
        self.chat_container.configure(scrollregion=self.chat_container.bbox("all"))

    def update_ui(self, event=None):
        # Adjust the input box size based on content
        self.text_input.config(height=self.text_input.get("1.0", "end-1c").count('\n')+1)

        # Update the submit button state
        self.submit_button.config(state="normal" if self.text_input.get("1.0", "end-1c").strip() else "disabled")

        # Prevent the default behavior of the Enter key
        if event.keysym == "Return":
            return "break"
          
    def on_enter_key(self, event=None):
        if self.submit_button["state"] == "normal":
            self.on_submit()
        return "break"
        
    def switch_theme(self):
        self.dark_mode = not self.dark_mode
        self.setup_ui()

    def set_theme(self):
        if self.dark_mode:
            self.bg_color = "#2D2D2D"
            self.text_color = "#CCCCCC"
            self.user_msg_bg = "#3C3F41"
            self.button_color = "#5F5F5F"
            self.gpt_msg_bg = "#333333"
        else:
            # Define light mode colors here
            pass

    def display_message(self, sender, message, message_id=None):
        bg_color = self.user_msg_bg if sender == "Buu" else self.gpt_msg_bg

        # Frame for each message
        message_frame = tk.Frame(self.messages_frame, bg=bg_color)
        message_frame.pack(side=tk.TOP, fill=tk.X, expand=True)
        
        # Bold font for sender
        bold_font = (self.custom_font[0], self.custom_font[1], 'bold')

        # Text widget for sender and message
        # Text widget for sender with centered text
        sender_text = tk.Text(message_frame, font=bold_font, bg=bg_color, fg=self.text_color, width=10, height=1, padx=5, pady=5)
        sender_text.insert(tk.END, f"{sender}")
        sender_text.configure(state=tk.DISABLED, relief=tk.FLAT)
        sender_text.tag_configure("center", justify=tk.CENTER)
        sender_text.tag_add("center", "1.0", "end")
        sender_text.pack(side=tk.LEFT, padx=(5, 0))

        # Calculate the required height for message_text based on the content
        num_lines = message.count('\n') + 1  # Counting the number of lines in the message
        
        message_text = tk.Text(message_frame, height=num_lines, font=self.custom_font, bg=bg_color, fg=self.text_color, wrap='none', borderwidth=0)
        message_text.insert('1.0', message)
        message_text.configure(state='disabled', inactiveselectbackground=message_text.cget("selectbackground"))
        message_text.pack(side=tk.LEFT, fill=tk.X, padx=(5, 10), pady=(7, 7), expand=True)

        if sender == "GPT":
            action_btn = tk.Button(message_frame, text="📋", command=lambda msg=message: self.copy_to_clipboard(msg))
        else:
            action_btn = tk.Button(message_frame, text="✏️", command=lambda msg_id=message_id: self.edit_message(msg_id))

        action_btn.pack(side=tk.RIGHT, padx=5)

        self.update_scroll()
        
    def copy_to_clipboard(self, message):
        pyperclip.copy(message)

    def edit_message(self, message_id):
        if self.text_input.cget('state') != tk.NORMAL:
            return
      
        # Get the original message and put it in the input box
        original_message = self.previous_messages[message_id]["content"]
        self.text_input.delete("1.0", tk.END)
        self.text_input.insert("1.0", original_message)

        # Focus on the input box
        self.text_input.focus_set()

        # Delete the message and all following messages from the display and previous_messages
        self.delete_following_messages(message_id)
        
    def delete_following_messages(self, message_id):
        # Remove messages from the display
        for widget in self.messages_frame.winfo_children()[message_id:]:
            widget.destroy()

        # Remove messages from the previous_messages list
        del self.previous_messages[message_id:]
            
    def resend_requests(self):
        # Clear messages and resend all
        self.clear_messages()
        self.handle_request()
        
    def clear_messages(self):
        for widget in self.messages_frame.winfo_children():
            widget.destroy()

    def update_wraplength(self, event=None):
        # Update wraplength for message labels when window resizes
        new_wrap_length = self.root.winfo_width() - 150  # Adjust 150 based on your layout
        for child in self.messages_frame.winfo_children():
            for label in child.winfo_children():
                if isinstance(label, tk.Label) and label != child.winfo_children()[0]:  # Skip the sender label
                    label.config(wraplength=new_wrap_length)
        
    def update_scroll(self):
        self.messages_frame.update_idletasks()  # Update the frame to recalculate sizes
        self.chat_container.configure(scrollregion=self.chat_container.bbox("all"))  # Update the scroll region
        self.chat_container.yview_moveto(1)  # Auto-scroll to the bottom

    def on_frame_configure(self, event=None):
        # Update the scroll region to encompass the inner frame
        self.chat_container.configure(scrollregion=self.chat_container.bbox("all"))

        # Adjust the width of the canvas window
        self.chat_container.itemconfig(self.messages_frame_window, width=event.width)

        # Update wraplength for message labels
        new_wrap_length = event.width - 150  # Adjust based on your layout
        for child in self.messages_frame.winfo_children():
            # Assuming the second widget in each child frame is the message label
            if len(child.winfo_children()) > 1:
                message_label = child.winfo_children()[1]
                if isinstance(message_label, tk.Label):
                    message_label.config(wraplength=new_wrap_length)

    def on_submit(self):
        user_input = self.text_input.get("1.0", "end-1c").strip()
        if user_input:
            message_id = len(self.previous_messages)
            self.previous_messages.append({"content": user_input, "role": "user", "id": message_id})

            self.display_message("Buu", user_input, message_id)
            self.text_input.delete("1.0", tk.END)
            request_thread = threading.Thread(target=self.handle_request)
            request_thread.start()

    def handle_request(self):
        response = self.send_request()
        gpt_response = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        self.previous_messages.append({"content": gpt_response, "role": "assistant"})
        
        self.root.after(0, self.display_message, "GPT", gpt_response)
        self.root.after(0, self.enable_input_text)
        
    def enable_input_text(self):
        self.text_input.config(state=tk.NORMAL)

    def send_request(self):
        self.text_input.config(state=tk.DISABLED)
      
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "OpenAI-Organization": self.organization_id
        }
        
        # Transform the messages, excluding any fields not expected by the API
        transformed_messages = [{"role": msg["role"], "content": msg["content"]} for msg in self.previous_messages]

        data = {
            "model": "gpt-4",
            "messages": transformed_messages
        }
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        return response.json()

    def update_submit_button(self, event=None):
        self.submit_button.config(state="normal" if self.text_input.get("1.0", "end-1c").strip() else "disabled")
