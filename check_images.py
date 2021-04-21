from PIL import Image
from pathlib import Path


def main():
    data_dir = Path("data-large/guitar-jpg")
    for image_path in data_dir.glob("*"):
        im = Image.open(image_path)
        if im.mode != "RGB":
            raise ValueError(f"image {image_path} has mode {im.mode}")


if __name__ == '__main__':
    main()
