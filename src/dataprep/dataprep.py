import cv2
import numpy as np
import random
import os
import argparse


def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    # add arguments
    parser.add_argument("--input_folder", type=str)
    parser.add_argument("--output_folder", type=str)
    parser.add_argument("--run_mode", type=str, default="local")

    # parse args
    args = parser.parse_args()

    # return args
    return args



# Random cropping function
def random_crop(img, crop_size):
    h, w = img.shape[:2]
    y = 500 # random.randint(100, h - crop_size[0])
    x = 500 #random.randint(100, w - crop_size[1])
    return img[y:y+crop_size[0], x:x+crop_size[1]]

def center_crop(img, crop_size):
    h, w = img.shape[:2]
    y = (h - crop_size[0]) // 2
    x = (w - crop_size[1]) // 2
    return img[y:y+crop_size[0], x:x+crop_size[1]]

# Data augmentation functions
def random_flip(img):
    flip_code = random.choice([-1, 0, 1])  # -1: both axes, 0: vertical, 1: horizontal
    return cv2.flip(img, flip_code)

def random_rotation(img):
    angle = random.uniform(-35, 85)
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1)
    return cv2.warpAffine(img, M, (w, h))

def random_brightness_contrast(img):
    brightness = random.uniform(0.5, 1.5)
    contrast = random.uniform(0.5, 1.5)
    dummy = np.int16(img)
    dummy = dummy * contrast + brightness * 127
    dummy = np.clip(dummy, 0, 255)
    return np.uint8(dummy)

def resize_image(img, dimension):
   
    # Resize the image
    resized_img = cv2.resize(img, dimension, interpolation=cv2.INTER_AREA)
    return resized_img
    

def start_dataprep(input_folder, output_folder):
    # Load existing images
    image_files = [f for f in os.listdir(input_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]

    for set in range (1, 2):
        for img_file in image_files:
            img_path = os.path.join(input_folder, img_file)
            img = cv2.imread(img_path)

            # Random cropping
            #cropped = random_crop(img, (500, 700))  # Assuming you want 100x100 crops
            cropped = resize_image(img, (700, 700))
            output_path = os.path.join(output_folder, f'set{set}_cropped_augmented_{img_file}')
            cv2.imwrite(output_path, cropped)
            # Apply other augmentations
            #flipped = random_flip(cropped)
            #output_path = os.path.join(output_dir, f'set{set}_flipped_augmented_{img_file}')
            #cv2.imwrite(output_path, flipped)
            #rotated = random_rotation(cropped)
            #output_path = os.path.join(output_dir, f'set{set}_rotated_augmented_{img_file}')
            #cv2.imwrite(output_path, rotated)
            #adjusted = random_brightness_contrast(rotated)

            # Save the result
            #output_path = os.path.join(output_dir, f'augmented_{img_file}')
            #cv2.imwrite(output_path, rotated)


def main(args):
    start_dataprep(args.input_folder, args.output_folder)


# run script
if __name__ == "__main__":
    # parse args
    args = parse_args()

    # run main function
    main(args)