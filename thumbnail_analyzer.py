import subprocess
import json
import numpy as np
from PIL import Image, ImageStat

def fetch_thumbnail(url):
    """Download thumbnail using yt-dlp and return file path."""
    info_cmd = ["yt-dlp", "--dump-json", url]
    result = subprocess.run(info_cmd, capture_output=True, text=True)

    info = json.loads(result.stdout)
    vid_id = info["id"]
    thumbnail_url = info["thumbnail"]

    # Save thumbnail file
    thumb_path = f"{vid_id}.jpg"
    subprocess.run(["yt-dlp", thumbnail_url, "-o", thumb_path],
                   capture_output=True)

    return thumb_path, info["title"]


def brightness_score(img):
    stat = ImageStat.Stat(img.convert("L"))
    return stat.mean[0]  # 0–255


def contrast_score(img):
    arr = np.array(img.convert("L"))
    return arr.std()  # higher = more contrast


def sharpness_score(img):
    arr = np.array(img.convert("L"))
    gy, gx = np.gradient(arr.astype("float"))
    return (np.abs(gx) + np.abs(gy)).mean()


def colorfulness_score(img):
    arr = np.array(img)
    r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
    rg = np.abs(r - g)
    yb = np.abs(0.5*(r + g) - b)
    return (rg.mean() + yb.mean())


def analyze_thumbnail(path):
    img = Image.open(path)

    brightness = brightness_score(img)
    contrast = contrast_score(img)
    sharpness = sharpness_score(img)
    color = colorfulness_score(img)

    # Normalize to 0–100 score
    score = (
        (brightness / 255) * 25 +
        min(contrast, 80) / 80 * 25 +
        min(sharpness, 20) / 20 * 25 +
        min(color, 150) / 150 * 25
    )

    return brightness, contrast, sharpness, color, round(score, 2)


def suggestions(brightness, contrast, sharpness, color):
    s = []

    if brightness < 90:
        s.append("Increase brightness.")
    if contrast < 30:
        s.append("Increase contrast.")
    if sharpness < 5:
        s.append("Make the subject sharper.")
    if color < 30:
        s.append("Use more vibrant colors.")

    if not s:
        s.append("Thumbnail looks great!")

    return s


def main():
    url = input("Enter YouTube URL: ").strip()
    thumb_path, title = fetch_thumbnail(url)

    print("\n=== VIDEO TITLE ===")
    print(title)

    print("\n=== ANALYZING THUMBNAIL ===")
    b, c, sh, col, score = analyze_thumbnail(thumb_path)

    print(f"Brightness: {b:.2f}")
    print(f"Contrast: {c:.2f}")
    print(f"Sharpness: {sh:.2f}")
    print(f"Colorfulness: {col:.2f}")
    print(f"\nThumbnail Score: {score}/100\n")

    print("=== SUGGESTIONS ===")
    for s in suggestions(b, c, sh, col):
        print("-", s)


if _name_ == "_main_":
    main()
