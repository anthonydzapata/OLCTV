#!/usr/bin/env python3
"""
OLC Broadcast Engine v1.0
A retro broadcast automation system using FFmpeg and random sequencing.
"""

import os
import random
import subprocess
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class MediaFile:
    """Represents a media file (show segment or ad)."""
    path: str
    duration: float
    media_type: str  # 'show' or 'ad'


class BroadcastEngine:
    """Core broadcast automation engine."""
    
    def __init__(self, assets_dir: str = "assets"):
        self.assets_dir = Path(assets_dir)
        self.shows_dir = self.assets_dir / "shows"
        self.ads_dir = self.assets_dir / "ads"
        self.output_dir = self.assets_dir / "output"
        self.vhs_filter = self._build_vhs_filter()
        
        # Create directories if they don't exist
        self.shows_dir.mkdir(parents=True, exist_ok=True)
        self.ads_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _build_vhs_filter(self) -> str:
        """
        Construct the VHS aesthetic FFmpeg filter chain.
        Includes: scanlines, color bleed, jitter, and 4:3 aspect ratio.
        """
        filters = [
            # Scale to 4:3 aspect ratio (720x540)
            "scale=720:540:force_original_aspect_ratio=decrease",
            "pad=720:540:(ow-iw)/2:(oh-ih)/2:color=black",
            
            # Scanlines (horizontal lines effect)
            "split[a][b]",
            "[a]scale=720:540[a1]",
            "[b]scale=720:2:[b1]",
            "[b1]scale=720:540[b2]",
            "[a1][b2]blend=all_mode=average",
            
            # Slight color shift (tape wear)
            "eq=saturation=1.1:contrast=0.95",
            
            # Subtle jitter (tracking error simulation)
            "split[x][y]",
            "[y]scale=716:540[y1]",
            "[x][y1]overlay=x=2:y=0:eof_action=repeat",
        ]
        return ",".join(filters)
    
    def scan_assets(self) -> tuple[List[MediaFile], List[MediaFile]]:
        """Scan and catalog available media files."""
        shows = []
        ads = []
        
        # Scan shows directory
        for video_file in self.shows_dir.glob("*"):
            if video_file.suffix.lower() in ['.mp4', '.mkv', '.avi', '.mov', '.m4v']:
                duration = self._get_duration(str(video_file))
                shows.append(MediaFile(str(video_file), duration, 'show'))
        
        # Scan ads directory
        for video_file in self.ads_dir.glob("*"):
            if video_file.suffix.lower() in ['.mp4', '.mkv', '.avi', '.mov', '.m4v']:
                duration = self._get_duration(str(video_file))
                ads.append(MediaFile(str(video_file), duration, 'ad'))
        
        return shows, ads
    
    def _get_duration(self, video_path: str) -> float:
        """Get duration of a video file in seconds using ffprobe."""
        try:
            result = subprocess.run(
                [
                    'ffprobe',
                    '-v', 'error',
                    '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1:noprint_wrappers=1',
                    video_path
                ],
                capture_output=True,
                text=True,
                timeout=5
            )
            return float(result.stdout.strip()) if result.stdout.strip() else 0.0
        except Exception as e:
            print(f"Warning: Could not determine duration for {video_path}: {e}")
            return 0.0
    
    def generate_broadcast_block(self, output_file: str = None) -> Optional[str]:
        """
        Generate a 10-minute broadcast block.
        Structure: Show (4min) → Ads (1min) → Show (4min) + Outro (1min)
        """
        shows, ads = self.scan_assets()
        
        if not shows:
            print("Error: No show files found in assets/shows/")
            return None
        if not ads:
            print("Error: No ad files found in assets/ads/")
            return None
        
        # Build playlist
        playlist = []
        
        # Intro (generate via text-to-video or use static image)
        intro_duration = 15  # 15 seconds
        intro_path = self._create_intro_segment(intro_duration)
        playlist.append(intro_path)
        
        # Show Segment A (randomly select)
        show_a = random.choice(shows)
        playlist.append(show_a.path)
        
        # Ad Break (3x ads, ~20 seconds each)
        for _ in range(3):
            ad = random.choice(ads)
            playlist.append(ad.path)
        
        # Show Segment B (randomly select, different from A if possible)
        remaining_shows = [s for s in shows if s.path != show_a.path] or shows
        show_b = random.choice(remaining_shows)
        playlist.append(show_b.path)
        
        # Outro (static + text overlay)
        outro_duration = 45  # 45 seconds
        outro_path = self._create_outro_segment(outro_duration)
        playlist.append(outro_path)
        
        # Concatenate with VHS filter
        output_file = output_file or str(self.output_dir / "broadcast_block.mp4")
        self._concatenate_with_filter(playlist, output_file)
        
        return output_file
    
    def _create_intro_segment(self, duration: int) -> str:
        """Generate a simple intro segment (black screen with text)."""
        output_path = self.output_dir / "intro.mp4"
        
        # Use ffmpeg to generate a silent video with text overlay
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', f'color=c=black:s=720x540:d={duration}',
            '-vf', (
                f'drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:'
                f'text="STATION ID":fontsize=72:fontcolor=yellow:x=(w-text_w)/2:y=(h-text_h)/2'
            ),
            '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=mono',
            '-shortest',
            str(output_path)
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, check=True, timeout=30)
        except Exception as e:
            print(f"Warning: Could not create intro: {e}")
        
        return str(output_path)
    
    def _create_outro_segment(self, duration: int) -> str:
        """Generate a simple outro segment (VHS snow + text)."""
        output_path = self.output_dir / "outro.mp4"
        
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', f'color=c=black:s=720x540:d={duration}',
            '-vf', (
                f'drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:'
                f'text="Coming Up Next...":fontsize=48:fontcolor=yellow:x=(w-text_w)/2:y=(h-text_h)/2'
            ),
            '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=mono',
            '-shortest',
            str(output_path)
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, check=True, timeout=30)
        except Exception as e:
            print(f"Warning: Could not create outro: {e}")
        
        return str(output_path)
    
    def _concatenate_with_filter(self, playlist: List[str], output_file: str):
        """Concatenate video files with VHS filter applied."""
        # Create a concat demuxer file
        concat_file = self.output_dir / "concat.txt"
        
        with open(concat_file, 'w') as f:
            for video in playlist:
                f.write(f"file '{os.path.abspath(video)}'\n")
        
        # FFmpeg command with filter chain
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-vf', self.vhs_filter,
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '18',
            '-c:a', 'aac',
            '-b:a', '128k',
            output_file
        ]
        
        print(f"Generating broadcast block: {output_file}")
        print(f"FFmpeg command: {' '.join(cmd)}")
        
        try:
            subprocess.run(cmd, check=True)
            print(f"✓ Broadcast block generated: {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error: FFmpeg failed with exit code {e.returncode}")
            raise


def main():
    """Entry point for broadcast engine."""
    engine = BroadcastEngine()
    
    print("=" * 60)
    print("OLC BROADCAST ENGINE v1.0")
    print("=" * 60)
    
    shows, ads = engine.scan_assets()
    print(f"\nAssets Found:")
    print(f"  • Shows: {len(shows)}")
    print(f"  • Ads: {len(ads)}")
    
    if len(shows) > 0 and len(ads) > 0:
        output = engine.generate_broadcast_block()
        print(f"\n✓ Broadcast block ready: {output}")
    else:
        print("\n✗ Not enough assets. Add video files to:")
        print(f"  • {engine.shows_dir}")
        print(f"  • {engine.ads_dir}")


if __name__ == "__main__":
    main()
