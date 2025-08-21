#!/usr/bin/env python3
"""
YouTube Uploader Module for Douyin Video Downloader
Handles uploading videos to YouTube using Google API
Supports YouTube Shorts optimization
"""

import os
import json
import pickle
import time
import subprocess
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class YouTubeUploader:
    def __init__(self, credentials_file="credentials.json", token_file="token.pickle"):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.youtube = None
        self.scopes = [
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube.readonly"
        ]
        
        # Advanced upload settings
        self.video_quality_settings = {
            'high_quality': {
                'video_codec': 'h264',
                'audio_codec': 'aac', 
                'crf': 18,  # Lower = higher quality
                'preset': 'slow',  # Higher quality encoding
                'bitrate_factor': 1.5
            },
            'youtube_optimized': {
                'video_codec': 'h264',
                'audio_codec': 'aac',
                'crf': 20,
                'preset': 'medium',
                'bitrate_factor': 1.2
            },
            'fast_upload': {
                'video_codec': 'h264', 
                'audio_codec': 'aac',
                'crf': 23,
                'preset': 'fast',
                'bitrate_factor': 1.0
            }
        }
        
    def authenticate(self):
        """Authenticate with YouTube API"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
                
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(f"Credentials file '{self.credentials_file}' not found!")
                    
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.scopes)
                creds = flow.run_local_server(port=0)
                
            # Save credentials for next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
                
        self.youtube = build('youtube', 'v3', credentials=creds)
        return True
        
    def detect_shorts_video(self, video_file):
        """
        Detect if video is suitable for YouTube Shorts
        Returns: dict with shorts info and recommendations
        """
        try:
            # Use ffprobe to get video info
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json', 
                '-show_format', '-show_streams', video_file
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    info = json.loads(result.stdout)
                else:
                    # Fallback: basic file analysis
                    return self._basic_shorts_detection(video_file)
            except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
                # FFprobe not available or failed, use basic detection
                return self._basic_shorts_detection(video_file)
            
            # Get video stream info
            video_stream = None
            audio_stream = None
            
            for stream in info.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                elif stream.get('codec_type') == 'audio':
                    audio_stream = stream
            
            if not video_stream:
                return {'is_shorts': False, 'reason': 'No video stream found'}
            
            # Get dimensions and duration
            width = int(video_stream.get('width', 0))
            height = int(video_stream.get('height', 0))
            duration = float(info.get('format', {}).get('duration', 0))
            
            # YouTube Shorts criteria
            is_vertical = height > width  # Portrait orientation
            is_short_duration = duration <= 60  # Max 60 seconds
            is_valid_resolution = height >= 720  # Minimum quality
            
            # Determine if it's suitable for Shorts
            is_shorts = is_vertical and is_short_duration and is_valid_resolution
            
            # Create recommendations
            recommendations = []
            shorts_tags = []
            
            if is_shorts:
                recommendations.append("✅ Perfect for YouTube Shorts!")
                shorts_tags = ["Shorts", "YouTubeShorts", "Short", "Vertical"]
            else:
                if not is_vertical:
                    recommendations.append("📱 Consider rotating to vertical (9:16) for Shorts")
                if not is_short_duration:
                    recommendations.append(f"⏱️ Duration {duration:.1f}s > 60s. Trim to ≤60s for Shorts")
                if not is_valid_resolution:
                    recommendations.append("📺 Increase resolution to ≥720p for better quality")
            
            return {
                'is_shorts': is_shorts,
                'width': width,
                'height': height,
                'duration': duration,
                'aspect_ratio': f"{width}:{height}",
                'is_vertical': is_vertical,
                'is_short_duration': is_short_duration,
                'is_valid_resolution': is_valid_resolution,
                'recommendations': recommendations,
                'shorts_tags': shorts_tags,
                'file_size_mb': round(os.path.getsize(video_file) / (1024*1024), 2)
            }
            
        except Exception as e:
            return {
                'is_shorts': False,
                'reason': f'Analysis failed: {str(e)}',
                'recommendations': ['❌ Could not analyze video properties']
            }
    
    def _basic_shorts_detection(self, video_file):
        """Basic shorts detection without ffprobe"""
        file_size = os.path.getsize(video_file)
        file_size_mb = round(file_size / (1024*1024), 2)
        
        # Very basic heuristics
        is_likely_shorts = file_size_mb < 50  # Small file size suggests short video
        
        return {
            'is_shorts': is_likely_shorts,
            'width': 'unknown',
            'height': 'unknown', 
            'duration': 'unknown',
            'aspect_ratio': 'unknown',
            'is_vertical': 'unknown',
            'is_short_duration': 'unknown',
            'is_valid_resolution': 'unknown',
            'recommendations': [
                '💡 Install FFmpeg for detailed video analysis',
                '📱 Ensure video is vertical (9:16 ratio)',
                '⏱️ Keep duration ≤60 seconds',
                '📺 Use minimum 720p resolution'
            ],
            'shorts_tags': ["Shorts", "YouTubeShorts"] if is_likely_shorts else [],
            'file_size_mb': file_size_mb
        }
        
    def analyze_video_quality(self, video_file):
        """
        Comprehensive video quality analysis
        Returns detailed technical information and optimization recommendations
        """
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', '-show_chapters', video_file
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode != 0:
                    return self._basic_quality_analysis(video_file)
                
                info = json.loads(result.stdout)
            except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
                return self._basic_quality_analysis(video_file)
            
            # Parse streams
            video_stream = None
            audio_stream = None
            
            for stream in info.get('streams', []):
                if stream.get('codec_type') == 'video' and not video_stream:
                    video_stream = stream
                elif stream.get('codec_type') == 'audio' and not audio_stream:
                    audio_stream = stream
            
            if not video_stream:
                return {'error': 'No video stream found'}
            
            # Video analysis
            analysis = self._analyze_video_stream(video_stream, info.get('format', {}))
            
            # Audio analysis
            if audio_stream:
                analysis.update(self._analyze_audio_stream(audio_stream))
            
            # Generate recommendations
            analysis['recommendations'] = self._generate_quality_recommendations(analysis)
            analysis['youtube_optimization'] = self._get_youtube_optimization_suggestions(analysis)
            
            return analysis
            
        except Exception as e:
            return {'error': f'Analysis failed: {str(e)}'}
    
    def _analyze_video_stream(self, video_stream, format_info):
        """Analyze video stream properties"""
        width = int(video_stream.get('width', 0))
        height = int(video_stream.get('height', 0))
        fps = self._parse_fps(video_stream.get('r_frame_rate', '0/1'))
        duration = float(format_info.get('duration', 0))
        bitrate = int(video_stream.get('bit_rate', 0)) if video_stream.get('bit_rate') else None
        codec = video_stream.get('codec_name', 'unknown')
        profile = video_stream.get('profile', 'unknown')
        level = video_stream.get('level', 'unknown')
        
        # Calculate metrics
        pixel_count = width * height
        total_pixels = pixel_count * fps * duration if fps > 0 and duration > 0 else 0
        
        # Determine quality level
        quality_level = self._determine_quality_level(width, height, fps, bitrate)
        
        return {
            'video': {
                'width': width,
                'height': height,
                'fps': fps,
                'duration': duration,
                'bitrate': bitrate,
                'codec': codec,
                'profile': profile,
                'level': level,
                'pixel_count': pixel_count,
                'total_pixels': total_pixels,
                'quality_level': quality_level,
                'aspect_ratio': f"{width}:{height}",
                'is_vertical': height > width,
                'is_square': width == height,
                'is_horizontal': width > height
            }
        }
    
    def _analyze_audio_stream(self, audio_stream):
        """Analyze audio stream properties"""
        sample_rate = int(audio_stream.get('sample_rate', 0))
        channels = int(audio_stream.get('channels', 0))
        bitrate = int(audio_stream.get('bit_rate', 0)) if audio_stream.get('bit_rate') else None
        codec = audio_stream.get('codec_name', 'unknown')
        
        # Determine audio quality
        audio_quality = 'unknown'
        if bitrate:
            if bitrate >= 320000:
                audio_quality = 'excellent'
            elif bitrate >= 192000:
                audio_quality = 'high'
            elif bitrate >= 128000:
                audio_quality = 'good'
            elif bitrate >= 96000:
                audio_quality = 'fair'
            else:
                audio_quality = 'poor'
        
        return {
            'audio': {
                'sample_rate': sample_rate,
                'channels': channels,
                'bitrate': bitrate,
                'codec': codec,
                'quality_level': audio_quality,
                'is_stereo': channels == 2,
                'is_mono': channels == 1,
                'is_surround': channels > 2
            }
        }
    
    def _parse_fps(self, fps_string):
        """Parse frame rate from ffprobe format"""
        try:
            if '/' in fps_string:
                num, den = fps_string.split('/')
                return float(num) / float(den) if float(den) != 0 else 0
            return float(fps_string)
        except:
            return 0
    
    def _determine_quality_level(self, width, height, fps, bitrate):
        """Determine overall video quality level"""
        # Resolution quality
        pixel_count = width * height
        
        if pixel_count >= 3840 * 2160:  # 4K
            res_quality = 'ultra_high'
        elif pixel_count >= 1920 * 1080:  # 1080p
            res_quality = 'high'
        elif pixel_count >= 1280 * 720:   # 720p
            res_quality = 'medium'
        elif pixel_count >= 854 * 480:    # 480p
            res_quality = 'low'
        else:
            res_quality = 'very_low'
        
        # FPS quality
        if fps >= 60:
            fps_quality = 'high'
        elif fps >= 30:
            fps_quality = 'medium'
        elif fps >= 24:
            fps_quality = 'low'
        else:
            fps_quality = 'very_low'
        
        # Bitrate quality (if available)
        bitrate_quality = 'unknown'
        if bitrate:
            # Rough bitrate quality for different resolutions
            if res_quality == 'ultra_high' and bitrate >= 45000000:
                bitrate_quality = 'excellent'
            elif res_quality == 'high' and bitrate >= 8000000:
                bitrate_quality = 'excellent'
            elif res_quality == 'medium' and bitrate >= 5000000:
                bitrate_quality = 'excellent'
            elif bitrate >= 2000000:
                bitrate_quality = 'good'
            elif bitrate >= 1000000:
                bitrate_quality = 'fair'
            else:
                bitrate_quality = 'poor'
        
        # Overall quality assessment
        qualities = [res_quality, fps_quality]
        if bitrate_quality != 'unknown':
            qualities.append(bitrate_quality)
        
        # Simple quality scoring
        quality_scores = {
            'ultra_high': 5, 'excellent': 5,
            'high': 4,
            'medium': 3, 'good': 3,
            'low': 2, 'fair': 2,
            'very_low': 1, 'poor': 1
        }
        
        avg_score = sum(quality_scores.get(q, 2) for q in qualities) / len(qualities)
        
        if avg_score >= 4.5:
            return 'excellent'
        elif avg_score >= 3.5:
            return 'high'
        elif avg_score >= 2.5:
            return 'medium'
        elif avg_score >= 1.5:
            return 'low'
        else:
            return 'poor'
    
    def _basic_quality_analysis(self, video_file):
        """Basic quality analysis when ffprobe is not available"""
        file_size = os.path.getsize(video_file)
        file_size_mb = round(file_size / (1024*1024), 2)
        
        return {
            'video': {
                'width': 'unknown',
                'height': 'unknown',
                'fps': 'unknown',
                'duration': 'unknown',
                'bitrate': 'unknown',
                'codec': 'unknown',
                'quality_level': 'unknown'
            },
            'audio': {
                'quality_level': 'unknown'
            },
            'file_size_mb': file_size_mb,
            'recommendations': ['Install FFmpeg for detailed analysis'],
            'youtube_optimization': ['Basic upload without optimization']
        }
        
    def _generate_quality_recommendations(self, analysis):
        """Generate quality improvement recommendations"""
        recommendations = []
        video = analysis.get('video', {})
        audio = analysis.get('audio', {})
        
        # Video recommendations
        if video.get('quality_level') == 'poor':
            recommendations.append("🔴 Poor video quality detected. Consider re-encoding.")
        elif video.get('quality_level') == 'low':
            recommendations.append("🟡 Low video quality. Recommend higher bitrate.")
        
        # Resolution recommendations
        width, height = video.get('width', 0), video.get('height', 0)
        if width < 1280 or height < 720:
            recommendations.append("📺 Resolution below 720p. Consider upscaling for better YouTube quality.")
        
        # FPS recommendations
        fps = video.get('fps', 0)
        if fps < 24:
            recommendations.append("🎬 Low frame rate. Consider 24fps minimum for smooth playback.")
        elif fps > 60:
            recommendations.append("⚡ High frame rate detected. May increase file size unnecessarily.")
        
        # Codec recommendations
        codec = video.get('codec', '')
        if codec not in ['h264', 'h265', 'vp9']:
            recommendations.append(f"🔧 Codec '{codec}' may not be optimal. H.264 recommended for YouTube.")
        
        # Audio recommendations  
        if audio.get('quality_level') == 'poor':
            recommendations.append("🔊 Poor audio quality. Consider 192kbps+ for better sound.")
        
        audio_codec = audio.get('codec', '')
        if audio_codec not in ['aac', 'mp3']:
            recommendations.append(f"🎵 Audio codec '{audio_codec}' may not be optimal. AAC recommended.")
        
        # File size recommendations
        file_size_mb = analysis.get('file_size_mb', 0)
        duration = video.get('duration', 0)
        if duration > 0:
            size_per_minute = file_size_mb / (duration / 60)
            if size_per_minute > 200:
                recommendations.append("💾 Large file size. Consider compression to reduce upload time.")
            elif size_per_minute < 10:
                recommendations.append("💾 Small file size may indicate low quality.")
        
        if not recommendations:
            recommendations.append("✅ Video quality looks good for YouTube upload!")
        
        return recommendations
    
    def _get_youtube_optimization_suggestions(self, analysis):
        """Get YouTube-specific optimization suggestions"""
        suggestions = []
        video = analysis.get('video', {})
        
        # YouTube preferred specs
        width, height = video.get('width', 0), video.get('height', 0)
        fps = video.get('fps', 0)
        
        # Resolution suggestions
        if video.get('is_vertical'):
            suggestions.append("📱 Vertical video detected - perfect for YouTube Shorts!")
            if height < 1920:
                suggestions.append("📱 Consider 1080x1920 for optimal Shorts quality")
        else:
            if width >= 1920 and height >= 1080:
                suggestions.append("🎬 Good resolution for standard YouTube content")
            else:
                suggestions.append("🎬 Consider 1920x1080 for optimal YouTube quality")
        
        # FPS suggestions
        if fps in [24, 25, 30, 50, 60]:
            suggestions.append(f"⚡ Frame rate {fps}fps is YouTube-optimized")
        else:
            suggestions.append("⚡ Consider standard frame rates: 24, 30, or 60fps")
        
        # Codec suggestions
        codec = video.get('codec', '')
        if codec == 'h264':
            suggestions.append("✅ H.264 codec is perfect for YouTube")
        elif codec == 'h265':
            suggestions.append("✅ H.265 codec provides good compression")
        else:
            suggestions.append("🔧 Consider converting to H.264 for best YouTube compatibility")
        
        # Bitrate suggestions
        bitrate = video.get('bitrate', 0)
        pixel_count = video.get('pixel_count', 0)
        
        if pixel_count >= 1920 * 1080:  # 1080p+
            recommended_bitrate = 8000000  # 8Mbps
            if bitrate and bitrate < recommended_bitrate * 0.5:
                suggestions.append("📡 Low bitrate for resolution. Consider 8-12Mbps for 1080p")
        elif pixel_count >= 1280 * 720:  # 720p
            recommended_bitrate = 5000000  # 5Mbps
            if bitrate and bitrate < recommended_bitrate * 0.5:
                suggestions.append("📡 Low bitrate for resolution. Consider 5-8Mbps for 720p")
        
        return suggestions
    
    def optimize_video_for_youtube(self, input_file, output_file, quality_preset='youtube_optimized', custom_settings=None):
        """
        Optimize video for YouTube upload using FFmpeg
        
        Args:
            input_file: Source video file
            output_file: Output optimized file
            quality_preset: 'high_quality', 'youtube_optimized', or 'fast_upload'
            custom_settings: Optional dict to override preset settings
        """
        if not os.path.exists(input_file):
            return {'success': False, 'error': 'Input file not found'}
        
        # Get quality settings
        settings = self.video_quality_settings.get(quality_preset, self.video_quality_settings['youtube_optimized'])
        if custom_settings:
            settings.update(custom_settings)
        
        try:
            # Analyze source video
            analysis = self.analyze_video_quality(input_file)
            if 'error' in analysis:
                return {'success': False, 'error': f'Analysis failed: {analysis["error"]}'}
            
            # Build FFmpeg command
            cmd = self._build_ffmpeg_command(input_file, output_file, settings, analysis)
            
            # Execute optimization
            print(f"🔧 Optimizing video with preset: {quality_preset}")
            print(f"📋 Command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)  # 10 min timeout
            
            if result.returncode == 0:
                # Verify output file
                if os.path.exists(output_file):
                    output_size = os.path.getsize(output_file)
                    input_size = os.path.getsize(input_file)
                    
                    return {
                        'success': True,
                        'input_size_mb': round(input_size / (1024*1024), 2),
                        'output_size_mb': round(output_size / (1024*1024), 2),
                        'compression_ratio': round(output_size / input_size, 2),
                        'optimization_preset': quality_preset,
                        'ffmpeg_output': result.stderr
                    }
                else:
                    return {'success': False, 'error': 'Output file was not created'}
            else:
                return {
                    'success': False,
                    'error': f'FFmpeg failed: {result.stderr}',
                    'command': ' '.join(cmd)
                }
                
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Optimization timeout (10 minutes)'}
        except Exception as e:
            return {'success': False, 'error': f'Optimization error: {str(e)}'}
    
    def _build_ffmpeg_command(self, input_file, output_file, settings, analysis):
        """Build FFmpeg command for optimization"""
        cmd = ['ffmpeg', '-y', '-i', input_file]
        
        video_info = analysis.get('video', {})
        audio_info = analysis.get('audio', {})
        
        # Video encoding
        cmd.extend(['-c:v', settings['video_codec']])
        
        if settings['video_codec'] == 'h264':
            cmd.extend(['-preset', settings['preset']])
            cmd.extend(['-crf', str(settings['crf'])])
            cmd.extend(['-profile:v', 'high'])
            cmd.extend(['-level', '4.0'])
            cmd.extend(['-pix_fmt', 'yuv420p'])  # YouTube compatibility
        
        # Audio encoding
        cmd.extend(['-c:a', settings['audio_codec']])
        
        if settings['audio_codec'] == 'aac':
            # Calculate audio bitrate based on channels
            channels = audio_info.get('channels', 2)
            base_bitrate = 128000  # 128k for stereo
            if channels == 1:
                base_bitrate = 64000   # 64k for mono
            elif channels > 2:
                base_bitrate = 256000  # 256k for surround
            
            target_bitrate = int(base_bitrate * settings['bitrate_factor'])
            cmd.extend(['-b:a', f'{target_bitrate}'])
            cmd.extend(['-ar', '48000'])  # YouTube preferred sample rate
        
        # Video bitrate optimization
        width = video_info.get('width', 1920)
        height = video_info.get('height', 1080)
        fps = video_info.get('fps', 30)
        
        # Calculate target bitrate based on resolution and fps
        target_bitrate = self._calculate_optimal_bitrate(width, height, fps, settings['bitrate_factor'])
        if target_bitrate:
            cmd.extend(['-b:v', f'{target_bitrate}'])
            cmd.extend(['-maxrate', f'{int(target_bitrate * 1.2)}'])
            cmd.extend(['-bufsize', f'{int(target_bitrate * 2)}'])
        
        # Additional optimizations
        cmd.extend(['-movflags', '+faststart'])  # Web optimization
        cmd.extend(['-avoid_negative_ts', 'make_zero'])  # Timestamp fix
        
        # Output file
        cmd.append(output_file)
        
        return cmd
    
    def _calculate_optimal_bitrate(self, width, height, fps, factor=1.0):
        """Calculate optimal video bitrate for YouTube"""
        pixel_count = width * height
        
        # Base bitrates for different resolutions (bps)
        if pixel_count >= 3840 * 2160:  # 4K
            base_bitrate = 45000000
        elif pixel_count >= 1920 * 1080:  # 1080p
            base_bitrate = 8000000
        elif pixel_count >= 1280 * 720:   # 720p
            base_bitrate = 5000000
        elif pixel_count >= 854 * 480:    # 480p
            base_bitrate = 2500000
        else:
            base_bitrate = 1000000
        
        # Adjust for frame rate
        if fps > 30:
            base_bitrate = int(base_bitrate * 1.5)
        
        # Apply factor
        target_bitrate = int(base_bitrate * factor)
        
        return f'{target_bitrate}'
        
    def upload_video(self, video_file, title, description="", tags=None, category_id="22", privacy_status="private"):
        """
        Upload video to YouTube
        
        Args:
            video_file: Path to video file
            title: Video title
            description: Video description
            tags: List of tags
            category_id: YouTube category ID (22 = People & Blogs)
            privacy_status: private, public, unlisted
        """
        if not self.youtube:
            raise Exception("Not authenticated! Call authenticate() first.")
            
        if not os.path.exists(video_file):
            raise FileNotFoundError(f"Video file '{video_file}' not found!")
            
        # Check file size (YouTube limits)
        file_size = os.path.getsize(video_file)
        if file_size > 256 * 1024 * 1024 * 1024:  # 256GB
            raise Exception(f"File too large: {file_size / (1024**3):.1f}GB. YouTube limit is 256GB")
            
        if tags is None:
            tags = []
            
        # Validate and clean title
        if len(title) > 100:
            title = title[:97] + "..."
            
        # Clean description
        if len(description) > 5000:
            description = description[:4997] + "..."
            
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags[:30],  # YouTube allows max 30 tags
                'categoryId': category_id,
                'defaultLanguage': 'en',
                'defaultAudioLanguage': 'en'
            },
            'status': {
                'privacyStatus': privacy_status,
                'embeddable': True,
                'license': 'youtube',
                'publicStatsViewable': True,
                'publishAt': None  # Publish immediately
            }
        }
        
        # Create media upload object
        media = MediaFileUpload(
            video_file,
            chunksize=-1,  # Upload in single chunk
            resumable=True
        )
        
        # Execute upload
        insert_request = self.youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
        
        return self._resumable_upload(insert_request)
        
    def upload_optimized_video(self, video_file, title, description="", tags=None, category_id="22", 
                              privacy_status="private", optimize_quality=True, quality_preset='youtube_optimized'):
        """
        Upload video with advanced optimization
        
        Args:
            video_file: Path to video file
            title: Video title
            description: Video description
            tags: List of tags
            category_id: YouTube category ID
            privacy_status: private, public, unlisted
            optimize_quality: Whether to optimize video before upload
            quality_preset: Optimization preset ('high_quality', 'youtube_optimized', 'fast_upload')
        """
        if not self.youtube:
            raise Exception("Not authenticated! Call authenticate() first.")
            
        if not os.path.exists(video_file):
            raise FileNotFoundError(f"Video file '{video_file}' not found!")
        
        upload_file = video_file
        optimization_info = None
        
        # Optimize video if requested
        if optimize_quality:
            try:
                # Analyze video first
                analysis = self.analyze_video_quality(video_file)
                
                # Only optimize if needed
                if self._should_optimize_video(analysis):
                    optimized_file = self._get_optimized_filename(video_file)
                    
                    print(f"🔧 Optimizing video for better YouTube quality...")
                    optimization_result = self.optimize_video_for_youtube(
                        video_file, optimized_file, quality_preset
                    )
                    
                    if optimization_result['success']:
                        upload_file = optimized_file
                        optimization_info = optimization_result
                        print(f"✅ Optimization complete: {optimization_result['input_size_mb']}MB → {optimization_result['output_size_mb']}MB")
                    else:
                        print(f"⚠️ Optimization failed: {optimization_result['error']}")
                        print("📤 Uploading original file...")
                else:
                    print("✅ Video quality is already good, uploading without optimization")
                    
            except Exception as e:
                print(f"⚠️ Optimization error: {e}")
                print("📤 Uploading original file...")
        
        # Prepare metadata with quality info
        if tags is None:
            tags = []
        
        # Add quality tags if optimized
        if optimization_info:
            tags.extend(['optimized', 'high_quality', quality_preset])
        
        # Enhanced description with technical info
        enhanced_description = description
        if optimization_info:
            enhanced_description += f"\n\n📊 Video Quality:\n"
            enhanced_description += f"• Optimized with {quality_preset} preset\n"
            enhanced_description += f"• Size: {optimization_info['input_size_mb']}MB → {optimization_info['output_size_mb']}MB\n"
            enhanced_description += f"• Compression ratio: {optimization_info['compression_ratio']}\n"
        
        # Validate and clean metadata
        if len(title) > 100:
            title = title[:97] + "..."
        if len(enhanced_description) > 5000:
            enhanced_description = enhanced_description[:4997] + "..."
            
        # Upload metadata
        body = {
            'snippet': {
                'title': title,
                'description': enhanced_description,
                'tags': tags[:30],
                'categoryId': category_id,
                'defaultLanguage': 'en',
                'defaultAudioLanguage': 'en'
            },
            'status': {
                'privacyStatus': privacy_status,
                'embeddable': True,
                'license': 'youtube',
                'publicStatsViewable': True,
                'publishAt': None
            }
        }
        
        # Create media upload object
        media = MediaFileUpload(
            upload_file,
            chunksize=1024*1024*8,  # 8MB chunks for better reliability
            resumable=True
        )
        
        # Execute upload
        insert_request = self.youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
        
        try:
            result = self._resumable_upload(insert_request)
            
            # Add optimization info to result
            if optimization_info:
                result['optimization'] = optimization_info
                result['optimized_file_used'] = True
                
                # Clean up temporary optimized file
                if upload_file != video_file and os.path.exists(upload_file):
                    try:
                        os.remove(upload_file)
                        print(f"🗑️ Cleaned up temporary file: {upload_file}")
                    except:
                        pass
            
            return result
            
        except Exception as e:
            # Clean up on error
            if upload_file != video_file and os.path.exists(upload_file):
                try:
                    os.remove(upload_file)
                except:
                    pass
            raise e
    
    def _should_optimize_video(self, analysis):
        """Determine if video should be optimized"""
        if 'error' in analysis:
            return False
        
        video = analysis.get('video', {})
        
        # Don't optimize if already excellent quality
        if video.get('quality_level') == 'excellent':
            return False
        
        # Optimize if quality is poor or medium
        if video.get('quality_level') in ['poor', 'low', 'medium']:
            return True
        
        # Check specific criteria
        codec = video.get('codec', '')
        width = video.get('width', 0)
        height = video.get('height', 0)
        
        # Optimize if not using YouTube-preferred codec
        if codec not in ['h264', 'h265']:
            return True
        
        # Optimize if resolution is not standard
        standard_resolutions = [
            (1920, 1080), (1280, 720), (854, 480), (640, 360),
            (1080, 1920), (720, 1280)  # Vertical formats
        ]
        
        if (width, height) not in standard_resolutions:
            return True
        
        return False
    
    def _get_optimized_filename(self, original_file):
        """Generate filename for optimized video"""
        base, ext = os.path.splitext(original_file)
        return f"{base}_optimized_yt{ext}"
        
    def upload_shorts_video(self, video_file, title, description="", tags=None, privacy_status="public"):
        """
        Upload video optimized for YouTube Shorts
        
        Args:
            video_file: Path to video file
            title: Video title (will be optimized for Shorts)
            description: Video description (will include Shorts hashtags)
            tags: List of tags (Shorts tags will be added)
            privacy_status: private, public, unlisted (default: public for Shorts)
        """
        if not self.youtube:
            raise Exception("Not authenticated! Call authenticate() first.")
            
        if not os.path.exists(video_file):
            raise FileNotFoundError(f"Video file '{video_file}' not found!")
            
        # Analyze video for Shorts compatibility
        shorts_info = self.detect_shorts_video(video_file)
        
        # Prepare Shorts-optimized metadata
        if tags is None:
            tags = []
        
        # Add Shorts-specific tags
        shorts_tags = ["Shorts", "YouTubeShorts", "Short", "Vertical", "QuickVideo", "Mobile"]
        tags.extend(shorts_tags)
        tags = list(set(tags))[:30]  # Remove duplicates and limit to 30
        
        # Optimize title for Shorts
        if not any(keyword in title.lower() for keyword in ["shorts", "short", "#shorts"]):
            title = f"{title} #Shorts"
        
        # Optimize description for Shorts
        shorts_description = description
        if shorts_description:
            shorts_description += "\n\n"
        
        shorts_description += "📱 #Shorts #YouTubeShorts #Vertical\n"
        shorts_description += "🎬 Quick entertainment for mobile viewing\n"
        
        if shorts_info.get('is_shorts'):
            shorts_description += "✅ Optimized for YouTube Shorts\n"
        else:
            shorts_description += "💡 Best viewed on mobile\n"
            if shorts_info.get('recommendations'):
                shorts_description += f"📝 Note: {shorts_info['recommendations'][0]}\n"
        
        # Add video specs to description
        if shorts_info.get('duration') != 'unknown':
            shorts_description += f"⏱️ Duration: {shorts_info['duration']:.1f}s\n"
        if shorts_info.get('file_size_mb'):
            shorts_description += f"📊 Size: {shorts_info['file_size_mb']}MB\n"
        
        # Validate and clean title
        if len(title) > 100:
            title = title[:97] + "..."
            
        # Clean description
        if len(shorts_description) > 5000:
            shorts_description = shorts_description[:4997] + "..."
            
        body = {
            'snippet': {
                'title': title,
                'description': shorts_description,
                'tags': tags,
                'categoryId': "24",  # Entertainment category for Shorts
                'defaultLanguage': 'en',
                'defaultAudioLanguage': 'en'
            },
            'status': {
                'privacyStatus': privacy_status,
                'embeddable': True,
                'license': 'youtube',
                'publicStatsViewable': True,
                'publishAt': None,  # Publish immediately
                'selfDeclaredMadeForKids': False  # Important for Shorts
            }
        }
        
        # Create media upload object
        media = MediaFileUpload(
            video_file,
            chunksize=-1,  # Upload in single chunk
            resumable=True
        )
        
        # Execute upload
        insert_request = self.youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
        
        # Upload and add Shorts info to result
        result = self._resumable_upload(insert_request)
        if result.get('success'):
            result['shorts_info'] = shorts_info
            result['shorts_optimized'] = True
            
        return result
        
    def _resumable_upload(self, insert_request):
        """Handle resumable upload with retry logic"""
        response = None
        error = None
        retry = 0
        
        while response is None:
            try:
                status, response = insert_request.next_chunk()
                if response is not None:
                    if 'id' in response:
                        # Get additional video info
                        video_id = response['id']
                        video_url = f"https://www.youtube.com/watch?v={video_id}"
                        
                        # Check if video is actually available
                        try:
                            video_info = self.youtube.videos().list(
                                part='snippet,status,processingDetails',
                                id=video_id
                            ).execute()
                            
                            if video_info['items']:
                                video_data = video_info['items'][0]
                                processing_status = video_data.get('processingDetails', {}).get('processingStatus', 'unknown')
                                upload_status = video_data.get('status', {}).get('uploadStatus', 'unknown')
                                
                                return {
                                    'success': True,
                                    'video_id': video_id,
                                    'url': video_url,
                                    'processing_status': processing_status,
                                    'upload_status': upload_status,
                                    'privacy_status': video_data.get('status', {}).get('privacyStatus', 'unknown')
                                }
                            else:
                                return {
                                    'success': False,
                                    'error': 'Video uploaded but not found in channel. May need processing time.'
                                }
                        except Exception as info_error:
                            # Still consider successful if we got video ID
                            return {
                                'success': True,
                                'video_id': video_id,
                                'url': video_url,
                                'processing_status': 'unknown',
                                'upload_status': 'uploaded',
                                'privacy_status': 'unknown',
                                'warning': f'Could not get video details: {info_error}'
                            }
                    else:
                        return {
                            'success': False,
                            'error': f"Upload failed: {response}"
                        }
                        
            except HttpError as e:
                if e.resp.status in [500, 502, 503, 504]:
                    # Retriable error
                    retry += 1
                    if retry > 5:
                        return {
                            'success': False,
                            'error': f"Max retries exceeded: {e}"
                        }
                    time.sleep(2 ** retry)
                else:
                    return {
                        'success': False,
                        'error': f"HTTP Error: {e}"
                    }
                    
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Unexpected error: {e}"
                }
                
    def check_video_status(self, video_id):
        """Check detailed video status after upload"""
        if not self.youtube:
            return {'success': False, 'error': 'Not authenticated'}
            
        try:
            # Get comprehensive video information
            response = self.youtube.videos().list(
                part='snippet,status,processingDetails,contentDetails',
                id=video_id
            ).execute()
            
            if not response['items']:
                return {
                    'success': False,
                    'error': 'Video not found - may have been removed or processing failed'
                }
                
            video = response['items'][0]
            snippet = video.get('snippet', {})
            status = video.get('status', {})
            processing = video.get('processingDetails', {})
            content = video.get('contentDetails', {})
            
            return {
                'success': True,
                'video_id': video_id,
                'title': snippet.get('title', 'Unknown'),
                'privacy_status': status.get('privacyStatus', 'unknown'),
                'upload_status': status.get('uploadStatus', 'unknown'),
                'processing_status': processing.get('processingStatus', 'unknown'),
                'processing_progress': processing.get('processingProgress', {}),
                'failure_reason': status.get('failureReason', None),
                'rejection_reason': status.get('rejectionReason', None),
                'embeddable': status.get('embeddable', False),
                'license': status.get('license', 'unknown'),
                'duration': content.get('duration', 'unknown'),
                'published_at': snippet.get('publishedAt', None),
                'channel_id': snippet.get('channelId', 'unknown')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to check video status: {str(e)}'
            }
            
    def list_recent_uploads(self, max_results=10):
        """List recent uploads from channel"""
        if not self.youtube:
            return {'success': False, 'error': 'Not authenticated'}
            
        try:
            # Get channel uploads playlist
            channels_response = self.youtube.channels().list(
                part='contentDetails',
                mine=True
            ).execute()
            
            if not channels_response['items']:
                return {'success': False, 'error': 'No channel found'}
                
            uploads_playlist_id = channels_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get recent videos from uploads playlist
            playlist_response = self.youtube.playlistItems().list(
                part='snippet,contentDetails',
                playlistId=uploads_playlist_id,
                maxResults=max_results
            ).execute()
            
            videos = []
            for item in playlist_response['items']:
                video_id = item['contentDetails']['videoId']
                video_info = self.check_video_status(video_id)
                
                if video_info['success']:
                    videos.append({
                        'video_id': video_id,
                        'title': video_info['title'],
                        'privacy_status': video_info['privacy_status'],
                        'upload_status': video_info['upload_status'],
                        'processing_status': video_info['processing_status'],
                        'published_at': video_info.get('published_at', 'unknown')
                    })
                    
            return {
                'success': True,
                'videos': videos,
                'total_found': len(videos)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to list uploads: {str(e)}'
            }
            
    def get_todays_uploads(self):
        """Get videos uploaded today from channel"""
        if not self.youtube:
            return {'success': False, 'error': 'Not authenticated'}
            
        try:
            from datetime import datetime, timezone
            
            # Get today's date range
            today = datetime.now(timezone.utc)
            today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Get channel uploads playlist
            channels_response = self.youtube.channels().list(
                part='contentDetails,snippet',
                mine=True
            ).execute()
            
            if not channels_response['items']:
                return {'success': False, 'error': 'No channel found'}
                
            channel_info = channels_response['items'][0]
            channel_title = channel_info['snippet']['title']
            uploads_playlist_id = channel_info['contentDetails']['relatedPlaylists']['uploads']
            
            # Get recent videos (last 50 to check for today's uploads)
            playlist_response = self.youtube.playlistItems().list(
                part='snippet,contentDetails',
                playlistId=uploads_playlist_id,
                maxResults=50
            ).execute()
            
            todays_videos = []
            total_checked = 0
            
            for item in playlist_response['items']:
                total_checked += 1
                video_id = item['contentDetails']['videoId']
                published_at_str = item['snippet']['publishedAt']
                
                # Parse published date
                try:
                    published_at = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
                    
                    # Check if video was published today
                    if today_start <= published_at <= today_end:
                        # Get detailed video info
                        video_info = self.check_video_status(video_id)
                        
                        if video_info['success']:
                            todays_videos.append({
                                'video_id': video_id,
                                'title': video_info['title'],
                                'privacy_status': video_info['privacy_status'],
                                'upload_status': video_info['upload_status'],
                                'processing_status': video_info['processing_status'],
                                'published_at': published_at_str,
                                'duration': video_info.get('duration', 'unknown'),
                                'failure_reason': video_info.get('failure_reason'),
                                'rejection_reason': video_info.get('rejection_reason'),
                                'url': f"https://www.youtube.com/watch?v={video_id}"
                            })
                    else:
                        # If we've gone past today, stop checking
                        if published_at < today_start:
                            break
                            
                except Exception as date_error:
                    continue
                    
            return {
                'success': True,
                'channel_title': channel_title,
                'videos': todays_videos,
                'total_today': len(todays_videos),
                'total_checked': total_checked,
                'date_range': {
                    'start': today_start.isoformat(),
                    'end': today_end.isoformat()
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get today\'s uploads: {str(e)}'
            }
        
    def get_channel_info(self):
        """Get information about the authenticated channel"""
        if not self.youtube:
            raise Exception("Not authenticated!")
            
        try:
            response = self.youtube.channels().list(
                part='snippet,statistics',
                mine=True
            ).execute()
            
            if response['items']:
                channel = response['items'][0]
                return {
                    'success': True,
                    'channel_id': channel['id'],
                    'title': channel['snippet']['title'],
                    'subscriber_count': channel['statistics'].get('subscriberCount', 'N/A'),
                    'video_count': channel['statistics'].get('videoCount', 'N/A')
                }
            else:
                return {
                    'success': False,
                    'error': 'No channel found'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
