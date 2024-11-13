# install the library first -> pip install albumentations opencv-python

import cv2
import albumentations as A
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
        A.RandomSunFlare(p=0.1),
    ], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))

# Augment a single image and its annotations
def augment_image_and_annotations(image_path, annotation_path, save_dir, augmentation_pipeline, num_variations=5):
    # Load image
    image = cv2.imread(image_path)
    base_name = os.path.basename(image_path).split('.')[0]

    # Load annotations
    bboxes = []
    class_labels = []
    if os.path.exists(annotation_path):
        with open(annotation_path, 'r') as f:
            for line in f:
                label, x, y, w, h = map(float, line.strip().split())
                bboxes.append([x, y, w, h])
                class_labels.append(int(label))

    # Generate augmentations
    for i in range(num_variations):
        augmented = augmentation_pipeline(image=image, bboxes=bboxes, class_labels=class_labels)
        augmented_image = augmented['image']
        augmented_bboxes = augmented['bboxes']
        augmented_labels = augmented['class_labels']

        # Save augmented image
        aug_filename = f"{base_name}_aug_{i}.jpg"
        aug_filepath = os.path.join(save_dir, "images", aug_filename)
        cv2.imwrite(aug_filepath, augmented_image)

        # Save updated annotations
        aug_annotation_path = os.path.join(save_dir, "labels", f"{base_name}_aug_{i}.txt")
        with open(aug_annotation_path, 'w') as f:
            for bbox, label in zip(augmented_bboxes, augmented_labels):
                f.write(f"{label} {' '.join(map(str, bbox))}\n")

# Batch process all images and annotations in a directory
def augment_images_and_annotations_in_directory(image_dir, annotation_dir, output_dir, num_variations=5):
    image_output_dir = os.path.join(output_dir, "images")
    annotation_output_dir = os.path.join(output_dir, "labels")
    os.makedirs(image_output_dir, exist_ok=True)
    os.makedirs(annotation_output_dir, exist_ok=True)

    augmentation_pipeline = get_augmentation_pipeline()
    for filename in tqdm(os.listdir(image_dir)):
        image_path = os.path.join(image_dir, filename)
        annotation_path = os.path.join(annotation_dir, filename.replace('.jpg', '.txt'))
        if os.path.isfile(image_path):
            augment_image_and_annotations(image_path, annotation_path, output_dir, augmentation_pipeline, num_variations)

# Folder paths
input_image_directory = "A:/testdata/images"
input_annotation_directory = "A:/testdata/label"
output_directory = "A:/testdata/output"

augment_images_and_annotations_in_directory(input_image_directory, input_annotation_directory, output_directory, num_variations=5)
