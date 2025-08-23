import sys
import shutil
from pathlib import Path
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

def download_youtube_as_mp3(url: str, output_dir: str = "downloads", bitrate: str = "192") -> Path:
    outdir = Path(output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Check for ffmpeg; if present we'll convert to MP3 automatically
    ffmpeg = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")
    postprocessors = []
    ydl_extra = {}

    if ffmpeg:
        # Enable MP3 conversion
        postprocessors = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": bitrate,
        }]
        # Point yt-dlp at the folder containing ffmpeg
        ydl_extra["ffmpeg_location"] = str(Path(ffmpeg).parent)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(outdir / "%(title)s.%(ext)s"),
        "noplaylist": True,
        "quiet": False,
        "no_warnings": True,
        "postprocessors": postprocessors,
        **ydl_extra,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)  # downloads and returns metadata
            downloaded = Path(ydl.prepare_filename(info))
    except DownloadError as e:
        raise SystemExit(f"Download failed: {e}") from e

    # If ffmpeg ran, final file will be .mp3
    final_path = downloaded.with_suffix(".mp3") if postprocessors else downloaded

    # In rare cases, double-check the file exists; fall back to any matching file
    if not final_path.exists():
        matches = list(Path(output_dir).glob(f"{downloaded.stem}.*"))
        if matches:
            final_path = matches[0]

    print(f"Saved: {final_path.resolve()}")
    return final_path

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else input("Enter YouTube URL: ").strip()
    download_youtube_as_mp3(url)
