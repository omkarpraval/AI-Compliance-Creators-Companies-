import os
import urllib.request

fixtures_dir = "scripts/fixtures"
os.makedirs(fixtures_dir, exist_ok=True)
storage_dir = "storage_data/uploads"
os.makedirs(storage_dir, exist_ok=True)

# Three public domain / royalty free short video samples (Big Buck Bunny / test clips)
# or generate local webm/mp4 samples
samples = [
    ("sample_skincare_review.mp4", "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"),
    ("sample_unboxing.mp4", "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4"),
    ("sample_routine.mp4", "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4"),
]

for filename, url in samples:
    target_fixture = os.path.join(fixtures_dir, filename)
    target_storage = os.path.join(storage_dir, filename)
    if not os.path.exists(target_fixture):
        try:
            print(f"Downloading fixture {filename}...")
            urllib.request.urlretrieve(url, target_fixture)
            print(f"Downloaded {filename}")
        except Exception as e:
            print(f"Could not download {filename}, generating placeholder MP4: {e}")
            # Create valid minimal mp4 container placeholder
            with open(target_fixture, "wb") as f:
                f.write(b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00isommp42\x00\x00\x00\x08free")

    # Copy to storage
    if os.path.exists(target_fixture):
        with open(target_fixture, "rb") as src, open(target_storage, "wb") as dst:
            dst.write(src.read())

print("Video fixtures initialized successfully.")
