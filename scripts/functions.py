"""
import subprocess
import sys

modules = ['ultralytics', 'supervision', 'gdown', 'pytube', 'openai']

for module in modules:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', module])
"""

from pytube import YouTube
import os

import cv2
import math
import json
import copy
import base64
import requests

import numpy as np
import pandas as pd
import supervision as sv

from tqdm.notebook import tqdm
from ultralytics import YOLO
from typing import List, Optional, Dict, Iterator, Tuple

def single_video_download(path, url):
    try:
        os.makedirs(path, exist_ok=True)

        yt = YouTube(url)

        video = yt.streams.filter(progressive=True, file_extension='mp4', res="720p").first()

        if not video:
            video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

        if video:
            video.download(output_path=path)

            print(f"Downloaded {yt.title} at {video.resolution} successfully")


        else:
            print(f"No video available for {url}")

    except Exception as e:
        print(f"Failed to download {url}: {str(e)}")


COLOR_HEX_LIST = [
    "#EE4B2B",
    "#FFFF00",
    "#D3D3D3"
]


def annotate_prompt(
    image: np.ndarray,
    detections: sv.Detections,
    labels: Optional[List[str]] = None
) -> np.ndarray:
    """
    Annotates an image with bounding boxes and labels based on provided detections.

    Parameters:
        image (np.ndarray): The image to be annotated. It should be in a format compatible with sv.BoundingBoxAnnotator
            and sv.LabelAnnotator, typically a NumPy array.
        detections (sv.Detections): A collection of detections, each typically containing information like
            bounding box coordinates, class IDs, etc., to be used for annotation.
        labels (Optional[List[str]]): A list of strings representing the labels for each detection. If not
            provided, labels are automatically generated as sequential numbers.

    Returns:
        np.ndarray: An annotated version of the input image, with bounding boxes and labels drawn over it.

    """
    bounding_box_annotator = sv.BoundingBoxAnnotator(
        color=sv.Color.black(),
        color_lookup=sv.ColorLookup.CLASS)
    label_annotator = sv.LabelAnnotator(
        color=sv.Color.black(),
        text_color=sv.Color.white(),
        color_lookup=sv.ColorLookup.CLASS,
        text_scale=0.7)

    if labels is None:
        labels = [str(i) for i in range(len(detections))]

    annotated_image = image.copy()
    annotated_image = bounding_box_annotator.annotate(
        annotated_image, detections=detections)
    annotated_image = label_annotator.annotate(
        annotated_image, detections=detections, labels=labels)

    return annotated_image


def annotate_result(
    image: np.ndarray,
    detections: sv.Detections
) -> np.ndarray:
    """
    Annotates a given image with ellipses around detected objects.

    Parameters:
        image (np.ndarray): The image to be annotated. It should be in the format
            acceptable by sv.EllipseAnnotator.
        detections (sv.Detections): An object of sv.Detections, which contains
            the detected objects' information to be annotated on the image.

    Returns:
        np.ndarray: An image (numpy array) with ellipses drawn around the detected
            objects. This image is a modified copy of the input image.
    """
    h, w, _ = image.shape
    text_scale = sv.calculate_dynamic_text_scale(resolution_wh=(w, h))
    text_scale = min(text_scale, 0.8)
    line_thickness = sv.calculate_dynamic_line_thickness(resolution_wh=(w, h))
    ellipse_annotator = sv.EllipseAnnotator(
        color=sv.ColorPalette.from_hex(color_hex_list=COLOR_HEX_LIST),
        color_lookup=sv.ColorLookup.CLASS,
        thickness=line_thickness)
    label_annotator = sv.LabelAnnotator(
        color=sv.ColorPalette.from_hex(color_hex_list=COLOR_HEX_LIST),
        text_color=sv.Color.black(),
        color_lookup=sv.ColorLookup.CLASS,
        text_position=sv.Position.BOTTOM_CENTER,
        text_scale=text_scale)

    labels = [f"#{tracker_id}" for tracker_id in detections.tracker_id]

    annotated_image = image.copy()
    annotated_image = ellipse_annotator.annotate(
        annotated_image, detections)
    annotated_image = label_annotator.annotate(
        annotated_image, detections, labels=labels)
    return annotated_image


OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"


def encode_image_to_base64(image: np.ndarray) -> str:
    success, buffer = cv2.imencode('.jpg', image)
    if not success:
        raise ValueError("Could not encode image to JPEG format.")

    encoded_image = base64.b64encode(buffer).decode('utf-8')
    return encoded_image


def compose_payload(images: np.ndarray, prompt: str) -> dict:
    text_content = {
        "type": "text",
        "text": prompt
    }
    image_content = [
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{encode_image_to_base64(image=image)}"
            }
        }
        for image
        in images
    ]
    return {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [text_content] + image_content
            }
        ],
        "max_tokens": 300
    }


def compose_headers(api_key: str) -> dict:
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }


def prompt_image(api_key: str, images: np.ndarray, prompt: str) -> str:
    headers = compose_headers(api_key=api_key)
    payload = compose_payload(images=images, prompt=prompt)
    response = requests.post(url=OPENAI_API_URL, headers=headers, json=payload).json()

    if 'error' in response:
        raise ValueError(response['error']['message'])
    return response['choices'][0]['message']['content']

def resize_images(images: List[np.ndarray], size: Tuple[int, int]) -> List[np.ndarray]:
    """
    Resizes all images to the specified size.

    Args:
        images (List[np.ndarray]): A list of images to be resized. Each image is a 3D NumPy array.
        size (Tuple[int, int]): The target size for the images, specified as (width, height).

    Returns:
        List[np.ndarray]: A list of resized images.
    """
    return [cv2.resize(image, size) for image in images]


def blend_images(images: List[np.ndarray]) -> np.ndarray:
    """
    Blends a list of images into a single image.

    Args:
    images: A list of images where each image is a NumPy array. All images must have the same shape and dtype.

    Returns:
    A blended image as a NumPy array.

    Raises:
    ValueError: If the input list is empty.
    """
    if not images:
        raise ValueError("The list of images is empty.")

    image_stack = np.stack(images)
    blended_image = np.mean(image_stack, axis=0)

    return blended_image.astype(np.uint8)


def chunk_list(lst: List, n: int) -> Iterator[List]:
    """
    Yield successive n-sized chunks from a list.

    Parameters:
        lst (List): The list to be chunked.
        n (int): The size of each chunk.

    Yields:
        Iterator[List]: An iterator over the chunks of the list, each being a list of maximum `n` elements.
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


