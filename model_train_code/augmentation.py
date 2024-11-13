# install the library first-> pip install albumentations opencv-python

import cv2
import albumentations as A
from albumentations.pytorch import ToTensorV2
import numpy as np
import os
from tqdm import tqdm

# Define augmentation pipeline
def get_augmentation_pipeline():
    return A.Compose([
        A.RandomCrop(width=2560, height=2560),   # Randomly crop to reduce original size slightly
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.5),
        A.RandomRotate90(p=0.5),
        A.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1, p=0.5),
        A.GaussianBlur(blur_limit=(3, 7), p=0.3),
        A.MotionBlur(blur_limit=7, p=0.3),
        A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.5),
        A.HueSaturationValue(hue_shift_limit=20, sat_shift_limit=30, val_shift_limit=20, p=0.5),
        A.RandomShadow(p=0.2),
        A.RandomRain(p=0.1),
        A.RandomSnow(p=0.1),
        A.RandomFog(p=0.1),
        A.RandomSunFlare(p=0.1)
    ])

# Augment a single image
def augment_image(image_path, save_dir, augmentation_pipeline, num_variations=5):
    # Load image
    image = cv2.imread(image_path)
    base_name = os.path.basename(image_path).split('.')[0]

    # Generate augmentations
    for i in range(num_variations):
        augmented = augmentation_pipeline(image=image)['image']
        
        # Convert tensor back to NumPy if needed
        if isinstance(augmented, np.ndarray):
            augmented_np = augmented
        else:
            augmented_np = augmented.permute(1, 2, 0).cpu().numpy()
            augmented_np = (augmented_np * 255).astype(np.uint8)

        aug_filename = f"{base_name}_aug_{i}.jpg"
        aug_filepath = os.path.join(save_dir, aug_filename)
        cv2.imwrite(aug_filepath, augmented_np)
        print(f"Saved augmented image: {aug_filepath}")

# Batch process all images in a directory
def augment_images_in_directory(input_dir, output_dir, num_variations=5):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    augmentation_pipeline = get_augmentation_pipeline()
    for filename in tqdm(os.listdir(input_dir)):
        file_path = os.path.join(input_dir, filename)
        if os.path.isfile(file_path):
            augment_image(file_path, output_dir, augmentation_pipeline, num_variations)

# folder paths
input_directory = "A:/cropdetector/data/images/train" #thic folder contains the original images
output_directory = "A:/cropdetector/augmente_images"  #this is where the augmented images will export
augment_images_in_directory(input_directory, output_directory, num_variations=5) # 5 variations of each images will be created (change according to you)
