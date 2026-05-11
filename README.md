## OLC Broadcast Engine

A retro broadcast automation system that generates classic Saturday morning cartoon blocks with VHS aesthetic effects.

### What It Does

- **Scans** your video assets from `assets/shows/` and `assets/ads/`
- **Randomly sequences** them: Intro → Show A → Ad Break → Show B → Outro
- **Applies VHS filters**: 4:3 aspect ratio, scanlines, color bleed, tracking jitter
- **Outputs** a concatenated MP4 broadcast block ready for streaming or playback

### Requirements

- Python 3.8+
- FFmpeg (with libx264 and aac support)
- ffprobe (included with FFmpeg)

### Installation

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html or use:
```bash
choco install ffmpeg
```

### Quick Start

1. **Prepare your assets:**
   ```
   assets/
   ├── shows/
   │   ├── superman.mp4
   │   ├── popeye.mp4
   │   └── ...
   └── ads/
       ├── gi_joe_ad.mp4
       ├── transformers_ad.mp4
       └── ...
   ```

2. **Run the engine:**
   ```bash
   python broadcast_engine.py
   ```

3. **Output:**
   ```
   assets/output/broadcast_block.mp4
   ```

### Output Options

Edit `broadcast_engine.py` to customize:
- **VHS filter strength**: Adjust saturation, contrast, and jitter values
- **Aspect ratio**: Change the `scale` values in `_build_vhs_filter()`
- **Duration**: Modify intro/outro duration in `generate_broadcast_block()`
- **Playlist structure**: Reorder or add segments before concatenation

### Technical Details

**VHS Filter Chain:**
- Scale to 4:3 (720x540) with black pillarboxing
- Scanline overlay (simulated via split/scale/blend)
- Color shift (saturation boost + contrast reduction)
- Horizontal jitter (offset overlay for tracking error effect)

**Video Codec:**
- H.264 (libx264) @ CRF 18 (high quality)
- AAC audio @ 128kbps
- Output: 720x540 @ 25fps

### Troubleshooting

**"ffmpeg: command not found"**
- Install FFmpeg (see Requirements above)
- Verify it's in your PATH: `ffmpeg -version`

**"No show files found"**
- Ensure video files are in `assets/shows/`
- Supported formats: `.mp4`, `.mkv`, `.avi`, `.mov`, `.m4v`

**"FFmpeg failed with exit code X"**
- Check that your video files are not corrupted: `ffprobe your_video.mp4`
- Ensure sufficient disk space for output file
- Try with a single short test video first

### Example Workflow

```bash
# 1. Create asset directories
mkdir -p assets/{shows,ads,output}

# 2. Add your video files
cp my_show.mp4 assets/shows/
cp my_ad.mp4 assets/ads/

# 3. Generate broadcast block
python broadcast_engine.py

# 4. Play or stream the output
ffplay assets/output/broadcast_block.mp4
```

### File Structure

```
OLCTV/
├── broadcast_engine.py          # Main automation script
├── README.md                    # This file
├── MISSION.md                   # Project vision & values
└── assets/
    ├── shows/                   # Your cartoon/show segments
    ├── ads/                     # Your vintage ads
    └── output/                  # Generated broadcast blocks
```

### Future Enhancements

- [ ] Audio tape hiss layer (optional white noise track)
- [ ] "Station ID" watermark overlay
- [ ] CLI arguments for custom durations & filters
- [ ] Real-time playlist generation (RNG-based daily schedules)
- [ ] Web interface for asset management

### License

MIT (open source retro broadcast preservation)

### Questions?

Check the MISSION.md for project philosophy, or inspect `broadcast_engine.py` for filter customization.

---

**Last Updated:** May 2026 | **Version:** 1.0 (MVP)
