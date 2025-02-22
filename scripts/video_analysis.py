from pytube import YouTube
from moviepy.editor import VideoFileClip
import os

import numpy as np
import supervision as sv
from ultralytics import YOLO

def single_video_download(path="Data", url='https://www.youtube.com/watch?v=8ZabZYk8tBg'):
    try:
        if not os.path.exists(path):
            os.makedirs(path)

        yt = YouTube(url)

        video = yt.streams.filter(progressive=True, file_extension='mp4', res="720p").first()

        if not video:
            video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

        if video:
            video.download(output_path=path)

            print(f"Téléchargement de {yt.title} en {video.resolution} réussi")


        else:
            print(f"Aucune vidéo disponible pour {url}")

    except Exception as e:
        print(f"Échec du téléchargement de {url}: {str(e)}")


def reduce_video_size(input_path="input_video.mp4", output_path="output_video.mp4", start_time=30, duration=60):
    try:
        video = VideoFileClip(input_path)
        reduced_video = video.subclip(start_time, start_time + duration)
        reduced_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
        print(f"La vidéo a été réduite avec succès et enregistrée sous {output_path}")
    except Exception as e:
        print(f"Erreur lors de la réduction de la vidéo : {str(e)}")


if __name__ == "__main__":
    #single_video_download()
    reduce_video_size("Data\\test.mp4", "data\\match.mp4", 0, 60)


model = YOLO("yolov8n.pt")
box_annotator = sv.BoundingBoxAnnotator()

def callback(frame: np.ndarray, _: int) -> np.ndarray:
    results = model(frame)[0]
    detections = sv.Detections.from_ultralytics(results)
    return box_annotator.annotate(frame.copy(), detections=detections)

sv.process_video(
    source_path="Data\\match.mp4",
    target_path="result\\result1.mp4",
    callback=callback
)