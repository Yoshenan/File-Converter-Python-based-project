import os
import subprocess

def convert_video(user_input, output_user):
    out = ["ffmpeg", "-i", user_input, "-y", output_user]
    try:
        subprocess.run(out, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Saved: {output_user}")
    except FileNotFoundError:
        print("ffmpeg is not installed or not in system PATH")
    except subprocess.CalledProcessError as e:
        print(f"ffmpeg error: {e.stderr.decode()}")

def image_to_video(user_input, output_user, duration=5):
    out = [
        "ffmpeg",
        "-loop", "1",
        "-i", user_input,
        "-c:v", "libx264",
        "-t", str(duration),
        "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
        "-pix_fmt", "yuv420p",
        "-y",
        output_user
    ]
    try:
        subprocess.run(out, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Saved: {output_user}")
    except FileNotFoundError:
        print("ffmpeg is not installed or not in system PATH")
    except subprocess.CalledProcessError as e:
        print(f"ffmpeg error: {e.stderr.decode()}")

def convert_audio(user_input, output_user):
    out = ["ffmpeg", "-i", user_input, "-vn", "-y", output_user]
    try:
        subprocess.run(out, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Saved: {output_user}")
    except FileNotFoundError:
        print("ffmpeg is not installed or not in system PATH")
    except subprocess.CalledProcessError as e:
        print(f"ffmpeg error: {e.stderr.decode()}")

def add_audio_to_image(image_input, audio_input, output_user):
    out = [
        "ffmpeg",
        "-loop", "1",
        "-i", image_input,
        "-i", audio_input,
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "1920k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "-y",
        output_user
    ]
    try:
        subprocess.run(out, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Saved: {output_user}")
    except Exception as e:
        print(f"Error merging files: {e}")