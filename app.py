import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np
from tkinter import ttk
import os

class VideoWatermarker:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Watermarker")
        self.root.geometry("800x600")

        self.video_path = ""
        self.watermark_path = ""
        self.watermark_position = tk.StringVar(value="Top Left")

        self.create_widgets()

    def create_widgets(self):
       # Dark mode style
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.root.configure(bg="gray10")  # Set background color

        # Video thumbnail
        self.video_thumbnail = tk.Label(self.root, bg="gray10")
        self.video_thumbnail.pack(pady=10)

        # Select video button
        self.video_button = ttk.Button(self.root, text="Select Video/Image", command=self.select_input)
        self.video_button.pack(pady=10)

        # Watermark image options
        self.watermark_label = tk.Label(self.root, text="Select Watermark Image:", bg="gray10", fg="white")
        self.watermark_label.pack()

        self.white_watermark = Image.open("white.png")
        self.white_watermark = self.white_watermark.resize((100, 40))
        self.white_watermark_photo = ImageTk.PhotoImage(self.white_watermark)

        self.blue_watermark = Image.open("blue.png")
        self.blue_watermark = self.blue_watermark.resize((100, 40))
        self.blue_watermark_photo = ImageTk.PhotoImage(self.blue_watermark)

        self.white_watermark_button = ttk.Button(
            self.root, image=self.white_watermark_photo, command=lambda: self.select_watermark("white"),
            style="RoundedButton.TButton"  # Apply custom style
        )
        self.white_watermark_button.pack()

        self.blue_watermark_button = ttk.Button(
            self.root, image=self.blue_watermark_photo, command=lambda: self.select_watermark("blue"),
            style="RoundedButton.TButton"  # Apply custom style
        )
        self.blue_watermark_button.pack()

        # Watermark position options
        self.position_label = tk.Label(self.root, text="Select Watermark Position:", bg="gray10", fg="white")
        self.position_label.pack()

        positions = ["Top Left", "Top Right", "Bottom Left", "Bottom Right"]
        for position in positions:
            ttk.Radiobutton(self.root, text=position, variable=self.watermark_position, value=position, style="Dark.TRadiobutton").pack()

        # Apply watermark button
        self.apply_button = ttk.Button(self.root, text="Apply Watermark", command=self.apply_watermark, style="Dark.TButton")
        self.apply_button.pack(pady=10)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100, style="Dark.Horizontal.TProgressbar")
        self.progress.pack(fill='x', pady=10)

        # Done text
        self.done_text = tk.Label(self.root, text="", font=("Helvetica", 20), bg="gray10", fg="white")
        self.done_text.pack()

        # Dark mode style configurations
        self.style.configure("TButton", background="gray30", foreground="white")
        self.style.configure("TRadiobutton", background="gray10", foreground="white")
        self.style.configure("Horizontal.TProgressbar", background="gray20", troughcolor="gray10", bordercolor="gray10")
        self.style.configure("Dark.TButton", background="gray30", foreground="white")
        self.style.configure("Dark.TRadiobutton", background="gray10", foreground="white")
        self.style.configure("Dark.Horizontal.TProgressbar", background="green", troughcolor="gray10", bordercolor="gray10")

        # Rounded button style
        self.style.configure("RoundedButton.TButton", background="gray30", foreground="white", borderwidth=0)
        self.root.option_add("*TButton*highlightThickness", 0)  # Remove the highlight thickness

    def select_input(self):
        self.input_path = filedialog.askopenfilename(filetypes=[("Video/Image Files", "*.mp4 *.avi *.mkv *.jpg *.png")])
        if self.input_path:
            if self.input_path.lower().endswith(('.jpg', '.png')):
                self.update_image_thumbnail()
            else:
                self.update_video_thumbnail()
                
    def update_image_thumbnail(self):
        image = Image.open(self.input_path)
        image.thumbnail((200, 200))
        self.video_thumbnail.image = ImageTk.PhotoImage(image)
        self.video_thumbnail.configure(image=self.video_thumbnail.image)


    def update_video_thumbnail(self):
        cap = cv2.VideoCapture(self.input_path)
        ret, frame = cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_pil = Image.fromarray(frame_rgb)
            frame_pil.thumbnail((200, 200))
            self.video_thumbnail.image = ImageTk.PhotoImage(frame_pil)
            self.video_thumbnail.configure(image=self.video_thumbnail.image)


    def select_watermark(self, color):
        self.watermark_path = f"{color}.png"

    def apply_watermark(self):
        if not self.input_path or not self.watermark_path:
            return
        
        self.progress_var.set(0)
        self.done_text.config(text="")
        
        if self.input_path.lower().endswith(('.jpg', '.png')):
            self.add_watermark_image(self.input_path, self.watermark_path, self.watermark_position.get())
        else:
            self.add_watermark_video(self.input_path, self.watermark_path, self.watermark_position.get())

    def add_watermark_image(self, image_path, watermark_path, position):
        image = Image.open(image_path)
        watermark = Image.open(watermark_path)

        watermark_position = self.get_watermark_position(image, watermark, position)
        image_with_watermark = self.apply_single_watermark(image, watermark, watermark_position)

        output_path = "ETiK_" + image_path.split("/")[-1]
        output_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=output_path,
            filetypes=[("Image Files", "*.png")]
        )
        
        image_with_watermark.save(output_path)
        self.progress_var.set(100)
        self.done_text.config(text="Done!")

    def add_watermark_video(self, video_path, watermark_path, position):
        cap = cv2.VideoCapture(video_path)
        watermark = Image.open(watermark_path)

        output_path = "ETiK_" + video_path.split("/")[-1]
        output_path = filedialog.asksaveasfilename(
            defaultextension=".avi",
            initialfile=output_path,
            filetypes=[("Video Files", "*.avi")]
        )
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_pil = Image.fromarray(frame_rgb)

            watermark_position = self.get_watermark_position(frame_pil, watermark, position)
            frame_with_watermark = self.apply_single_watermark(frame_pil, watermark, watermark_position)

            frame_with_watermark_cv = cv2.cvtColor(np.array(frame_with_watermark), cv2.COLOR_RGB2BGR)
            out.write(frame_with_watermark_cv)

            # Update progress bar
            current_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
            progress_percent = (current_frame / frame_count) * 100
            self.progress_var.set(progress_percent)
            self.root.update_idletasks()
        
        cap.release()
        out.release()
        
        self.progress_var.set(100)  # Set progress to 100%
        self.done_text.config(text="Done!")  # Show "Done" text
        
        
        
        if not output_path:
            return

        print(f"Watermarked video saved as {output_path}")
        
        self.progress_var.set(0)
        self.done_text.config(text="")
        
        
    def get_watermark_position(self, frame, watermark, position):
        frame_width, frame_height = frame.size
        watermark_width, watermark_height = watermark.size

        if position == "Top Right":
            return (frame_width - watermark_width, 95)
        elif position == "Bottom Left":
            return (95, frame_height - watermark_height)
        elif position == "Bottom Right":
            return (frame_width - watermark_width, frame_height - watermark_height)
        else:  # Default to Top Left
            return (95, 95)

    def apply_single_watermark(self, frame, watermark, position):
        frame.paste(watermark, position, watermark)
        return frame

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoWatermarker(root)
    root.mainloop()
