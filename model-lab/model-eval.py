import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import cv2
import numpy as np
from ultralytics import YOLO
import os

class YOLODetectionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YOLO11 Object Detection")
        self.root.geometry("1000x700")
        
        # Initialize model
        self.model = None
        self.current_image = None
        self.current_image_path = None
        
        self.setup_ui()
        self.load_model()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Control panel
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Buttons
        ttk.Button(control_frame, text="Select Image", command=self.select_image).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="Detect Objects", command=self.detect_objects).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="Clear", command=self.clear_results).pack(side=tk.LEFT)
        
        # Model status
        self.status_label = ttk.Label(control_frame, text="Loading model...")
        self.status_label.pack(side=tk.RIGHT)
        
        # Image display
        self.image_frame = ttk.Frame(main_frame, relief=tk.SUNKEN, borderwidth=2)
        self.image_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        self.image_label = ttk.Label(self.image_frame, text="No image selected", anchor=tk.CENTER)
        self.image_label.pack(expand=True, fill=tk.BOTH)
        
        # Results panel
        results_frame = ttk.Frame(main_frame)
        results_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(results_frame, text="Detection Results:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        # Results listbox with scrollbar
        list_frame = ttk.Frame(results_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Courier", 10))
        self.results_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.results_listbox.yview)
        
        # Confidence threshold
        threshold_frame = ttk.Frame(results_frame)
        threshold_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(threshold_frame, text="Confidence Threshold:").pack(side=tk.LEFT)
        self.confidence_var = tk.DoubleVar(value=0.5)
        self.confidence_scale = ttk.Scale(threshold_frame, from_=0.1, to=1.0, 
                                        variable=self.confidence_var, orient=tk.HORIZONTAL)
        self.confidence_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        
        self.confidence_label = ttk.Label(threshold_frame, text="0.50")
        self.confidence_label.pack(side=tk.RIGHT)
        
        # Update confidence label
        self.confidence_var.trace('w', self.update_confidence_label)
    
    def load_model(self):
        """Load the YOLO model by letting user select the file"""
        try:
            # File dialog to select model file
            filetypes = [
                ("Engine files", "*.engine"),
                ("PyTorch files", "*.pt"),
                ("ONNX files", "*.onnx"),
                ("All files", "*.*")
            ]
            
            model_path = filedialog.askopenfilename(
                title="Select YOLO model file",
                filetypes=filetypes,
                initialdir="yolo11"  # Start in yolo11 folder if it exists
            )
            
            if not model_path:
                self.status_label.config(text="No model selected - please restart and select a model")
                messagebox.showwarning("Warning", "No model file selected. Please restart the application and select a model file.")
                return
            
            self.model = YOLO(model_path)
            model_name = os.path.basename(model_path)
            self.status_label.config(text=f"Model loaded: {model_name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load model: {str(e)}")
            self.status_label.config(text="Model loading failed")
    
    def select_image(self):
        """Open file dialog to select an image"""
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("PNG files", "*.png"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=filetypes
        )
        
        if file_path:
            self.current_image_path = file_path
            self.display_image(file_path)
            self.clear_results()
    
    def display_image(self, image_path, results=None):
        """Display the selected image in the GUI"""
        try:
            # Open and resize image for display
            image = Image.open(image_path)
            self.current_image = image.copy()
            
            # Calculate display size (max 400x400)
            display_size = (400, 400)
            image.thumbnail(display_size, Image.Resampling.LANCZOS)
            
            # If results are provided, draw bounding boxes
            if results:
                image = self.draw_detections(image, results, image_path)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Update label
            self.image_label.config(image=photo, text="")
            self.image_label.image = photo  # Keep a reference
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display image: {str(e)}")
    
    def draw_detections(self, display_image, results, original_image_path):
        """Draw bounding boxes and labels on the image"""
        try:
            # Get original image dimensions
            original_image = Image.open(original_image_path)
            orig_width, orig_height = original_image.size
            disp_width, disp_height = display_image.size
            
            # Calculate scaling factors
            scale_x = disp_width / orig_width
            scale_y = disp_height / orig_height
            
            draw = ImageDraw.Draw(display_image)
            
            # Try to load a font
            try:
                font = ImageFont.truetype("arial.ttf", 12)
            except Exception:
                font = ImageFont.load_default()
            
            # Draw bounding boxes
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get box coordinates and scale them
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        x1, y1, x2, y2 = int(x1 * scale_x), int(y1 * scale_y), int(x2 * scale_x), int(y2 * scale_y)
                        
                        # Get confidence and class
                        confidence = box.conf[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())
                        class_name = self.model.names[class_id]
                        
                        # Only draw if confidence is above threshold
                        if confidence >= self.confidence_var.get():
                            # Draw rectangle
                            draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
                            
                            # Draw label
                            label = f"{class_name}: {confidence:.2f}"
                            draw.text((x1, y1 - 15), label, fill="red", font=font)
            
            return display_image
            
        except Exception as e:
            print(f"Error drawing detections: {e}")
            return display_image
    
    def detect_objects(self):
        """Run YOLO detection on the selected image"""
        if not self.model:
            messagebox.showerror("Error", "Model not loaded")
            return
        
        if not self.current_image_path:
            messagebox.showerror("Error", "No image selected")
            return
        
        try:
            # Run inference
            results = self.model(self.current_image_path, conf=self.confidence_var.get())
            
            # Display results
            self.display_results(results)
            
            # Update image with bounding boxes
            self.display_image(self.current_image_path, results)
            
        except Exception as e:
            messagebox.showerror("Error", f"Detection failed: {str(e)}")
    
    def display_results(self, results):
        """Display detection results in the listbox"""
        self.results_listbox.delete(0, tk.END)
        
        total_detections = 0
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    confidence = box.conf[0].cpu().numpy()
                    class_id = int(box.cls[0].cpu().numpy())
                    class_name = self.model.names[class_id]
                    
                    if confidence >= self.confidence_var.get():
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        
                        result_text = f"{class_name:<15} {confidence:.3f} [{int(x1)},{int(y1)},{int(x2)},{int(y2)}]"
                        self.results_listbox.insert(tk.END, result_text)
                        total_detections += 1
        
        if total_detections == 0:
            self.results_listbox.insert(tk.END, "No objects detected above threshold")
        else:
            self.results_listbox.insert(0, f"--- {total_detections} objects detected ---")
    
    def clear_results(self):
        """Clear the results listbox"""
        self.results_listbox.delete(0, tk.END)
        if self.current_image_path:
            self.display_image(self.current_image_path)
    
    def update_confidence_label(self, *args):
        """Update the confidence threshold label"""
        self.confidence_label.config(text=f"{self.confidence_var.get():.2f}")

def main():
    root = tk.Tk()
    YOLODetectionGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
