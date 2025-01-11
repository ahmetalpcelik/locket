import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import sys

class MinimalImageViewer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        
        # Ana canvas
        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Görüntü değişkenleri
        self.image = None
        self.photo = None
        self.aspect_ratio = 1.0
        self.min_size = 20
        
        # Zoom değişkenleri
        self.zoom_mode = False  # Ctrl tuşu basılı mı?
        self.zoom_factor = 1.0  # Mevcut zoom seviyesi
        self.zoom_min = 1.0     # Minimum zoom
        self.zoom_max = 10.0    # Maximum zoom
        self.pan_x = 0         # Kaydırma koordinatları
        self.pan_y = 0
        
        # Sürükleme değişkenleri
        self.start_x = None
        self.start_y = None
        
        # Olay bağlayıcıları
        self.canvas.bind('<Button-1>', self.start_drag)
        self.canvas.bind('<B1-Motion>', self.drag)
        self.canvas.bind('<Button-3>', self.show_menu)
        self.root.bind('<MouseWheel>', self.on_mousewheel)
        self.root.bind('<Configure>', self.on_resize)
        
        # Ctrl tuşu kontrolü
        self.root.bind('<Control-KeyPress>', self.ctrl_press)
        self.root.bind('<Control-KeyRelease>', self.ctrl_release)
        
        # Sağ tık menüsü
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Resim Seç", command=self.load_image)
        self.menu.add_command(label="Zoom Sıfırla", command=self.reset_zoom)
        self.menu.add_command(label="Kapat", command=self.root.quit)
        
        # Başlangıçta resim seç
        self.load_image()
    
    def ctrl_press(self, event):
        self.zoom_mode = True
        
    def ctrl_release(self, event):
        self.zoom_mode = False
    
    def reset_zoom(self):
        self.zoom_factor = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.update_image()
    
    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Resim Dosyaları", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Tüm Dosyalar", "*.*")
            ]
        )
        
        if file_path:
            self.image = Image.open(file_path)
            self.aspect_ratio = self.image.width / self.image.height
            
            # Zoom değerlerini sıfırla
            self.reset_zoom()
            
            # Başlangıç boyutu
            initial_width = 200
            initial_height = int(initial_width / self.aspect_ratio)
            
            self.root.geometry(f"{initial_width}x{initial_height}")
            self.update_image()
    
    def calculate_dimensions(self, container_width, container_height, image_width, image_height):
        container_ratio = container_width / container_height
        image_ratio = image_width / image_height
        
        if image_ratio > container_ratio:
            new_width = container_width
            new_height = int(container_width / image_ratio)
        else:
            new_height = container_height
            new_width = int(container_height * image_ratio)
            
        return new_width, new_height
    
    def update_image(self):
        if self.image:
            # Pencere boyutlarını al
            container_width = self.root.winfo_width()
            container_height = self.root.winfo_height()
            
            # Temel boyutları hesapla
            base_width, base_height = self.calculate_dimensions(
                container_width, container_height,
                self.image.width, self.image.height
            )
            
            # Zoom uygulanmış boyutlar
            zoom_width = int(base_width * self.zoom_factor)
            zoom_height = int(base_height * self.zoom_factor)
            
            # Resmi yeniden boyutlandır
            resized = self.image.resize((zoom_width, zoom_height), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(resized)
            
            # Canvas'ı temizle ve yeni resmi çiz
            self.canvas.delete("all")
            
            # Resmin konumunu hesapla
            x = (container_width - zoom_width) // 2 + self.pan_x
            y = (container_height - zoom_height) // 2 + self.pan_y
            
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
        if not self.image:
            return
            
        if self.zoom_mode:  # Ctrl basılı, zoom yap
            # Mouse pozisyonunu al
            mouse_x = event.x
            mouse_y = event.y
            
            # Eski zoom faktörü
            old_zoom = self.zoom_factor
            
            # Yeni zoom faktörünü hesapla
            if event.delta > 0:
                self.zoom_factor = min(self.zoom_factor * 1.1, self.zoom_max)
            else:
                self.zoom_factor = max(self.zoom_factor * 0.9, self.zoom_min)
            
            # Zoom merkezini ayarla
            zoom_delta = self.zoom_factor / old_zoom
            
            # Pan değerlerini güncelle
            self.pan_x = mouse_x - (mouse_x - self.pan_x) * zoom_delta
            self.pan_y = mouse_y - (mouse_y - self.pan_y) * zoom_delta
            
            self.update_image()
        else:  # Normal pencere boyutlandırma
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            
            if event.delta > 0:
                width = int(width * 1.1)
                height = int(height * 1.1)
            else:
                width = max(self.min_size, int(width * 0.9))
                height = max(self.min_size, int(width / self.aspect_ratio))
            
            self.root.geometry(f"{width}x{height}")
    
    def on_resize(self, event):
        self.update_image()

def main():
    viewer = MinimalImageViewer()
    viewer.root.mainloop()

if __name__ == "__main__":
    main()