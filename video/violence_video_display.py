# violent_video_display.py
import os
import cv2
import joblib

class VideoClassifier:
    def __init__(self, model_path, video_folder):
        # Load the trained model
        self.model = joblib.load(model_path)
        self.video_folder = video_folder

    def extract_features(self, video_path):
        """
        Extract features from the video.
        For simplicity, we'll just use the total frame count as a dummy feature.
        Replace this with your actual feature extraction.
        """
        cap = cv2.VideoCapture(r"E:\New folder\loginpage\video\1.mp4")
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        return [frame_count]  # Example feature, replace with real ones

    def predict_video(self, video_path):
        features = self.extract_features(video_path)
        prediction = self.model.predict([features])[0]
        return prediction

    def display_videos(self):
        for video_file in os.listdir(self.video_folder):
            if not video_file.endswith(('.mp4', '.avi', '.mov')):
                continue

            video_path = os.path.join(self.video_folder, video_file)
            prediction = self.predict_video(video_path)

            print(f"Video: {video_file} | Predicted: {prediction}")

            cap = cv2.VideoCapture(video_path)
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                cv2.putText(frame, f"Prediction: {prediction}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.imshow('Video', frame)
                if cv2.waitKey(30) & 0xFF == ord('q'):
                    break
            cap.release()
        cv2.destroyAllWindows()


# Example usage:
if __name__ == "__main__":
    model_path = "95427a29-4ced-4feb-82a0-9cd201e21e1b.joblib"
    video_folder = r"E:\New folder\loginpage\video"  # Replace with your folder path
    vc = VideoClassifier(model_path, video_folder)
    vc.display_videos()
