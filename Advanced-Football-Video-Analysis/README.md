Okay, got it. Here's the updated README with the model training section:

# Advanced Football Video Analysis

This project aims to develop a set of tools to thoroughly analyze football match videos. From the videos, the system is able to detect and track players, estimate their movements, speeds and distances covered, as well as identify the teams involved.

## Features

- Detection and tracking of players in the videos using YOLOv5 and YOLOv8 models
- Camera motion estimation to adjust player positions
- View transformation to obtain an ideal perspective
- Ball position interpolation
- Estimation of player speed and distance covered
- Automatic assignment of players to their respective teams using K-means clustering for team color identification
- Identification of ball possession by the different teams

## Model Training

The player detection and tracking models were trained using the YOLOv5 and YOLOv8 architectures. The training datasets were collected and annotated using Roboflow.

To train the models:

1. Prepare the dataset:
   - Collect football match videos and annotate the players using Roboflow.
   - Split the dataset into training, validation, and test sets.
2. Train the YOLOv5 and YOLOv8 models:
   - Use the Roboflow SDK or the official YOLOv5 and YOLOv8 repositories to train the models on the prepared dataset.
   - Fine-tune the models for optimal performance on the football video analysis task.
3. Save the trained models:
   - Export the trained models and save them in the `models/` directory.


## Usage

1. Place the input videos in the `input_videos/` folder.
2. Run the main script:
```
python main.py
```
3. The analyzed videos will be saved in the `output_videos/` folder.
