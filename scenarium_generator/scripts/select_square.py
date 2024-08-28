import gdal
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import RectangleSelector, Button, TextBox
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d import Axes3D
import rasterio
from rasterio.windows import Window
import os

def visualize_large_tif(file_path, downsampling_factor=1000):
    dataset = gdal.Open(file_path)
    
    if dataset is None:
        print("Erro ao abrir o arquivo.")
        return None, None
    
    num_bands = dataset.RasterCount
    width = dataset.RasterXSize
    height = dataset.RasterYSize
    
    new_width = width // downsampling_factor
    new_height = height // downsampling_factor
    
    img = np.zeros((new_height, new_width, num_bands), dtype=np.float32)
    
    for i in range(num_bands):
        band = dataset.GetRasterBand(i + 1)
        band_data = band.ReadAsArray(buf_xsize=new_width, buf_ysize=new_height)
        img[:, :, i] = band_data
    
    img = (img - np.min(img)) / (np.max(img) - np.min(img))
    
    if num_bands > 3:
        img = img[:, :, :3]
    
    return img, (width, height)

def read_tif_section(tif_path, xoff, yoff, xsize, ysize):
    dataset = gdal.Open(tif_path, gdal.GA_ReadOnly)
    if dataset is None:
        print(f"Unable to open {tif_path}")
        return None
    
    band = dataset.GetRasterBand(1)
    data = band.ReadAsArray(xoff, yoff, xsize, ysize)
    return data

def visualize_tif(data, ax2d, ax3d):
    ax2d.clear()
    ax3d.clear()

    ax2d.imshow(data, cmap='gray')
    ax2d.set_title('2D Visualization')
    ax2d.axis('off')

    x = np.linspace(0, data.shape[1] - 1, data.shape[1])
    y = np.linspace(0, data.shape[0] - 1, data.shape[0])
    x, y = np.meshgrid(x, y)
    ax3d.plot_surface(y, x, data, cmap='terrain')
    ax3d.set_title('3D Visualization')
    ax3d.set_xlabel('Y')
    ax3d.set_ylabel('X')
    ax3d.set_zlabel('Altitude')

    plt.draw()

def save_section(input_path, output_path, x, y, square_fraction, img_width):
    window_size = int(square_fraction * img_width)
    x1_orig = max(0, x - window_size // 2)
    y1_orig = max(0, y - window_size // 2)

    with rasterio.open(input_path) as src:
        window = Window(x1_orig, y1_orig, window_size, window_size)
        data = src.read(window=window)

        transform = src.window_transform(window)
        metadata = src.meta
        metadata.update({
            'height': window.height,
            'width': window.width,
            'transform': transform
        })

        with rasterio.open(output_path, 'w', **metadata) as dst:
            dst.write(data)
        print(f"Image saved as {output_path}")

def main(file_path, downsampling_factor=1000, square_fraction=0.005):
    img, orig_dims = visualize_large_tif(file_path, downsampling_factor)
    img_width, img_height = orig_dims
    square_size = int(img_width * square_fraction)

    fig = plt.figure(figsize=(18, 8))  
    fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.25)  

    ax_main = fig.add_subplot(1, 3, 1)
    ax2d = fig.add_subplot(1, 3, 2)
    ax3d = fig.add_subplot(1, 3, 3, projection='3d')

    im = ax_main.imshow(img)
    ax_main.set_title("Downsampled Image")
    ax_main.axis('off')

    initial_x = (img.shape[1] - square_size // downsampling_factor) // 2
    initial_y = (img.shape[0] - square_size // downsampling_factor) // 2
    rect = Rectangle((initial_x, initial_y), square_size // downsampling_factor, square_size // downsampling_factor, linewidth=1, edgecolor='red', facecolor='none')
    ax_main.add_patch(rect)

    def update_visualizations():
        x1, y1 = rect.get_xy()
        x1_orig = int(x1 * downsampling_factor)
        y1_orig = int(y1 * downsampling_factor)

        tif_data = read_tif_section(file_path, x1_orig, y1_orig, square_size, square_size)
        if tif_data is not None:
            visualize_tif(tif_data, ax2d, ax3d)

        plt.draw()

    def on_click(event):
        if event.inaxes == ax_main:
            x1, y1 = event.xdata, event.ydata
            rect.set_xy((x1 - rect.get_width() / 2, y1 - rect.get_height() / 2))
            rect.set_visible(True)
            update_visualizations()

    def update_square_size(text):
        nonlocal square_size
        try:
            new_fraction = float(text)
            if new_fraction > 0:
                square_size = int(img_width * new_fraction)
                rect.set_width(square_size // downsampling_factor)
                rect.set_height(square_size // downsampling_factor)
                update_visualizations()
        except ValueError:
            print("Please insert a valid number.")

    def save_button_callback(event):
        x1, y1 = rect.get_xy()
        x1_orig = int(x1 * downsampling_factor)
        y1_orig = int(y1 * downsampling_factor)
        output_file = "../cropped_tifs/" + text_box_filename.text
        #save_section(file_path, x1_orig, y1_orig, square_size, square_size, output_file)
        save_section(file_path, output_file, x1_orig, y1_orig, square_fraction, img_width)

    cid_click = fig.canvas.mpl_connect('button_press_event', on_click)

    axbox = plt.axes([0.15, 0.1, 0.1, 0.05])
    text_box = TextBox(axbox, 'Square Size Fraction:', initial=str(square_fraction))
    text_box.on_submit(update_square_size)

    axbox_filename = plt.axes([0.45, 0.1, 0.2, 0.05])
    text_box_filename = TextBox(axbox_filename, 'Output Filename:', initial="output_cropped_image.tif")

    ax_save = plt.axes([0.27, 0.1, 0.1, 0.05])
    save_button = Button(ax_save, 'Save Image')
    save_button.on_clicked(save_button_callback)

    plt.show()

# Caminho para o arquivo .tif
file_path = '/home/lucca/nasa/space-ros-docker/scenarium_generator/curiosity_hirise_mosaic.tif'

# Executar o script principal com 0.5% da largura como o tamanho do quadrado
main(file_path, downsampling_factor=1000, square_fraction=0.005)