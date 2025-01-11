import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import sys

class MinimalImageViewer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)  # Üst çubuğu kaldır
        self.root.attributes('-topmost', True)  # Her zaman üstte
        
        # Ana canvas
        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Görüntü değişkenleri
        self.image = None
        self.photo = None
        self.aspect_ratio = 1.0
        self.min_size = 20  # Minimum pencere boyutu (piksel)
        
        # Sürükleme değişkenleri
        self.start_x = None
        self.start_y = None
        
        # Olay bağlayıcıları
        self.canvas.bind('<Button-1>', self.start_drag)
        self.canvas.bind('<B1-Motion>', self.drag)
        self.canvas.bind('<Button-3>', self.show_menu)  # Sağ tık menüsü
        self.root.bind('<MouseWheel>', self.on_mousewheel)  # Mouse tekerleği ile boyutlandırma
        self.root.bind('<Configure>', self.on_resize)  # Pencere boyutu değişince
        
        # Sağ tık menüsü
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Resim Seç", command=self.load_image)
        self.menu.add_command(label="Kapat", command=self.root.quit)
        
        # Başlangıçta resim seç
        self.load_image()
        
    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Resim Dosyaları", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Tüm Dosyalar", "*.*")
            ]
        )
        
        if file_path:
            # Resmi yükle
            self.image = Image.open(file_path)
            self.aspect_ratio = self.image.width / self.image.height
            
            # Başlangıç boyutu
            initial_width = 200
            initial_height = int(initial_width / self.aspect_ratio)
            
            self.root.geometry(f"{initial_width}x{initial_height}")
            self.update_image()
    
    def calculate_dimensions(self, container_width, container_height, image_width, image_height):
        """Resmin tam sığması için boyutları hesapla"""
        container_ratio = container_width / container_height
        image_ratio = image_width / image_height
        
        if image_ratio > container_ratio:
            # Resim daha geniş, genişliğe göre ölçekle
            new_width = container_width
            new_height = int(container_width / image_ratio)
        else:
            # Resim daha uzun, yüksekliğe göre ölçekle
            new_height = container_height
            new_width = int(container_height * image_ratio)
            
        return new_width, new_height
    
    def update_image(self):
        if self.image:
            # Mevcut pencere boyutunu al
            container_width = self.root.winfo_width()
            container_height = self.root.winfo_height()
            
            # Resmin tam sığması için boyutları hesapla
            width, height = self.calculate_dimensions(
                container_width, container_height,
                self.image.width, self.image.height
            )
            
            # Resmi yeniden boyutlandır
            resized = self.image.resize((width, height), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(resized)
            
            # Canvas'ı temizle ve yeni resmi ortala
            self.canvas.delete("all")
            x = (container_width - width) // 2
            y = (container_height - height) // 2
            self.canvas.create_image(x, y, image=self.photo, anchor='nw')
    
    def start_drag(self, event):
        self.start_x = event.x_root - self.root.winfo_x()
        self.start_y = event.y_root - self.root.winfo_y()
    
    def drag(self, event):
        if self.start_x is not None and self.start_y is not None:
            x = event.x_root - self.start_x
            y = event.y_root - self.start_y
            self.root.geometry(f"+{x}+{y}")
    
    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)
    
    def on_mousewheel(self, event):
        if self.image:
            # Mevcut boyutları al
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            
            # Mouse tekerleği yukarı = büyüt, aşağı = küçült
            if event.delta > 0:
                width = int(width * 1.1)
                height = int(height * 1.1)
            else:
                width = max(self.min_size, int(width * 0.9))
                height = max(self.min_size, int(width / self.aspect_ratio))
            
            self.root.geometry(f"{width}x{height}")
    
    def on_resize(self, event):
        """Pencere boyutu değiştiğinde resmi güncelle"""
        self.update_image()

def main():
    viewer = MinimalImageViewer()
    viewer.root.mainloop()

if __name__ == "__main__":
    main()
