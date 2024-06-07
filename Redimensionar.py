from PIL import Image, ImageFile
import os
import tkinter as tk
from tkinter import filedialog, Button, ttk, simpledialog, messagebox, Radiobutton, IntVar

# Configurações PIL para lidar com imagens grandes e truncadas
Image.MAX_IMAGE_PIXELS = None
ImageFile.LOAD_TRUNCATED_IMAGES = True

class ImageResizer:
    def __init__(self, root):
        self.root = root
        self.source_folder_button = None
        self.destination_folder_button = None
        self.source_folder = ""
        self.destination_folder = ""
        self.target_width = None
        self.target_height = None
        self.proportional = IntVar(value=0)  # Radio button state

        self.setup_ui()

    def setup_ui(self):
        self.root.title("Redimensionador de Imagens")
        self.root.geometry("400x400")  # Adjusted to include radio buttons

        # Buttons to select source and destination folders
        self.source_folder_button = Button(self.root, text="Selecionar Pasta de Origem", command=self.select_source_folder)
        self.source_folder_button.pack(pady=10)
        self.destination_folder_button = Button(self.root, text="Selecionar Pasta de Destino", command=self.select_destination_folder)
        self.destination_folder_button.pack(pady=10)

        # Options for resizing
        Button(self.root, text="Definir Dimensões Específicas", command=self.set_specific_dimensions).pack(pady=10)
        Button(self.root, text="Redimensionar pelo Lado Maior", command=lambda: self.resize_by_side(use_larger_side=True)).pack(pady=5)
        Button(self.root, text="Redimensionar pelo Lado Menor", command=lambda: self.resize_by_side(use_larger_side=False)).pack(pady=5)

        # Radio buttons for choosing resize mode
        Radiobutton(self.root, text="Redimensionar Proporcionalmente", variable=self.proportional, value=1).pack()
        Radiobutton(self.root, text="Manter Dimensões Originais", variable=self.proportional, value=0).pack()

        # Progress bar
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=300, mode='determinate')
        self.progress.pack(pady=10)

        # Button to start resizing
        Button(self.root, text="Iniciar Redimensionamento", command=self.start_resizing).pack(pady=20)

    def select_source_folder(self):
        folder = filedialog.askdirectory(title="Selecione a pasta de origem")
        if folder:
            self.source_folder = folder
            self.source_folder_button.config(text=os.path.basename(folder))

    def select_destination_folder(self):
        folder = filedialog.askdirectory(title="Selecione a pasta de destino")
        if folder:
            self.destination_folder = folder
            self.destination_folder_button.config(text=os.path.basename(folder))

    def set_specific_dimensions(self):
        width = simpledialog.askstring("Largura", "Digite a largura desejada (opcional):", parent=self.root)
        height = simpledialog.askstring("Altura", "Digite a altura desejada (opcional):", parent=self.root)
        try:
            self.target_width = int(float(width)) if width.strip() else None
            self.target_height = int(float(height)) if height.strip() else None
        except ValueError:
            messagebox.showerror("Erro de Entrada", "Por favor, insira um número válido.")

    def resize_by_side(self, use_larger_side):
        size = simpledialog.askstring("Tamanho", f"Digite o tamanho desejado para o {'lado maior' if use_larger_side else 'lado menor'}:", parent=self.root)
        try:
            if size:
                self.target_size = int(float(size))
                if use_larger_side:
                    self.target_width = self.target_size
                    self.target_height = None
                else:
                    self.target_width = None
                    self.target_height = self.target_size
        except ValueError:
            messagebox.showerror("Erro de Entrada", "Por favor, insira um número válido.")

    def start_resizing(self):
        if not self.source_folder or not self.destination_folder:
            print("Por favor, selecione as pastas antes de redimensionar.")
            return

        self.resize_images()

    def resize_images(self):
        image_files = [f for f in os.listdir(self.source_folder) if f.endswith((".png", ".jpg", ".jpeg"))]
        total_images = len(image_files)
        self.progress['maximum'] = total_images
        os.makedirs(self.destination_folder, exist_ok=True)

        for index, filename in enumerate(image_files):
            image_path = os.path.join(self.source_folder, filename)
            try:
                with Image.open(image_path) as img:
                    original_width, original_height = img.size
                    new_width = self.target_width if self.target_width is not None else original_width
                    new_height = self.target_height if self.target_height is not None else original_height

                    if self.proportional.get() == 1 and (self.target_width or self.target_height):
                        # Calculate scale factors and apply proportionally
                        if self.target_width and not self.target_height:
                            scale_factor = self.target_width / original_width
                            new_height = int(original_height * scale_factor)
                        elif self.target_height and not self.target_width:
                            scale_factor = self.target_height / original_height
                            new_width = int(original_width * scale_factor)

                    new_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    new_img.save(os.path.join(self.destination_folder, filename))

                    self.progress['value'] = index + 1
                    self.root.update_idletasks()
            except Exception as e:
                print(f"Erro ao processar {filename}: {e}")

        print("Redimensionamento concluído!")
        self.reset_settings()

    def reset_settings(self):
        self.target_width = None
        self.target_height = None
        print("Configurações resetadas.")

# Start the application
root = tk.Tk()
app = ImageResizer(root)
root.mainloop()
