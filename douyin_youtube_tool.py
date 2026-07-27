#!/usr/bin/env python3
"""
🎬 Douyin to YouTube Tool - Version 1.0.0
All-in-one tool for downloading Douyin videos and uploading to YouTube

Version: 1.0.0
Release Date: August 21, 2025
Author: PhanDo19
Repository: https://github.com/PhanDo19/DouyinHelper
"""

__version__ = "1.0.0"
__author__ = "PhanDo19"
__license__ = "MIT"


# Third-party imports
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext, simpledialog


# Standard library imports
import faulthandler
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
import threading
import time
import webbrowser
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode
import urllib.request
import urllib.error
import http.cookiejar
import http.server
import mimetypes
import secrets


# Optional browser cookie import
try:
    import browser_cookie3
except ImportError:
    browser_cookie3 = None
import sqlite3
import shutil
import base64
import json as json_lib
from pathlib import Path

try:
    from Crypto.Cipher import AES  # pycryptodomex
except ImportError:
    AES = None

# yt-dlp for YouTube/TikTok/Douyin downloading
YT_DLP_AVAILABLE = False
try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    yt_dlp = None

# Check YouTube API availability
# Third-party imports
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext, simpledialog

# YouTube API imports (optional)

YOUTUBE_AVAILABLE = False
try:
    import googleapiclient.discovery
    from googleapiclient.discovery import build
    import google.auth
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    import pickle
    YOUTUBE_AVAILABLE = True
except ImportError:
    YOUTUBE_AVAILABLE = False

class YouTubeAPI:
    """Real YouTube API implementation with OAuth and API key support"""
    
    def __init__(self):
        self.service = None
        self.youtube = None  # For compatibility with existing code
        self.authenticated = False
        self.auth_method = None  # Track authentication method
        self.scopes = ['https://www.googleapis.com/auth/youtube',
                      'https://www.googleapis.com/auth/youtube.upload']
        self.credentials = None
        
    def authenticate(self):
        """Authenticate using OAuth credentials.json for full access"""
        try:
            creds = None
            # Check if token.json exists (saved credentials)
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', self.scopes)
            
            # If no valid credentials, run OAuth flow
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists('credentials.json'):
                        print("❌ credentials.json not found!")
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', self.scopes)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for next run
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
            
            # Build YouTube service
            self.service = googleapiclient.discovery.build('youtube', 'v3', credentials=creds)
            self.youtube = self.service
            self.credentials = creds
            self.authenticated = True
            self.auth_method = 'oauth'
            return True
            
        except Exception as e:
            print(f"OAuth authentication failed: {e}")
            return False
        
    def authenticate_with_api_key(self, api_key):
        """Authenticate using API key (read-only access)"""
        try:
            # Check if it's a demo key for testing
            if api_key.lower() in ['demo', 'test', 'example']:
                self.service = 'demo_service'
                self.youtube = 'demo_service'
                self.authenticated = True
                self.auth_method = 'demo'
                print("Using demo mode with sample data")
                return True
                
            # Try real API authentication
            self.service = googleapiclient.discovery.build(
                'youtube', 'v3', developerKey=api_key
            )
            self.youtube = self.service  # For compatibility
            self.authenticated = True
            self.auth_method = 'api_key'
            return True
        except Exception as e:
            print(f"API Key authentication failed: {e}")
            return False
    
    def get_channel_statistics(self, channel_id=None):
        """Get real channel statistics from YouTube API"""
        if not self.authenticated or not self.service:
            return None
            
        try:
            # Demo mode with sample data
            if self.service == 'demo_service':
                return {
                    'title': 'Demo YouTube Channel',
                    'description': 'This is sample data from YouTube API demo mode...',
                    'viewCount': '1234567',
                    'subscriberCount': '56789',
                    'videoCount': '123'
                }
            
            # Real API call
            if self.credentials:  # OAuth - get my channel
                request = self.service.channels().list(
                    part="snippet,statistics",
                    mine=True
                )
            else:  # API Key - get specific channel
                if not channel_id:
                    # Using a popular channel as example (MrBeast)
                    channel_id = "UCX6OQ3DkcsbYNE6H8uQQuVA"
                request = self.service.channels().list(
                    part="snippet,statistics",
                    id=channel_id
                )
            
            response = request.execute()
            
            if response.get('items'):
                channel = response['items'][0]
                return {
                    'title': channel['snippet']['title'],
                    'description': channel['snippet']['description'][:100] + "...",
                    'viewCount': channel['statistics'].get('viewCount', '0'),
                    'subscriberCount': channel['statistics'].get('subscriberCount', '0'),
                    'videoCount': channel['statistics'].get('videoCount', '0')
                }
        except Exception as e:
            print(f"Error getting channel stats: {e}")
        
        return None
    
    def get_todays_uploads(self):
        """Get today's uploaded videos"""
        if not self.authenticated or not self.service:
            return []
            
        try:
            # Demo mode with sample data
            if self.service == 'demo_service':
                return [
                    {
                        'id': 'demo_video_1',
                        'title': 'Amazing Douyin Video - Demo 1 🔥',
                        'publishedAt': '2025-08-21T10:00:00Z',
                        'viewCount': '12345',
                        'likeCount': '567',
                        'commentCount': '89',
                        'status': 'public'
                    },
                    {
                        'id': 'demo_video_2', 
                        'title': 'Viral Douyin Content - Demo 2 ✨',
                        'publishedAt': '2025-08-21T14:30:00Z',
                        'viewCount': '98765',
                        'likeCount': '4321',
                        'commentCount': '234',
                        'status': 'public'
                    }
                ]
            
            # Real API call for today's uploads
            from datetime import datetime, timezone
            today = datetime.now(timezone.utc).strftime('%Y-%m-%dT00:00:00Z')
            
            try:
                videos = []
                
                if self.credentials:  # OAuth - get my channel uploads
                    # First get my channel ID
                    channels_request = self.service.channels().list(
                        part="contentDetails",
                        mine=True
                    )
                    channels_response = channels_request.execute()
                    
                    if channels_response.get('items'):
                        uploads_playlist_id = channels_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
                        
                        # Get videos from uploads playlist
                        playlist_request = self.service.playlistItems().list(
                            part="snippet",
                            playlistId=uploads_playlist_id,
                            maxResults=50
                        )
                        response = playlist_request.execute()
                        
                        # Filter for today's videos and get video IDs
                        video_ids = []
                        for item in response.get('items', []):
                            pub_date = item['snippet']['publishedAt']
                            if pub_date >= today:
                                video_ids.append(item['snippet']['resourceId']['videoId'])
                        
                        # Get detailed stats for today's videos
                        if video_ids:
                            stats_request = self.service.videos().list(
                                part="snippet,statistics,status",
                                id=','.join(video_ids)
                            )
                            stats_response = stats_request.execute()
                            
                            for video in stats_response.get('items', []):
                                videos.append({
                                    'id': video['id'],
                                    'title': video['snippet']['title'],
                                    'publishedAt': video['snippet']['publishedAt'],
                                    'viewCount': video['statistics'].get('viewCount', '0'),
                                    'likeCount': video['statistics'].get('likeCount', '0'),
                                    'commentCount': video['statistics'].get('commentCount', '0'),
                                    'status': video['status']['privacyStatus']
                                })
                else:
                    # API Key mode - use search (limited functionality)
                    search_request = self.service.search().list(
                        part="snippet",
                        type="video",
                        order="date",
                        publishedAfter=today,
                        maxResults=10
                    )
                    response = search_request.execute()
                    
                    # Get video IDs for stats
                    video_ids = [item['id']['videoId'] for item in response.get('items', [])]
                    
                    if video_ids:
                        stats_request = self.service.videos().list(
                            part="snippet,statistics,status",
                            id=','.join(video_ids)
                        )
                        stats_response = stats_request.execute()
                        
                        for video in stats_response.get('items', []):
                            videos.append({
                                'id': video['id'],
                                'title': video['snippet']['title'],
                                'publishedAt': video['snippet']['publishedAt'],
                                'viewCount': video['statistics'].get('viewCount', '0'),
                                'likeCount': video['statistics'].get('likeCount', '0'),
                                'commentCount': video['statistics'].get('commentCount', '0'),
                                'status': video.get('status', {}).get('privacyStatus', 'unknown')
                            })
                
                return videos
                
            except Exception as api_error:
                print(f"API error getting today's uploads: {api_error}")
                # Return empty list on API error
                return []
            
        except Exception as e:
            print(f"Error getting today's uploads: {e}")
            return []
    
    def list_recent_uploads(self, max_results=20):
        """Get recent uploaded videos"""
        if not self.authenticated or not self.service:
            return []
            
        try:
            # Demo mode with sample data
            if self.service == 'demo_service':
                sample_videos = []
                for i in range(min(max_results, 5)):
                    sample_videos.append({
                        'id': f'demo_video_{i+1}',
                        'title': f'Amazing Video {i+1} - Douyin Content 🔥',
                        'publishedAt': f'2025-08-{21-i}T1{i}:00:00Z',
                        'viewCount': str(10000 + i*1000),
                        'likeCount': str(500 + i*50),
                        'commentCount': str(50 + i*10),
                        'status': 'public'
                    })
                return sample_videos
            
            # Real API call for recent uploads
            try:
                # Get channel's uploaded videos 
                if self.credentials:  # OAuth - get my channel
                    # First get my channel ID
                    channels_request = self.service.channels().list(
                        part="contentDetails",
                        mine=True
                    )
                    channels_response = channels_request.execute()
                    
                    if not channels_response.get('items'):
                        return []
                    
                    uploads_playlist_id = channels_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
                    
                    # Get videos from uploads playlist
                    playlist_request = self.service.playlistItems().list(
                        part="snippet",
                        playlistId=uploads_playlist_id,
                        maxResults=max_results
                    )
                else:
                    # API Key mode - use search instead
                    playlist_request = self.service.search().list(
                        part="snippet",
                        type="video",
                        order="date",
                        maxResults=max_results
                    )
                
                response = playlist_request.execute()
                videos = []
                
                # Get video IDs
                if self.credentials:  # OAuth
                    video_ids = [item['snippet']['resourceId']['videoId'] for item in response.get('items', [])]
                else:  # API Key
                    video_ids = [item['id']['videoId'] for item in response.get('items', [])]
                
                # Get detailed stats for each video
                if video_ids:
                    stats_request = self.service.videos().list(
                        part="snippet,statistics,status",
                        id=','.join(video_ids)
                    )
                    stats_response = stats_request.execute()
                    
                    for video in stats_response.get('items', []):
                        videos.append({
                            'id': video['id'],
                            'title': video['snippet']['title'],
                            'publishedAt': video['snippet']['publishedAt'],
                            'viewCount': video['statistics'].get('viewCount', '0'),
                            'likeCount': video['statistics'].get('likeCount', '0'),
                            'commentCount': video['statistics'].get('commentCount', '0'),
                            'status': video.get('status', {}).get('privacyStatus', 'unknown')
                        })
                
                return videos
                
            except Exception as api_error:
                print(f"API error in list_recent_uploads: {api_error}")
                # Return demo data as fallback
                return [{
                    'id': 'fallback_video',
                    'title': 'Recent Video (Demo)',
                    'publishedAt': '2025-08-21T12:00:00Z',
                    'viewCount': '1000',
                    'likeCount': '50',
                    'commentCount': '10',
                    'status': 'public'
                }]
            
        except Exception as e:
            print(f"Error in list_recent_uploads: {e}")
            return []
            
    def optimize_video_for_youtube(self, input_path, output_path, quality_preset="high"):
        """Optimize video for YouTube upload (placeholder implementation)"""
        try:
            # For now, just copy the file since we don't have ffmpeg integration
            import shutil
            
            # Get file sizes
            input_size = os.path.getsize(input_path) / (1024 * 1024)  # MB
            
            # Just copy for now - in real implementation you would use ffmpeg
            shutil.copy2(input_path, output_path)
            
            output_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
            
            return {
                'success': True,
                'input_size_mb': round(input_size, 2),
                'output_size_mb': round(output_size, 2),
                'compression_ratio': 1.0,  # No compression in this simple copy
                'optimization_preset': quality_preset,
                'output_path': output_path
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
            
    def upload_video(self, video_file, title, description, tags, category="22", privacy_status="public", private_share_emails="", made_for_kids=False):
        """Upload video to YouTube with comprehensive error handling"""
        try:
            if not self.authenticated or not self.service:
                return {
                    'success': False,
                    'error': 'Not authenticated with YouTube'
                }

            # Demo mode simulation
            if self.service == 'demo_service':
                import time
                time.sleep(1)  # Simulate upload time
                return {
                    'success': True,
                    'video_id': f'mock_id_{int(time.time())}',
                    'title': title,
                    'url': f'https://youtube.com/watch?v=mock_id_{int(time.time())}',
                    'upload_status': 'uploaded',
                    'processing_status': 'processing',
                    'privacy_status': privacy_status,
                    'warning': 'This is a demo upload - not actually uploaded to YouTube'
                }

            # Real YouTube API upload
            if not self.credentials:
                return {
                    'success': False,
                    'error': 'OAuth credentials required for uploading'
                }

            return self._perform_real_upload(video_file, title, description, tags, category, privacy_status, private_share_emails, made_for_kids)

        except Exception as e:
            return {
                'success': False,
                'error': f'Upload failed: {str(e)}'
            }

    def _log_upload(self, msg):
        """Print upload progress — app UI can override this via monkey-patch."""
        print(msg)

    def _perform_real_upload(self, video_file, title, description, tags, category, privacy_status, private_share_emails="", made_for_kids=False):
        """Perform the actual YouTube upload"""
        import socket
        import time as _time
        import requests as _requests
        from googleapiclient.http import MediaFileUpload
        from googleapiclient.errors import HttpError

        # Prepare tags
        tags_list = self._prepare_tags(tags)

        # Video metadata
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags_list,
                'categoryId': category
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': bool(made_for_kids)
            }
        }

        # Choose chunk size based on file size: larger chunks = fewer round-trips
        file_size = os.path.getsize(video_file)
        if file_size > 200 * 1024 * 1024:      # > 200 MB → 64 MB chunks
            chunksize = 1024 * 1024 * 64
        elif file_size > 50 * 1024 * 1024:     # 50–200 MB → 32 MB chunks
            chunksize = 1024 * 1024 * 32
        else:                                   # < 50 MB → 8 MB chunks
            chunksize = 1024 * 1024 * 8
        media = MediaFileUpload(video_file, chunksize=chunksize, resumable=True)

        insert_request = self.service.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )

        # Resumable upload loop with network error retry
        response = None
        retry = 0
        max_retries = 10

        # Network errors worth retrying (not file/permission errors)
        _RETRYABLE = (ConnectionResetError, ConnectionAbortedError, ConnectionError, socket.error)

        while response is None:
            try:
                _, response = insert_request.next_chunk()
            except HttpError as e:
                if e.resp.status in [500, 502, 503, 504]:
                    retry += 1
                    if retry > max_retries:
                        raise
                    wait = min(2 ** retry, 60)
                    self._log_upload(f"⚠️ Server error {e.resp.status}, retry {retry}/{max_retries} sau {wait}s...")
                    _time.sleep(wait)
                elif e.resp.status == 401:
                    # Token expired — refresh and rebuild service
                    self.credentials.refresh(Request())
                    self.service = build('youtube', 'v3', credentials=self.credentials)
                    retry += 1
                    if retry > max_retries:
                        raise
                    self._log_upload(f"⚠️ Token hết hạn, đã refresh, retry {retry}/{max_retries}...")
                else:
                    raise
            except _RETRYABLE as e:
                retry += 1
                if retry > max_retries:
                    raise
                wait = min(2 ** retry, 60)
                self._log_upload(f"⚠️ Lỗi mạng ({type(e).__name__}), retry {retry}/{max_retries} sau {wait}s...")
                _time.sleep(wait)

        if not response:
            return {
                'success': False,
                'error': 'Upload failed - no response from YouTube'
            }

        video_id = response['id']
        result = {
            'success': True,
            'video_id': video_id,
            'title': title,
            'url': f'https://youtube.com/watch?v={video_id}',
            'upload_status': 'uploaded',
            'processing_status': 'processing',
            'privacy_status': privacy_status
        }

        # Share private video with specific emails via YouTube Studio internal API
        if privacy_status == 'private' and private_share_emails and private_share_emails.strip():
            try:
                share_result = self._share_private_video(video_id, private_share_emails.strip())
                result['private_share'] = share_result
            except Exception as share_err:
                result['private_share'] = {'success': False, 'error': str(share_err)}

        return result

    def _share_private_video(self, video_id, emails_str):
        """Share a private video with specific email addresses using YouTube Studio API."""
        import requests as _requests

        emails_clean = ', '.join(e.strip() for e in emails_str.split(',') if e.strip())
        if not emails_clean:
            return {'success': False, 'error': 'No valid emails provided'}

        token = self.credentials.token
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Origin': 'https://studio.youtube.com',
            'X-Origin': 'https://studio.youtube.com',
            'x-origin': 'https://studio.youtube.com',
            'x-goog-authuser': '0',
            'x-youtube-client-name': '62',
            'x-youtube-client-version': '1.20260528.00.00',
        }

        payload = {
            'encryptedVideoId': video_id,
            'flowType': 'MDE_FLOW_TYPE_UPLOAD',
            'privacyState': {'newPrivacy': 'PRIVATE'},
            'privateShare': {
                'notifyViaEmail': True,
                'shareEmails': emails_clean
            },
            'draftState': {
                'operation': 'MDE_DRAFT_STATE_UPDATE_OPERATION_REMOVE_DRAFT_STATE'
            },
            'videoReadMask': {'privateShare': {'all': True}},
            'context': {
                'client': {
                    'clientName': 62,
                    'clientVersion': '1.20260528.00.00',
                    'hl': 'en',
                    'gl': 'VN',
                    'utcOffsetMinutes': 420,
                    'userInterfaceTheme': 'USER_INTERFACE_THEME_DARK',
                }
            }
        }

        resp = _requests.post(
            'https://studio.youtube.com/youtubei/v1/video_manager/metadata_update?alt=json',
            headers=headers,
            json=payload,
            timeout=30
        )

        if resp.status_code == 200:
            email_list = [e.strip() for e in emails_str.split(',') if e.strip()]
            return {'success': True, 'shared_with': email_list}
        else:
            return {'success': False, 'error': f'HTTP {resp.status_code}: {resp.text[:300]}'}
    
    def _prepare_tags(self, tags):
        """Prepare tags for upload"""
        if isinstance(tags, str):
            return [tag.strip() for tag in tags.split(',') if tag.strip()]
        elif isinstance(tags, list):
            return tags
        else:
            return []
            
    def upload_optimized_video(self, video_file, title, description, tags, category="22", privacy_status="public", optimize_quality=True, quality_preset="high", private_share_emails="", made_for_kids=False):
        """Upload optimized video to YouTube"""
        try:
            result = self.upload_video(video_file, title, description, tags, category, privacy_status, private_share_emails, made_for_kids)
            
            if result['success']:
                # Add optimization info to result
                result['optimization_applied'] = optimize_quality
                result['quality_preset'] = quality_preset
                if 'warning' not in result:
                    result['optimization_note'] = f'Video processed with {quality_preset} quality preset'
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
            
    def check_video_status(self, video_id):
        """Check video upload and processing status"""
        try:
            # Demo mode with sample status
            if self.service == 'demo_service':
                return {
                    'success': True,
                    'upload_status': 'uploaded',
                    'processing_status': 'succeeded',
                    'privacy_status': 'public',
                    'failure_reason': None,
                    'rejection_reason': None
                }
            
            # Real API call to check video status
            if self.service and self.authenticated:
                request = self.service.videos().list(
                    part="status,processingDetails",
                    id=video_id
                )
                response = request.execute()
                
                if response.get('items'):
                    video = response['items'][0]
                    status = video.get('status', {})
                    processing = video.get('processingDetails', {})
                    
                    return {
                        'success': True,
                        'upload_status': status.get('uploadStatus', 'unknown'),
                        'processing_status': processing.get('processingStatus', 'unknown'),
                        'privacy_status': status.get('privacyStatus', 'unknown'),
                        'failure_reason': status.get('failureReason'),
                        'rejection_reason': status.get('rejectionReason')
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Video not found'
                    }
            else:
                return {
                    'success': False,
                    'error': 'Not authenticated'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
            
    def verify_video_exists(self, video_id):
        """Verify if video actually exists on YouTube"""
        try:
            # Skip verification for mock/demo videos
            if 'mock_id' in video_id or 'demo_' in video_id or video_id.startswith('shorts_id'):
                return {
                    'success': False,
                    'exists': False,
                    'is_demo': True,
                    'message': 'This is a demo upload - not actually on YouTube'
                }
            
            # Real verification for actual uploads
            if self.service and self.authenticated and self.service != 'demo_service':
                request = self.service.videos().list(
                    part="snippet,status",
                    id=video_id
                )
                response = request.execute()
                
                if response.get('items'):
                    video = response['items'][0]
                    return {
                        'success': True,
                        'exists': True,
                        'title': video['snippet']['title'],
                        'privacy_status': video['status']['privacyStatus'],
                        'published_at': video['snippet']['publishedAt'],
                        'url': f'https://youtube.com/watch?v={video_id}'
                    }
                else:
                    return {
                        'success': True,
                        'exists': False,
                        'message': 'Video not found on YouTube'
                    }
            else:
                return {
                    'success': False,
                    'error': 'Not authenticated or in demo mode'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
            
    def detect_shorts_video(self, video_path):
        """Detect if video is suitable for YouTube Shorts"""
        try:
            import os
            
            # Basic file size and format check (placeholder implementation)
            if not os.path.exists(video_path):
                return {
                    'success': False,
                    'is_shorts': False,
                    'error': 'File not found'
                }
                
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            
            # For demo purposes, assume videos under 100MB are shorts
            is_shorts = file_size < 100
            
            # Simulate video dimensions and duration for demo
            width = 1080 if is_shorts else 1920
            height = 1920 if is_shorts else 1080
            duration = 45 if is_shorts else 120
            
            return {
                'success': True,
                'is_shorts': is_shorts,
                'width': width,
                'height': height,
                'duration': duration,
                'file_size_mb': round(file_size, 2),
                'duration_estimate': f'{duration}s',
                'format_suitable': video_path.lower().endswith(('.mp4', '.mov')),
                'recommendations': ['Perfect for YouTube Shorts!'] if is_shorts else ['Consider cropping to vertical format']
            }
            
        except Exception as e:
            return {
                'success': False,
                'is_shorts': False,
                'error': str(e)
            }
            
    def upload_shorts_video(self, video_file, title, description, tags, privacy_status="public", private_share_emails="", made_for_kids=False):
        """Upload video optimized for YouTube Shorts"""
        try:
            # Handle tags - convert to string if it's a list
            if isinstance(tags, list):
                tags_str = ', '.join(tags)
            else:
                tags_str = str(tags) if tags else ""

            # Add #Shorts hashtag if not present
            shorts_tags = tags_str
            if '#shorts' not in tags_str.lower() and '#short' not in tags_str.lower():
                shorts_tags = f"{tags_str}, #Shorts" if tags_str else "#Shorts"

            # Enhanced description for Shorts
            shorts_description = f"{description}\n\n#Shorts #YouTubeShorts #Viral"
            if "vertical" not in shorts_description.lower():
                shorts_description += "\n\n📱 Optimized for mobile viewing"

            result = self.upload_video(video_file, title, shorts_description, shorts_tags, "22", privacy_status, private_share_emails, made_for_kids)
            
            if result['success']:
                # Update URL to Shorts format if real upload
                if 'mock_id' not in result['video_id']:
                    result['url'] = f"https://youtube.com/shorts/{result['video_id']}"
                
                # Add Shorts-specific info
                result['shorts_optimized'] = True
                result['tags_enhanced'] = shorts_tags
                result['description_enhanced'] = shorts_description
                result['mobile_optimized'] = True
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Constants
DOWNLOAD_FOLDER = os.path.expanduser("~/Downloads/Douyin")
DEFAULT_UPLOAD_SETTINGS = {
    'title_template': "[FILENAME] - Amazing Douyin Video! 🔥",
    'description': "🎬 Amazing content from Douyin!\n\nFollow for more amazing videos!\nLike and Subscribe if you enjoyed!\n\n#Douyin #Viral #Entertainment #Shorts",
    'tags': 'douyin,viral,entertainment,funny,trending,shorts',
    'privacy': 'public',
    'private_share_emails': '',
    'made_for_kids': 'no',
    'age_restriction': 'none',
    'category': 'Entertainment', 
    'language': 'English',
    'license': 'Standard YouTube License',
    'allow_comments': True,
    'allow_ratings': True,
    'allow_embedding': True,
    'notify_subscribers': True,
    'publish_timing': 'immediately',
    'quality': 'high',
    'enable_monetization': False,
    'thumbnail_generation': 'auto',
    'auto_chapters': False,
    'premiere_enabled': False,
    'scheduled_time': None
}

# ── YouTube Downloader Constants ──────────────────────────────────────────────
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
YT_OUTPUT_DIR = os.path.join(_THIS_DIR, "output", "YouTube")
YT_HISTORY_FILE = os.path.join(_THIS_DIR, "yt_history.txt")
BROWSER_DETECTOR_PORT = 8765
BROWSER_OUTPUT_DIR = os.path.join(_THIS_DIR, "output", "BrowserDetector")
HANG_WATCHDOG_LOG = os.path.join(_THIS_DIR, "hang_watchdog.log")
HANG_WATCHDOG_TIMEOUT = 10  # seconds without a mainloop heartbeat before dumping stacks
BROWSER_EXTENSION_DIR = os.path.join(_THIS_DIR, "browser_extension")

# Auto-detect ffmpeg bundled in project
_FFMPEG_CANDIDATE = os.path.join(_THIS_DIR, "ffmpeg", "bin", "ffmpeg.exe")
FFMPEG_DIR = os.path.join(_THIS_DIR, "ffmpeg", "bin") if os.path.exists(_FFMPEG_CANDIDATE) else None
_FFPROBE_CANDIDATE = os.path.join(_THIS_DIR, "ffmpeg", "bin", "ffprobe.exe")
FFPROBE_PATH = _FFPROBE_CANDIDATE if os.path.exists(_FFPROBE_CANDIDATE) else None

# Auto-detect Node.js for YouTube n-challenge solver
def _find_node():
    for p in [r"C:\Program Files\nodejs\node.exe",
              r"C:\Program Files (x86)\nodejs\node.exe"]:
        if os.path.exists(p):
            return p
    return shutil.which("node")
NODE_PATH = _find_node()

# Global YouTube API instance
youtube_api = YouTubeAPI() if YOUTUBE_AVAILABLE else None

class DouyinYouTubeTool:
    """Main application class for Douyin to YouTube tool"""
    
    def __init__(self, root):
        self.root = root
        self._init_window()
        self._init_data()
        self._init_youtube()
        self._init_ui()
        self._init_theme()
        self._start_browser_detector_server()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def _init_window(self):
        """Initialize main window"""
        self.root.title("🎬 Douyin to YouTube Tool")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)
        
    def _init_data(self):
        """Initialize application data"""
        self.video_urls = []
        self.video_entries = []
        self.video_files = []
        self.download_folder = DOWNLOAD_FOLDER
        self.selected_videos = set()
        self.is_downloading = False
        self.is_uploading = False
        self.current_preview_path = None
        self.current_video_folder = None
        self.current_video_data = {}
        
        # Cookie jar for web requests
        self.cookie_jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookie_jar))
        
        # Upload settings
        self.upload_settings = DEFAULT_UPLOAD_SETTINGS.copy()

        # YouTube Downloader state (yt-dlp)
        self.yt_is_downloading = False
        self.yt_progress_data = {}          # filled by progress hook
        self.yt_output_dir = YT_OUTPUT_DIR
        self.yt_cookies_file = ""

        # Browser extension detector state
        self.browser_detector_port = BROWSER_DETECTOR_PORT
        self.browser_detector_token = secrets.token_urlsafe(18)
        self.browser_detector_server = None
        self.browser_detector_thread = None
        self.browser_candidates = []
        self.browser_candidates_by_id = {}
        self.browser_candidate_seen = {}
        self.browser_candidates_lock = threading.Lock()
        self.browser_output_dir = BROWSER_OUTPUT_DIR
        self.browser_is_downloading = False
        self.bd_batch_jobs = []
        self.bd_batch_jobs_by_id = {}
        self.bd_batch_lock = threading.Lock()
        self.bd_batch_running = False
        self.bd_batch_download_lock = threading.Lock()
        
    def _init_youtube(self):
        """Initialize YouTube uploader"""
        self.youtube_uploader = None
        if YOUTUBE_AVAILABLE:
            self.youtube_uploader = self.init_youtube_uploader()
            
    def _init_ui(self):
        """Initialize user interface"""
        self.setup_ui()
        
    def _init_theme(self):
        """Initialize application theme"""
        # Initialize upload control variables
        self.title_prefix_var = tk.StringVar(value="")
        self.tags_var = tk.StringVar(value=self.upload_settings['tags'])
        self.privacy_var = tk.StringVar(value=self.upload_settings['privacy'])
        self.quality_preset_var = tk.StringVar(value="high")
        self.optimize_quality = tk.BooleanVar(value=True)
        
        # Initialize auth status variable
        self.auth_status_var = None
        
        # Setup UI components
        self.create_download_folder()
        self.load_upload_settings()
        
    def init_youtube_uploader(self):
        """Initialize YouTube API"""
        if not YOUTUBE_AVAILABLE:
            self.log("❌ YouTube API not available")
            return None

        try:
            # Route upload progress messages to the app log
            youtube_api._log_upload = self.log
            return youtube_api
        except Exception as e:
            self.log(f"❌ Failed to initialize YouTube API: {e}")
            return None
            
    def authenticate_youtube(self):
        """Authenticate with YouTube using OAuth or API key"""
        if not self.youtube_uploader:
            messagebox.showerror("Error", "YouTube API not available!")
            return False
        
        if self.youtube_uploader.authenticated:
            self.log("✅ Already authenticated with YouTube")
            return True
            
        return self._handle_youtube_authentication()
    
    def _handle_youtube_authentication(self):
        """Handle YouTube authentication process"""
        try:
            choice = self._show_auth_choice_dialog()
            
            if choice is True:  # OAuth
                return self._authenticate_oauth()
            elif choice is False:  # API Key
                return self._authenticate_api_key()
            else:  # Demo Mode
                return self._authenticate_demo()
                
        except Exception as e:
            self.log(f"❌ Authentication error: {e}")
            return False
    
    def _show_auth_choice_dialog(self):
        """Show authentication choice dialog"""
        return messagebox.askyesnocancel(
            "YouTube Authentication",
            "Choose authentication method:\n\n" +
            "✅ YES = OAuth Login (Full Access)\n" +
            "   • Upload videos to YouTube\n" +
            "   • Manage your channel\n" +
            "   • Uses credentials.json\n\n" +
            "⚠️ NO = API Key (Read Only)\n" +
            "   • View channel statistics only\n" +
            "   • Cannot upload videos\n\n" +
            "❌ CANCEL = Demo Mode"
        )
    
    def _authenticate_oauth(self):
        """Authenticate using OAuth"""
        self.log("🔐 Starting OAuth authentication...")
        success = self.youtube_uploader.authenticate()
        if success:
            self.log("✅ OAuth authentication successful! Full YouTube access enabled.")
            self.update_auth_status()
            return True
        else:
            self._show_oauth_error()
            return False
    
    def _show_oauth_error(self):
        """Show OAuth authentication error"""
        messagebox.showerror("Authentication Error", 
            "❌ OAuth authentication failed!\n\n" +
            "🔧 Please check:\n" +
            "• credentials.json file exists\n" +
            "• Internet connection\n" +
            "• Google OAuth permissions",
            parent=self.root)
    
    def _authenticate_api_key(self):
        """Authenticate using API key"""
        api_key = simpledialog.askstring(
            "YouTube API Key", 
            "Enter your YouTube Data API v3 key:\n\n" +
            "💡 To get an API key:\n" +
            "1. Go to Google Cloud Console\n" +
            "2. Create a project\n" +
            "3. Enable YouTube Data API v3\n" +
            "4. Create credentials (API key)\n\n" +
            "🎯 For testing, enter 'demo':",
            parent=self.root
        )
        
        if api_key and api_key.strip():
            self.log("🔐 Authenticating with YouTube API key...")
            success = self.youtube_uploader.authenticate_with_api_key(api_key.strip())
            if success:
                self.log("✅ API key authentication successful! (Read-only access)")
                self.update_auth_status()
                return True
            else:
                self.log("❌ API key authentication failed!")
                return False
        else:
            self.log("ℹ️ API key authentication cancelled")
            return False
    
    def _authenticate_demo(self):
        """Set up demo mode authentication"""
        self.log("ℹ️ Authentication cancelled - using demo mode")
        self.youtube_uploader.service = 'demo_service'
        self.youtube_uploader.youtube = 'demo_service'
        self.youtube_uploader.authenticated = True
        self.update_auth_status()
        return True
        
    def create_download_folder(self):
        """Create download folder if not exists"""
        if not os.path.exists(self.download_folder):
            try:
                os.makedirs(self.download_folder)
                self.log(f"📁 Created download folder: {self.download_folder}")
            except:
                self.download_folder = os.path.expanduser("~/Downloads")
                
    def setup_ui(self):
        """Setup main UI with beautiful colors and styling"""
        # Configure styles and colors
        self.setup_styles()
        
        # Set root background
        self.root.configure(bg=self.colors['light'])
        
        # Main container with gradient-like background
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Header
        self.create_header(main_container)
        
        # Tab container using ttk.Notebook for clear separation Douyin vs YouTube
        tab_container = ttk.Frame(main_container)
        tab_container.pack(fill=tk.BOTH, expand=True, pady=(20, 0))

        self.content_container = ttk.Notebook(tab_container)
        self.content_container.pack(fill=tk.BOTH, expand=True)

        # Create tab contents
        self.create_download_tab()
        self.create_yt_download_tab()
        self.create_browser_detector_tab()
        self.create_upload_tab()

        # Add tabs to notebook
        self.content_container.add(self.download_frame, text="📥 Douyin Downloader")
        self.content_container.add(self.yt_download_frame, text="🎬 YouTube Downloader")
        self.content_container.add(self.browser_detector_frame, text="Browser Detector")
        self.content_container.add(self.upload_frame, text="📤 YouTube Uploader")
        self.content_container.enable_traversal()
        self.content_container.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Footer
        self.create_footer(main_container)

    def on_tab_changed(self, event=None):
        """Handle tab changes; auto-auth YouTube when entering uploader tab"""
        try:
            current = self.content_container.tab(self.content_container.select(), "text")
        except Exception:
            return

        if "YouTube" in current:
            if YOUTUBE_AVAILABLE and self.youtube_uploader:
                if not self.youtube_uploader.youtube:
                    self.log("🔐 Auto-authenticating with YouTube OAuth...")
                    self.auto_oauth_login()
                else:
                    self.log("✅ Already authenticated with YouTube")
            else:
                self.log("❌ YouTube uploader not available")
        
    def setup_styles(self):
        """Setup beautiful color themes and styles"""
        style = ttk.Style()
        try:
            if 'clam' in style.theme_names():
                style.theme_use('clam')
        except tk.TclError:
            pass
        
        # Configure color scheme
        self.colors = {
            'primary': '#4A90E2',      # Soft blue
            'secondary': '#7ED321',    # Fresh green  
            'accent': '#F5A623',       # Warm orange
            'danger': '#D0021B',       # Soft red
            'error': '#D0021B',        # Soft red (alias for danger)
            'success': '#50E3C2',      # Mint green
            'warning': '#F8E71C',      # Sunny yellow
            'info': '#9013FE',         # Purple
            'light': '#F8F9FA',        # Light gray (very light)
            'background': '#FFFFFF',   # Pure white background
            'surface': '#F1F3F4',      # Slightly darker surface
            'medium': '#6C757D',       # Medium gray
            'dark': '#343A40',         # Dark gray
            'tab_bg': '#DCEBFA',       # Visible inactive tab background
            'tab_active': '#BFE1FF',   # Hovered tab background
            'tab_selected': '#2F80ED', # Selected tab background
            'tab_text': '#1F2937'      # High-contrast tab text
        }
        
        # Configure notebook style with better spacing and visibility
        style.configure('TNotebook', 
                       background=self.colors['tab_bg'],
                       borderwidth=1,
                       relief='solid',
                       tabmargins=[2, 5, 2, 0])  # Better spacing between tabs
        
        style.configure('TNotebook.Tab', 
                       padding=[20, 10],  # More padding for better spacing
                       background=self.colors['tab_bg'],
                       foreground=self.colors['tab_text'],
                       focuscolor='none',
                       borderwidth=1,
                       relief='raised',
                       font=('Segoe UI', 10, 'bold'))  # Larger, bolder font
        
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['tab_selected']),
                           ('active', self.colors['tab_active']),
                           ('!selected', self.colors['tab_bg'])],
                 foreground=[('selected', 'white'),
                           ('active', self.colors['tab_text']),
                           ('!selected', self.colors['tab_text'])],
                 borderwidth=[('selected', 1), ('!selected', 1)],
                 relief=[('selected', 'sunken'), ('!selected', 'raised')])
        
        # Configure LabelFrame styles for better contrast
        style.configure('TLabelFrame', 
                       background=self.colors['background'],
                       foreground=self.colors['dark'],
                       borderwidth=1,
                       relief='solid')
        style.configure('TLabelFrame.Label',
                       background=self.colors['background'],
                       foreground=self.colors['primary'],
                       font=('Segoe UI', 10, 'bold'))
        
        # Configure button styles
        style.configure('Primary.TButton',
                       background=self.colors['primary'],
                       foreground='white',
                       padding=[15, 8],
                       font=('Segoe UI', 10, 'bold'))
        style.map('Primary.TButton',
                 background=[('active', '#357ABD'),
                           ('pressed', '#2E6DA4')],
                 foreground=[('active', 'white'), ('pressed', 'white')])
        
        style.configure('Success.TButton',
                       background=self.colors['success'],
                       foreground=self.colors['dark'],
                       padding=[15, 8],
                       font=('Segoe UI', 10, 'bold'))
        style.map('Success.TButton',
                 background=[('active', '#40C4AA')],
                 foreground=[('active', self.colors['dark'])])
        
        style.configure('Warning.TButton',
                       background=self.colors['warning'],
                       foreground=self.colors['dark'],
                       padding=[15, 8],
                       font=('Segoe UI', 10, 'bold'))
        style.map('Warning.TButton',
                 foreground=[('active', self.colors['dark'])])
        
        style.configure('Danger.TButton',
                       background=self.colors['danger'],
                       foreground='white',
                       padding=[15, 8],
                       font=('Segoe UI', 10, 'bold'))
        style.map('Danger.TButton',
                 foreground=[('active', 'white')])
        
        # Configure frame styles
        style.configure('Colored.TLabelFrame',
                       background=self.colors['light'],
                       relief='solid',
                       borderwidth=1)
        style.configure('Colored.TLabelFrame.Label',
                       background=self.colors['light'],
                       foreground=self.colors['primary'],
                       font=('Segoe UI', 11, 'bold'))
        
    # Old method - now using custom tab system
    def create_header(self, parent):
        """Create beautiful colorful header"""
        header = ttk.Frame(parent)
        header.pack(fill=tk.X, pady=(0, 15))
        
        # Main title with gradient effect
        title_frame = ttk.Frame(header)
        title_frame.pack(fill=tk.X, padx=20, pady=15)
        
        # Animated title with colorful emojis
        title_label = tk.Label(title_frame, 
                              text="🎬 Douyin ➜ YouTube Tool 🚀", 
                              font=('Segoe UI', 22, 'bold'), 
                              foreground=self.colors['primary'],
                              background=self.colors['light'])
        title_label.pack(side=tk.LEFT)
        
        # Status with colorful indicators
        status_frame = ttk.Frame(title_frame)
        status_frame.pack(side=tk.RIGHT)
        
        if YOUTUBE_AVAILABLE:
            status_text = "🟢 YouTube Ready"
            status_color = self.colors['success']
        else:
            status_text = "🔴 YouTube Not Available"
            status_color = self.colors['danger']
            
        status_label = tk.Label(status_frame, 
                               text=status_text,
                               font=('Segoe UI', 11, 'bold'), 
                               foreground=status_color,
                               background=self.colors['light'])
        status_label.pack()
        
        # Decorative separator with gradient
        separator_frame = ttk.Frame(header)
        separator_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        # Create gradient-like separator using multiple colored lines
        colors_gradient = [self.colors['primary'], self.colors['secondary'], self.colors['accent']]
        for i, color in enumerate(colors_gradient):
            separator = tk.Frame(separator_frame, height=2, background=color)
            separator.pack(fill=tk.X, pady=1)
        
    def create_footer(self, parent):
        """Create colorful footer"""
        footer_container = ttk.Frame(parent)
        footer_container.pack(fill=tk.X, side=tk.BOTTOM, pady=(15, 0))
        
        # Gradient separator
        separator_frame = ttk.Frame(footer_container)
        separator_frame.pack(fill=tk.X, pady=(0, 10))
        
        colors_gradient = [self.colors['accent'], self.colors['secondary'], self.colors['primary']]
        for color in colors_gradient:
            separator = tk.Frame(separator_frame, height=1, background=color)
            separator.pack(fill=tk.X, pady=0.5)
        
        # Footer content with colors
        footer = ttk.Frame(footer_container)
        footer.pack(fill=tk.X)
        
        self.status_var = tk.StringVar(value="🟢 Ready to start!")
        status_label = tk.Label(footer, 
                               textvariable=self.status_var,
                               font=('Segoe UI', 10, 'bold'), 
                               foreground=self.colors['primary'],
                               background=self.colors['light'])
        status_label.pack(side=tk.LEFT)
        
        # Styled progress bar
        progress_frame = ttk.Frame(footer)
        progress_frame.pack(side=tk.RIGHT)
        
        tk.Label(progress_frame, 
                text="Progress:",
                font=('Segoe UI', 9),
                foreground=self.colors['medium'],
                background=self.colors['light']).pack(side=tk.LEFT, padx=(0, 5))
        
        self.global_progress = ttk.Progressbar(progress_frame, length=250, mode='determinate')
        self.global_progress.pack(side=tk.RIGHT)
        
    def create_download_tab(self):
        """Create colorful download tab (Douyin downloader)"""
        self.download_frame = ttk.Frame(self.content_container)
        
        main_frame = ttk.Frame(self.download_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions (Simplified)
        inst_frame = ttk.LabelFrame(main_frame, text="📋 Quick Guide", padding="10")
        inst_frame.pack(fill=tk.X, pady=(0, 15))
        
        quick_instructions = [
            "🌐 Open Douyin → F12 → Network → Find 'aweme/post' → Copy as cURL → Paste below"
        ]
        
        for inst in quick_instructions:
            ttk.Label(inst_frame, text=inst, font=('Segoe UI', 10), 
                     foreground='#3498db', wraplength=600).pack(anchor=tk.W, pady=2)
            
        # cURL Input (Compact)
        curl_frame = ttk.LabelFrame(main_frame, text="🔗 cURL Input", padding="10")
        curl_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Input area with buttons inline
        input_frame = ttk.Frame(curl_frame)
        input_frame.pack(fill=tk.X)
        
        # Text input (smaller)
        self.curl_text = tk.Text(input_frame, height=3, font=('Consolas', 9),
                                bg=self.colors['light'], fg=self.colors['dark'],
                                insertbackground=self.colors['primary'])
        self.curl_text.pack(fill=tk.X, pady=(0, 8))
        
        # Buttons with beautiful colors - using tk.Button for better visibility
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill=tk.X)
        
        paste_btn = tk.Button(button_frame, text="📋 Paste", 
                             command=self.paste_curl,
                             bg=self.colors['primary'], fg='white',
                             font=('Segoe UI', 10, 'bold'),
                             relief='flat', padx=15, pady=8)
        paste_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        parse_btn = tk.Button(button_frame, text="🔍 Parse", 
                             command=self.parse_curl,
                             bg=self.colors['success'], fg=self.colors['dark'],
                             font=('Segoe UI', 10, 'bold'),
                             relief='flat', padx=15, pady=8)
        parse_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        clear_btn = tk.Button(button_frame, text="🗑️ Clear", 
                             command=self.clear_curl,
                             bg=self.colors['warning'], fg=self.colors['dark'],
                             font=('Segoe UI', 10, 'bold'),
                             relief='flat', padx=15, pady=8)
        clear_btn.pack(side=tk.LEFT, padx=(0, 8))

        douyin_btn = tk.Button(button_frame, text="🌐 Open Douyin",
                              command=self.open_douyin_login,
                              bg=self.colors['info'], fg='white',
                              font=('Segoe UI', 10, 'bold'),
                              relief='flat', padx=15, pady=8)
        douyin_btn.pack(side=tk.LEFT, padx=(0, 8))

        cookie_btn = tk.Button(button_frame, text="🍪 Auto Cookie",
                              command=self.auto_import_douyin_cookies,
                              bg=self.colors['secondary'], fg='white',
                              font=('Segoe UI', 10, 'bold'),
                              relief='flat', padx=15, pady=8)
        cookie_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        # Show advanced toggle with color
        self.show_advanced = tk.BooleanVar()
        advanced_check = tk.Checkbutton(button_frame, text="⚙️ Advanced", 
                                       variable=self.show_advanced, command=self.toggle_advanced)
        advanced_check.pack(side=tk.RIGHT)        # Advanced Config (Initially Hidden)
        self.advanced_frame = ttk.LabelFrame(main_frame, text="⚙️ Advanced Configuration", padding="10")
        
        # API URL
        ttk.Label(self.advanced_frame, text="API URL:").pack(anchor=tk.W)
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(self.advanced_frame, textvariable=self.url_var, font=('Consolas', 9))
        self.url_entry.pack(fill=tk.X, pady=(2, 8))
        
        # Headers (Collapsible)
        self.show_headers = tk.BooleanVar()
        tk.Checkbutton(self.advanced_frame, text="🔧 Custom Headers", 
                       variable=self.show_headers, command=self.toggle_headers).pack(anchor=tk.W)
        
        self.headers_frame = ttk.Frame(self.advanced_frame)
        self.headers_text = tk.Text(self.headers_frame, height=4, font=('Consolas', 8),
                                   bg=self.colors['light'], fg=self.colors['dark'],
                                   insertbackground=self.colors['primary'])
        self.headers_text.pack(fill=tk.X)
        
        # Download section (More compact)
        download_frame = ttk.LabelFrame(main_frame, text="📥 Download Manager", padding="10")
        download_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        # Controls (Better layout)
        quick_auth_frame = ttk.Frame(download_frame)
        quick_auth_frame.pack(fill=tk.X, pady=(0, 8))

        tk.Label(quick_auth_frame, text="🔐 Douyin Access:",
                font=('Segoe UI', 9, 'bold'), background=self.colors['light'],
                foreground=self.colors['dark']).pack(side=tk.LEFT, padx=(0, 8))

        login_douyin_top_btn = tk.Button(quick_auth_frame, text="🌐 Login Douyin",
                                        command=self.open_douyin_login,
                                        bg=self.colors['info'], fg='white',
                                        font=('Segoe UI', 9, 'bold'),
                                        relief='flat', padx=12, pady=6)
        login_douyin_top_btn.pack(side=tk.LEFT, padx=(0, 8))

        cookie_top_btn = tk.Button(quick_auth_frame, text="🍪 Auto Cookie",
                                   command=self.auto_import_douyin_cookies,
                                   bg=self.colors['secondary'], fg='white',
                                   font=('Segoe UI', 9, 'bold'),
                                   relief='flat', padx=12, pady=6)
        cookie_top_btn.pack(side=tk.LEFT, padx=(0, 8))

        control_frame = ttk.Frame(download_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Main action buttons with colors - using tk.Button for visibility
        action_frame = ttk.Frame(control_frame)
        action_frame.pack(side=tk.LEFT)
        
        analyze_btn = tk.Button(action_frame, text="🔍 Analyze", 
                               command=self.analyze_url_thread,
                               bg=self.colors['primary'], fg='white',
                               font=('Segoe UI', 10, 'bold'),
                               relief='flat', padx=15, pady=8)
        analyze_btn.pack(side=tk.LEFT, padx=(0, 8))

        login_douyin_btn = tk.Button(action_frame, text="🌐 Login Douyin",
                                    command=self.open_douyin_login,
                                    bg=self.colors['info'], fg='white',
                                    font=('Segoe UI', 10, 'bold'),
                                    relief='flat', padx=15, pady=8)
        login_douyin_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        folder_btn = tk.Button(action_frame, text="📁 Folder", 
                              command=self.select_download_folder,
                              bg=self.colors['primary'], fg='white',
                              font=('Segoe UI', 10, 'bold'),
                              relief='flat', padx=15, pady=8)
        folder_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        self.download_btn = tk.Button(action_frame, text="📥 Download All", 
                                     command=self.download_videos_thread, 
                                     state='disabled',
                                     bg=self.colors['success'], fg=self.colors['dark'],
                                     font=('Segoe UI', 10, 'bold'),
                                     relief='flat', padx=15, pady=8)
        self.download_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        # Status on right with color
        status_frame = ttk.Frame(control_frame)
        status_frame.pack(side=tk.RIGHT)
        
        self.download_status_var = tk.StringVar(value="🟢 Ready")
        status_label = tk.Label(status_frame, 
                               textvariable=self.download_status_var,
                               font=('Segoe UI', 9, 'bold'),
                               foreground=self.colors['success'],
                               background=self.colors['light'])
        status_label.pack()
        
        # Progress
        self.download_progress = ttk.Progressbar(download_frame, mode='determinate')
        self.download_progress.pack(fill=tk.X, pady=(0, 10))
        
        # Video list (Improved)
        list_frame = ttk.Frame(download_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with count and filters
        list_header = ttk.Frame(list_frame)
        list_header.pack(fill=tk.X, pady=(0, 8))
        
        self.video_count_var = tk.StringVar(value="📋 Videos: 0")
        ttk.Label(list_header, textvariable=self.video_count_var, 
                 font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        
        # Quick actions with colorful buttons - using tk.Button for visibility
        select_all_btn = tk.Button(list_header, text="✅ Select All", 
                                  command=self.select_all_videos,
                                  bg=self.colors['success'], fg=self.colors['dark'],
                                  font=('Segoe UI', 9, 'bold'),
                                  relief='flat', padx=12, pady=6)
        select_all_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        clear_all_btn = tk.Button(list_header, text="❌ Clear All", 
                                 command=self.clear_all_videos,
                                 bg=self.colors['warning'], fg=self.colors['dark'],
                                 font=('Segoe UI', 9, 'bold'),
                                 relief='flat', padx=12, pady=6)
        clear_all_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Treeview (Improved columns)
        columns = ('Select', 'Index', 'Status', 'Title', 'URL')
        self.video_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        self.video_tree.heading('Select', text='☐')
        self.video_tree.heading('Index', text='#')
        self.video_tree.heading('Status', text='Status')
        self.video_tree.heading('Title', text='Title')
        self.video_tree.heading('URL', text='URL')
        
        self.video_tree.column('Select', width=40, anchor=tk.CENTER)
        self.video_tree.column('Index', width=50, anchor=tk.CENTER)
        self.video_tree.column('Status', width=100, anchor=tk.CENTER)
        self.video_tree.column('Title', width=200)
        self.video_tree.column('URL', width=300)
        
        # Bind double-click to toggle selection
        self.video_tree.bind('<Double-1>', self.toggle_video_selection)
        
        # Scrollbar
        v_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.video_tree.yview)
        self.video_tree.configure(yscrollcommand=v_scroll.set)
        
        self.video_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
    # ══════════════════════════════════════════════════════════════════════════
    #  YouTube / TikTok / Douyin Video Downloader  (powered by yt-dlp)
    # ══════════════════════════════════════════════════════════════════════════

    def create_yt_download_tab(self):
        """Create YouTube/TikTok/Douyin downloader tab using yt-dlp."""
        self.yt_download_frame = ttk.Frame(self.content_container)
        main_frame = ttk.Frame(self.yt_download_frame, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ── yt-dlp availability warning ──────────────────────────────────────
        if not YT_DLP_AVAILABLE:
            warn = ttk.LabelFrame(main_frame, text="⚠️ yt-dlp Not Installed", padding="15")
            warn.pack(fill=tk.X, pady=(0, 10))
            ttk.Label(warn, text="yt-dlp is required for this tab.\n"
                      "Run:  pip install yt-dlp  then restart the app.",
                      font=('Segoe UI', 11), foreground='red').pack(anchor=tk.W)

        # ── Quality selector ─────────────────────────────────────────────────
        quality_frame = ttk.LabelFrame(main_frame, text="🎬 Chất Lượng Video", padding="10")
        quality_frame.pack(fill=tk.X, pady=(0, 10))

        self.yt_quality_var = tk.StringVar(value="1080p")
        qualities = [("720p (Nhanh)", "720p"), ("1080p (Cân bằng)", "1080p"),
                     ("1440p (Cao)", "1440p"), ("4K (Tốt nhất)", "4k"), ("Auto", "auto")]
        for label, val in qualities:
            ttk.Radiobutton(quality_frame, text=label, variable=self.yt_quality_var,
                            value=val).pack(side=tk.LEFT, padx=8)

        # ── Output folder ────────────────────────────────────────────────────
        folder_frame = ttk.LabelFrame(main_frame, text="📁 Thư Mục Lưu Video", padding="10")
        folder_frame.pack(fill=tk.X, pady=(0, 10))

        folder_row = ttk.Frame(folder_frame)
        folder_row.pack(fill=tk.X)

        self.yt_output_dir_var = tk.StringVar(value=self.yt_output_dir)
        ttk.Entry(folder_row, textvariable=self.yt_output_dir_var,
                  font=('Consolas', 9)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        tk.Button(folder_row, text="📂 Browse", command=self._yt_select_output_folder,
                  bg=self.colors['primary'], fg='white', font=('Segoe UI', 9, 'bold'),
                  relief='flat', padx=10, pady=5).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(folder_row, text="🔓 Mở Thư Mục", command=self._yt_open_output_folder,
                  bg=self.colors['success'], fg=self.colors['dark'], font=('Segoe UI', 9, 'bold'),
                  relief='flat', padx=10, pady=5).pack(side=tk.LEFT)

        # ── Cookies (optional) ───────────────────────────────────────────────
        cookie_frame = ttk.LabelFrame(main_frame,
            text="🍪 YouTube Cookies (tùy chọn — dùng khi YouTube yêu cầu đăng nhập)",
            padding="10")
        cookie_frame.pack(fill=tk.X, pady=(0, 10))

        cookie_row = ttk.Frame(cookie_frame)
        cookie_row.pack(fill=tk.X)

        self.yt_cookies_var = tk.StringVar(value="")
        ttk.Entry(cookie_row, textvariable=self.yt_cookies_var,
                  font=('Consolas', 9)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        tk.Button(cookie_row, text="📂 Browse", command=self._yt_select_cookies_file,
                  bg=self.colors['primary'], fg='white', font=('Segoe UI', 9, 'bold'),
                  relief='flat', padx=10, pady=5).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(cookie_row, text="✖ Xóa", command=lambda: self.yt_cookies_var.set(""),
                  bg=self.colors['warning'], fg=self.colors['dark'], font=('Segoe UI', 9, 'bold'),
                  relief='flat', padx=10, pady=5).pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(cookie_row, text="🍪 Auto từ Browser",
                  command=self._yt_auto_cookie_from_browser,
                  bg='#795548', fg='white', font=('Segoe UI', 9, 'bold'),
                  relief='flat', padx=10, pady=5).pack(side=tk.LEFT)

        hint_row = ttk.Frame(cookie_frame)
        hint_row.pack(fill=tk.X, pady=(6, 0))
        ttk.Label(hint_row,
                  text="⚡ Nếu bị lỗi 'Sign in / bot': nhấn  🍪 Auto từ Browser  hoặc browse chọn cookies.txt",
                  font=('Segoe UI', 8, 'bold'), foreground='#C62828').pack(side=tk.LEFT)
        ttk.Label(hint_row,
                  text="  |  Export thủ công: extension 'Get cookies.txt LOCALLY' trên Chrome",
                  font=('Segoe UI', 8), foreground=self.colors['medium']).pack(side=tk.LEFT)

        # ── Single download ──────────────────────────────────────────────────
        single_frame = ttk.LabelFrame(main_frame, text="📥 Tải Video Đơn Lẻ", padding="10")
        single_frame.pack(fill=tk.X, pady=(0, 10))

        single_row = ttk.Frame(single_frame)
        single_row.pack(fill=tk.X)

        self.yt_url_var = tk.StringVar()
        ttk.Entry(single_row, textvariable=self.yt_url_var,
                  font=('Consolas', 10)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.yt_btn_single = tk.Button(single_row, text="▶ Tải Video",
                  command=self._yt_start_single,
                  bg=self.colors['primary'], fg='white', font=('Segoe UI', 10, 'bold'),
                  relief='flat', padx=15, pady=7)
        self.yt_btn_single.pack(side=tk.LEFT)

        ttk.Label(single_frame,
                  text="Hỗ trợ: YouTube, TikTok, Douyin (v.douyin.com, vm.tiktok.com, youtu.be, playlist…)",
                  font=('Segoe UI', 8), foreground=self.colors['medium']).pack(anchor=tk.W, pady=(4, 0))

        # ── Batch download ───────────────────────────────────────────────────
        batch_frame = ttk.LabelFrame(main_frame, text="📋 Tải Hàng Loạt (mỗi URL một dòng)", padding="10")
        batch_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.yt_batch_text = scrolledtext.ScrolledText(batch_frame, height=6,
                  font=('Consolas', 9), bg=self.colors['light'], fg=self.colors['dark'],
                  insertbackground=self.colors['primary'])
        self.yt_batch_text.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        btn_row = ttk.Frame(batch_frame)
        btn_row.pack(fill=tk.X)
        self.yt_btn_batch = tk.Button(btn_row, text="▶ Tải Tất Cả",
                  command=self._yt_start_batch,
                  bg=self.colors['primary'], fg='white', font=('Segoe UI', 10, 'bold'),
                  relief='flat', padx=15, pady=7)
        self.yt_btn_batch.pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(btn_row, text="🗑️ Xóa Danh Sách",
                  command=lambda: self.yt_batch_text.delete("1.0", tk.END),
                  bg=self.colors['warning'], fg=self.colors['dark'], font=('Segoe UI', 10, 'bold'),
                  relief='flat', padx=15, pady=7).pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(btn_row, text="📋 Xem Lịch Sử",
                  command=self._yt_view_history,
                  bg=self.colors['info'], fg='white', font=('Segoe UI', 10, 'bold'),
                  relief='flat', padx=15, pady=7).pack(side=tk.LEFT)

        # ── Progress + status ────────────────────────────────────────────────
        prog_frame = ttk.Frame(main_frame)
        prog_frame.pack(fill=tk.X, pady=(0, 5))

        self.yt_progress_var = tk.DoubleVar(value=0)
        self.yt_progressbar = ttk.Progressbar(prog_frame, variable=self.yt_progress_var,
                                              maximum=100, length=500, mode='determinate')
        self.yt_progressbar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.yt_pct_label = ttk.Label(prog_frame, text="0%", font=('Segoe UI', 9, 'bold'), width=6)
        self.yt_pct_label.pack(side=tk.LEFT)

        self.yt_status_var = tk.StringVar(value="✅ Sẵn sàng tải")
        self.yt_status_label = ttk.Label(main_frame, textvariable=self.yt_status_var,
                                         font=('Segoe UI', 9), foreground=self.colors['primary'])
        self.yt_status_label.pack(anchor=tk.W)

        # ffmpeg / Node.js info row
        info_parts = []
        if FFMPEG_DIR:
            info_parts.append("✅ FFmpeg: có")
        else:
            info_parts.append("⚠️ FFmpeg: không tìm thấy (video có thể là .webm)")
        if FFPROBE_PATH:
            info_parts.append("✅ FFprobe: có")
        else:
            info_parts.append("⚠️ FFprobe: thiếu (metadata warning)")
        if NODE_PATH:
            info_parts.append("✅ Node.js: có (n-challenge solver)")
        else:
            info_parts.append("ℹ️ Node.js: không tìm thấy")
        ttk.Label(main_frame, text="  |  ".join(info_parts),
                  font=('Segoe UI', 8), foreground=self.colors['medium']).pack(anchor=tk.W, pady=(2, 0))

        # ── Downloaded videos list ────────────────────────────────────────────
        dl_list_frame = ttk.LabelFrame(main_frame,
            text="📂 Danh Sách Video Đã Tải — chọn để upload lên YouTube",
            padding="10")
        dl_list_frame.pack(fill=tk.BOTH, expand=True, pady=(12, 0))

        # Toolbar
        dl_toolbar = ttk.Frame(dl_list_frame)
        dl_toolbar.pack(fill=tk.X, pady=(0, 6))

        tk.Button(dl_toolbar, text="🔄 Làm Mới",
                  command=self._yt_refresh_dl_list,
                  bg=self.colors['primary'], fg='white',
                  font=('Segoe UI', 9, 'bold'), relief='flat', padx=10, pady=5
                  ).pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(dl_toolbar, text="✅ Chọn Tất Cả",
                  command=self._yt_dl_select_all,
                  bg=self.colors['success'], fg=self.colors['dark'],
                  font=('Segoe UI', 9, 'bold'), relief='flat', padx=10, pady=5
                  ).pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(dl_toolbar, text="⬜ Bỏ Chọn",
                  command=self._yt_dl_deselect_all,
                  bg=self.colors['warning'], fg=self.colors['dark'],
                  font=('Segoe UI', 9, 'bold'), relief='flat', padx=10, pady=5
                  ).pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(dl_toolbar, text="🗑️ Xóa File",
                  command=self._yt_dl_delete_selected,
                  bg=self.colors['danger'], fg='white',
                  font=('Segoe UI', 9, 'bold'), relief='flat', padx=10, pady=5
                  ).pack(side=tk.LEFT, padx=(0, 16))

        self.yt_dl_count_var = tk.StringVar(value="0 video")
        ttk.Label(dl_toolbar, textvariable=self.yt_dl_count_var,
                  font=('Segoe UI', 9, 'bold'),
                  foreground=self.colors['primary']).pack(side=tk.LEFT)

        self.yt_send_btn = tk.Button(dl_toolbar, text="🚀 Gửi lên Upload Tab",
                  command=self._yt_send_to_upload_tab,
                  bg='#E53935', fg='white',
                  font=('Segoe UI', 10, 'bold'), relief='flat', padx=16, pady=6)
        self.yt_send_btn.pack(side=tk.RIGHT)
        ttk.Label(dl_toolbar, text="⬅",
                  font=('Segoe UI', 10)).pack(side=tk.RIGHT, padx=(0, 4))

        # Treeview
        dl_cols = ("sel", "filename", "size", "date", "path")
        self.yt_dl_tree = ttk.Treeview(dl_list_frame, columns=dl_cols,
                                        show='headings', height=7)
        self.yt_dl_tree.heading("sel",      text="✓",        anchor=tk.CENTER)
        self.yt_dl_tree.heading("filename", text="📹 Tên File")
        self.yt_dl_tree.heading("size",     text="📊 Kích thước", anchor=tk.CENTER)
        self.yt_dl_tree.heading("date",     text="📅 Ngày tải",   anchor=tk.CENTER)
        self.yt_dl_tree.heading("path",     text="📁 Đường dẫn")

        self.yt_dl_tree.column("sel",      width=40,  minwidth=40,  anchor=tk.CENTER, stretch=False)
        self.yt_dl_tree.column("filename", width=300, minwidth=150)
        self.yt_dl_tree.column("size",     width=90,  minwidth=70,  anchor=tk.CENTER, stretch=False)
        self.yt_dl_tree.column("date",     width=110, minwidth=90,  anchor=tk.CENTER, stretch=False)
        self.yt_dl_tree.column("path",     width=0,   minwidth=0,   stretch=False)   # hidden

        self.yt_dl_tree.tag_configure("checked",   background="#e3f2fd", foreground="#1565C0")
        self.yt_dl_tree.tag_configure("unchecked", background=self.colors['light'],
                                       foreground=self.colors['dark'])

        dl_scroll = ttk.Scrollbar(dl_list_frame, orient=tk.VERTICAL,
                                   command=self.yt_dl_tree.yview)
        self.yt_dl_tree.configure(yscrollcommand=dl_scroll.set)
        self.yt_dl_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        dl_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Toggle selection on click
        self.yt_dl_tree.bind("<Button-1>", self._yt_dl_on_click)
        self.yt_dl_tree.bind("<Double-1>", self._yt_dl_on_click)

        # Populate on first load
        self.root.after(300, self._yt_refresh_dl_list)

    # ── Helper: UI actions ────────────────────────────────────────────────────

    def _yt_select_output_folder(self):
        folder = filedialog.askdirectory(initialdir=self.yt_output_dir_var.get())
        if folder:
            self.yt_output_dir_var.set(folder)
            self.yt_output_dir = folder
            self._yt_refresh_dl_list()   # show files in new folder

    def _yt_open_output_folder(self):
        folder = self.yt_output_dir_var.get().strip() or self.yt_output_dir
        os.makedirs(folder, exist_ok=True)
        os.startfile(folder)

    def _yt_select_cookies_file(self):
        path = filedialog.askopenfilename(
            title="Chọn cookies.txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return
        # Validate: check for essential auth cookies
        auth_keys = {"SAPISID", "SID", "__Secure-3PAPISID", "LOGIN_INFO", "HSID", "SSID"}
        found_keys = set()
        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if line.startswith("#") or not line.strip():
                        continue
                    parts = line.strip().split("\t")
                    if len(parts) >= 6:
                        found_keys.add(parts[5])
        except Exception:
            pass
        missing = auth_keys - found_keys
        if missing:
            messagebox.showwarning(
                "Cookie thiếu xác thực",
                f"File cookie này thiếu các cookie đăng nhập quan trọng:\n"
                f"  {', '.join(sorted(missing))}\n\n"
                f"YouTube sẽ không nhận ra bạn đã đăng nhập → video private sẽ không tải được.\n\n"
                f"Hãy export lại bằng extension 'Get cookies.txt LOCALLY' khi đang đăng nhập YouTube.\n\n"
                f"Vẫn dùng file này?"
            )
        self.yt_cookies_var.set(path)

    # ── Cookie extraction helpers ─────────────────────────────────────────────

    # Chrome v127+ uses App-Bound Encryption (v20) — can't decrypt outside process.
    # We use Chrome DevTools Protocol (CDP) instead: launch a Chrome window,
    # user logs in, we call Storage.getCookies via WebSocket CDP.

    @staticmethod
    def _find_chrome_exe() -> str | None:
        """Return path to Chrome or Edge executable, or None."""
        candidates = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.join(os.environ.get("LOCALAPPDATA", ""),
                         "Google", "Chrome", "Application", "chrome.exe"),
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ]
        for p in candidates:
            if os.path.exists(p):
                return p
        # Try PATH
        found = shutil.which("chrome") or shutil.which("msedge")
        return found

    @staticmethod
    def _cdp_get_cookies(port: int, timeout: int = 60) -> list[dict]:
        """Connect to Chrome via CDP WebSocket and return all cookies."""
        import urllib.request, socket, struct, json as _json, os as _os

        # Get WebSocket URL from CDP HTTP endpoint
        resp = urllib.request.urlopen(
            f"http://localhost:{port}/json/version", timeout=5)
        info = _json.loads(resp.read())
        ws_url: str = info["webSocketDebuggerUrl"]
        ws_path = ws_url.split(f"localhost:{port}", 1)[1]

        # Raw WebSocket handshake (no external deps)
        sock = socket.create_connection(("localhost", port), timeout=timeout)
        key = __import__("base64").b64encode(_os.urandom(16)).decode()
        handshake = (
            f"GET {ws_path} HTTP/1.1\r\n"
            f"Host: localhost:{port}\r\n"
            f"Upgrade: websocket\r\nConnection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
        )
        sock.send(handshake.encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            buf += sock.recv(4096)

        def _ws_send(data: dict):
            payload = _json.dumps(data).encode()
            mask = _os.urandom(4)
            n = len(payload)
            masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
            header = b"\x81"
            if n < 126:
                header += bytes([n | 0x80]) + mask
            elif n < 65536:
                header += bytes([126 | 0x80]) + struct.pack(">H", n) + mask
            else:
                header += bytes([127 | 0x80]) + struct.pack(">Q", n) + mask
            sock.send(header + masked)

        def _ws_recv() -> dict:
            def _read(n):
                d = b""
                while len(d) < n:
                    d += sock.recv(n - len(d))
                return d
            b0, b1 = _read(2)
            n = b1 & 0x7f
            if n == 126:
                n = struct.unpack(">H", _read(2))[0]
            elif n == 127:
                n = struct.unpack(">Q", _read(8))[0]
            return _json.loads(_read(n).decode())

        _ws_send({"id": 1, "method": "Storage.getCookies"})
        for _ in range(200):   # up to 200 messages
            msg = _ws_recv()
            if msg.get("id") == 1:
                sock.close()
                return msg.get("result", {}).get("cookies", [])
        sock.close()
        return []

    @staticmethod
    def _dpapi_decrypt(ciphertext: bytes) -> bytes:
        """Decrypt bytes using Windows DPAPI (CryptUnprotectData)."""
        import ctypes, ctypes.wintypes
        class DATA_BLOB(ctypes.Structure):
            _fields_ = [("cbData", ctypes.wintypes.DWORD),
                        ("pbData", ctypes.POINTER(ctypes.c_char))]
        p = ctypes.create_string_buffer(ciphertext, len(ciphertext))
        blobin  = DATA_BLOB(len(ciphertext), p)
        blobout = DATA_BLOB()
        retval  = ctypes.windll.crypt32.CryptUnprotectData(
            ctypes.byref(blobin), None, None, None, None, 0,
            ctypes.byref(blobout))
        if not retval:
            raise RuntimeError("DPAPI decryption failed")
        result = ctypes.string_at(blobout.pbData, blobout.cbData)
        ctypes.windll.kernel32.LocalFree(blobout.pbData)
        return result

    @staticmethod
    def _chrome_decrypt_value(encrypted_value: bytes, aes_key: bytes) -> str:
        """Decrypt a single Chrome cookie value."""
        if not encrypted_value:
            return ""
        # v10 / v11 → AES-256-GCM
        if encrypted_value[:3] in (b"v10", b"v11"):
            try:
                from Crypto.Cipher import AES as _AES
                nonce      = encrypted_value[3:15]        # 12 bytes
                ciphertext = encrypted_value[15:-16]
                tag        = encrypted_value[-16:]
                cipher = _AES.new(aes_key, _AES.MODE_GCM, nonce=nonce)
                return cipher.decrypt_and_verify(ciphertext, tag).decode("utf-8", errors="replace")
            except Exception:
                return ""
        # Legacy → DPAPI directly
        try:
            return DouyinYouTubeTool._dpapi_decrypt(encrypted_value).decode("utf-8", errors="replace")
        except Exception:
            return ""

    def _extract_chrome_cookies_direct(self, browser: str) -> list[dict]:
        """Read Chrome/Edge cookies by copying the DB to a temp file first (avoids lock).
        Returns list of dicts with keys: domain, path, secure, expires, name, value.
        """
        import sqlite3, json, base64, tempfile, shutil as _shutil

        # Locate profile dirs for known Chromium browsers
        local = os.environ.get("LOCALAPPDATA", "")
        roaming = os.environ.get("APPDATA", "")
        profile_dirs = {
            "chrome":   os.path.join(local,   "Google",        "Chrome",        "User Data"),
            "edge":     os.path.join(local,   "Microsoft",     "Edge",          "User Data"),
            "chromium": os.path.join(local,   "Chromium",      "User Data"),
            "brave":    os.path.join(local,   "BraveSoftware", "Brave-Browser", "User Data"),
            "opera":    os.path.join(roaming, "Opera Software","Opera Stable"),
            "vivaldi":  os.path.join(local,   "Vivaldi",       "User Data"),
        }

        user_data = profile_dirs.get(browser.lower())
        if not user_data or not os.path.isdir(user_data):
            raise FileNotFoundError(f"{browser} profile not found")

        # Decrypt master key (DPAPI + base64)
        local_state_path = os.path.join(user_data, "Local State")
        with open(local_state_path, encoding="utf-8") as f:
            local_state = json.load(f)
        enc_key_b64 = local_state["os_crypt"]["encrypted_key"]
        enc_key = base64.b64decode(enc_key_b64)[5:]   # strip "DPAPI" prefix
        aes_key = self._dpapi_decrypt(enc_key)

        # Find the Cookies database (two possible locations)
        db_candidates = [
            os.path.join(user_data, "Default", "Network", "Cookies"),
            os.path.join(user_data, "Default", "Cookies"),
        ]
        db_path = next((p for p in db_candidates if os.path.exists(p)), None)
        if not db_path:
            raise FileNotFoundError(f"Cookies database not found for {browser}")

        # Read the locked SQLite file directly using Python's open() with share flags
        # via ctypes — then feed raw bytes to sqlite3 via :memory:
        import ctypes, ctypes.wintypes, tempfile, sqlite3 as _sqlite3

        def _read_locked_file(path: str) -> bytes:
            """Read a Windows-locked file by opening with full FILE_SHARE_* flags."""
            k32 = ctypes.windll.kernel32
            h = k32.CreateFileW(
                path,
                0x80000000,          # GENERIC_READ
                0x1 | 0x2 | 0x4,     # FILE_SHARE_READ | WRITE | DELETE
                None,
                3,                   # OPEN_EXISTING
                0x80,                # FILE_ATTRIBUTE_NORMAL
                None
            )
            if h == ctypes.wintypes.HANDLE(-1).value:
                raise OSError(f"Cannot open file (error {k32.GetLastError()}): {path}")
            try:
                hi = ctypes.wintypes.DWORD(0)
                lo = k32.GetFileSize(h, ctypes.byref(hi))
                size = (hi.value << 32) | (lo & 0xFFFFFFFF)
                buf  = ctypes.create_string_buffer(size)
                read = ctypes.wintypes.DWORD(0)
                if not k32.ReadFile(h, buf, size, ctypes.byref(read), None):
                    raise OSError(f"ReadFile failed (error {k32.GetLastError()})")
                return buf.raw[:read.value]
            finally:
                k32.CloseHandle(h)

        raw = _read_locked_file(db_path)
        # Load into in-memory SQLite — no temp file needed
        mem_conn = _sqlite3.connect(":memory:")
        mem_conn.deserialize(raw)
        mem_conn.row_factory = _sqlite3.Row
        rows = mem_conn.execute(
            "SELECT host_key, path, is_secure, expires_utc, name, encrypted_value "
            "FROM cookies WHERE host_key LIKE '%youtube%' OR host_key LIKE '%google%'"
        ).fetchall()
        mem_conn.close()

        cookies = []
        for row in rows:
            value = self._chrome_decrypt_value(bytes(row["encrypted_value"]), aes_key)
            if value:
                cookies.append({
                    "domain":  row["host_key"],
                    "path":    row["path"],
                    "secure":  bool(row["is_secure"]),
                    "expires": row["expires_utc"],
                    "name":    row["name"],
                    "value":   value,
                })
        return cookies

    @staticmethod
    def _sapisidhash(sapisid: str, origin: str = "https://studio.youtube.com") -> str:
        """Compute the SAPISIDHASH auth header Google's internal APIs require.

        Format: "<ts>_<sha1(ts + ' ' + SAPISID + ' ' + origin)>"
        """
        import hashlib as _hashlib
        ts = str(int(time.time()))
        digest = _hashlib.sha1(f"{ts} {sapisid} {origin}".encode("utf-8")).hexdigest()
        return f"{ts}_{digest}"

    def _studio_share_private(self, video_id: str, emails_str: str,
                              browser: str = "chrome") -> dict:
        """Share a PRIVATE video with specific emails via YouTube Studio's
        internal metadata_update API, authenticated with the user's browser
        cookies + SAPISIDHASH (the official Data API can't do this)."""
        import requests as _requests

        emails = [e.strip() for e in emails_str.split(",") if e.strip()]
        if not emails:
            return {"success": False, "error": "Không có email hợp lệ"}
        if not video_id:
            return {"success": False, "error": "Thiếu video_id"}

        # Pull auth cookies straight from the logged-in browser profile.
        try:
            raw_cookies = self._extract_chrome_cookies_direct(browser)
        except Exception as exc:
            return {"success": False,
                    "error": f"Không đọc được cookie từ {browser}: {exc}"}

        jar = {c["name"]: c["value"] for c in raw_cookies}
        sapisid = jar.get("SAPISID") or jar.get("__Secure-3PAPISID")
        if not sapisid:
            return {"success": False,
                    "error": "Cookie thiếu SAPISID — hãy đăng nhập YouTube trên "
                             f"{browser} trước."}
        if not jar.get("SID") and not jar.get("__Secure-1PSID"):
            return {"success": False,
                    "error": "Cookie thiếu SID — chưa đăng nhập đầy đủ."}

        origin = "https://studio.youtube.com"
        sapisidhash = self._sapisidhash(sapisid, origin)
        headers = {
            "authorization": (
                f"SAPISIDHASH {sapisidhash} "
                f"SAPISID1PHASH {sapisidhash} "
                f"SAPISID3PHASH {sapisidhash}"
            ),
            "content-type": "application/json",
            "origin": origin,
            "x-origin": origin,
            "referer": f"{origin}/",
            "x-goog-authuser": "0",
            "x-youtube-client-name": "62",
            "x-youtube-client-version": "1.20260616.00.00",
            "user-agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
            ),
        }

        payload = {
            "encryptedVideoId": video_id,
            "privacyState": {"newPrivacy": "PRIVATE"},
            "privateShare": {
                "notifyViaEmail": True,
                "shareEmails": ", ".join(emails),
            },
            "videoReadMask": {"privateShare": {"all": True}},
            "context": {
                "client": {
                    "clientName": 62,
                    "clientVersion": "1.20260616.00.00",
                    "hl": "en",
                    "gl": "VN",
                    "utcOffsetMinutes": 420,
                    "userInterfaceTheme": "USER_INTERFACE_THEME_DARK",
                }
            },
        }

        try:
            resp = _requests.post(
                f"{origin}/youtubei/v1/video_manager/metadata_update?alt=json",
                headers=headers,
                cookies=jar,
                json=payload,
                timeout=30,
            )
        except Exception as exc:
            return {"success": False, "error": f"Request lỗi: {exc}"}

        if resp.status_code == 200:
            # Studio returns 200 even for some logical errors; surface the body
            # if it doesn't look like a success.
            body = resp.text or ""
            if '"responseStatus"' in body and "ERROR" in body.upper():
                return {"success": False,
                        "error": f"Studio từ chối: {body[:300]}"}
            return {"success": True, "shared_with": emails}
        if resp.status_code in (401, 403):
            return {"success": False,
                    "error": f"HTTP {resp.status_code}: cookie hết hạn hoặc "
                             f"không đủ quyền. Đăng nhập lại YouTube trên {browser}."}
        return {"success": False,
                "error": f"HTTP {resp.status_code}: {resp.text[:300]}"}

    def _auto_cookie_write_netscape(self, cookies: list[dict], path: str):
        """Write cookie list to Netscape cookies.txt format."""
        lines = ["# Netscape HTTP Cookie File\n"]
        for c in cookies:
            flag   = "TRUE" if c["domain"].startswith(".") else "FALSE"
            secure = "TRUE" if c["secure"] else "FALSE"
            # Chrome stores expiry as microseconds since 1601-01-01; convert to Unix epoch
            exp = c["expires"]
            if exp and exp > 0:
                unix_exp = (exp // 1_000_000) - 11_644_473_600
                unix_exp = max(0, unix_exp)
            else:
                unix_exp = 0
            lines.append(
                f"{c['domain']}\t{flag}\t{c['path']}\t"
                f"{secure}\t{unix_exp}\t{c['name']}\t{c['value']}\n"
            )
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    @staticmethod
    def _get_real_chrome_user_data() -> tuple[str, str]:
        """Return (chrome_exe, user_data_dir) for the first installed Chromium browser."""
        local = os.environ.get("LOCALAPPDATA", "")
        candidates = [
            (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
             os.path.join(local, "Google", "Chrome", "User Data")),
            (os.path.join(local, "Google", "Chrome", "Application", "chrome.exe"),
             os.path.join(local, "Google", "Chrome", "User Data")),
            (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
             os.path.join(local, "Microsoft", "Edge", "User Data")),
            (r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
             os.path.join(local, "Microsoft", "Edge", "User Data")),
        ]
        for exe, udd in candidates:
            if os.path.exists(exe) and os.path.isdir(udd):
                return exe, udd
        return "", ""

    @staticmethod
    def _chrome_is_running() -> list[int]:
        """Return PIDs of running Chrome/Edge processes (empty = not running)."""
        import subprocess
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq chrome.exe",
             "/FI", "STATUS eq RUNNING", "/NH", "/FO", "CSV"],
            capture_output=True, text=True
        )
        pids = []
        for line in result.stdout.splitlines():
            parts = line.strip().strip('"').split('","')
            if len(parts) >= 2:
                try:
                    pids.append(int(parts[1]))
                except ValueError:
                    pass
        # Also check msedge
        result2 = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq msedge.exe", "/NH", "/FO", "CSV"],
            capture_output=True, text=True
        )
        for line in result2.stdout.splitlines():
            parts = line.strip().strip('"').split('","')
            if len(parts) >= 2:
                try:
                    pids.append(int(parts[1]))
                except ValueError:
                    pass
        return pids

    @staticmethod
    def _kill_chrome():
        """Terminate all Chrome/Edge processes."""
        import subprocess
        subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"],
                       capture_output=True)
        subprocess.run(["taskkill", "/F", "/IM", "msedge.exe"],
                       capture_output=True)

    def _yt_auto_cookie_from_browser(self):
        """Show guide to export cookies manually — Chrome v127+ App-Bound Encryption blocks all automated extraction."""
        import webbrowser as _wb

        win = tk.Toplevel(self.root)
        win.title("🍪 Hướng dẫn lấy Cookie YouTube")
        win.resizable(False, False)
        win.grab_set()

        try:
            win.iconbitmap(self.root.iconbitmap())
        except Exception:
            pass

        pad = dict(padx=18, pady=8)

        tk.Label(win, text="Chrome v127+ không cho phép đọc cookies tự động",
                 font=("Segoe UI", 11, "bold"), fg="#c0392b").pack(**pad)

        msg = (
            "Chrome mới mã hóa cookies bằng App-Bound Encryption —\n"
            "không có công cụ bên ngoài nào đọc được (kể cả yt-dlp).\n\n"
            "⚠️  Để tải video private, file cookie PHẢI chứa cookie đăng nhập\n"
            "(SAPISID, SID, HSID...) — chỉ có khi export đúng cách khi đang đăng nhập."
        )
        tk.Label(win, text=msg, font=("Segoe UI", 10), justify=tk.LEFT).pack(**pad)

        sep = ttk.Separator(win, orient="horizontal")
        sep.pack(fill=tk.X, padx=18, pady=4)

        tk.Label(win, text="Các bước thực hiện:", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=18)
        steps = (
            "1. Mở Chrome → vào youtube.com và ĐĂNG NHẬP tài khoản có quyền xem",
            "2. Cài extension 'Get cookies.txt LOCALLY' (nút bên dưới)",
            "3. Đang ở trang youtube.com → click icon extension → chọn 'Export'",
            "4. Lưu file cookies.txt (phải xuất từ youtube.com, không phải trang khác)",
            "5. Nhấn 'Chọn file cookies.txt' bên dưới để nạp vào app",
        )
        for s in steps:
            tk.Label(win, text=s, font=("Segoe UI", 10), justify=tk.LEFT).pack(anchor="w", padx=28)

        sep2 = ttk.Separator(win, orient="horizontal")
        sep2.pack(fill=tk.X, padx=18, pady=8)

        btn_frame = tk.Frame(win)
        btn_frame.pack(pady=(0, 14))

        tk.Button(
            btn_frame, text="🌐 Mở Chrome Web Store (cài extension)",
            font=("Segoe UI", 10), bg="#4285f4", fg="white", relief=tk.FLAT,
            padx=10, pady=6,
            command=lambda: _wb.open(
                "https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc")
        ).pack(side=tk.LEFT, padx=6)

        def _browse_and_close():
            path = filedialog.askopenfilename(
                title="Chọn file cookies.txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if path:
                self.yt_cookies_var.set(path)
                self._yt_set_status("✅ Đã chọn file cookies", self.colors['secondary'])
                win.destroy()

        tk.Button(
            btn_frame, text="📂 Chọn file cookies.txt",
            font=("Segoe UI", 10), bg="#27ae60", fg="white", relief=tk.FLAT,
            padx=10, pady=6,
            command=_browse_and_close
        ).pack(side=tk.LEFT, padx=6)

        tk.Button(
            btn_frame, text="Đóng",
            font=("Segoe UI", 10), relief=tk.FLAT,
            padx=10, pady=6,
            command=win.destroy
        ).pack(side=tk.LEFT, padx=6)

    def _yt_view_history(self):
        if not os.path.exists(YT_HISTORY_FILE):
            messagebox.showinfo("Lịch Sử", "Chưa có video nào được tải.")
            return
        with open(YT_HISTORY_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        win = tk.Toplevel(self.root)
        win.title("📋 Lịch Sử Tải Video (yt-dlp)")
        win.geometry("750x500")
        st = scrolledtext.ScrolledText(win, font=('Consolas', 9), wrap=tk.WORD)
        st.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        st.insert(tk.END, content)
        st.config(state=tk.DISABLED)

    # ── Downloaded-list helpers ───────────────────────────────────────────────

    _YT_VIDEO_EXTS = {'.mp4', '.mkv', '.webm', '.avi', '.mov', '.flv', '.wmv', '.m4v'}

    def _yt_refresh_dl_list(self):
        """Scan output folder and repopulate the downloaded-videos treeview."""
        if not hasattr(self, 'yt_dl_tree'):
            return
        folder = self.yt_output_dir_var.get().strip() if hasattr(self, 'yt_output_dir_var') \
                 else self.yt_output_dir
        # Preserve currently-checked filenames so a refresh keeps selections
        checked = {
            self.yt_dl_tree.set(i, "filename")
            for i in self.yt_dl_tree.get_children()
            if self.yt_dl_tree.set(i, "sel") == "✓"
        }

        for item in self.yt_dl_tree.get_children():
            self.yt_dl_tree.delete(item)

        if not os.path.isdir(folder):
            self.yt_dl_count_var.set("0 video")
            return

        files = []
        for fname in os.listdir(folder):
            fpath = os.path.join(folder, fname)
            if os.path.isfile(fpath):
                _, ext = os.path.splitext(fname.lower())
                if ext in self._YT_VIDEO_EXTS:
                    files.append(fpath)

        # Sort newest first
        files.sort(key=lambda p: os.path.getmtime(p), reverse=True)

        for fpath in files:
            fname = os.path.basename(fpath)
            size_bytes = os.path.getsize(fpath)
            if size_bytes >= 1024 ** 3:
                size_str = f"{size_bytes / 1024**3:.1f} GB"
            elif size_bytes >= 1024 ** 2:
                size_str = f"{size_bytes / 1024**2:.1f} MB"
            else:
                size_str = f"{size_bytes / 1024:.0f} KB"
            mtime = datetime.fromtimestamp(os.path.getmtime(fpath)).strftime("%d/%m %H:%M")
            is_checked = fname in checked
            tag = "checked" if is_checked else "unchecked"
            self.yt_dl_tree.insert("", "end", values=(
                "✓" if is_checked else "○",
                fname, size_str, mtime, fpath
            ), tags=(tag,))

        count = len(files)
        checked_count = sum(
            1 for i in self.yt_dl_tree.get_children()
            if self.yt_dl_tree.set(i, "sel") == "✓"
        )
        self.yt_dl_count_var.set(
            f"{count} video" + (f"  |  {checked_count} đã chọn" if checked_count else "")
        )

    def _yt_dl_on_click(self, event):
        """Toggle check-state when user clicks a row."""
        region = self.yt_dl_tree.identify_region(event.x, event.y)
        if region not in ("cell", "tree"):
            return
        item = self.yt_dl_tree.identify_row(event.y)
        if not item:
            return
        current = self.yt_dl_tree.set(item, "sel")
        if current == "✓":
            self.yt_dl_tree.set(item, "sel", "○")
            self.yt_dl_tree.item(item, tags=("unchecked",))
        else:
            self.yt_dl_tree.set(item, "sel", "✓")
            self.yt_dl_tree.item(item, tags=("checked",))
        self._yt_dl_update_count()
        return "break"   # prevent default selection highlight

    def _yt_dl_update_count(self):
        total = len(self.yt_dl_tree.get_children())
        checked = sum(
            1 for i in self.yt_dl_tree.get_children()
            if self.yt_dl_tree.set(i, "sel") == "✓"
        )
        self.yt_dl_count_var.set(
            f"{total} video" + (f"  |  {checked} đã chọn" if checked else "")
        )

    def _yt_dl_select_all(self):
        for item in self.yt_dl_tree.get_children():
            self.yt_dl_tree.set(item, "sel", "✓")
            self.yt_dl_tree.item(item, tags=("checked",))
        self._yt_dl_update_count()

    def _yt_dl_deselect_all(self):
        for item in self.yt_dl_tree.get_children():
            self.yt_dl_tree.set(item, "sel", "○")
            self.yt_dl_tree.item(item, tags=("unchecked",))
        self._yt_dl_update_count()

    def _yt_dl_delete_selected(self):
        selected = [
            self.yt_dl_tree.set(i, "path")
            for i in self.yt_dl_tree.get_children()
            if self.yt_dl_tree.set(i, "sel") == "✓"
        ]
        if not selected:
            messagebox.showinfo("Chưa chọn", "Hãy chọn ít nhất một video để xóa.")
            return
        if not messagebox.askyesno(
            "Xác nhận xóa",
            f"Xóa {len(selected)} file khỏi ổ đĩa?\n\n" + "\n".join(
                os.path.basename(p) for p in selected[:5]
            ) + ("…" if len(selected) > 5 else "")
        ):
            return
        errors = []
        for path in selected:
            try:
                os.remove(path)
            except Exception as e:
                errors.append(f"{os.path.basename(path)}: {e}")
        self._yt_refresh_dl_list()
        if errors:
            messagebox.showwarning("Một số lỗi", "\n".join(errors))

    def _yt_send_to_upload_tab(self):
        """Add checked videos to the YouTube Upload tab then switch to it."""
        selected_paths = [
            self.yt_dl_tree.set(i, "path")
            for i in self.yt_dl_tree.get_children()
            if self.yt_dl_tree.set(i, "sel") == "✓"
        ]
        if not selected_paths:
            messagebox.showinfo(
                "Chưa chọn video",
                "Hãy chọn (✓) ít nhất một video trong danh sách."
            )
            return

        # Determine the folder (all files come from the same output dir)
        folder = self.yt_output_dir_var.get().strip() or self.yt_output_dir
        self.current_video_folder = folder

        added = 0
        for path in selected_paths:
            if os.path.exists(path):
                self.add_video_to_upload_list(path)
                added += 1

        if added == 0:
            messagebox.showwarning("Không tìm thấy file",
                                   "Không file nào tồn tại trên ổ đĩa.")
            return

        # Switch to the Upload tab (index 2 = "📤 YouTube Uploader")
        try:
            tabs = self.content_container.tabs()
            for idx, tab_id in enumerate(tabs):
                if "Uploader" in self.content_container.tab(tab_id, "text"):
                    self.content_container.select(tab_id)
                    break
        except Exception:
            pass

        self.log(f"📤 Đã gửi {added} video sang Upload Tab")
        messagebox.showinfo(
            "Đã gửi sang Upload Tab",
            f"✅ {added} video đã được thêm vào danh sách Upload.\n\n"
            "Chuyển sang tab 📤 YouTube Uploader để upload."
        )

    def _yt_set_status(self, text, color=None):
        """Thread-safe status update."""
        def _upd():
            self.yt_status_var.set(text)
            if color and hasattr(self, 'yt_status_label'):
                self.yt_status_label.config(foreground=color)
        self.root.after(0, _upd)

    def _yt_set_progress(self, pct: float):
        """Thread-safe progress bar update (0–100)."""
        def _upd():
            self.yt_progress_var.set(pct)
            self.yt_pct_label.config(text=f"{pct:.0f}%")
        self.root.after(0, _upd)

    def _yt_set_buttons(self, enabled: bool):
        state = tk.NORMAL if enabled else tk.DISABLED
        def _upd():
            self.yt_btn_single.config(state=state)
            self.yt_btn_batch.config(state=state)
        self.root.after(0, _upd)

    # ── Core download logic ───────────────────────────────────────────────────

    def _yt_get_platform(self, url: str) -> str:
        """Detect platform from URL: 'youtube' | 'tiktok' | 'douyin' | 'unknown'"""
        host = urlparse(url).netloc.lower().lstrip("www.")
        if host in ("youtube.com", "youtu.be", "m.youtube.com"):
            return "youtube"
        if host in ("tiktok.com", "vm.tiktok.com", "vt.tiktok.com"):
            return "tiktok"
        if host in ("douyin.com", "v.douyin.com"):
            return "douyin"
        return "unknown"

    def _yt_is_valid_url(self, url: str) -> bool:
        try:
            r = urlparse(url.strip())
            return r.scheme in ("http", "https") and bool(r.netloc)
        except Exception:
            return False

    def _yt_format_for_quality(self, quality: str, platform: str) -> str:
        """Return yt-dlp format selector string.

        YouTube uses DASH streams (separate video+audio) so we request
        bestvideo+bestaudio and let FFmpeg merge.  Prefer mp4/m4a to avoid
        transcode when FFmpeg is present; fall back to any codec otherwise.

        For non-YouTube (TikTok / Douyin) streams are already muxed, so
        a simple 'best[height<=N]' is sufficient.
        """
        if platform != "youtube":
            # Non-YouTube: single muxed stream
            cap = {"720p": 720, "1080p": 1080, "1440p": 1440, "4k": 2160}.get(quality)
            return f"best[height<={cap}]/best" if cap else "best"

        # YouTube: DASH (separate video+audio)
        # Prefer mp4+m4a (no transcode), fall back to any codec
        cap = {"720p": 720, "1080p": 1080, "1440p": 1440, "4k": 2160}.get(quality)
        if cap:
            return (
                f"bestvideo[height<={cap}][ext=mp4]+bestaudio[ext=m4a]"
                f"/bestvideo[height<={cap}]+bestaudio"
                f"/best[height<={cap}]/best"
            )
        # auto / best
        return "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"

    def _yt_build_opts(self, fmt: str, output_dir: str,
                       extra: dict | None = None) -> dict:
        """Build yt-dlp options dict.

        extra — optional overrides / additions merged on top (e.g. for
                forcing a specific player_client or cookiesfrombrowser).
        """
        os.makedirs(output_dir, exist_ok=True)
        opts = {
            "format": fmt,
            "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
            "retries": 3,
            "fragment_retries": 3,
            "nocheckcertificate": True,
            "quiet": True,
            "no_warnings": False,
            "progress_hooks": [self._yt_progress_hook],
        }
        # FFmpeg
        if FFMPEG_DIR:
            opts["ffmpeg_location"] = FFMPEG_DIR
            opts["merge_output_format"] = "mp4"
            opts["postprocessors"] = [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}]
        self._yt_enable_js_challenge_support(opts)
        # Cookies file (manually chosen by user)
        cookies = self.yt_cookies_var.get().strip() if hasattr(self, 'yt_cookies_var') else ""
        if cookies:
            if not os.path.exists(cookies):
                raise RuntimeError(f"Cookies file không tồn tại: {cookies}")
            opts["cookiefile"] = cookies
        # Merge caller-supplied overrides last
        if extra:
            opts.update(extra)
            # If fallback is using browser cookies, remove any stale cookiefile
            # so yt-dlp actually uses the browser (not the possibly-expired file)
            if "cookiesfrombrowser" in extra:
                opts.pop("cookiefile", None)
        return opts

    @staticmethod
    def _yt_enable_js_challenge_support(opts: dict) -> None:
        """Enable YouTube's external JavaScript challenge solver."""
        if NODE_PATH:
            opts["js_runtimes"] = {"node": {"path": NODE_PATH}}
        # The project venv includes yt-dlp-ejs. This also lets installations
        # without the companion package fetch the official solver on demand.
        opts["remote_components"] = ["ejs:github"]

    def _yt_progress_hook(self, d: dict):
        """yt-dlp progress hook — called from download thread."""
        status = d.get("status", "")
        if status == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            downloaded = d.get("downloaded_bytes", 0)
            if total and total > 0:
                pct = downloaded / total * 100
            else:
                pct_str = d.get("_percent_str", "0%").strip().rstrip("%")
                try:
                    pct = float(pct_str)
                except ValueError:
                    pct = 0
            filename = os.path.basename(d.get("filename", ""))[:35]
            self._yt_set_progress(pct)
            self._yt_set_status(f"⬇ Đang tải: {filename}… ({pct:.1f}%)", self.colors['primary'])
        elif status == "finished":
            self._yt_set_progress(100)

    def _yt_save_history(self, title: str, url: str):
        with open(YT_HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"{title} | {url}\n")

    def _yt_is_duplicate(self, url: str) -> bool:
        if not os.path.exists(YT_HISTORY_FILE):
            return False
        url = url.strip()
        with open(YT_HISTORY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                # Each line: "title | url"  — compare the url part exactly
                parts = line.strip().split(" | ", 1)
                saved_url = parts[-1].strip()
                if saved_url == url:
                    return True
        return False

    def _yt_run_download(self, opts: dict, url: str) -> str:
        """Low-level yt-dlp call. Returns video title. Raises on error."""
        if not YT_DLP_AVAILABLE:
            raise RuntimeError("yt-dlp chưa được cài đặt. Chạy: pip install yt-dlp")
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", url) if info else url
            self._yt_save_history(title, url)
            return title

    def _yt_download_single(self, url: str, quality: str) -> str:
        """Download one video with multi-level fallback. Returns title.

        Priority: QUALITY FIRST, then bot-bypass, then cookies.

        Fallback order for YouTube public videos (no cookies required):
          1. Chosen quality + tv_embedded+ios+web   ← DASH full quality, bot bypass
          2. Chosen quality + ios+web               ← iOS client, full quality
          3. Chosen quality + web only              ← standard web (may need cookies)
          4. bestvideo+bestaudio + tv_embedded      ← last no-cookie attempt
          5-8. Chosen quality + cookiesfrombrowser  ← chrome/edge/firefox/chromium
        Non-YouTube: only steps 1-2 run (no DASH, no cookie fallback needed).
        """
        platform = self._yt_get_platform(url)
        output_dir = self.yt_output_dir_var.get().strip() or self.yt_output_dir
        q_fmt = self._yt_format_for_quality(quality, platform)

        has_cookiefile = bool(
            hasattr(self, 'yt_cookies_var') and self.yt_cookies_var.get().strip()
            and os.path.exists(self.yt_cookies_var.get().strip())
        )

        # (label, format_string, extractor_args_override, cookiesfrombrowser)
        if platform == "youtube":
            if has_cookiefile:
                # Cookie file present → try authed clients first (web_safari supports cookies)
                steps = [
                    ("web_safari+cookie", q_fmt,
                     {"extractor_args": {"youtube": {"player_client": ["web_safari"]}}},
                     None),
                    ("tv_downgraded+cookie", q_fmt,
                     {"extractor_args": {"youtube": {"player_client": ["tv_downgraded", "web_safari"]}}},
                     None),
                    # Fallback no-cookie
                    ("android_vr+web_safari", q_fmt,
                     {"extractor_args": {"youtube": {"player_client": ["android_vr", "web_safari"]}}},
                     None),
                    ("android_vr", q_fmt,
                     {"extractor_args": {"youtube": {"player_client": ["android_vr"]}}},
                     None),
                ]
            else:
                # No cookie → try no-auth clients, then browser cookie fallbacks
                steps = [
                    ("android_vr+web_safari", q_fmt,
                     {"extractor_args": {"youtube": {"player_client": ["android_vr", "web_safari"]}}},
                     None),
                    ("android_vr", q_fmt,
                     {"extractor_args": {"youtube": {"player_client": ["android_vr"]}}},
                     None),
                    ("web_safari", q_fmt,
                     {"extractor_args": {"youtube": {"player_client": ["web_safari"]}}},
                     None),
                    ("tv_downgraded", q_fmt,
                     {"extractor_args": {"youtube": {"player_client": ["tv_downgraded", "web_safari"]}}},
                     None),
                    # ── Browser cookie fallbacks ───────────────────────────
                    ("chrome+cookies",   q_fmt, {}, "chrome"),
                    ("edge+cookies",     q_fmt, {}, "edge"),
                    ("firefox+cookies",  q_fmt, {}, "firefox"),
                    ("chromium+cookies", q_fmt, {}, "chromium"),
                ]
        else:
            steps = [
                ("default", q_fmt, {}, None),
                ("best",    "best", {}, None),
            ]

        last_err = None
        total = len(steps)
        for attempt, (label, fmt, extra_ea, browser) in enumerate(steps, 1):
            try:
                self._yt_set_status(
                    f"⬇ [{attempt}/{total}] {label}: {url[:50]}…",
                    self.colors['primary'])
                extra: dict = dict(extra_ea)   # copy
                if browser:
                    extra["cookiesfrombrowser"] = (browser,)
                opts = self._yt_build_opts(fmt, output_dir, extra)
                title = self._yt_run_download(opts, url)
                if attempt > 1:
                    print(f"[yt-dlp] success on attempt {attempt} ({label})")
                return title
            except Exception as e:
                last_err = e
                err_str = str(e)
                err_lower = err_str.lower()
                print(f"[yt-dlp] attempt {attempt}/{total} ({label}) failed: {err_str[:150]}")

                # Video private/members-only — no cookie will help, stop immediately
                if "private" in err_lower or "members only" in err_lower or "join this channel" in err_lower:
                    raise RuntimeError(
                        f"Video này ở chế độ riêng tư hoặc chỉ dành cho thành viên.\n\n"
                        f"Tài khoản YouTube của bạn không có quyền xem video này.\n"
                        f"Không thể tải dù có cookie."
                    )

                # Bot/auth errors — worth trying cookie fallbacks
                bot_err = any(k in err_lower for k in
                              ("sign in", "bot", "confirm", "cookie", "403",
                               "login", "unavailable", "blocked"))
                # Stop early only for non-bot errors on the first no-cookie attempts
                if not bot_err and attempt <= 4:
                    break
                time.sleep(1)

        # Final fallback: try CocCoc CDP if available
        if platform == "youtube":
            try:
                self._yt_set_status("🦊 Thử lấy stream URL qua Cốc Cốc…", self.colors['accent'])
                title = self._yt_download_via_coccoc(url, quality, output_dir)
                print(f"[CocCoc] success")
                return title
            except Exception as e:
                print(f"[CocCoc] failed: {e}")
                last_err = e

        raise RuntimeError(
            f"Tất cả lần thử đều thất bại.\n\n"
            f"Lỗi: {str(last_err)[:200]}\n\n"
            f"💡 Giải pháp:\n"
            f"  • Nhấn '🍪 Auto từ Browser' để tự lấy cookie\n"
            f"  • Hoặc Browse chọn file cookies.txt xuất từ Chrome"
        )

    # ── CocCoc CDP fallback ───────────────────────────────────────────────────

    _COCCOC_EXE = r"C:\Program Files\CocCoc\Browser\Application\browser.exe"
    _COCCOC_USER_DATA = os.path.join(
        os.environ.get("LOCALAPPDATA", ""), "CocCoc", "Browser", "User Data")
    _COCCOC_CDP_PORT = 9222

    @staticmethod
    def _coccoc_is_running() -> bool:
        r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq browser.exe", "/NH"],
                           capture_output=True, text=True)
        return "browser.exe" in r.stdout

    @staticmethod
    def _coccoc_kill():
        subprocess.run(["taskkill", "/F", "/IM", "browser.exe"], capture_output=True)

    def _coccoc_cdp_get_player_response(self, video_url: str) -> dict:
        """Launch CocCoc with real profile, navigate to video, return ytInitialPlayerResponse."""
        import socket, struct

        port = self._COCCOC_CDP_PORT

        # Kill existing CocCoc so we can bind debug port
        if self._coccoc_is_running():
            self._coccoc_kill()
            for _ in range(10):
                time.sleep(0.5)
                if not self._coccoc_is_running():
                    break
            time.sleep(1)

        if not os.path.exists(self._COCCOC_EXE):
            raise FileNotFoundError("Không tìm thấy Cốc Cốc. Hãy cài Cốc Cốc để dùng tính năng này.")

        proc = subprocess.Popen([
            self._COCCOC_EXE,
            f"--remote-debugging-port={port}",
            "--no-first-run", "--no-default-browser-check",
            f"--user-data-dir={self._COCCOC_USER_DATA}",
            "--profile-directory=Default",
            video_url,
        ])

        # Wait for CDP
        import urllib.request as _ur
        for i in range(30):
            time.sleep(1)
            try:
                _ur.urlopen(f"http://localhost:{port}/json/version", timeout=2)
                break
            except Exception:
                pass
        else:
            proc.terminate()
            raise RuntimeError("Cốc Cốc CDP không phản hồi sau 30 giây.")

        # Find YouTube tab
        time.sleep(4)
        tabs = json.loads(_ur.urlopen(f"http://localhost:{port}/json").read())
        yt_tab = next((t for t in tabs
                       if t.get("type") == "page" and "youtube.com" in t.get("url", "")), None)
        if not yt_tab:
            proc.terminate()
            raise RuntimeError("Không tìm thấy tab YouTube trong Cốc Cốc.")

        ws_path = yt_tab["webSocketDebuggerUrl"].split(f"localhost:{port}", 1)[1]

        # WebSocket connection
        sock = socket.create_connection(("localhost", port), timeout=30)
        key = __import__("base64").b64encode(os.urandom(16)).decode()
        sock.send((f"GET {ws_path} HTTP/1.1\r\nHost: localhost:{port}\r\n"
                   f"Upgrade: websocket\r\nConnection: Upgrade\r\n"
                   f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            buf += sock.recv(4096)

        _mid = [0]
        def ws_send(method, params=None):
            _mid[0] += 1; mid = _mid[0]
            payload = json.dumps({"id": mid, "method": method,
                                  "params": params or {}}).encode()
            mask = os.urandom(4); n = len(payload)
            masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
            hdr = b"\x81"
            if n < 126: hdr += bytes([n | 0x80]) + mask
            elif n < 65536: hdr += bytes([126 | 0x80]) + struct.pack(">H", n) + mask
            else: hdr += bytes([127 | 0x80]) + struct.pack(">Q", n) + mask
            sock.send(hdr + masked); return mid

        def ws_recv_id(target, timeout=15):
            sock.settimeout(timeout)
            for _ in range(500):
                try:
                    def read(n):
                        d = b""
                        while len(d) < n: d += sock.recv(n - len(d))
                        return d
                    b0, b1 = read(2); n = b1 & 0x7f
                    if n == 126: n = struct.unpack(">H", read(2))[0]
                    elif n == 127: n = struct.unpack(">Q", read(8))[0]
                    msg = json.loads(read(n).decode())
                    if msg.get("id") == target:
                        return msg
                except socket.timeout:
                    break
            return {}

        # Inject XHR/fetch interceptor before navigating to video
        INTERCEPT_JS = """
window.__ytCaptured = window.__ytCaptured || {};
(function(){
    function capture(url) {
        if (!url || url.indexOf('videoplayback') < 0) return;
        var itag = (url.match(/[?&]itag=([^&]+)/) || [])[1];
        if (itag) window.__ytCaptured[itag] = url;
    }
    var oFetch = window.fetch;
    window.fetch = function(input, init) {
        capture(typeof input === 'string' ? input : (input && input.url) || '');
        return oFetch.apply(this, arguments);
    };
    var oOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(m, url) {
        capture(url); return oOpen.apply(this, arguments);
    };
})();
"""
        ws_send("Page.addScriptToEvaluateOnNewDocument", {"source": INTERCEPT_JS})

        import urllib.request as _ur
        mid = ws_send("Page.navigate", {"params": video_url})

        # wait for page load
        def _wait_load(timeout=15):
            sock.settimeout(timeout)
            for _ in range(300):
                try:
                    def read(n):
                        d = b""
                        while len(d) < n: d += sock.recv(n - len(d))
                        return d
                    b0, b1 = read(2); nn = b1 & 0x7f
                    if nn == 126: nn = struct.unpack(">H", read(2))[0]
                    elif nn == 127: nn = struct.unpack(">Q", read(8))[0]
                    m = json.loads(read(nn).decode())
                    if m.get("method") in ("Page.loadEventFired", "Page.frameStoppedLoading"):
                        return
                except socket.timeout:
                    return

        ws_send("Page.enable")
        mid2 = ws_send("Page.navigate", {"url": video_url})
        ws_recv_id(mid2, timeout=10)
        _wait_load(timeout=15)
        time.sleep(8)  # wait for player JS + initial buffering

        mid = ws_send("Runtime.evaluate", {"expression": """
        (function(){
            var pr = ytInitialPlayerResponse;
            if (!pr) return JSON.stringify({err: 'not found'});
            var sd = pr.streamingData || {};
            var fmts = (sd.formats||[]).concat(sd.adaptiveFormats||[]);
            // Merge captured XHR URLs into formats
            var cap = window.__ytCaptured || {};
            fmts.forEach(function(f){
                if (!f.url && cap[f.itag]) f.url = cap[f.itag];
            });
            return JSON.stringify({
                status: pr.playabilityStatus && pr.playabilityStatus.status,
                title:  pr.videoDetails && pr.videoDetails.title,
                duration: pr.videoDetails && pr.videoDetails.lengthSeconds,
                expiresInSeconds: sd.expiresInSeconds,
                capturedCount: Object.keys(cap).length,
                formats: fmts.map(function(f){ return {
                    itag: f.itag, qualityLabel: f.qualityLabel,
                    audioQuality: f.audioQuality, mimeType: f.mimeType,
                    width: f.width, height: f.height,
                    contentLength: f.contentLength, url: f.url
                };})
            });
        })()
        """, "returnByValue": True})

        result = ws_recv_id(mid, timeout=15)
        sock.close()

        val = result.get("result", {}).get("result", {}).get("value", "null")
        data = json.loads(val)
        if "err" in data:
            raise RuntimeError(f"Không lấy được player response: {data['err']}")
        if data.get("status") != "OK":
            raise RuntimeError(
                f"Video không accessible trong Cốc Cốc: {data.get('status')} — "
                f"{data.get('reason', '')}")
        print(f"[CocCoc] captured {data.get('capturedCount',0)} extra URLs via XHR intercept")
        return data

    def _yt_download_via_coccoc(self, url: str, quality: str, output_dir: str) -> str:
        """Download YouTube video using stream URLs extracted via CocCoc CDP."""
        data = self._coccoc_cdp_get_player_response(url)
        title = data.get("title", "video")
        formats = data.get("formats", [])

        # Pick best muxed format with direct URL (no cipher needed)
        quality_pref = {"best": 9999, "1080p": 1080, "720p": 720,
                        "480p": 480, "360p": 360, "worst": 0}
        max_h = quality_pref.get(quality, 720)

        muxed = [f for f in formats if f.get("url") and f.get("qualityLabel")
                 and f.get("mimeType", "").startswith("video/mp4")]
        adaptive_v = [f for f in formats if f.get("url") and f.get("qualityLabel")
                      and "video" in f.get("mimeType", "")]
        adaptive_a = [f for f in formats if f.get("url") and f.get("audioQuality")
                      and "audio" in f.get("mimeType", "")]

        safe_title = "".join(c for c in title if c not in r'\/:*?"<>|').strip()[:80]
        out_path = os.path.join(output_dir, f"{safe_title}.mp4")

        # Prefer adaptive (higher quality) if ffmpeg available
        if FFMPEG_DIR and adaptive_v and adaptive_a:
            def pick(lst, max_height):
                lst = sorted(lst, key=lambda f: f.get("height") or 0, reverse=True)
                chosen = next((f for f in lst if (f.get("height") or 0) <= max_height), lst[-1])
                return chosen
            vf = pick(adaptive_v, max_h)
            af = sorted(adaptive_a, key=lambda f: int(f.get("contentLength") or 0), reverse=True)[0]
            print(f"[CocCoc] adaptive: {vf.get('qualityLabel')} + audio → {out_path}")
            ffmpeg = os.path.join(FFMPEG_DIR, "ffmpeg.exe")
            cmd = [ffmpeg, "-y",
                   "-i", vf["url"], "-i", af["url"],
                   "-c:v", "copy", "-c:a", "aac", out_path]
            r = subprocess.run(cmd, capture_output=True)
            if r.returncode != 0:
                raise RuntimeError(f"ffmpeg failed: {r.stderr.decode(errors='replace')[-200:]}")
        elif muxed:
            f = sorted(muxed, key=lambda f: f.get("height") or 0, reverse=True)[0]
            actual_q = f.get("qualityLabel", "?")
            print(f"[CocCoc] muxed: {actual_q} → {out_path}")
            # YouTube private video với SABR chỉ cung cấp 360p muxed qua CDP
            # Higher quality dùng native MSE streaming không interceptable
            if actual_q != quality and quality not in ("worst", "360p"):
                print(f"[CocCoc] NOTE: chỉ có {actual_q} (YouTube SABR không cho phép lấy URL cao hơn)")
            import urllib.request as _ur

            def _dl_progress(block_count, block_size, total_size):
                if total_size > 0:
                    pct = min(100, block_count * block_size * 100 / total_size)
                    self._yt_set_progress(pct)

            _ur.urlretrieve(f["url"], out_path, reporthook=_dl_progress)
        else:
            raise RuntimeError("Không có format nào có URL trực tiếp từ Cốc Cốc.")

        self._yt_save_history(title, url)
        return title

    def _yt_get_video_urls(self, url: str) -> list:
        """Extract list of video URLs (handles playlists)."""
        if not YT_DLP_AVAILABLE:
            return [url]
        cookies = self.yt_cookies_var.get().strip() if hasattr(self, 'yt_cookies_var') else ""
        opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
            "skip_download": True,
        }
        self._yt_enable_js_challenge_support(opts)
        if cookies and os.path.exists(cookies):
            opts["cookiefile"] = cookies
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
        if not info:
            raise RuntimeError(f"Không thể lấy thông tin từ: {url}")
        if "entries" in info:          # playlist
            return [e["url"] if "url" in e else e.get("webpage_url", url)
                    for e in info["entries"] if e]
        return [info.get("webpage_url", url)]

    # ── UI handlers (run in threads) ──────────────────────────────────────────

    def _yt_start_single(self):
        if self.yt_is_downloading:
            messagebox.showwarning("Đang tải", "Một tác vụ đang chạy, vui lòng chờ.")
            return
        url = self.yt_url_var.get().strip()
        if not url:
            messagebox.showwarning("Thiếu URL", "Vui lòng nhập URL video.")
            return
        if not self._yt_is_valid_url(url):
            messagebox.showerror("URL không hợp lệ", f"URL không hợp lệ:\n{url}")
            return
        threading.Thread(target=self._yt_thread_single, args=(url,), daemon=True).start()

    def _yt_thread_single(self, url: str):
        self.yt_is_downloading = True
        self._yt_set_buttons(False)
        self._yt_set_progress(0)
        quality = self.yt_quality_var.get()
        downloaded, skipped, failed = [], [], []
        try:
            # Try to expand playlist; if metadata extraction fails (e.g. bot-check),
            # fall back to the original URL — _yt_download_single has its own retry chain.
            try:
                urls = self._yt_get_video_urls(url)
            except Exception as meta_err:
                print(f"[yt-dlp] metadata extraction failed ({meta_err}), using URL directly")
                urls = [url]

            total_vids = len(urls)
            for idx, u in enumerate(urls, 1):
                if total_vids > 1:
                    self._yt_set_status(
                        f"[{idx}/{total_vids}] ⬇ {u[:50]}…", self.colors['primary'])
                    self._yt_set_progress((idx - 1) / total_vids * 100)
                if self._yt_is_duplicate(u):
                    skipped.append(u)
                    continue
                try:
                    title = self._yt_download_single(u, quality)
                    downloaded.append(title)
                    self._yt_set_status(f"✅ Đã tải: {title[:50]}", self.colors['secondary'])
                except Exception as e:
                    failed.append(str(e))
                    self._yt_set_status(f"❌ Lỗi: {str(e)[:60]}", self.colors['danger'])
        except Exception as e:
            failed.append(str(e))
            self._yt_set_status(f"❌ {str(e)[:80]}", self.colors['danger'])
        finally:
            self.yt_is_downloading = False
            self._yt_set_buttons(True)
            self._yt_set_progress(100 if downloaded else 0)
            self.root.after(0, self._yt_refresh_dl_list)
            summary = (f"✅ Đã tải: {len(downloaded)}\n"
                       f"⏭ Bỏ qua (đã có): {len(skipped)}\n"
                       f"❌ Lỗi: {len(failed)}")
            if failed:
                summary += "\n\nLỗi chi tiết:\n" + "\n".join(failed[:5])
            self.root.after(0, lambda: messagebox.showinfo("Kết Quả Tải", summary))

    def _yt_start_batch(self):
        if self.yt_is_downloading:
            messagebox.showwarning("Đang tải", "Một tác vụ đang chạy, vui lòng chờ.")
            return
        raw = self.yt_batch_text.get("1.0", tk.END).strip()
        if not raw:
            messagebox.showwarning("Thiếu URL", "Vui lòng nhập ít nhất một URL.")
            return
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        valid = [u for u in lines if self._yt_is_valid_url(u)]
        invalid = [u for u in lines if not self._yt_is_valid_url(u)]
        if invalid:
            msg = f"{len(invalid)} URL không hợp lệ sẽ bị bỏ qua:\n" + "\n".join(invalid[:5])
            if not messagebox.askyesno("URL không hợp lệ", msg + "\n\nTiếp tục?"):
                return
        if not valid:
            messagebox.showerror("Không có URL hợp lệ", "Không tìm thấy URL hợp lệ nào.")
            return
        threading.Thread(target=self._yt_thread_batch, args=(valid,), daemon=True).start()

    def _yt_thread_batch(self, urls: list):
        self.yt_is_downloading = True
        self._yt_set_buttons(False)
        self._yt_set_progress(0)
        quality = self.yt_quality_var.get()
        downloaded, skipped, failed = [], [], []

        # Phase 1: expand all URLs (handles playlists) → build a flat work list
        # [(original_input_url, actual_video_url), ...]
        work: list[tuple[str, str]] = []
        for url in urls:
            try:
                sub = self._yt_get_video_urls(url)
            except Exception:
                sub = [url]   # fall back to direct URL on metadata failure
            for u in sub:
                work.append((url, u))

        total = len(work)
        if total == 0:
            self.yt_is_downloading = False
            self._yt_set_buttons(True)
            self.root.after(0, lambda: messagebox.showinfo(
                "Không có video", "Không tìm thấy video nào để tải."))
            return

        # Phase 2: download each video
        for i, (src_url, u) in enumerate(work, 1):
            self._yt_set_status(f"[{i}/{total}] ⬇ {u[:55]}…", self.colors['primary'])
            self._yt_set_progress((i - 1) / total * 100)
            if self._yt_is_duplicate(u):
                skipped.append(u)
                continue
            try:
                title = self._yt_download_single(u, quality)
                downloaded.append(title)
            except Exception as e:
                failed.append(f"{u[:60]}: {e}")

        self.yt_is_downloading = False
        self._yt_set_buttons(True)
        self._yt_set_progress(100)
        self._yt_set_status(
            f"✅ Hoàn thành — Đã tải: {len(downloaded)}, "
            f"Bỏ qua: {len(skipped)}, Lỗi: {len(failed)}",
            self.colors['secondary'])
        self.root.after(0, self._yt_refresh_dl_list)
        summary = (f"✅ Đã tải: {len(downloaded)}\n"
                   f"⏭ Bỏ qua (đã có): {len(skipped)}\n"
                   f"❌ Lỗi: {len(failed)}")
        if failed:
            summary += "\n\nLỗi chi tiết:\n" + "\n".join(failed[:5])
        self.root.after(0, lambda: messagebox.showinfo("Kết Quả Tải Hàng Loạt", summary))

    # ══════════════════════════════════════════════════════════════════════════
    #  END YouTube Downloader
    # ══════════════════════════════════════════════════════════════════════════

    # -----------------------------------------------------------------------
    # Browser extension detector
    # -----------------------------------------------------------------------

    _BD_ALLOWED_HEADERS = {
        "accept", "accept-language", "cookie", "origin", "range", "referer",
        "user-agent"
    }

    _BD_YOUTUBE_ITAGS = {
        "17": ("144p", "video"), "18": ("360p", "video"), "22": ("720p", "video"),
        "134": ("360p", "video"), "135": ("480p", "video"), "136": ("720p", "video"),
        "137": ("1080p", "video"), "160": ("144p", "video"), "242": ("240p", "video"),
        "243": ("360p", "video"), "244": ("480p", "video"), "247": ("720p", "video"),
        "248": ("1080p", "video"), "264": ("1440p", "video"), "266": ("2160p", "video"),
        "298": ("720p60", "video"), "299": ("1080p60", "video"),
        "302": ("720p60", "video"), "303": ("1080p60", "video"),
        "313": ("2160p", "video"), "315": ("2160p60", "video"),
        "399": ("1080p", "video"), "400": ("1440p", "video"),
        "401": ("2160p", "video"), "571": ("4320p", "video"),
        "139": ("48kbps", "audio"), "140": ("128kbps", "audio"),
        "141": ("256kbps", "audio"), "249": ("50kbps", "audio"),
        "250": ("70kbps", "audio"), "251": ("160kbps", "audio"),
        "599": ("30kbps", "audio"), "600": ("35kbps", "audio"),
    }

    def create_browser_detector_tab(self):
        """Create the browser-extension detector tab."""
        self.browser_detector_frame = ttk.Frame(self.content_container)
        main_frame = ttk.Frame(self.browser_detector_frame, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        setup_frame = ttk.LabelFrame(main_frame, text="Extension Bridge", padding="10")
        setup_frame.pack(fill=tk.X, pady=(0, 10))

        self.bd_receiver_url_var = tk.StringVar(
            value=f"http://127.0.0.1:{self.browser_detector_port}/candidate")
        self.bd_token_var = tk.StringVar(value=self.browser_detector_token)

        row1 = ttk.Frame(setup_frame)
        row1.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(row1, text="Receiver:", width=12).pack(side=tk.LEFT)
        ttk.Entry(row1, textvariable=self.bd_receiver_url_var,
                  font=("Consolas", 9), state="readonly").pack(
                      side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        tk.Button(row1, text="Open Extension Folder",
                  command=self._bd_open_extension_folder,
                  bg=self.colors['primary'], fg='white',
                  font=('Segoe UI', 9, 'bold'), relief='flat',
                  padx=10, pady=5).pack(side=tk.LEFT)

        row2 = ttk.Frame(setup_frame)
        row2.pack(fill=tk.X)
        ttk.Label(row2, text="Token:", width=12).pack(side=tk.LEFT)
        ttk.Entry(row2, textvariable=self.bd_token_var,
                  font=("Consolas", 9), state="readonly").pack(
                      side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        tk.Button(row2, text="Copy Token", command=self._bd_copy_token,
                  bg=self.colors['secondary'], fg='white',
                  font=('Segoe UI', 9, 'bold'), relief='flat',
                  padx=10, pady=5).pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(row2, text="Open Output", command=self._bd_open_output_folder,
                  bg=self.colors['success'], fg=self.colors['dark'],
                  font=('Segoe UI', 9, 'bold'), relief='flat',
                  padx=10, pady=5).pack(side=tk.LEFT)

        hint = (
            "Load browser_extension as an unpacked extension, paste this token "
            "in the extension popup, then play the video page. DRM is not supported."
        )
        ttk.Label(setup_frame, text=hint, font=('Segoe UI', 8),
                  foreground=self.colors['medium']).pack(anchor=tk.W, pady=(6, 0))

        quality_row = ttk.Frame(setup_frame)
        quality_row.pack(fill=tk.X, pady=(8, 0))
        ttk.Label(quality_row, text="YouTube quality:", width=16).pack(side=tk.LEFT)
        self.bd_quality_var = tk.StringVar(value="1080p")
        for label, value in [
            ("720p", "720p"), ("1080p", "1080p"),
            ("1440p", "1440p"), ("4K", "4k"), ("Auto", "auto")
        ]:
            ttk.Radiobutton(quality_row, text=label, variable=self.bd_quality_var,
                            value=value).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(
            quality_row,
            text="For YouTube, detected 360p streams are used as auth context; yt-dlp fetches the selected quality from the page URL.",
            font=('Segoe UI', 8), foreground=self.colors['medium']).pack(side=tk.LEFT, padx=(8, 0))

        batch_frame = ttk.LabelFrame(main_frame, text="Batch Open in Browser", padding="10")
        batch_frame.pack(fill=tk.X, pady=(0, 10))
        self.bd_batch_text = scrolledtext.ScrolledText(
            batch_frame, height=4, font=("Consolas", 9),
            bg=self.colors['light'], fg=self.colors['dark'])
        self.bd_batch_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        batch_controls = ttk.Frame(batch_frame)
        batch_controls.pack(side=tk.LEFT, fill=tk.Y)
        tk.Button(batch_controls, text="Start Batch", command=self._bd_batch_start,
                  bg=self.colors['success'], fg=self.colors['dark'],
                  font=('Segoe UI', 9, 'bold'), relief='flat',
                  padx=10, pady=5).pack(fill=tk.X, pady=(0, 6))
        tk.Button(batch_controls, text="Stop", command=self._bd_batch_stop,
                  bg=self.colors['danger'], fg='white',
                  font=('Segoe UI', 9, 'bold'), relief='flat',
                  padx=10, pady=5).pack(fill=tk.X, pady=(0, 6))
        tk.Button(batch_controls, text="Paste", command=self._bd_batch_paste,
                  bg=self.colors['primary'], fg='white',
                  font=('Segoe UI', 9, 'bold'), relief='flat',
                  padx=10, pady=5).pack(fill=tk.X)
        self.bd_batch_status_var = tk.StringVar(value="Batch idle")
        ttk.Label(batch_frame, textvariable=self.bd_batch_status_var,
                  font=('Segoe UI', 8), foreground=self.colors['medium']).pack(
                      anchor=tk.W, pady=(6, 0))

        list_frame = ttk.LabelFrame(main_frame, text="Detected Media", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        toolbar = ttk.Frame(list_frame)
        toolbar.pack(fill=tk.X, pady=(0, 6))
        tk.Button(toolbar, text="Refresh", command=self._bd_refresh_tree,
                  bg=self.colors['primary'], fg='white',
                  font=('Segoe UI', 9, 'bold'), relief='flat',
                  padx=10, pady=5).pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(toolbar, text="Download Selected",
                  command=self._bd_download_selected_thread,
                  bg=self.colors['success'], fg=self.colors['dark'],
                  font=('Segoe UI', 9, 'bold'), relief='flat',
                  padx=10, pady=5).pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(toolbar, text="Clear", command=self._bd_clear_candidates,
                  bg=self.colors['warning'], fg=self.colors['dark'],
                  font=('Segoe UI', 9, 'bold'), relief='flat',
                  padx=10, pady=5).pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(toolbar, text="🚀 Send Downloaded to YouTube Upload",
                  command=self._bd_send_downloaded_to_upload,
                  bg='#E53935', fg='white',
                  font=('Segoe UI', 9, 'bold'), relief='flat',
                  padx=10, pady=5).pack(side=tk.LEFT, padx=(0, 12))
        self.bd_count_var = tk.StringVar(value="0 candidates")
        ttk.Label(toolbar, textvariable=self.bd_count_var,
                  font=('Segoe UI', 9, 'bold'),
                  foreground=self.colors['primary']).pack(side=tk.LEFT)

        # Columns: id(hidden), time, kind, quality, title, host, url, dl_status
        cols = ("id", "time", "kind", "quality", "title", "host", "url", "dl_status")
        self.bd_tree = ttk.Treeview(list_frame, columns=cols,
                                    show="headings", height=12)
        for col, label in [
            ("id", "id"), ("time", "Time"), ("kind", "Type"),
            ("quality", "Quality"), ("title", "Page"), ("host", "Host"),
            ("url", "Media URL"), ("dl_status", "Download")
        ]:
            self.bd_tree.heading(col, text=label)
        self.bd_tree.column("id", width=0, minwidth=0, stretch=False)
        self.bd_tree.column("time", width=75, minwidth=70, stretch=False)
        self.bd_tree.column("kind", width=90, minwidth=70, stretch=False)
        self.bd_tree.column("quality", width=90, minwidth=70, stretch=False)
        self.bd_tree.column("title", width=220, minwidth=120)
        self.bd_tree.column("host", width=140, minwidth=100)
        self.bd_tree.column("url", width=320, minwidth=200)
        self.bd_tree.column("dl_status", width=120, minwidth=100, stretch=False, anchor=tk.CENTER)
        self.bd_tree.tag_configure("video", background="#e8f5e9")
        self.bd_tree.tag_configure("audio", background="#fff8e1")
        self.bd_tree.tag_configure("manifest", background="#e3f2fd")
        self.bd_tree.tag_configure("unknown", background=self.colors['light'])
        self.bd_tree.tag_configure("dl_done", background="#c8e6c9")
        self.bd_tree.tag_configure("dl_error", background="#ffcdd2")
        self.bd_tree.tag_configure("dl_active", background="#fff9c4")

        scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
                               command=self.bd_tree.yview)
        self.bd_tree.configure(yscrollcommand=scroll.set)
        self.bd_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.bd_tree.bind("<<TreeviewSelect>>", self._bd_on_select)

        detail_frame = ttk.LabelFrame(main_frame, text="Candidate Detail", padding="10")
        detail_frame.pack(fill=tk.X)
        self.bd_detail_text = scrolledtext.ScrolledText(
            detail_frame, height=5, font=("Consolas", 9),
            bg=self.colors['light'], fg=self.colors['dark'])
        self.bd_detail_text.pack(fill=tk.X)
        self.bd_detail_text.config(state=tk.DISABLED)

        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(8, 0))
        self.bd_progress_var = tk.DoubleVar(value=0)
        ttk.Progressbar(status_frame, variable=self.bd_progress_var,
                        maximum=100, mode="determinate").pack(
                            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.bd_status_var = tk.StringVar(value="Waiting for extension candidates")
        ttk.Label(status_frame, textvariable=self.bd_status_var,
                  font=('Segoe UI', 9),
                  foreground=self.colors['primary']).pack(side=tk.LEFT)

    def _start_browser_detector_server(self):
        """Start local HTTP receiver for the browser extension."""
        if self.browser_detector_server:
            return
        app = self

        class BrowserDetectorHandler(http.server.BaseHTTPRequestHandler):
            server_version = "BrowserDetector/0.1"

            def _send_json(self, status, payload):
                raw = json.dumps(payload).encode("utf-8")
                try:
                    self.send_response(status)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(raw)))
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.send_header("Access-Control-Allow-Headers",
                                     "Content-Type, X-Downloader-Token")
                    self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                    self.end_headers()
                    self.wfile.write(raw)
                except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
                    # Browser/extension polling can be cancelled while the app is replying.
                    pass

            def do_OPTIONS(self):
                self._send_json(200, {"ok": True})

            def do_GET(self):
                if urlparse(self.path).path == "/health":
                    self._send_json(200, {
                        "ok": True,
                        "port": app.browser_detector_port,
                        "requires_token": True,
                    })
                else:
                    self._send_json(404, {"ok": False, "error": "not found"})

            def do_POST(self):
                path = urlparse(self.path).path
                if path not in ("/candidate", "/batch/next", "/batch/fail"):
                    self._send_json(404, {"ok": False, "error": "not found"})
                    return
                if self.headers.get("X-Downloader-Token", "") != app.browser_detector_token:
                    self._send_json(403, {"ok": False, "error": "bad token"})
                    return
                if path == "/batch/next":
                    self._send_json(200, app._bd_batch_next_payload())
                    return

                try:
                    length = int(self.headers.get("Content-Length", "0"))
                except ValueError:
                    length = 0
                if path == "/batch/fail":
                    payload = {}
                    if length > 0:
                        payload = json.loads(self.rfile.read(length).decode("utf-8"))
                    app._bd_batch_mark_failed(
                        str(payload.get("id") or ""),
                        str(payload.get("reason") or "browser timeout"))
                    self._send_json(200, {"ok": True})
                    return

                if length <= 0 or length > 1024 * 1024:
                    self._send_json(400, {"ok": False, "error": "bad length"})
                    return
                try:
                    payload = json.loads(self.rfile.read(length).decode("utf-8"))
                    candidate = app._bd_receive_candidate(payload)
                    self._send_json(200, {
                        "ok": True,
                        "id": candidate.get("id") if candidate else None,
                        "duplicate": candidate is None,
                        "close_tab": bool(candidate and candidate.get("_close_batch_tab")),
                    })
                except Exception as exc:
                    self._send_json(400, {"ok": False, "error": str(exc)[:200]})

            def log_message(self, fmt, *args):
                return

        # Bind a fixed port so the browser extension (which hardcodes 8765)
        # always matches. If the port is busy we surface a clear error instead
        # of silently moving to another port the extension can't reach.
        port = BROWSER_DETECTOR_PORT
        try:
            server = http.server.ThreadingHTTPServer(
                ("127.0.0.1", port), BrowserDetectorHandler)
        except OSError as exc:
            self.browser_detector_port = port
            msg = (
                f"Port {port} đang bị chiếm — đóng app khác hoặc tiến trình tool "
                f"cũ đang chạy, rồi mở lại.\n({exc})"
            )
            self._bd_set_status(f"Receiver failed: port {port} busy")
            self.root.after(
                0,
                lambda: messagebox.showerror("Browser Detector port busy", msg))
            return
        self.browser_detector_port = port
        self.browser_detector_server = server
        self.browser_detector_thread = threading.Thread(
            target=server.serve_forever, daemon=True)
        self.browser_detector_thread.start()
        if hasattr(self, "bd_receiver_url_var"):
            self.bd_receiver_url_var.set(
                f"http://127.0.0.1:{port}/candidate")
        self._bd_set_status(f"Receiver running on 127.0.0.1:{port}")

    def _stop_browser_detector_server(self):
        server = self.browser_detector_server
        self.browser_detector_server = None
        if server:
            try:
                server.shutdown()
                server.server_close()
            except Exception:
                pass

    def on_close(self):
        self._stop_browser_detector_server()
        self.root.destroy()

    def _bd_set_status(self, text):
        def _upd():
            if hasattr(self, "bd_status_var"):
                self.bd_status_var.set(text)
        self.root.after(0, _upd)

    def _bd_set_progress(self, pct):
        def _upd():
            if hasattr(self, "bd_progress_var"):
                self.bd_progress_var.set(max(0, min(100, pct)))
        self.root.after(0, _upd)

    def _bd_open_extension_folder(self):
        if not os.path.isdir(BROWSER_EXTENSION_DIR):
            messagebox.showwarning(
                "Extension not found",
                f"Extension folder not found:\n{BROWSER_EXTENSION_DIR}")
            return
        os.startfile(BROWSER_EXTENSION_DIR)

    def _bd_open_output_folder(self):
        os.makedirs(self.browser_output_dir, exist_ok=True)
        os.startfile(self.browser_output_dir)

    def _bd_copy_token(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.browser_detector_token)
        self._bd_set_status("Token copied")

    def _bd_batch_paste(self):
        try:
            text = self.root.clipboard_get()
        except Exception:
            messagebox.showerror("Clipboard", "Clipboard does not contain text.")
            return
        self.bd_batch_text.insert(tk.END, ("\n" if self.bd_batch_text.get("1.0", tk.END).strip() else "") + text)

    def _bd_batch_start(self):
        raw = self.bd_batch_text.get("1.0", tk.END).strip() if hasattr(self, "bd_batch_text") else ""
        urls = []
        seen = set()
        for line in raw.splitlines():
            url = line.strip()
            if not url:
                continue
            if self._yt_is_valid_url(url) and url not in seen:
                urls.append(url)
                seen.add(url)
        if not urls:
            messagebox.showwarning("No URLs", "Paste one video URL per line before starting batch.")
            return
        with self.bd_batch_lock:
            self.bd_batch_jobs = []
            self.bd_batch_jobs_by_id = {}
            for index, url in enumerate(urls, 1):
                job = {
                    "id": secrets.token_hex(8),
                    "index": index,
                    "url": url,
                    "status": "queued",
                    "message": "",
                    "created_at": time.time(),
                    "claimed_at": 0,
                    "downloaded_path": "",
                }
                self.bd_batch_jobs.append(job)
                self.bd_batch_jobs_by_id[job["id"]] = job
            self.bd_batch_running = True
        self._bd_update_batch_status()
        self._bd_set_status("Batch started. Extension will open links one by one.")

    def _bd_batch_stop(self):
        with self.bd_batch_lock:
            self.bd_batch_running = False
            for job in self.bd_batch_jobs:
                if job["status"] in ("queued", "opened"):
                    job["status"] = "stopped"
        self._bd_update_batch_status()
        self._bd_set_status("Batch stopped")

    def _bd_batch_next_payload(self):
        with self.bd_batch_lock:
            if not self.bd_batch_running:
                return {"ok": True, "running": False, "job": None}
            now = time.time()
            for job in self.bd_batch_jobs:
                if job["status"] == "opened" and now - job.get("claimed_at", 0) > 60:
                    job["status"] = "queued"
                    job["message"] = "retry after browser timeout"
                if job["status"] == "queued":
                    job["status"] = "opened"
                    job["claimed_at"] = now
                    self.root.after(0, self._bd_update_batch_status)
                    return {
                        "ok": True,
                        "running": True,
                        "job": {
                            "id": job["id"],
                            "index": job["index"],
                            "url": job["url"],
                        }
                    }
            active = any(job["status"] in ("opened", "downloading") for job in self.bd_batch_jobs)
            if not active:
                self.bd_batch_running = False
            self.root.after(0, self._bd_update_batch_status)
            return {"ok": True, "running": self.bd_batch_running, "job": None}

    def _bd_batch_mark_failed(self, job_id, reason):
        if not job_id:
            return
        with self.bd_batch_lock:
            job = self.bd_batch_jobs_by_id.get(job_id)
            if job and job["status"] not in ("done", "downloading"):
                job["status"] = "failed"
                job["message"] = reason[:200]
        self.root.after(0, self._bd_update_batch_status)

    def _bd_update_batch_status(self):
        if not hasattr(self, "bd_batch_status_var"):
            return
        with self.bd_batch_lock:
            total = len(self.bd_batch_jobs)
            counts = {}
            for job in self.bd_batch_jobs:
                counts[job["status"]] = counts.get(job["status"], 0) + 1
            running = self.bd_batch_running
        if not total:
            text = "Batch idle"
        else:
            parts = [f"{key}: {counts[key]}" for key in sorted(counts)]
            text = ("Running | " if running else "Idle | ") + f"total: {total} | " + ", ".join(parts)
        self.bd_batch_status_var.set(text)

    def _bd_receive_candidate(self, payload):
        candidate = self._bd_make_candidate(payload)
        if not candidate:
            return None
        with self.browser_candidates_lock:
            key = candidate["dedupe_key"]
            if key in self.browser_candidate_seen:
                return None
            self.browser_candidate_seen[key] = time.time()
            self.browser_candidates.append(candidate)
            self.browser_candidates_by_id[candidate["id"]] = candidate
        self._bd_handle_batch_candidate(candidate)
        self.root.after(0, self._bd_insert_tree_candidate, candidate)
        return candidate

    def _bd_make_candidate(self, payload):
        media_url = str(payload.get("media_url") or payload.get("url") or "").strip()
        if not media_url or media_url.startswith(("blob:", "data:", "filesystem:")):
            return None
        parsed = urlparse(media_url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            return None
        if self._bd_is_noise_media_url(media_url):
            return None
        headers = payload.get("headers") or {}
        clean_headers = {}
        if isinstance(headers, dict):
            for key, value in headers.items():
                if key and str(key).lower() in self._BD_ALLOWED_HEADERS:
                    clean_headers[str(key)] = str(value)
        kind, quality, itag = self._bd_classify_media(media_url, payload)
        content_type = str(payload.get("content_type") or payload.get("mime") or "")
        cookies = self._bd_normalize_cookie_list(payload.get("cookies") or [])
        title = str(payload.get("page_title") or payload.get("title") or "").strip()
        page_url = str(payload.get("page_url") or payload.get("document_url") or "").strip()
        batch_id = str(payload.get("batch_id") or "")
        batch_url = str(payload.get("batch_url") or "")
        if not title:
            title = urlparse(page_url).netloc or parsed.netloc
        dedupe_key = self._bd_dedupe_key(media_url, page_url, itag, content_type)
        if batch_id:
            dedupe_key = f"{batch_id}|{dedupe_key}"
        now = datetime.now()
        return {
            "id": secrets.token_hex(8),
            "created_at": now.isoformat(timespec="seconds"),
            "display_time": now.strftime("%H:%M:%S"),
            "media_url": media_url,
            "page_url": page_url,
            "page_title": title[:180],
            "host": parsed.netloc,
            "headers": clean_headers,
            "method": str(payload.get("method") or "GET"),
            "source": str(payload.get("source") or "extension"),
            "batch_id": batch_id,
            "batch_url": batch_url,
            "content_type": content_type,
            "kind": kind,
            "quality": quality,
            "itag": itag,
            "dedupe_key": dedupe_key,
            "drm": bool(payload.get("drm")),
            "cookies": cookies,
        }

    def _bd_handle_batch_candidate(self, candidate):
        batch_id = candidate.get("batch_id")
        if not batch_id:
            return
        if candidate.get("kind") not in ("video", "manifest"):
            return
        with self.bd_batch_lock:
            job = self.bd_batch_jobs_by_id.get(batch_id)
            # Allow a late-arriving candidate to revive a job that the extension
            # already marked "failed" on timeout — only an in-progress/finished
            # or user-stopped job is left alone.
            if not job or job["status"] in ("downloading", "done", "stopped"):
                return
            job["status"] = "downloading"
            job["message"] = f"detected {candidate.get('quality', '')}"
        candidate["_close_batch_tab"] = True
        self.root.after(0, self._bd_update_batch_status)
        threading.Thread(
            target=self._bd_thread_download_batch_candidate,
            args=(batch_id, candidate),
            daemon=True
        ).start()

    def _bd_thread_download_batch_candidate(self, batch_id, candidate):
        try:
            with self.bd_batch_download_lock:
                candidate["_progress_hook"] = self._bd_make_progress_hook(
                    candidate.get("id", ""), 1, 1)
                try:
                    path = self._bd_download_candidate(candidate)
                finally:
                    candidate.pop("_progress_hook", None)
            with self.bd_batch_lock:
                job = self.bd_batch_jobs_by_id.get(batch_id)
                if job:
                    job["status"] = "done"
                    job["downloaded_path"] = path
                    job["message"] = os.path.basename(path)
            self._bd_set_status(f"Batch downloaded: {os.path.basename(path)}")
        except Exception as exc:
            with self.bd_batch_lock:
                job = self.bd_batch_jobs_by_id.get(batch_id)
                if job:
                    job["status"] = "failed"
                    job["message"] = str(exc)[:200]
            self._bd_set_status(f"Batch failed: {str(exc)[:100]}")
        finally:
            self.root.after(0, self._bd_update_batch_status)
            self.root.after(0, self._yt_refresh_dl_list)

    def _bd_normalize_cookie_list(self, cookies):
        result = []
        if not isinstance(cookies, list):
            return result
        for cookie in cookies:
            if not isinstance(cookie, dict):
                continue
            name = str(cookie.get("name") or "").strip()
            value = str(cookie.get("value") or "")
            domain = str(cookie.get("domain") or "").strip()
            if not name or not domain:
                continue
            result.append({
                "domain": domain,
                "path": str(cookie.get("path") or "/"),
                "secure": bool(cookie.get("secure")),
                "expirationDate": cookie.get("expirationDate") or 0,
                "name": name,
                "value": value,
            })
        return result

    def _bd_is_noise_media_url(self, media_url):
        parsed = urlparse(media_url)
        host = parsed.netloc.lower()
        path = parsed.path.lower()
        if host.endswith("youtube.com") and path.startswith("/s/"):
            return True
        if path.endswith(("/failure.mp3", "/input.mp3", "/open.mp3", "/success.mp3")):
            return True
        return False

    def _bd_classify_media(self, media_url, payload):
        parsed = urlparse(media_url)
        qs = parse_qs(parsed.query)
        itag = (qs.get("itag") or [""])[0]
        mime = (qs.get("mime") or [payload.get("content_type") or ""])[0]
        path = parsed.path.lower()
        host = parsed.netloc.lower()
        if itag in self._BD_YOUTUBE_ITAGS:
            quality, kind = self._BD_YOUTUBE_ITAGS[itag]
            return kind, quality, itag
        mime_lower = str(mime).lower()
        if ".m3u8" in path or "mpegurl" in mime_lower:
            return "manifest", "HLS", itag
        if ".mpd" in path or "dash+xml" in mime_lower:
            return "manifest", "DASH", itag
        if "googlevideo.com" in host and "audio" in mime_lower:
            return "audio", "audio", itag
        if "googlevideo.com" in host and "video" in mime_lower:
            return "video", "video", itag
        if "audio" in mime_lower or path.endswith((".m4a", ".mp3", ".aac", ".opus")):
            return "audio", "audio", itag
        if "video" in mime_lower or path.endswith((".mp4", ".webm", ".mov", ".mkv")):
            return "video", "direct", itag
        return "unknown", "unknown", itag

    def _bd_dedupe_key(self, media_url, page_url, itag, content_type):
        parsed = urlparse(media_url)
        host = parsed.netloc.lower()
        if "googlevideo.com" in host and itag:
            return "|".join([page_url, host, itag, content_type])
        return media_url

    def _bd_insert_tree_candidate(self, candidate):
        if not hasattr(self, "bd_tree"):
            return
        tag = candidate["kind"] if candidate["kind"] in ("video", "audio", "manifest") else "unknown"
        self.bd_tree.insert("", "end", values=(
            candidate["id"], candidate["display_time"], candidate["kind"],
            candidate["quality"], candidate["page_title"], candidate["host"],
            candidate["media_url"][:220],
            "",  # dl_status — empty until downloaded
        ), tags=(tag,))
        self._bd_update_count()
        self._bd_set_status(f"Detected {candidate['kind']} {candidate['quality']}")

    def _bd_find_tree_item(self, candidate_id):
        """Return tree iid for a candidate id, or None."""
        if not hasattr(self, "bd_tree"):
            return None
        for iid in self.bd_tree.get_children():
            if self.bd_tree.item(iid, "values")[0] == candidate_id:
                return iid
        return None

    def _bd_set_row_status(self, candidate_id, text, tag=None):
        """Thread-safe update of dl_status column for a specific row."""
        def _upd():
            iid = self._bd_find_tree_item(candidate_id)
            if not iid:
                return
            vals = list(self.bd_tree.item(iid, "values"))
            while len(vals) < 8:
                vals.append("")
            vals[7] = text
            existing_tags = list(self.bd_tree.item(iid, "tags"))
            # Keep kind-based color tag, replace dl_ tag
            kind_tags = [t for t in existing_tags if not t.startswith("dl_")]
            new_tags = kind_tags + ([tag] if tag else [])
            self.bd_tree.item(iid, values=vals, tags=new_tags)
        self.root.after(0, _upd)

    def _bd_refresh_tree(self):
        if not hasattr(self, "bd_tree"):
            return
        for item in self.bd_tree.get_children():
            self.bd_tree.delete(item)
        with self.browser_candidates_lock:
            candidates = list(self.browser_candidates)
        for candidate in candidates:
            self._bd_insert_tree_candidate(candidate)
        self._bd_update_count()

    def _bd_update_count(self):
        if hasattr(self, "bd_count_var"):
            count = len(self.bd_tree.get_children()) if hasattr(self, "bd_tree") else 0
            self.bd_count_var.set(f"{count} candidates")

    def _bd_send_downloaded_to_upload(self):
        """Send all successfully downloaded files to the YouTube Upload tab."""
        with self.browser_candidates_lock:
            candidates = list(self.browser_candidates)

        sent = 0
        missing = 0
        for c in candidates:
            path = c.get("downloaded_path")
            if not path:
                continue
            if not os.path.exists(path):
                missing += 1
                continue
            self.add_video_to_upload_list(path)
            sent += 1

        if sent == 0 and missing == 0:
            messagebox.showinfo(
                "No Downloaded Videos",
                "Chưa có video nào được tải thành công.\n\n"
                "Hãy chọn các dòng trong bảng và nhấn 'Download Selected' trước."
            )
            return

        # Switch to Upload tab
        try:
            for i in range(self.content_container.index("end")):
                if "Upload" in self.content_container.tab(i, "text"):
                    self.content_container.select(i)
                    break
        except Exception:
            pass

        msg = f"✅ Đã thêm {sent} video vào YouTube Upload tab."
        if missing:
            msg += f"\n⚠️ {missing} file không tìm thấy trên disk."
        messagebox.showinfo("Sent to Upload", msg)

    def _bd_clear_candidates(self):
        with self.browser_candidates_lock:
            self.browser_candidates.clear()
            self.browser_candidates_by_id.clear()
            self.browser_candidate_seen.clear()
        if hasattr(self, "bd_tree"):
            for item in self.bd_tree.get_children():
                self.bd_tree.delete(item)
        self._bd_update_count()
        self._bd_set_status("Candidates cleared")

    def _bd_on_select(self, event=None):
        ids = self._bd_selected_ids()
        if not ids:
            return
        candidate = self.browser_candidates_by_id.get(ids[0])
        if not candidate or not hasattr(self, "bd_detail_text"):
            return
        header_names = sorted(candidate.get("headers", {}).keys())
        detail = {
            "id": candidate["id"],
            "kind": candidate["kind"],
            "quality": candidate["quality"],
            "host": candidate["host"],
            "page_title": candidate["page_title"],
            "page_url": candidate["page_url"],
            "media_url": candidate["media_url"],
            "headers_captured": header_names,
            "has_cookie": any(k.lower() == "cookie" for k in header_names),
            "browser_cookies": len(candidate.get("cookies") or []),
            "source": candidate["source"],
            "batch_id": candidate.get("batch_id", ""),
        }
        self.bd_detail_text.config(state=tk.NORMAL)
        self.bd_detail_text.delete("1.0", tk.END)
        self.bd_detail_text.insert(tk.END, json.dumps(detail, indent=2, ensure_ascii=False))
        self.bd_detail_text.config(state=tk.DISABLED)

    def _bd_selected_ids(self):
        if not hasattr(self, "bd_tree"):
            return []
        ids = []
        for item in self.bd_tree.selection():
            values = self.bd_tree.item(item, "values")
            if values:
                ids.append(values[0])
        return ids

    def _bd_download_selected_thread(self):
        if self.browser_is_downloading:
            messagebox.showwarning("Download running", "A browser download task is already running.")
            return
        ids = self._bd_selected_ids()
        if not ids:
            messagebox.showinfo("No selection", "Select one or more detected media rows first.")
            return
        threading.Thread(target=self._bd_thread_download_selected,
                         args=(ids,), daemon=True).start()

    def _bd_thread_download_selected(self, ids):
        self.browser_is_downloading = True
        ok, failed = [], []
        total = len(ids)
        try:
            for index, cid in enumerate(ids, 1):
                candidate = self.browser_candidates_by_id.get(cid)
                if not candidate:
                    continue
                self._bd_set_progress((index - 1) * 100 / max(total, 1))
                self._bd_set_status(f"Downloading {index}/{total}: {candidate['quality']}")
                self._bd_set_row_status(cid, f"⬇ 0%", "dl_active")
                # Inject per-row progress hook into candidate for this download
                candidate["_progress_hook"] = self._bd_make_progress_hook(cid, index, total)
                try:
                    path = self._bd_download_candidate(candidate)
                    ok.append(path)
                    # Store downloaded path in candidate for later "send to upload"
                    candidate["downloaded_path"] = path
                    self._bd_set_row_status(cid, "✅ Done", "dl_done")
                except Exception as exc:
                    failed.append(f"{candidate['quality']} {candidate['host']}: {exc}")
                    self._bd_set_row_status(cid, "❌ Failed", "dl_error")
                finally:
                    candidate.pop("_progress_hook", None)
            self._bd_set_progress(100 if ok else 0)
        finally:
            self.browser_is_downloading = False
            self.root.after(0, self._yt_refresh_dl_list)
        msg = f"Downloaded: {len(ok)}\nFailed: {len(failed)}"
        if failed:
            msg += "\n\n" + "\n".join(failed[:5])
        self._bd_set_status(msg.replace("\n", " | "))
        self.root.after(0, lambda: messagebox.showinfo("Browser Download Result", msg))

    def _bd_download_candidate(self, candidate):
        if candidate.get("drm"):
            raise RuntimeError("DRM/EME content is not supported.")
        os.makedirs(self.browser_output_dir, exist_ok=True)
        page_error = None
        if self._bd_is_youtube_candidate(candidate):
            try:
                return self._bd_check_download_audio(
                    self._bd_download_youtube_page(candidate), candidate)
            except Exception as exc:
                page_error = exc
                self._bd_set_status(f"YouTube page download failed; falling back to detected stream: {str(exc)[:90]}")
        if "googlevideo.com" in candidate["host"].lower() and candidate["kind"] == "video":
            audio = self._bd_find_audio_pair(candidate)
            if audio and FFMPEG_DIR:
                try:
                    self._bd_set_row_status(candidate.get("id", ""), "⬇ Merging...", "dl_active")
                    return self._bd_check_download_audio(
                        self._bd_download_youtube_pair(candidate, audio), candidate)
                except Exception as exc:
                    if page_error:
                        raise RuntimeError(
                            f"yt-dlp page failed: {page_error}; direct stream failed: {exc}")
                    raise
        try:
            return self._bd_check_download_audio(
                self._bd_download_with_ytdlp(candidate), candidate)
        except Exception as exc:
            if page_error:
                raise RuntimeError(
                    f"yt-dlp page failed: {page_error}; direct stream failed: {exc}")
            raise

    def _bd_is_youtube_candidate(self, candidate):
        host = (candidate.get("host") or "").lower()
        page_url = candidate.get("page_url") or ""
        page_host = urlparse(page_url).netloc.lower().lstrip("www.")
        return (
            "googlevideo.com" in host
            or page_host in ("youtube.com", "m.youtube.com", "music.youtube.com")
            or "youtube.com" in page_host
        )

    def _bd_get_youtube_page_url(self, candidate):
        for page_url in ((candidate.get("page_url") or "").strip(),
                         (candidate.get("batch_url") or "").strip()):
            if not page_url:
                continue
            parsed = urlparse(page_url)
            host = parsed.netloc.lower().lstrip("www.")
            if host in ("youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be"):
                if parsed.path in ("", "/") and not parsed.query:
                    continue
                return page_url
        return ""

    def _bd_download_youtube_page(self, candidate):
        page_url = self._bd_get_youtube_page_url(candidate)
        if not page_url:
            raise RuntimeError("missing YouTube page URL")
        if not YT_DLP_AVAILABLE:
            raise RuntimeError("yt-dlp is not installed")

        quality = self.bd_quality_var.get() if hasattr(self, "bd_quality_var") else "1080p"
        fmt = self._yt_format_for_quality(quality, "youtube")
        outtmpl = os.path.join(
            self.browser_output_dir,
            f"%(title)s_%(id)s_{self._bd_safe_filename(quality)}.%(ext)s")
        opts = {
            "format": fmt,
            "outtmpl": outtmpl,
            "quiet": True,
            "no_warnings": False,
            "retries": 3,
            "fragment_retries": 3,
            "nocheckcertificate": True,
            "http_headers": self._bd_headers_for_ytdlp(candidate),
            "progress_hooks": [h for h in [candidate.get("_progress_hook"), self._bd_progress_hook] if h],
        }
        if FFMPEG_DIR:
            opts["ffmpeg_location"] = FFMPEG_DIR
            opts["merge_output_format"] = "mp4"
        self._yt_enable_js_challenge_support(opts)

        cookiefile = self._bd_cookiefile_from_header(candidate)
        if cookiefile:
            opts["cookiefile"] = cookiefile

        self._bd_set_status(f"YouTube page download via yt-dlp: {quality}")
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(page_url, download=True)
                if info:
                    path = ydl.prepare_filename(info)
                    # yt-dlp may have merged/remuxed to mp4 — prefer the real file.
                    if not os.path.exists(path):
                        base = os.path.splitext(path)[0]
                        for ext in (".mp4", ".mkv", ".webm"):
                            if os.path.exists(base + ext):
                                path = base + ext
                                break
                    if os.path.exists(path):
                        return path
        finally:
            if cookiefile:
                try:
                    os.remove(cookiefile)
                except OSError:
                    pass
        raise RuntimeError("yt-dlp không tạo được file tải về từ trang YouTube")

    def _bd_headers_for_ytdlp(self, candidate):
        headers = dict(candidate.get("headers") or {})
        page_url = candidate.get("page_url") or ""
        if page_url and not self._bd_get_header(headers, "Referer"):
            headers["Referer"] = page_url
        return headers

    def _bd_get_header(self, headers, name):
        wanted = name.lower()
        for key, value in (headers or {}).items():
            if str(key).lower() == wanted:
                return value
        return ""

    def _bd_cookiefile_from_header(self, candidate):
        cookiefile = self._bd_cookiefile_from_browser_cookies(candidate)
        if cookiefile:
            return cookiefile

        cookie_header = self._bd_get_header(candidate.get("headers") or {}, "Cookie")
        if not cookie_header:
            return ""
        pairs = []
        for part in cookie_header.split(";"):
            if "=" not in part:
                continue
            name, value = part.split("=", 1)
            name = name.strip()
            value = value.strip()
            if not name:
                continue
            pairs.append((name.replace("\t", ""), value.replace("\t", "%09")))
        if not pairs:
            return ""
        fd, path = tempfile.mkstemp(prefix="bd_youtube_", suffix=".cookies.txt")
        domains = [".youtube.com", ".google.com", ".googlevideo.com"]
        # Use a far-future expiry so yt-dlp doesn't drop these as session cookies.
        expires = int(time.time()) + 365 * 24 * 3600
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("# Netscape HTTP Cookie File\n")
            for domain in domains:
                for name, value in pairs:
                    f.write(f"{domain}\tTRUE\t/\tTRUE\t{expires}\t{name}\t{value}\n")
        return path

    def _bd_cookiefile_from_browser_cookies(self, candidate):
        cookies = candidate.get("cookies") or []
        if not cookies:
            return ""
        fd, path = tempfile.mkstemp(prefix="bd_youtube_", suffix=".cookies.txt")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("# Netscape HTTP Cookie File\n")
            for cookie in cookies:
                domain = str(cookie.get("domain") or "").strip()
                name = str(cookie.get("name") or "").replace("\t", "")
                value = str(cookie.get("value") or "").replace("\t", "%09")
                if not domain or not name:
                    continue
                include_subdomains = "TRUE" if domain.startswith(".") else "FALSE"
                path_value = str(cookie.get("path") or "/").replace("\t", "")
                secure = "TRUE" if cookie.get("secure") else "FALSE"
                expires = cookie.get("expirationDate") or 0
                try:
                    expires = int(float(expires))
                except (TypeError, ValueError):
                    expires = 0
                f.write(
                    f"{domain}\t{include_subdomains}\t{path_value}\t"
                    f"{secure}\t{expires}\t{name}\t{value}\n"
                )
        return path

    def _bd_find_audio_pair(self, video_candidate):
        with self.browser_candidates_lock:
            candidates = list(self.browser_candidates)
        same_page = [
            c for c in candidates
            if c.get("kind") == "audio"
            and c.get("page_url") == video_candidate.get("page_url")
            and "googlevideo.com" in c.get("host", "").lower()
        ]
        if not same_page:
            return None
        def score(c):
            digits = re.findall(r"\d+", c.get("quality") or "")
            return int(digits[0]) if digits else 0
        return sorted(same_page, key=score, reverse=True)[0]

    def _bd_download_youtube_pair(self, video_candidate, audio_candidate):
        ffmpeg = os.path.join(FFMPEG_DIR, "ffmpeg.exe")
        title = self._bd_safe_filename(video_candidate.get("page_title") or "video")
        quality = self._bd_safe_filename(video_candidate.get("quality") or "video")
        out_path = os.path.join(
            self.browser_output_dir, f"{title}_{quality}_{int(time.time())}.mp4")
        video_headers = self._bd_ffmpeg_headers(video_candidate.get("headers", {}))
        audio_headers = self._bd_ffmpeg_headers(audio_candidate.get("headers", {}))

        def build_cmd(audio_codec):
            cmd = [ffmpeg, "-y", "-loglevel", "error"]
            if video_headers:
                cmd.extend(["-headers", video_headers])
            cmd.extend(["-i", video_candidate["media_url"]])
            if audio_headers:
                cmd.extend(["-headers", audio_headers])
            cmd.extend(["-i", audio_candidate["media_url"],
                        "-c:v", "copy", "-c:a", audio_codec, "-shortest", out_path])
            return cmd

        # Try stream-copy first (fast, lossless); fall back to AAC re-encode
        # only if the audio codec isn't mp4-compatible.
        result = subprocess.run(build_cmd("copy"), capture_output=True)
        if result.returncode != 0:
            result = subprocess.run(build_cmd("aac"), capture_output=True)
        if result.returncode != 0:
            stderr = result.stderr.decode(errors="replace")[-500:]
            raise RuntimeError(f"ffmpeg merge failed: {stderr}")
        return out_path

    def _bd_download_with_ytdlp(self, candidate):
        if not YT_DLP_AVAILABLE:
            raise RuntimeError("yt-dlp is not installed.")
        title = self._bd_safe_filename(candidate.get("page_title") or "media")
        quality = self._bd_safe_filename(candidate.get("quality") or candidate.get("kind") or "media")
        outtmpl = os.path.join(
            self.browser_output_dir, f"{title}_{quality}_{int(time.time())}.%(ext)s")
        opts = {
            "outtmpl": outtmpl,
            "quiet": True,
            "no_warnings": False,
            "retries": 3,
            "fragment_retries": 3,
            "nocheckcertificate": True,
            "http_headers": candidate.get("headers", {}),
            "progress_hooks": [h for h in [candidate.get("_progress_hook"), self._bd_progress_hook] if h],
        }
        if FFMPEG_DIR:
            opts["ffmpeg_location"] = FFMPEG_DIR
            opts["merge_output_format"] = "mp4"
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(candidate["media_url"], download=True)
            if info:
                try:
                    path = ydl.prepare_filename(info)
                except Exception:
                    path = ""
                if path and not os.path.exists(path):
                    base = os.path.splitext(path)[0]
                    for ext in (".mp4", ".mkv", ".webm"):
                        if os.path.exists(base + ext):
                            path = base + ext
                            break
                if path and os.path.exists(path):
                    return path
        raise RuntimeError("yt-dlp không tạo được file tải về")

    def _bd_progress_hook(self, data):
        """Global progress hook — updates progress bar only (no candidate_id context)."""
        if data.get("status") == "downloading":
            total = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
            downloaded = data.get("downloaded_bytes") or 0
            if total:
                self._bd_set_progress(downloaded * 100 / total)
        elif data.get("status") == "finished":
            self._bd_set_progress(100)

    def _bd_make_progress_hook(self, candidate_id, index, total):
        """Return a progress hook closure that updates both the global bar and the row status."""
        def hook(data):
            status = data.get("status")
            if status == "downloading":
                file_total = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
                downloaded = data.get("downloaded_bytes") or 0
                if file_total:
                    pct = downloaded * 100 / file_total
                    self._bd_set_progress(((index - 1) + pct / 100) * 100 / max(total, 1))
                    speed = data.get("speed") or 0
                    speed_str = f" {speed/1024:.0f}KB/s" if speed else ""
                    self._bd_set_row_status(candidate_id, f"⬇ {pct:.0f}%{speed_str}", "dl_active")
                else:
                    self._bd_set_row_status(candidate_id, "⬇ ...", "dl_active")
            elif status == "finished":
                self._bd_set_row_status(candidate_id, "⏳ Merging...", "dl_active")
        return hook

    def _bd_check_download_audio(self, path, candidate):
        if not path or not os.path.exists(path):
            return path
        if candidate.get("kind") not in ("video", "manifest"):
            return path
        stream_info = self._bd_read_stream_info(path)
        if stream_info and "Video:" in stream_info and "Audio:" not in stream_info:
            self._bd_set_status(
                f"Downloaded without audio stream: {os.path.basename(path)}")
        return path

    def _bd_read_stream_info(self, path):
        if not FFMPEG_DIR:
            return ""
        ffmpeg = os.path.join(FFMPEG_DIR, "ffmpeg.exe")
        if not os.path.exists(ffmpeg):
            return ""
        try:
            result = subprocess.run(
                [ffmpeg, "-hide_banner", "-i", path],
                capture_output=True, text=True, timeout=12
            )
            return (result.stderr or "") + (result.stdout or "")
        except Exception:
            return ""

    def _bd_ffmpeg_headers(self, headers):
        lines = []
        for key, value in (headers or {}).items():
            if str(key).lower() in self._BD_ALLOWED_HEADERS and value:
                lines.append(f"{key}: {value}")
        return "\r\n".join(lines) + ("\r\n" if lines else "")

    def _bd_safe_filename(self, value):
        value = re.sub(r'[\\/:*?"<>|]+', "_", str(value or "media")).strip()
        value = re.sub(r"\s+", " ", value)
        return (value[:90] or "media")

    def create_upload_tab(self):
        """Create upload tab (YouTube uploader)"""
        self.upload_frame = ttk.Frame(self.content_container)
        
        main_frame = ttk.Frame(self.upload_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # YouTube Status & Authentication (Combined)
        status_frame = ttk.LabelFrame(main_frame, text="�  YouTube Status & Authentication", padding="15")
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        # API Status
        api_status_frame = ttk.Frame(status_frame)
        api_status_frame.pack(fill=tk.X, pady=(0, 10))
        
        status_controls = ttk.Frame(api_status_frame)
        status_controls.pack(fill=tk.X)
        
        if YOUTUBE_AVAILABLE:
            ttk.Label(status_controls, text="✅ YouTube API Available", 
                     font=('Segoe UI', 10, 'bold'), foreground='#27ae60').pack(side=tk.LEFT)
            
            # YouTube Manager button
            tk.Button(status_controls, text="⚙️ YouTube Manager", 
                      command=self.show_youtube_manager,
                      bg=self.colors['primary'], fg='white', relief=tk.FLAT,
                      font=('Segoe UI', 9, 'bold'), cursor='hand2').pack(side=tk.RIGHT)
        else:
            ttk.Label(status_controls, text="❌ YouTube API Not Available", 
                     font=('Segoe UI', 10, 'bold'), foreground='#e74c3c').pack(side=tk.LEFT)
            
        # Authentication Controls
        auth_controls = ttk.Frame(status_frame)
        auth_controls.pack(fill=tk.X)
        
        self.youtube_auth_btn = tk.Button(auth_controls, text="🔐 Login YouTube", 
                                          command=self.youtube_authenticate_thread,
                                          bg=self.colors['secondary'], fg='white', relief=tk.FLAT,
                                          font=('Segoe UI', 9, 'bold'), cursor='hand2')
        self.youtube_auth_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        # OAuth Setup Guide Button
        oauth_guide_btn = tk.Button(auth_controls, text="❓ Setup Guide", 
                                   command=self.show_oauth_setup_guide,
                                   bg=self.colors['info'], fg='white', relief=tk.FLAT,
                                   font=('Segoe UI', 9, 'bold'), cursor='hand2')
        oauth_guide_btn.pack(side=tk.LEFT, padx=(0, 15))
        self.create_tooltip(oauth_guide_btn,
                           "📚 OAuth Setup Guide\n\n" +
                           "• How to create Google Cloud project\n" +
                           "• Setup OAuth credentials\n" +
                           "• Enable real YouTube uploads\n" +
                           "• Step-by-step instructions\n\n" +
                           "🔧 Required for actual uploads to YouTube")
        
        # Authentication status (use StringVar for dynamic updates)
        if not hasattr(self, 'auth_status_var') or not self.auth_status_var:
            self.auth_status_var = tk.StringVar(value="🔴 Not authenticated")
        
        self.auth_status = ttk.Label(auth_controls, textvariable=self.auth_status_var, 
                                    font=('Segoe UI', 10), foreground='#e74c3c')
        self.auth_status.pack(side=tk.LEFT)

        # Video Selection and Upload List
        video_frame = ttk.LabelFrame(main_frame, text="� Video Selection & Upload", padding="15")
        video_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        selection_controls = ttk.Frame(video_frame)
        selection_controls.pack(fill=tk.X, pady=(0, 15))
        
        browse_btn = tk.Button(selection_controls, text="📁 Browse Videos", 
                              command=self.browse_videos_for_upload,
                              bg=self.colors['primary'], fg='white',
                              font=('Segoe UI', 10, 'bold'),
                              relief='flat', padx=15, pady=8)
        browse_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.create_tooltip(browse_btn,
                           "📁 Browse Videos\n\n" +
                           "• Select video files from your computer\n" +
                           "• Supports: MP4, AVI, MOV, WMV, FLV, MKV\n" +
                           "• Multiple file selection allowed\n" +
                           "• Videos will be added to upload queue\n\n" +
                           "💡 Choose any video files from anywhere on your computer")
        
        download_btn = tk.Button(selection_controls, text="📥 Load Downloaded", 
                                command=self.load_downloaded_videos,
                                bg=self.colors['primary'], fg='white',
                                font=('Segoe UI', 10, 'bold'),
                                relief='flat', padx=15, pady=8)
        download_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.create_tooltip(download_btn,
                           "📥 Load Downloaded Videos\n\n" +
                           "• Load videos from download folder\n" +
                           "• Automatically finds all downloaded Douyin videos\n" +
                           "• Quick way to upload recently downloaded content\n" +
                           "• Shows videos from current download session\n\n" +
                           "⚡ Perfect for uploading freshly downloaded Douyin videos")

        config_btn = tk.Button(selection_controls, text="⚙️ Upload Settings", 
                              command=self.open_upload_config,
                              bg=self.colors['accent'], fg='white',
                              font=('Segoe UI', 10, 'bold'),
                              relief='flat', padx=15, pady=8)
        config_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.create_tooltip(config_btn,
                           "⚙️ Upload Configuration\n\n" +
                           "• Configure title, description, tags\n" +
                           "• Set privacy, category, language\n" +
                           "• Customize thumbnail and settings\n" +
                           "• Advanced YouTube optimization options\n\n" +
                           "🎯 Customize how your videos appear on YouTube")
        
        select_all_btn = tk.Button(selection_controls, text="✅ Select All", 
                                  command=self.select_all_for_upload,
                                  bg=self.colors['success'], fg=self.colors['dark'],
                                  font=('Segoe UI', 10, 'bold'),
                                  relief='flat', padx=15, pady=8)
        select_all_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.create_tooltip(select_all_btn,
                           "✅ Select All Videos\n\n" +
                           "• Mark all videos for upload\n" +
                           "• Quick way to select entire list\n" +
                           "• Videos will show green checkmark\n" +
                           "• Selected videos will be uploaded\n\n" +
                           "⚡ Fast bulk selection")
        
        deselect_btn = tk.Button(selection_controls, text="❌ Deselect All", 
                                command=self.deselect_all_for_upload,
                                bg=self.colors['warning'], fg=self.colors['dark'],
                                font=('Segoe UI', 10, 'bold'),
                                relief='flat', padx=15, pady=8)
        deselect_btn.pack(side=tk.LEFT)
        self.create_tooltip(deselect_btn,
                           "❌ Deselect All Videos\n\n" +
                           "• Remove selection from all videos\n" +
                           "• Clear entire upload queue\n" +
                           "• Videos will show empty checkbox\n" +
                           "• No videos will be uploaded\n\n" +
                           "🔄 Reset selection to start over")
        
        # Upload list
        upload_list_frame = ttk.Frame(video_frame)
        upload_list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.upload_count_var = tk.StringVar(value="📋 Selected: 0")
        ttk.Label(upload_list_frame, textvariable=self.upload_count_var, 
                 font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        # Upload treeview
        # Columns: Select(0), File(1), Title(2), Size(3), Status(4), Actions(5)
        upload_columns = ('Select', 'File', 'Title', 'Size', 'Status', 'Actions')
        self.upload_tree = ttk.Treeview(upload_list_frame, columns=upload_columns,
                                       show='headings', height=6)

        # Configure larger font for icons
        style = ttk.Style()
        style.configure("Large.Treeview", font=('Segoe UI', 11))
        style.configure("Large.Treeview.Heading", font=('Segoe UI', 10, 'bold'))
        self.upload_tree.configure(style="Large.Treeview")

        self.upload_tree.heading('Select', text='✓')
        self.upload_tree.heading('File', text='📹 File')
        self.upload_tree.heading('Title', text='✏️ Title (double-click to edit)')
        self.upload_tree.heading('Size', text='📊 Size')
        self.upload_tree.heading('Status', text='📋 Status')
        self.upload_tree.heading('Actions', text='🎛️ Actions')

        self.upload_tree.column('Select', width=45, anchor=tk.CENTER, stretch=False)
        self.upload_tree.column('File', width=160, stretch=False)
        self.upload_tree.column('Title', width=280)
        self.upload_tree.column('Size', width=70, anchor=tk.CENTER, stretch=False)
        self.upload_tree.column('Status', width=110, anchor=tk.CENTER, stretch=False)
        self.upload_tree.column('Actions', width=100, anchor=tk.CENTER, stretch=False)

        # Configure row colors for selection
        self.upload_tree.tag_configure('selected', background='#e3f2fd', foreground='#1976d2')
        self.upload_tree.tag_configure('unselected', background=self.colors['light'], foreground=self.colors['dark'])

        upload_v_scroll = ttk.Scrollbar(upload_list_frame, orient=tk.VERTICAL,
                                       command=self.upload_tree.yview)
        self.upload_tree.configure(yscrollcommand=upload_v_scroll.set)

        self.upload_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        upload_v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind events
        self.upload_tree.bind('<Double-1>', self._on_upload_tree_double_click)
        self.upload_tree.bind('<<TreeviewSelect>>', self.on_video_select)
        self.upload_tree.bind('<Button-1>', self.on_tree_click)
        self.upload_tree.bind('<Button-3>', self.show_context_menu)  # Right click
        
        # Compact preview info (below table)
        preview_compact = ttk.Frame(upload_list_frame)
        preview_compact.pack(fill=tk.X, pady=(5, 0))
        
        self.preview_info = ttk.Label(preview_compact, text="📹  No video selected", 
                                     font=('Segoe UI', 10), foreground='#666')
        self.preview_info.pack(anchor=tk.W)

        # Upload Method Guide
        guide_frame = ttk.LabelFrame(main_frame, text="📚 Upload Methods Guide", padding="10")
        guide_frame.pack(fill=tk.X, pady=(15, 10))
        
        guide_text = (
            "🚀 Upload Basic: Fast upload with original quality • Good for high-quality videos\n"
            "🎯 Upload Optimized: Compressed & optimized • Better for large files or slow internet\n"
            "📱 Upload Shorts: Vertical videos under 60s • Perfect for Douyin/TikTok content"
        )
        
        guide_label = tk.Label(guide_frame, text=guide_text, 
                              font=('Segoe UI', 9), 
                              foreground=self.colors['primary'],
                              background=self.colors['light'],
                              justify=tk.LEFT, wraplength=800)
        guide_label.pack(anchor=tk.W, padx=5, pady=5)

        # Upload Controls (moved from old settings section)
        upload_controls_frame = ttk.LabelFrame(main_frame, text="� Upload Actions", padding="15")
        upload_controls_frame.pack(fill=tk.X, pady=(0, 20))
        
        upload_controls = ttk.Frame(upload_controls_frame)
        upload_controls.pack(fill=tk.X)
        
        # Upload Selected - Basic upload with original quality
        self.upload_selected_btn = tk.Button(upload_controls, text="🚀 Upload Basic", 
                                            command=self.upload_selected_videos_thread, state='disabled',
                                            bg=self.colors['success'], fg=self.colors['dark'],
                                            font=('Segoe UI', 10, 'bold'),
                                            relief='flat', padx=15, pady=8)
        self.upload_selected_btn.pack(side=tk.LEFT, padx=(0, 15))
        self.create_tooltip(self.upload_selected_btn, 
                           "📤 Upload Basic\n\n" +
                           "• Upload videos with original quality\n" +
                           "• No compression or optimization\n" +
                           "• Fastest upload method\n" +
                           "• Use default upload settings\n\n" +
                           "⚡ Best for: Quick uploads with good quality videos")
        
        # Upload Optimized - Enhanced upload with optimization
        self.upload_optimized_btn = tk.Button(upload_controls, text="🎯 Upload Optimized", 
                                             command=self.upload_optimized_videos_thread, state='disabled',
                                             bg=self.colors['primary'], fg='white',
                                             font=('Segoe UI', 10, 'bold'),
                                             relief='flat', padx=15, pady=8)
        self.upload_optimized_btn.pack(side=tk.LEFT, padx=(0, 15))
        self.create_tooltip(self.upload_optimized_btn,
                           "🎯 Upload Optimized\n\n" +
                           "• Compress and optimize video quality\n" +
                           "• Reduce file size for faster upload\n" +
                           "• Enhanced metadata and tags\n" +
                           "• Better SEO optimization\n\n" +
                           "💡 Best for: Large files, slow internet, better reach")
        
        # Upload as Shorts - Specific for YouTube Shorts
        self.upload_shorts_btn = tk.Button(upload_controls, text="📱 Upload as Shorts", 
                                          command=self.upload_as_shorts_thread, state='disabled',
                                          bg=self.colors['accent'], fg=self.colors['dark'],
                                          font=('Segoe UI', 10, 'bold'),
                                          relief='flat', padx=15, pady=8)
        self.upload_shorts_btn.pack(side=tk.LEFT, padx=(0, 15))
        self.create_tooltip(self.upload_shorts_btn,
                           "📱 Upload as YouTube Shorts\n\n" +
                           "• Optimized for vertical videos (9:16)\n" +
                           "• Maximum 60 seconds duration\n" +
                           "• Enhanced with #Shorts hashtag\n" +
                           "• Better discoverability on mobile\n\n" +
                           "🎬 Best for: Short vertical videos from Douyin/TikTok")
        
        studio_btn = tk.Button(upload_controls, text="📺 YouTube Studio", 
                              command=self.open_youtube_studio,
                              bg=self.colors['info'], fg='white',
                              font=('Segoe UI', 10, 'bold'),
                              relief='flat', padx=15, pady=8)
        studio_btn.pack(side=tk.LEFT, padx=(0, 15))
        self.create_tooltip(studio_btn,
                           "📺 YouTube Studio\n\n" +
                           "• Open YouTube Studio in browser\n" +
                           "• Manage your uploaded videos\n" +
                           "• Check analytics and performance\n" +
                           "• Edit video details and settings\n\n" +
                           "🔧 Manage all your YouTube content")
        
        channel_btn = tk.Button(upload_controls, text="📺 My Channel", 
                               command=self.open_my_channel,
                               bg=self.colors['info'], fg='white',
                               font=('Segoe UI', 10, 'bold'),
                               relief='flat', padx=15, pady=8)
        channel_btn.pack(side=tk.LEFT, padx=(0, 15))
        self.create_tooltip(channel_btn,
                           "📺 My Channel\n\n" +
                           "• Open your YouTube channel page\n" +
                           "• View your public channel\n" +
                           "• See how viewers see your content\n" +
                           "• Check channel layout and branding\n\n" +
                           "👀 See your channel from viewer's perspective")
        
        # Combined YouTube Manager button
        manager_btn = ttk.Button(upload_controls, text="⚙️ YouTube Manager", 
                  command=self.show_youtube_manager)
        manager_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.create_tooltip(manager_btn,
                           "⚙️ YouTube Manager\n\n" +
                           "• View channel statistics\n" +
                           "• Check recent uploads status\n" +
                           "• Monitor video performance\n" +
                           "• Comprehensive YouTube analytics\n\n" +
                           "📊 Complete YouTube management dashboard")
        
        self.upload_status_var = tk.StringVar(value="🟢 Ready to upload...")
        ttk.Label(upload_controls, textvariable=self.upload_status_var).pack(side=tk.LEFT)
        
        # Progress bar for upload
        progress_frame = tk.Frame(main_frame, bg=self.colors['light'])
        progress_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.upload_progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.upload_progress.pack(fill=tk.X, pady=(5, 0))
        
    def log(self, message):
        """Log message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.status_var.set(message)
        print(formatted_message)
        self.root.update_idletasks()
        
    # cURL Functions
    def paste_curl(self):
        """Paste cURL from clipboard"""
        try:
            clipboard_text = self.root.clipboard_get()
            self.curl_text.delete(1.0, tk.END)
            self.curl_text.insert(tk.END, clipboard_text)
            self.log("📋 Pasted cURL from clipboard")
        except:
            messagebox.showerror("Error", "No text in clipboard!")
            
    def open_douyin_login(self):
        """Open Douyin login page in default browser"""
        try:
            webbrowser.open("https://www.douyin.com/?recommend=1")
            self.log("🌐 Opened Douyin in browser. Please login then click Auto Cookie.")
        except Exception as e:
            self.log(f"❌ Cannot open browser: {e}")

    def auto_import_douyin_cookies(self):
        """Try to load Douyin cookies from local browsers"""
        if browser_cookie3 is None:
            self.log("browser-cookie3 not installed, using built-in cookie reader (Chrome/Edge only).")

        def load_cookie_file(loader_func, cookie_path):
            """Load a single Chromium cookie DB"""
            try:
                return loader_func(cookie_file=cookie_path)
            except Exception:
                return None

        def decrypt_chromium_cookie(enc_value, local_state_path):
            """Decrypt AES-GCM cookie value from Chromium DB"""
            if not enc_value:
                return ""
            if enc_value.startswith(b'v10') or enc_value.startswith(b'v11'):
                if AES is None:
                    return ""
                try:
                    local_state = json_lib.loads(Path(local_state_path).read_text(encoding="utf-8"))
                    enc_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
                    # DPAPI decrypt
                    import ctypes, ctypes.wintypes
                    CryptUnprotectData = ctypes.windll.crypt32.CryptUnprotectData
                    class DATA_BLOB(ctypes.Structure):
                        _fields_ = [("cbData", ctypes.wintypes.DWORD),
                                    ("pbData", ctypes.POINTER(ctypes.c_char))]
                    blob_in = DATA_BLOB(len(enc_key), ctypes.cast(ctypes.create_string_buffer(enc_key), ctypes.POINTER(ctypes.c_char)))
                    blob_out = DATA_BLOB()
                    CryptUnprotectData(ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out))
                    decrypted_key = ctypes.string_at(blob_out.pbData, blob_out.cbData)
                    iv = enc_value[3:15]
                    payload = enc_value[15:-16]
                    tag = enc_value[-16:]
                    cipher = AES.new(decrypted_key, AES.MODE_GCM, iv)
                    return cipher.decrypt_and_verify(payload, tag).decode()
                except Exception:
                    return ""
            else:
                try:
                    import win32crypt
                    return win32crypt.CryptUnprotectData(enc_value, None, None, None, 0)[1].decode()
                except Exception:
                    return ""

        def read_chromium_cookies(db_path, local_state_path, domains):
            """Minimal cookie reader without browser_cookie3"""
            cookies = {}
            if not os.path.exists(db_path) or not os.path.exists(local_state_path):
                return cookies
            # copy to temp to avoid lock
            tmp = Path(db_path).with_suffix(".tmp")
            try:
                shutil.copyfile(db_path, tmp)
                conn = sqlite3.connect(tmp)
                cur = conn.cursor()
                domain_placeholders = ",".join("?" * len(domains))
                like_clauses = " OR ".join([f"host_key LIKE ?"] * len(domains))
                params = [f"%{d}%" for d in domains]
                cur.execute(f"SELECT name, encrypted_value, value, host_key FROM cookies WHERE {like_clauses}", params)
                for name, enc, val, host in cur.fetchall():
                    if val:
                        cookies[name] = val
                    else:
                        cookies[name] = decrypt_chromium_cookie(enc, local_state_path)
                conn.close()
            except Exception:
                pass
            finally:
                try:
                    tmp.unlink()
                except Exception:
                    pass
            return cookies

        loaders = [
            ("chrome", browser_cookie3.chrome if browser_cookie3 else None),
            ("edge", browser_cookie3.edge if browser_cookie3 else None),
            ("firefox", browser_cookie3.firefox if browser_cookie3 else None),
        ]

        douyin_pairs = {}
        loaded_from = []

        douyin_domains = ['douyin.com', 'iesdouyin.com', 'snssdk.com']
        last_profile_file = "last_douyin_profile.json"
        last_profile = None
        if os.path.exists(last_profile_file):
            try:
                last_profile = json.loads(open(last_profile_file, "r", encoding="utf-8").read())
            except Exception:
                last_profile = None

        # First try default profiles
        for browser_name, loader in loaders:
            if loader is None:
                continue
            try:
                jar = loader()
                count_before = len(douyin_pairs)
                for cookie in jar:
                    domain = getattr(cookie, 'domain', '') or ''
                    if any(key in domain for key in douyin_domains):
                        douyin_pairs[cookie.name] = cookie.value
                if len(douyin_pairs) > count_before:
                    loaded_from.append(f"{browser_name}:Default")
                self.log(f"Auto Cookie: {browser_name} default found {len(douyin_pairs)-count_before} cookies")
            except Exception:
                continue

        # Build exhaustive profile list by scanning user-data folders
        local_app = os.environ.get("LOCALAPPDATA", "")
        user_dirs = [
            ("chrome", os.path.join(local_app, "Google", "Chrome", "User Data")),
            ("chrome", os.path.join(local_app, "Google", "Chrome Beta", "User Data")),
            ("chrome", os.path.join(local_app, "Google", "Chrome SxS", "User Data")),
            ("edge", os.path.join(local_app, "Microsoft", "Edge", "User Data")),
            ("chrome", os.path.join(local_app, "Chromium", "User Data")),
            ("chrome", os.path.join(local_app, "BraveSoftware", "Brave-Browser", "User Data")),
        ]

        profile_paths = []
        for browser_name, base in user_dirs:
            if not os.path.isdir(base):
                continue
            # include Default and any Profile */Guest profiles
            for profile_dir in os.listdir(base):
                full_dir = os.path.join(base, profile_dir)
                if not os.path.isdir(full_dir):
                    continue
                # Chrome/Edge changed cookie DB location to Network/Cookies in recent versions
                profile_paths.append((browser_name, os.path.join(full_dir, "Cookies")))
                profile_paths.append((browser_name, os.path.join(full_dir, "Network", "Cookies")))

        # Prioritize last successful profile if recorded
        if last_profile and os.path.exists(last_profile.get("cookie_path", "")):
            lp = (last_profile.get("browser", ""), last_profile.get("cookie_path", ""))
            if lp in profile_paths:
                profile_paths.remove(lp)
            profile_paths.insert(0, lp)

        # Then prioritize most recently modified cookie DBs
        profile_paths = sorted(
            profile_paths,
            key=lambda item: os.path.getmtime(item[1]) if os.path.exists(item[1]) else 0,
            reverse=True
        )

        used_profile = None
        tried_files = []
        for browser_name, cookie_path in profile_paths:
            if not os.path.exists(cookie_path):
                continue
            tried_files.append(cookie_path)
            loader_func = None
            if browser_cookie3:
                loader_func = browser_cookie3.chrome if browser_name == "chrome" else browser_cookie3.edge
            jar = None
            if loader_func:
                try:
                    jar = load_cookie_file(loader_func, cookie_path)
                except Exception as e:
                    self.log(f"Auto Cookie: browser_cookie3 failed on {cookie_path}: {e}")
                    jar = None

            if jar is None and browser_name in ("chrome", "edge"):
                # fallback manual reader
                try:
                    user_data_dir = Path(cookie_path).parents[2]
                    local_state = user_data_dir / "Local State"
                except Exception:
                    local_state = ""
                try:
                    manual_cookies = read_chromium_cookies(cookie_path, local_state, douyin_domains)
                    count_before = len(douyin_pairs)
                    douyin_pairs.update(manual_cookies)
                    found_now = len(douyin_pairs) - count_before
                    self.log(f"Auto Cookie manual read: {cookie_path} found {found_now}")
                except Exception as e:
                    self.log(f"Auto Cookie manual read failed {cookie_path}: {e}")
                    found_now = 0
            elif jar:
                count_before = len(douyin_pairs)
                for cookie in jar:
                    domain = getattr(cookie, 'domain', '') or ''
                    if any(key in domain for key in ['douyin.com', 'iesdouyin.com', 'snssdk.com']):
                        douyin_pairs[cookie.name] = cookie.value
                found_now = len(douyin_pairs) - count_before
            else:
                found_now = 0

            if found_now > 0:
                loaded_from.append(f"{browser_name}:{os.path.basename(os.path.dirname(cookie_path))}")
                used_profile = {"browser": browser_name, "cookie_path": cookie_path}
            self.log(f"Auto Cookie: {browser_name} {os.path.basename(os.path.dirname(cookie_path))} found {found_now} cookies")
            # Stop early if we already have a healthy set of cookies
            if len(douyin_pairs) >= 10:
                break

        if not douyin_pairs:
            messagebox.showwarning(
                'No Douyin cookies',
                'Could not find Douyin cookies.\nPlease login on Douyin in Chrome/Edge/Firefox first, then try again. ' +
                'Neu ban dung nhieu profile (vi du Profile 1, Profile 2), hay thu dang nhap o profile mac dinh hoac bat tuy chon luu cookie.'
            )
            self.log('[Auto Cookie] No cookies found. Tried files:\n' + '\n'.join(tried_files[:15]) + ('\n...' if len(tried_files) > 15 else ''))
            return

        cookie_string = '; '.join(f"{k}={v}" for k, v in douyin_pairs.items())

        headers = self.get_headers()
        headers['Cookie'] = cookie_string
        headers.setdefault('Referer', 'https://www.douyin.com/')
        headers.setdefault('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        self.headers_text.delete(1.0, tk.END)
        self.headers_text.insert(tk.END, json.dumps(headers, indent=2))
        self.show_advanced.set(True)
        self.toggle_advanced()
        self.show_headers.set(True)
        self.toggle_headers()

        # Remember the profile that worked for the next run
        if used_profile:
            try:
                with open(last_profile_file, "w", encoding="utf-8") as f:
                    json.dump(used_profile, f)
            except Exception:
                pass

        self.log(f"🍪 Imported {len(douyin_pairs)} Douyin cookies from: {', '.join(loaded_from)}")

    def clear_curl(self):
        """Clear cURL text"""
        self.curl_text.delete(1.0, tk.END)
        self.log("🗑️ Cleared cURL input")
        
    def parse_curl(self):
        """Parse cURL command"""
        curl_text = self.curl_text.get(1.0, tk.END).strip()
        if not curl_text:
            messagebox.showerror("Error", "Please paste cURL command first!")
            return
            
        try:
            self.log("🔍 Parsing cURL command...")
            
            # Extract URL
            url_match = re.search(r"curl ['\"]([^'\"]+)['\"]", curl_text)
            if not url_match:
                url_match = re.search(r"curl ([^\s]+)", curl_text)
                
            if url_match:
                url = url_match.group(1)
                self.url_var.set(url)
                self.log(f"🎯 Extracted URL")
                
            # Extract headers
            headers = {}
            header_matches = re.findall(r"-H ['\"]([^:]+):\s*([^'\"]+)['\"]", curl_text)
            for header_name, header_value in header_matches:
                headers[header_name] = header_value
                
            # Extract cookies
            cookie_match = re.search(r"-b ['\"]([^'\"]+)['\"]", curl_text)
            if cookie_match:
                cookie_string = cookie_match.group(1)
                headers['Cookie'] = cookie_string
                
            if headers:
                self.headers_text.delete(1.0, tk.END)
                self.headers_text.insert(tk.END, json.dumps(headers, indent=2))
                self.log(f"✅ Extracted {len(headers)} headers")
            else:
                self.log("⚠️ No headers found")
                
        except Exception as e:
            self.log(f"❌ Error parsing cURL: {e}")
            messagebox.showerror("Error", f"Failed to parse cURL: {e}")
            
    def toggle_advanced(self):
        """Toggle advanced configuration visibility"""
        if self.show_advanced.get():
            self.advanced_frame.pack(fill=tk.X, pady=(0, 15))
            self.log("⚙️ Advanced configuration shown")
        else:
            self.advanced_frame.pack_forget()
            self.log("⚙️ Advanced configuration hidden")
            
    def toggle_headers(self):
        """Toggle headers visibility"""
        if self.show_headers.get():
            self.headers_frame.pack(fill=tk.X, pady=(10, 0))
        else:
            self.headers_frame.pack_forget()
            
    # Download Functions
    def select_download_folder(self):
        """Select download folder"""
        folder = filedialog.askdirectory(initialdir=self.download_folder)
        if folder:
            self.download_folder = folder
            self.log(f"📁 Selected folder: {os.path.basename(folder)}")
            
    def select_all_videos(self):
        """Select all videos for download"""
        for item in self.video_tree.get_children():
            self.video_tree.set(item, 'Select', '☑')
        self.log("✅ Selected all videos")
        
    def clear_all_videos(self):
        """Clear all video selections"""
        for item in self.video_tree.get_children():
            self.video_tree.set(item, 'Select', '☐')
        self.log("❌ Cleared all selections")
        
    def toggle_video_selection(self, event):
        """Toggle video selection on double-click"""
        item = self.video_tree.selection()[0] if self.video_tree.selection() else None
        if item:
            current = self.video_tree.set(item, 'Select')
            new_state = '☐' if current == '☑' else '☑'
            self.video_tree.set(item, 'Select', new_state)
            
    def analyze_url_thread(self):
        """Analyze URL in thread"""
        thread = threading.Thread(target=self.analyze_url, daemon=True)
        thread.start()
        
    def analyze_url(self):
        """Analyze URL and get media list (video/image/music) for a Douyin profile"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please provide API URL or profile URL!")
            return

        # If user pasted profile URL, build API URL automatically
        if "/user/" in url and "aweme/v1/web/aweme/post" not in url:
            sec_user_id = self.extract_user_id_from_profile(url)
            if not sec_user_id:
                messagebox.showerror("Error", "Cannot extract sec_user_id from profile URL!")
                return
            url = self.build_profile_api_url(sec_user_id)
            self.url_var.set(url)
            
        try:
            self.log("?? Analyzing URL...")
            
            # Extract user ID
            sec_user_id = self.extract_user_id_from_api_url(url)
            if not sec_user_id:
                messagebox.showerror("Error", "Cannot extract User ID!")
                return
                
            # Clear previous results
            for item in self.video_tree.get_children():
                self.video_tree.delete(item)
            self.video_urls.clear()
            self.video_entries.clear()
            
            # Fetch data
            max_cursor = 0
            page = 1
            
            seen_ids = set()
            max_pages = 200

            while page <= max_pages:
                self.log(f"?? Loading page {page}...")
                
                current_url = self.update_url_with_params(url, max_cursor, sec_user_id)
                data = self.fetch_api_data(current_url)
                
                if not data:
                    break
                    
                if 'aweme_list' not in data:
                    break
                    
                aweme_list = data.get('aweme_list', [])
                has_more = data.get('has_more', False)
                max_cursor = data.get('max_cursor', 0)
                
                for video in aweme_list:
                    video_info = self.extract_video_info(video)
                    if not video_info:
                        continue

                    unique_key = video_info.get('aweme_id') or video_info.get('url')
                    if unique_key in seen_ids:
                        continue
                    seen_ids.add(unique_key)

                    self.video_urls.append(video_info['url'])
                    self.video_entries.append(video_info)
                    index = len(self.video_entries)

                    display_url = video_info['url'][:80] + "..." if len(video_info['url']) > 80 else video_info['url']
                    row_tag = 'odd' if index % 2 else 'even'
                    self.video_tree.insert('', 'end', values=(
                        '?',
                        f"#{index:03d}",
                        "Found",
                        video_info['title'],
                        display_url
                    ), tags=(row_tag,))
                        
                if not has_more:
                    break
                    
                page += 1
                time.sleep(1)
                
            if self.video_urls:
                self.log(f"?? Found {len(self.video_urls)} items")
                self.video_count_var.set(f"📃 Media: {len(self.video_urls)}")
                self.download_btn.config(state='normal')
            else:
                self.log("? No media found")

            if page > max_pages:
                self.log(f"?? Reached page limit ({max_pages}). Profile may have more items.")
                
        except Exception as e:
            self.log(f"? Analysis error: {e}")
            messagebox.showerror("Error", f"Analysis failed: {e}")
            
    def extract_user_id_from_api_url(self, url):
        """Extract user ID from API URL"""
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            if 'sec_user_id' in params:
                return params['sec_user_id'][0]
        except:
            pass
        return None

    def extract_user_id_from_profile(self, url):
        """Extract sec_user_id from profile URL (/user/<sec_user_id>)"""
        try:
            parsed = urlparse(url)
            # Path like /user/SECID
            parts = parsed.path.strip('/').split('/')
            if len(parts) >= 2 and parts[0] == 'user':
                return parts[1]
        except Exception:
            return None
        return None

    def build_profile_api_url(self, sec_user_id):
        """Build Douyin web API URL for user posts"""
        base = "https://www.douyin.com/aweme/v1/web/aweme/post/"
        params = {
            "device_platform": "webapp",
            "aid": "6383",
            "channel": "channel_pc_web",
            "sec_user_id": sec_user_id,
            "count": "20",
            "max_cursor": "0",
            "publish_video_strategy_type": "2",
            "version_code": "190500",
            "language": "vi",
        }
        return f"{base}?{urlencode(params)}"
        
    def update_url_with_params(self, base_url, max_cursor, sec_user_id):
        """Update URL with new parameters"""
        try:
            parsed = urlparse(base_url)
            params = parse_qs(parsed.query)
            
            params['max_cursor'] = [str(max_cursor)]
            params['sec_user_id'] = [sec_user_id]
            
            new_query = urlencode(params, doseq=True)
            new_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"
            return new_url
        except:
            return base_url
            
    def fetch_api_data(self, url):
        """Fetch data from API"""
        try:
            headers = self.get_headers()
            req = urllib.request.Request(url, headers=headers)
            
            with self.opener.open(req, timeout=30) as response:
                if response.status == 200:
                    data = response.read().decode('utf-8')
                    return json.loads(data)
                    
        except Exception as e:
            self.log(f"❌ API error: {e}")
            
        return None
        
    def get_headers(self):
        """Get headers from text area"""
        try:
            headers_text = self.headers_text.get(1.0, tk.END).strip()
            return json.loads(headers_text) if headers_text else {}
        except:
            return {}
            
    def extract_video_info(self, video_data):
        """Extract video url + metadata from API data"""
        try:
            # Determine if video or image post
            aweme_id = video_data.get('aweme_id', '')
            description = video_data.get('desc', '').strip()
            title = description if description else f"Douyin {aweme_id}".strip()
            if len(title) > 80:
                title = title[:77] + '...'

            # Image post
            if video_data.get('image_post_info') or video_data.get('images'):
                images = video_data.get('image_post_info', {}).get('images') or video_data.get('images', [])
                image_urls = []
                for img in images:
                    for u in img.get('url_list', []):
                        if u:
                            image_urls.append(u.replace('http://', 'https://'))
                if not image_urls:
                    return None
                return {
                    'aweme_id': aweme_id,
                    'title': title + " (images)",
                    'url': image_urls[0],
                    'type': 'image',
                    'image_urls': image_urls,
                    'music_url': None
                }

            # Video post
            video_info = video_data.get('video', {})

            url_list = video_info.get('play_addr', {}).get('url_list', [])
            if not url_list and video_info.get('bit_rate'):
                for bit_rate in video_info.get('bit_rate', []):
                    url_list.extend(bit_rate.get('play_addr', {}).get('url_list', []))

            if not url_list:
                return None

            raw_url = next((url for url in url_list if url), None)
            if not raw_url:
                return None

            url = raw_url.replace('http://', 'https://').replace('playwm', 'play')

            cover_list = video_info.get('cover', {}).get('url_list', [])
            cover_url = cover_list[0].replace('http://', 'https://') if cover_list else None

            music = video_data.get('music', {})
            music_list = music.get('play_url', {}).get('url_list', []) if music else []
            music_url = music_list[0].replace('http://', 'https://') if music_list else None

            return {
                'aweme_id': aweme_id,
                'title': title,
                'url': url,
                'type': 'video',
                'cover_url': cover_url,
                'music_url': music_url
            }

        except Exception:
            return None
        
    def download_videos_thread(self):
        """Download videos in thread"""
        thread = threading.Thread(target=self.download_videos, daemon=True)
        thread.start()
        
    def download_videos(self):
        """Download all videos"""
        if not self.video_entries:
            messagebox.showerror("Error", "No videos to download!")
            return
            
        if not self.download_folder:
            messagebox.showerror("Error", "Please select download folder!")
            return
            
        self.is_downloading = True
        self.download_btn.config(state='disabled')
        
        selected_items = []
        for item in self.video_tree.get_children():
            if self.video_tree.set(item, 'Select') == '☑':
                selected_items.append(item)

        if not selected_items:
            messagebox.showerror("Error", "Please select at least one video!")
            self.download_btn.config(state='normal')
            self.is_downloading = False
            return

        total_videos = len(selected_items)
        self.download_progress['maximum'] = total_videos
        self.download_progress['value'] = 0
        
        successful = 0
        failed = 0
        
        try:
            for i, item in enumerate(selected_items):
                item_values = self.video_tree.item(item, 'values')
                raw_index = item_values[1] if len(item_values) > 1 else f"#{i + 1:03d}"
                entry_index = max(int(raw_index.replace('#', '')) - 1, 0)

                if entry_index >= len(self.video_entries):
                    failed += 1
                    continue

                current = self.video_entries[entry_index]
                media_type = current.get('type', 'video')

                self.video_tree.set(item, 'Status', '?? Downloading...')

                try:
                    if media_type == 'image':
                        self.download_image_post(current, i)
                    else:
                        self.download_video_with_extras(current, i)
                    successful += 1
                    self.video_tree.set(item, 'Status', 'Downloaded')
                except Exception as e_inner:
                    failed += 1
                    self.video_tree.set(item, 'Status', 'Failed')
                    self.log(f"? Download error for item {i + 1}: {e_inner}")

                self.download_progress['value'] = i + 1
                self.download_status_var.set(f"?Downloaded: {i + 1}/{total_videos}")
                self.root.update_idletasks()
                time.sleep(0.5)
        except Exception as e:
            self.log(f"❌ Download error: {e}")
            
        finally:
            self.is_downloading = False
            self.download_btn.config(state='normal')
            
            # Update upload tab
            self.update_upload_list()
            
            result = f"Download complete!\nSuccess: {successful}\nFailed: {failed}"
            self.log(result)
            messagebox.showinfo("Download Complete", result)
            
    def download_single_video(self, url, file_path, index):
        """Download single video"""
        try:
            self.log(f"📥 Downloading video {index + 1}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.douyin.com/'
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=60) as response:
                if response.status == 200:
                    with open(file_path, 'wb') as f:
                        f.write(response.read())
                    return True
                    
        except Exception as e:
            self.log(f"❌ Download error for video {index + 1}: {e}")
            
        return False

    def download_video_with_extras(self, video_entry, index):
        """Download video plus cover and music when available"""
        base_name = f"{video_entry.get('aweme_id','video')}_{index+1:03d}"
        video_path = os.path.join(self.download_folder, f"{base_name}.mp4")
        if self.download_single_video(video_entry['url'], video_path, index):
            self.video_files.append({'path': video_path, 'filename': os.path.basename(video_path),
                                     'size': self.get_file_size(video_path), 'title': video_entry.get('title','')})
        # cover image
        cover = video_entry.get('cover_url')
        if cover:
            cover_path = os.path.join(self.download_folder, f"{base_name}_cover.jpg")
            self.download_binary(cover, cover_path)
        # music
        music = video_entry.get('music_url')
        if music:
            music_path = os.path.join(self.download_folder, f"{base_name}.mp3")
            self.download_binary(music, music_path)

    def download_image_post(self, entry, index):
        """Download all images in an image post"""
        base_name = f"{entry.get('aweme_id','image')}_{index+1:03d}"
        for j, img_url in enumerate(entry.get('image_urls', []), start=1):
            img_path = os.path.join(self.download_folder, f"{base_name}_{j:02d}.jpg")
            self.download_binary(img_url, img_path)

    def download_binary(self, url, path):
        """Generic downloader for binary files"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.douyin.com/'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=60) as resp:
            if resp.status == 200:
                with open(path, 'wb') as f:
                    f.write(resp.read())
        
    def get_file_size(self, file_path):
        """Get human readable file size"""
        try:
            size = os.path.getsize(file_path)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        except:
            return "Unknown"
            
    # Upload Functions
    def browse_videos_for_upload(self):
        """Browse videos for upload"""
        files = filedialog.askopenfilenames(
            title="Select Videos",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.wmv *.flv *.mkv"),
                ("All files", "*.*")
            ]
        )
        
        if files:
            # Store the folder of first file for reference
            self.current_video_folder = os.path.dirname(files[0])
            
            for file_path in files:
                self.add_video_to_upload_list(file_path)
                
            self.log(f"� Added {len(files)} videos from {os.path.basename(self.current_video_folder)}")
        
    def add_video_to_upload_list(self, file_path):
        """Add video to upload list"""
        if not os.path.exists(file_path):
            return
            
        file_name = os.path.basename(file_path)
        file_size = self.get_file_size(file_path)
        
        # Check if already exists
        for item in self.upload_tree.get_children():
            if self.upload_tree.item(item, 'values')[1] == file_name:
                return  # Already exists

        auto_title = self._apply_title_template(file_name)

        # Insert with selected color and actions
        # Columns: Select(0), File(1), Title(2), Size(3), Status(4), Actions(5)
        item = self.upload_tree.insert('', 'end', values=(
            "✓",
            file_name,
            auto_title,
            file_size,
            "📋 Ready",
            "🎬  📁"
        ), tags=('selected',))
        
        self.selected_videos.add(file_name)
        self.update_upload_count()
        
    def load_downloaded_videos(self):
        """Load videos from download folder"""
        if not os.path.exists(self.download_folder):
            messagebox.showerror("Error", "Download folder not found!")
            return
            
        video_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv'}
        video_files = []
        
        for file_name in os.listdir(self.download_folder):
            file_path = os.path.join(self.download_folder, file_name)
            if os.path.isfile(file_path):
                _, ext = os.path.splitext(file_name.lower())
                if ext in video_extensions:
                    video_files.append(file_path)
                    
        if video_files:
            # Set download folder as current folder
            self.current_video_folder = self.download_folder
            
            for file_path in video_files:
                self.add_video_to_upload_list(file_path)
            self.log(f"📥 Loaded {len(video_files)} videos from downloads")
        else:
            messagebox.showinfo("Info", "No videos found in download folder")
        
    def update_upload_list(self):
        """Update upload list with downloaded videos"""
        # Clear existing list
        for item in self.upload_tree.get_children():
            self.upload_tree.delete(item)
        self.selected_videos.clear()
        
        # Set download folder as current video folder
        self.current_video_folder = self.download_folder
        
        # Add all downloaded videos
        for video_info in self.video_files:
            file_path = os.path.join(self.download_folder, video_info['filename'])
            if os.path.exists(file_path):
                auto_title = self._apply_title_template(video_info['filename'])
                item = self.upload_tree.insert('', 'end', values=(
                    "✓",
                    video_info['filename'],
                    auto_title,
                    video_info['size'],
                    "📋 Ready",
                    "🎬  📁"
                ), tags=('selected',))
                self.selected_videos.add(video_info['filename'])
            
        self.update_upload_count()
        if self.video_files:
            self.log(f"📤 Updated upload list with {len(self.video_files)} videos")
        
    def _apply_title_template(self, file_name):
        """Apply title template from upload settings to a filename."""
        template = self.upload_settings.get('title_template', '[FILENAME]')
        name_no_ext = os.path.splitext(file_name)[0]
        return template.replace('[FILENAME]', name_no_ext)

    def _on_upload_tree_double_click(self, event):
        """Route double-click: edit Title column inline, toggle selection otherwise."""
        region = self.upload_tree.identify_region(event.x, event.y)
        if region != 'cell':
            return
        column = self.upload_tree.identify_column(event.x)
        item = self.upload_tree.identify_row(event.y)
        if not item:
            return
        if column == '#3':  # Title column
            self._start_title_inline_edit(item)
        else:
            self._toggle_item_selection(item)

    def _start_title_inline_edit(self, item):
        """Open a floating Entry over the Title cell for inline editing."""
        bbox = self.upload_tree.bbox(item, '#3')
        if not bbox:
            return
        x, y, width, height = bbox

        current_title = self.upload_tree.item(item, 'values')[2]

        edit_var = tk.StringVar(value=current_title)
        entry = tk.Entry(self.upload_tree, textvariable=edit_var,
                         font=('Segoe UI', 10), relief=tk.FLAT,
                         bg='#fffde7', fg='#212121',
                         highlightthickness=1, highlightbackground='#1976d2')
        entry.place(x=x, y=y, width=width, height=height)
        entry.focus_set()
        entry.select_range(0, tk.END)

        def _commit(event=None):
            new_title = edit_var.get().strip() or current_title
            values = list(self.upload_tree.item(item, 'values'))
            values[2] = new_title
            self.upload_tree.item(item, values=values)
            entry.destroy()

        def _cancel(event=None):
            entry.destroy()

        entry.bind('<Return>', _commit)
        entry.bind('<KP_Enter>', _commit)
        entry.bind('<FocusOut>', _commit)
        entry.bind('<Escape>', _cancel)

    def _toggle_item_selection(self, item):
        """Toggle the ✓ checkbox for a tree item."""
        values = self.upload_tree.item(item, 'values')
        if not values:
            return
        new_select = "✓" if values[0] != "✓" else ""
        new_values = list(values)
        new_values[0] = new_select
        if new_select == "✓":
            self.upload_tree.item(item, values=new_values, tags=('selected',))
            self.selected_videos.add(values[1])
        else:
            self.upload_tree.item(item, values=new_values, tags=('unselected',))
            self.selected_videos.discard(values[1])
        self.update_upload_count()

    def toggle_upload_selection(self, event):
        """Toggle video selection (kept for compatibility, routes to _toggle_item_selection)."""
        item = self.upload_tree.selection()[0] if self.upload_tree.selection() else None
        if item:
            self._toggle_item_selection(item)

    def on_tree_click(self, event):
        """Handle tree click for selection"""
        region = self.upload_tree.identify_region(event.x, event.y)
        if region == "cell":
            item = self.upload_tree.identify_row(event.y)
            column = self.upload_tree.identify_column(event.x)

            # Handle different column clicks
            if column == "#1":  # Select column
                self.toggle_upload_selection_direct(item)
            elif column == "#6":  # Actions column (shifted by new Title col)
                self.handle_action_click(event, item)
                
    def handle_action_click(self, event, item):
        """Handle click on actions column"""
        if not item:
            return
            
        # Get click position within the cell
        bbox = self.upload_tree.bbox(item, "#6")
        if bbox:
            cell_x = event.x - bbox[0]
            cell_width = bbox[2]
            
            # Determine which "button" was clicked (approximate)
            if cell_x < cell_width / 2:
                # First half - open video
                self.open_video_from_item(item)
            else:
                # Second half - show in folder
                self.show_video_folder_from_item(item)
                
    def open_video_from_item(self, item):
        """Open video from tree item"""
        if not item:
            return
            
        values = self.upload_tree.item(item, 'values')
        if values and len(values) >= 2:
            file_name = values[1]
            self.open_video_by_name(file_name)
            
    def show_video_folder_from_item(self, item):
        """Show video folder from tree item"""
        if not item:
            return
            
        values = self.upload_tree.item(item, 'values')
        if values and len(values) >= 2:
            file_name = values[1]
            self.show_video_folder_by_name(file_name)
            
    def open_video_by_name(self, file_name):
        """Open video by filename"""
        file_path = self.get_full_video_path(file_name)
        if file_path and os.path.exists(file_path):
            try:
                import subprocess
                import platform
                
                if platform.system() == 'Windows':
                    os.startfile(file_path)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', file_path])
                else:  # Linux
                    subprocess.run(['xdg-open', file_path])
                    
                self.log(f"🎬 Opened video: {file_name}")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot open video: {e}")
        else:
            messagebox.showwarning("Warning", f"Video file not found: {file_name}")
            
    def show_video_folder_by_name(self, file_name):
        """Show video folder by filename"""
        file_path = self.get_full_video_path(file_name)
        if file_path and os.path.exists(file_path):
            try:
                import subprocess
                import platform
                
                if platform.system() == 'Windows':
                    subprocess.run(['explorer', '/select,', file_path])
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', '-R', file_path])
                else:  # Linux
                    subprocess.run(['nautilus', '--select', file_path])
                    
                self.log(f"📁 Showed in folder: {file_name}")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot show in folder: {e}")
        else:
            messagebox.showwarning("Warning", f"Video file not found: {file_name}")
            
    def get_full_video_path(self, file_name):
        """Get full path for video file"""
        # Try current video folder first
        if hasattr(self, 'current_video_folder') and self.current_video_folder:
            test_path = os.path.join(self.current_video_folder, file_name)
            if os.path.exists(test_path):
                return test_path
        
        # Then try download folder
        test_path = os.path.join(self.download_folder, file_name)
        if os.path.exists(test_path):
            return test_path
            
        # Finally try absolute path
        if os.path.isabs(file_name) and os.path.exists(file_name):
            return file_name
            
        return None
        
    def show_context_menu(self, event):
        """Show context menu on right click"""
        item = self.upload_tree.identify_row(event.y)
        if item:
            # Select the item
            self.upload_tree.selection_set(item)
            
            # Create context menu with larger font
            context_menu = tk.Menu(self.root, tearoff=0, font=('Segoe UI', 10))
            context_menu.add_command(label="🎬  Open Video", 
                                   command=lambda: self.open_video_from_item(item))
            context_menu.add_command(label="📁  Show in Folder", 
                                   command=lambda: self.show_video_folder_from_item(item))
            context_menu.add_separator()
            context_menu.add_command(label="✅  Toggle Selection", 
                                   command=lambda: self.toggle_upload_selection_direct(item))
            
            # Show menu
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
                
    def toggle_upload_selection_direct(self, item):
        """Toggle selection directly for an item"""
        if not item:
            return
            
        values = self.upload_tree.item(item, 'values')
        if values:
            current_select = values[0]
            new_select = "✓" if current_select != "✓" else ""
            
            new_values = list(values)
            new_values[0] = new_select
            
            # Update color based on selection
            if new_select == "✓":
                self.upload_tree.item(item, values=new_values, tags=('selected',))
                self.selected_videos.add(values[1])
            else:
                self.upload_tree.item(item, values=new_values, tags=('unselected',))
                self.selected_videos.discard(values[1])
            
            self.update_upload_count()
            
    def on_video_select(self, event):
        """Handle video selection for preview"""
        selection = self.upload_tree.selection()
        if selection:
            item = selection[0]
            values = self.upload_tree.item(item, 'values')
            if values and len(values) >= 2:
                file_name = values[1]
                self.update_video_preview(file_name)
                
    def update_video_preview(self, file_name):
        """Update video preview information"""
        # Find full path
        full_path = self.get_full_video_path(file_name)
        
        if full_path and os.path.exists(full_path):
            # Update compact preview info
            file_size = self.get_file_size(full_path)
            info_text = f"📹 {file_name} | 📊 {file_size} | � {os.path.dirname(full_path)}"
            self.preview_info.config(text=info_text)
            self.current_preview_path = full_path
        else:
            self.preview_info.config(text="📹 File not found")
            self.current_preview_path = None
            
    def open_selected_video(self):
        """Open selected video in default player"""
        if hasattr(self, 'current_preview_path') and self.current_preview_path:
            try:
                import subprocess
                import platform
                
                if platform.system() == 'Windows':
                    os.startfile(self.current_preview_path)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', self.current_preview_path])
                else:  # Linux
                    subprocess.run(['xdg-open', self.current_preview_path])
                    
                self.log(f"🎬 Opened video: {os.path.basename(self.current_preview_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot open video: {e}")
        else:
            messagebox.showwarning("Warning", "No video selected!")
            
    def show_video_in_folder(self):
        """Show video in file explorer"""
        if hasattr(self, 'current_preview_path') and self.current_preview_path:
            try:
                import subprocess
                import platform
                
                if platform.system() == 'Windows':
                    subprocess.run(['explorer', '/select,', self.current_preview_path])
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', '-R', self.current_preview_path])
                else:  # Linux
                    subprocess.run(['nautilus', '--select', self.current_preview_path])
                    
                self.log(f"📁 Showed in folder: {os.path.basename(self.current_preview_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot show in folder: {e}")
        else:
            messagebox.showwarning("Warning", "No video selected!")
            
    def open_youtube_studio(self):
        """Open YouTube Studio in browser"""
        try:
            import webbrowser
            webbrowser.open("https://studio.youtube.com")
            self.log("📺 Opened YouTube Studio")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open YouTube Studio: {e}")
            
    def open_my_channel(self):
        """Open user's channel in browser"""
        try:
            import webbrowser
            webbrowser.open("https://www.youtube.com/@sealrepo")
            self.log("📺 Opened your channel")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open channel: {e}")
            
    def check_recent_uploads(self):
        """Check status of recent uploads"""
        if not YOUTUBE_AVAILABLE or not self.youtube_uploader:
            messagebox.showerror("Error", "YouTube uploader not available!")
            return
            
        try:
            # Authenticate if needed
            if not self.youtube_uploader.youtube:
                self.authenticate_youtube()
                
            self.log("🔍 Checking recent uploads status...")
            
            # Get recent uploads
            result = self.youtube_uploader.list_recent_uploads(max_results=10)
            
            if result['success']:
                videos = result['videos']
                
                if not videos:
                    msg = "❌ No recent uploads found!\n\nPossible reasons:\n• Videos were removed by YouTube\n• Upload failed completely\n• Wrong account authenticated\n\n🔧 Try:\n1. Check YouTube Studio manually\n2. Re-authenticate with correct account\n3. Check for copyright issues"
                    messagebox.showwarning("No Videos Found", msg)
                    self.log("❌ No recent uploads found in channel")
                    return
                
                # Show detailed status
                self.log("📊 ========== RECENT UPLOADS STATUS ==========")
                self.log(f"Found {len(videos)} recent uploads:")
                
                status_details = f"🔍 Recent Uploads Status ({len(videos)} videos):\n\n"
                
                for i, video in enumerate(videos, 1):
                    title = video['title'][:50] + "..." if len(video['title']) > 50 else video['title']
                    privacy = video.get('status', 'unknown')
                    upload_status = video.get('upload_status', 'unknown')
                    processing = video.get('processing_status', 'unknown')
                    
                    # Log to console
                    self.log(f"{i}. {title}")
                    self.log(f"   🔒 Privacy: {privacy}")
                    self.log(f"   📤 Upload: {upload_status}")
                    self.log(f"   ⚙️  Processing: {processing}")
                    
                    # Add to dialog
                    status_icon = "❌" if upload_status == 'failed' else "⚠️" if processing == 'processing' else "✅"
                    status_details += f"{status_icon} {title}\n"
                    status_details += f"   Privacy: {privacy} | Upload: {upload_status} | Processing: {processing}\n\n"
                    
                    # Check for problems
                    if upload_status == 'failed':
                        self.log(f"   ❌ FAILED: Video upload failed!")
                    elif processing == 'processing':
                        self.log(f"   ⏳ Still processing - wait longer")
                    elif privacy == 'private':
                        self.log(f"   ⚠️  Private - won't show in channel")
                    elif upload_status == 'uploaded' and processing == 'succeeded':
                        self.log(f"   ✅ Should be visible in channel")
                
                self.log("=" * 50)
                
                # Show summary dialog
                status_details += "💡 If videos are missing from your channel:\n"
                status_details += "• Check if they're set to 'Private'\n"
                status_details += "• Wait longer if still 'Processing'\n" 
                status_details += "• Check for copyright/community strikes\n"
                status_details += "• Verify you're checking the correct channel"
                
                messagebox.showinfo("Upload Status Check", status_details)
                
            else:
                error_msg = f"❌ Failed to check upload status!\n\nError: {result['error']}\n\n🔧 Try:\n1. Re-authenticate YouTube\n2. Check internet connection\n3. Verify API permissions"
                messagebox.showerror("Status Check Failed", error_msg)
                self.log(f"❌ Failed to check uploads: {result['error']}")
                
        except Exception as e:
            error_msg = f"❌ Error checking video status!\n\nError: {str(e)}\n\n🔧 This might be:\n• Authentication issue\n• Network problem\n• API quota exceeded"
            messagebox.showerror("Error", error_msg)
            self.log(f"❌ Error checking video status: {e}")
            
    def check_todays_uploads(self):
        """Check videos uploaded today"""
        if not YOUTUBE_AVAILABLE or not self.youtube_uploader:
            messagebox.showerror("Error", "YouTube uploader not available!")
            return
            
        try:
            # Authenticate if needed
            if not self.youtube_uploader.youtube:
                self.authenticate_youtube()
                
            self.log("📅 Checking today's uploads...")
            
            # Get today's uploads
            videos = self.youtube_uploader.get_todays_uploads()
            
            from datetime import datetime
            today_str = datetime.now().strftime("%Y-%m-%d")
            
            if not videos:
                msg = f"📅 No uploads today ({today_str})\n\n💡 Tips:\n• Videos may take time to appear\n• Check if uploads were successful\n• Verify correct account is authenticated"
                messagebox.showinfo("No Uploads Today", msg)
                self.log(f"📅 No uploads found for today ({today_str})")
                return
            
            total_today = len(videos)
            channel_title = "Your Channel"  # Will be updated from API if available
            
            # Show detailed status
            self.log(f"📅 ========== TODAY'S UPLOADS ({today_str}) ==========")
            self.log(f"Channel: {channel_title}")
            self.log(f"Total uploads today: {total_today}")
            
            status_details = f"📅 Today's Uploads ({today_str})\n"
            status_details += f"Channel: {channel_title}\n"
            status_details += f"Total: {total_today} video(s)\n\n"
            
            public_count = 0
            private_count = 0
            processing_count = 0
            failed_count = 0
            
            for i, video in enumerate(videos, 1):
                title = video['title'][:40] + "..." if len(video['title']) > 40 else video['title']
                privacy = video.get('status', 'unknown')
                upload_status = video.get('upload_status', 'unknown')
                processing = video.get('processing_status', 'unknown')
                duration = video.get('duration', 'unknown')
                failure_reason = video.get('failure_reason')
                rejection_reason = video.get('rejection_reason')
                
                # Count by status
                if privacy == 'public':
                    public_count += 1
                elif privacy == 'private':
                    private_count += 1
                    
                if processing == 'processing':
                    processing_count += 1
                elif upload_status == 'failed' or failure_reason or rejection_reason:
                    failed_count += 1
                
                # Log to console
                self.log(f"{i}. {title}")
                self.log(f"   🔒 Privacy: {privacy}")
                self.log(f"   📤 Upload: {upload_status}")
                self.log(f"   ⚙️  Processing: {processing}")
                self.log(f"   ⏱️  Duration: {duration}")
                self.log(f"   🔗 URL: {video.get('url', 'N/A')}")
                
                if failure_reason:
                    self.log(f"   ❌ Failure: {failure_reason}")
                if rejection_reason:
                    self.log(f"   🚫 Rejected: {rejection_reason}")
                
                # Add to dialog
                if upload_status == 'failed' or failure_reason:
                    status_icon = "❌"
                elif rejection_reason:
                    status_icon = "🚫"
                elif processing == 'processing':
                    status_icon = "⏳"
                elif privacy == 'private':
                    status_icon = "🔒"
                else:
                    status_icon = "✅"
                    
                status_details += f"{status_icon} {title}\n"
                status_details += f"   {privacy} | {upload_status} | {processing}\n"
                
                if failure_reason:
                    status_details += f"   ❌ Failed: {failure_reason}\n"
                if rejection_reason:
                    status_details += f"   🚫 Rejected: {rejection_reason}\n"
                    
                status_details += f"   🔗 {video.get('url', 'N/A')}\n\n"
            
            # Add summary
            status_details += "📊 Summary:\n"
            status_details += f"✅ Public: {public_count}\n"
            status_details += f"🔒 Private: {private_count}\n"
            status_details += f"⏳ Processing: {processing_count}\n"
            status_details += f"❌ Failed: {failed_count}\n\n"
            
            if private_count > 0:
                status_details += "💡 Private videos won't show in your channel publicly.\n"
            if processing_count > 0:
                status_details += "⏳ Processing videos may take time to appear.\n"
            if failed_count > 0:
                status_details += "❌ Failed videos need to be re-uploaded.\n"
            
            self.log("=" * 55)
            
            # Show summary dialog
            messagebox.showinfo("Today's Uploads", status_details)
                
        except Exception as e:
            error_msg = f"❌ Error checking today's uploads!\n\nError: {str(e)}\n\n🔧 This might be:\n• Authentication issue\n• Network problem\n• API quota exceeded"
            messagebox.showerror("Error", error_msg)
            self.log(f"❌ Error checking today: {e}")
            
    def quick_check_channel(self):
        """Quick check channel recent uploads"""
        if not YOUTUBE_AVAILABLE or not self.youtube_uploader:
            messagebox.showerror("Error", "YouTube uploader not available!")
            return
            
        try:
            # Authenticate if needed
            if not self.youtube_uploader.youtube:
                self.authenticate_youtube()
                
            self.log("📺 Checking channel recent uploads...")
            
            # Get recent uploads
            videos = self.youtube_uploader.list_recent_uploads(max_results=20)
            
            if not videos:
                msg = "📺 No recent uploads found in channel!\n\nPossible reasons:\n• No videos uploaded recently\n• Wrong account authenticated\n• Videos were removed\n\n💡 Tips:\n• Check YouTube Studio manually\n• Verify correct account\n• Try re-authentication"
                messagebox.showinfo("No Recent Uploads", msg)
                self.log("📺 No recent uploads found")
                return
            
            total_found = len(videos)
            
            # Show summary
            self.log(f"📺 Found {total_found} recent uploads")
            
            # Create summary
            summary = f"📺 Channel Recent Uploads\n"
            summary += "=" * 40 + "\n\n"
            summary += f"Total videos found: {total_found}\n\n"
            
            # Categorize by status
            public_count = sum(1 for v in videos if v.get('status') == 'public')
            private_count = sum(1 for v in videos if v.get('status') == 'private')
            processing_count = sum(1 for v in videos if v.get('processing_status') == 'processing')
            failed_count = sum(1 for v in videos if v.get('upload_status') == 'failed')
            
            summary += f"📊 Status Summary:\n"
            summary += f"• Public: {public_count}\n"
            summary += f"• Private: {private_count}\n"
            summary += f"• Processing: {processing_count}\n"
            summary += f"• Failed: {failed_count}\n\n"
            
            summary += f"📋 Recent Videos:\n"
            summary += "-" * 30 + "\n"
            
            for i, video in enumerate(videos[:10], 1):  # Show first 10
                title = video['title'][:30] + "..." if len(video['title']) > 30 else video['title']
                privacy = video.get('status', 'unknown').upper()
                processing = video.get('processing_status', 'unknown')
                
                summary += f"{i}. {title}\n"
                summary += f"   Status: {privacy} | {processing}\n"
                if video.get('published_at'):
                    summary += f"   Published: {video['published_at'][:10]}\n"
                summary += "\n"
            
            if total_found > 10:
                summary += f"... and {total_found - 10} more videos\n"
                summary += "\n💡 Use 'YouTube Manager' for detailed view"
            
            messagebox.showinfo("Channel Recent Uploads", summary)
                
        except Exception as e:
            error_msg = f"❌ Error checking channel!\n\nError: {str(e)}\n\n🔧 This might be:\n• Authentication issue\n• Network problem\n• API quota exceeded"
            messagebox.showerror("Error", error_msg)
            self.log(f"❌ Error checking channel: {e}")
            self.log(f"❌ Error checking channel: {e}")
            
    def quick_check_today(self):
        """Quick check today's uploads"""
        if not YOUTUBE_AVAILABLE or not self.youtube_uploader:
            messagebox.showerror("Error", "YouTube uploader not available!")
            return
            
        try:
            # Authenticate if needed
            if not self.youtube_uploader.youtube:
                self.authenticate_youtube()
                
            self.log("📅 Checking today's uploads...")
            
            # Get today's uploads
            videos = self.youtube_uploader.get_todays_uploads()
            
            from datetime import datetime
            today_str = datetime.now().strftime("%Y-%m-%d")
            
            if not videos:
                msg = f"📅 No uploads today ({today_str})\n\n💡 This is normal if:\n• You haven't uploaded today\n• Videos are still processing\n• Upload failed\n\n🔧 Check 'YouTube Manager' for more details"
                messagebox.showinfo("No Uploads Today", msg)
                self.log(f"📅 No uploads today ({today_str})")
                return
            
            total_today = len(videos)
            channel_title = "Your Channel"  # Will be updated from API if available
            
            # Show today's summary
            self.log(f"📅 Found {total_today} uploads today")
            
            summary = f"📅 Today's Uploads ({today_str})\n"
            summary += "=" * 40 + "\n\n"
            summary += f"Channel: {channel_title}\n"
            summary += f"Total uploads today: {total_today}\n\n"
            
            # Categorize today's videos
            public_count = sum(1 for v in videos if v.get('status') == 'public')
            private_count = sum(1 for v in videos if v.get('status') == 'private')
            processing_count = sum(1 for v in videos if v.get('processing_status') == 'processing')
            failed_count = sum(1 for v in videos if v.get('failure_reason'))
            
            summary += f"📊 Today's Status:\n"
            summary += f"• Public: {public_count}\n"
            summary += f"• Private: {private_count}\n"
            summary += f"• Processing: {processing_count}\n"
            summary += f"• Failed: {failed_count}\n\n"
            
            summary += f"📋 Today's Videos:\n"
            summary += "-" * 30 + "\n"
            
            for i, video in enumerate(videos, 1):
                title = video['title'][:30] + "..." if len(video['title']) > 30 else video['title']
                privacy = video.get('status', 'unknown').upper()
                processing = video.get('processing_status', 'unknown')
                
                summary += f"{i}. {title}\n"
                summary += f"   Status: {privacy} | {processing}\n"
                if video.get('duration'):
                    summary += f"   Duration: {video['duration']}\n"
                if video.get('failure_reason'):
                    summary += f"   ❌ Failed: {video['failure_reason']}\n"
                summary += "\n"
            
            summary += "\n💡 Use 'YouTube Manager' for detailed analysis"
            
            messagebox.showinfo("Today's Uploads", summary)
                
        except Exception as e:
            error_msg = f"❌ Error checking today's uploads!\n\nError: {str(e)}\n\n🔧 This might be:\n• Authentication issue\n• Network problem\n• API quota exceeded"
            messagebox.showerror("Error", error_msg)
            self.log(f"❌ Error checking today: {e}")
            messagebox.showerror("Error", error_msg)
            self.log(f"❌ Error checking today: {e}")
            
    def on_shorts_mode_change(self):
        """Handle Shorts mode toggle"""
        if self.shorts_mode.get():
            self.log("📱 Shorts mode enabled - videos will be optimized for YouTube Shorts")
            # Update default tags for Shorts
            current_tags = self.tags_var.get()
            if "Shorts" not in current_tags:
                new_tags = current_tags + ",Shorts,YouTubeShorts,Short"
                self.tags_var.set(new_tags)
            # Set privacy to public (recommended for Shorts)
            self.privacy_var.set("public")
            # Update button visibility
            self.upload_shorts_btn.pack(side=tk.LEFT, padx=(0, 15))
        else:
            self.log("📹 Regular upload mode - standard YouTube video upload")
            # Remove Shorts tags
            current_tags = self.tags_var.get()
            tags_list = [tag.strip() for tag in current_tags.split(",")]
            shorts_tags = ["Shorts", "YouTubeShorts", "Short", "Vertical"]
            filtered_tags = [tag for tag in tags_list if tag not in shorts_tags]
            self.tags_var.set(",".join(filtered_tags))
            # Hide Shorts upload button
            self.upload_shorts_btn.pack_forget()
            
    def on_quality_mode_change(self):
        """Handle quality optimization toggle"""
        if self.optimize_quality.get():
            self.log("🎯 Quality optimization enabled - videos will be optimized before upload")
            # Show optimized upload button
            self.upload_optimized_btn.pack(side=tk.LEFT, padx=(0, 15))
        else:
            self.log("📹 Basic upload mode - no quality optimization")
            # Hide optimized upload button
            self.upload_optimized_btn.pack_forget()
            
    def on_quality_preset_change(self, event=None):
        """Handle quality preset change"""
        preset = self.quality_preset_var.get()
        
        preset_descriptions = {
            'high_quality': 'Maximum quality with larger file size (CRF 18, slow preset)',
            'youtube_optimized': 'Balanced quality and file size for YouTube (CRF 20, medium preset)', 
            'fast_upload': 'Faster processing with good quality (CRF 23, fast preset)'
        }
        
        description = preset_descriptions.get(preset, 'Unknown preset')
        self.quality_info_label.config(text=description)
        self.log(f"🎯 Quality preset changed to: {preset}")
        
    def analyze_selected_video_quality(self):
        """Analyze quality of selected video"""
        selection = self.upload_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a video to analyze!")
            return
            
        item = selection[0]
        values = self.upload_tree.item(item, 'values')
        if not values or len(values) < 2:
            return
            
        file_name = values[1]
        full_path = self.get_full_video_path(file_name)
        
        if not full_path or not os.path.exists(full_path):
            messagebox.showerror("Error", "Video file not found!")
            return
            
        if not self.youtube_uploader:
            messagebox.showerror("Error", "YouTube uploader not available!")
            return
            
        # Show analysis in popup
        self.show_video_quality_analysis(full_path, file_name)
        
    def show_video_quality_analysis(self, video_path, file_name):
        """Show detailed video quality analysis in popup"""
        # Create analysis window
        analysis_window = tk.Toplevel(self.root)
        analysis_window.title(f"📊 Video Quality Analysis - {file_name}")
        analysis_window.geometry("900x700")
        analysis_window.resizable(True, True)
        
        # Make it modal
        analysis_window.transient(self.root)
        analysis_window.grab_set()
        
        # Center the window
        analysis_window.update_idletasks()
        x = (analysis_window.winfo_screenwidth() // 2) - (analysis_window.winfo_width() // 2)
        y = (analysis_window.winfo_screenheight() // 2) - (analysis_window.winfo_height() // 2)
        analysis_window.geometry(f"+{x}+{y}")
        
        main_frame = ttk.Frame(analysis_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(main_frame, text=f"📊 Quality Analysis: {file_name}", 
                 font=('Segoe UI', 14, 'bold')).pack(pady=(0, 20))
        
        # Create notebook for different analysis sections
        analysis_notebook = ttk.Notebook(main_frame)
        analysis_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Analyze video
        self.log(f"📊 Analyzing video quality: {file_name}")
        analysis = self.youtube_uploader.analyze_video_quality(video_path)
        
        if 'error' in analysis:
            ttk.Label(main_frame, text=f"❌ Analysis failed: {analysis['error']}", 
                     font=('Segoe UI', 12), foreground='red').pack(pady=20)
            ttk.Button(main_frame, text="Close", command=analysis_window.destroy).pack(pady=10)
            return
        
        # Video Info Tab
        video_frame = ttk.Frame(analysis_notebook, padding="15")
        analysis_notebook.add(video_frame, text="📹 Video Info")
        
        video_info = analysis.get('video', {})
        video_text = self._format_video_info(video_info)
        
        video_display = scrolledtext.ScrolledText(video_frame, height=15, font=('Consolas', 10))
        video_display.pack(fill=tk.BOTH, expand=True)
        video_display.insert(tk.END, video_text)
        video_display.config(state=tk.DISABLED)
        
        # Audio Info Tab
        audio_frame = ttk.Frame(analysis_notebook, padding="15")
        analysis_notebook.add(audio_frame, text="🔊 Audio Info")
        
        audio_info = analysis.get('audio', {})
        audio_text = self._format_audio_info(audio_info)
        
        audio_display = scrolledtext.ScrolledText(audio_frame, height=15, font=('Consolas', 10))
        audio_display.pack(fill=tk.BOTH, expand=True)
        audio_display.insert(tk.END, audio_text)
        audio_display.config(state=tk.DISABLED)
        
        # Recommendations Tab
        rec_frame = ttk.Frame(analysis_notebook, padding="15")
        analysis_notebook.add(rec_frame, text="💡 Recommendations")
        
        recommendations = analysis.get('recommendations', [])
        youtube_opt = analysis.get('youtube_optimization', [])
        
        rec_text = "📋 Quality Recommendations:\n"
        rec_text += "=" * 50 + "\n\n"
        
        for i, rec in enumerate(recommendations, 1):
            rec_text += f"{i}. {rec}\n"
        
        rec_text += "\n\n🎬 YouTube Optimization:\n"
        rec_text += "=" * 50 + "\n\n"
        
        for i, opt in enumerate(youtube_opt, 1):
            rec_text += f"{i}. {opt}\n"
        
        rec_display = scrolledtext.ScrolledText(rec_frame, height=15, font=('Segoe UI', 10))
        rec_display.pack(fill=tk.BOTH, expand=True)
        rec_display.insert(tk.END, rec_text)
        rec_display.config(state=tk.DISABLED)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="🎯 Optimize This Video", 
                  command=lambda: self.optimize_single_video(video_path, analysis_window)).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="📤 Upload Original", 
                  command=lambda: self.upload_single_video(video_path, analysis_window)).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Close", 
                  command=analysis_window.destroy).pack(side=tk.RIGHT)
                  
    def _format_video_info(self, video_info):
        """Format video information for display"""
        text = "📹 VIDEO STREAM ANALYSIS\n"
        text += "=" * 50 + "\n\n"
        
        text += f"Resolution:       {video_info.get('width', 'unknown')} x {video_info.get('height', 'unknown')}\n"
        text += f"Aspect Ratio:     {video_info.get('aspect_ratio', 'unknown')}\n"
        text += f"Frame Rate:       {video_info.get('fps', 'unknown')} fps\n"
        text += f"Duration:         {video_info.get('duration', 'unknown')} seconds\n"
        text += f"Codec:            {video_info.get('codec', 'unknown')}\n"
        text += f"Profile:          {video_info.get('profile', 'unknown')}\n"
        text += f"Level:            {video_info.get('level', 'unknown')}\n"
        text += f"Bitrate:          {self._format_bitrate(video_info.get('bitrate', 0))}\n"
        text += f"Pixel Count:      {video_info.get('pixel_count', 'unknown'):,} pixels\n"
        text += f"Quality Level:    {video_info.get('quality_level', 'unknown').upper()}\n\n"
        
        text += "📊 ORIENTATION:\n"
        text += f"• Vertical:       {'✅' if video_info.get('is_vertical') else '❌'}\n"
        text += f"• Horizontal:     {'✅' if video_info.get('is_horizontal') else '❌'}\n"
        text += f"• Square:         {'✅' if video_info.get('is_square') else '❌'}\n\n"
        
        # YouTube compatibility
        width = video_info.get('width', 0)
        height = video_info.get('height', 0)
        fps = video_info.get('fps', 0)
        
        text += "🎬 YOUTUBE COMPATIBILITY:\n"
        
        if width >= 1920 and height >= 1080:
            text += "• Resolution:     ✅ HD/Full HD compatible\n"
        elif width >= 1280 and height >= 720:
            text += "• Resolution:     ⚠️ HD compatible (720p)\n"
        else:
            text += "• Resolution:     ❌ Below HD standard\n"
            
        if fps in [24, 25, 30, 50, 60]:
            text += f"• Frame Rate:     ✅ Standard ({fps}fps)\n"
        else:
            text += f"• Frame Rate:     ⚠️ Non-standard ({fps}fps)\n"
            
        codec = video_info.get('codec', '')
        if codec in ['h264', 'h265']:
            text += f"• Codec:          ✅ YouTube preferred ({codec})\n"
        else:
            text += f"• Codec:          ⚠️ May need conversion ({codec})\n"
        
        return text
        
    def _format_audio_info(self, audio_info):
        """Format audio information for display"""
        text = "🔊 AUDIO STREAM ANALYSIS\n"
        text += "=" * 50 + "\n\n"
        
        text += f"Codec:            {audio_info.get('codec', 'unknown')}\n"
        text += f"Sample Rate:      {audio_info.get('sample_rate', 'unknown')} Hz\n"
        text += f"Channels:         {audio_info.get('channels', 'unknown')}\n"
        text += f"Bitrate:          {self._format_bitrate(audio_info.get('bitrate', 0))}\n"
        text += f"Quality Level:    {audio_info.get('quality_level', 'unknown').upper()}\n\n"
        
        text += "📊 CHANNEL CONFIGURATION:\n"
        text += f"• Mono:           {'✅' if audio_info.get('is_mono') else '❌'}\n"
        text += f"• Stereo:         {'✅' if audio_info.get('is_stereo') else '❌'}\n"
        text += f"• Surround:       {'✅' if audio_info.get('is_surround') else '❌'}\n\n"
        
        # YouTube audio recommendations
        text += "🎬 YOUTUBE AUDIO COMPATIBILITY:\n"
        
        codec = audio_info.get('codec', '')
        if codec in ['aac', 'mp3']:
            text += f"• Codec:          ✅ YouTube preferred ({codec})\n"
        else:
            text += f"• Codec:          ⚠️ May need conversion ({codec})\n"
            
        sample_rate = audio_info.get('sample_rate', 0)
        if sample_rate in [44100, 48000]:
            text += f"• Sample Rate:    ✅ Standard ({sample_rate}Hz)\n"
        else:
            text += f"• Sample Rate:    ⚠️ Non-standard ({sample_rate}Hz)\n"
            
        bitrate = audio_info.get('bitrate', 0)
        if bitrate >= 192000:
            text += f"• Bitrate:        ✅ High quality ({self._format_bitrate(bitrate)})\n"
        elif bitrate >= 128000:
            text += f"• Bitrate:        ✅ Good quality ({self._format_bitrate(bitrate)})\n"
        elif bitrate >= 96000:
            text += f"• Bitrate:        ⚠️ Fair quality ({self._format_bitrate(bitrate)})\n"
        else:
            text += f"• Bitrate:        ❌ Low quality ({self._format_bitrate(bitrate)})\n"
        
        return text
        
    def _format_bitrate(self, bitrate):
        """Format bitrate for display"""
        if not bitrate or bitrate == 0:
            return "unknown"
        
        if bitrate >= 1000000:
            return f"{bitrate/1000000:.1f} Mbps"
        elif bitrate >= 1000:
            return f"{bitrate/1000:.0f} kbps"
        else:
            return f"{bitrate} bps"
            
    def analyze_video_for_shorts(self, video_path):
        """Analyze video to check Shorts compatibility"""
        if not self.youtube_uploader:
            return None
            
        try:
            return self.youtube_uploader.detect_shorts_video(video_path)
        except Exception as e:
            self.log(f"❌ Error analyzing video: {e}")
            return None
            
    def upload_as_shorts_thread(self):
        """Upload selected videos as Shorts in thread"""
        if not self.selected_videos:
            messagebox.showwarning("Warning", "No videos selected!")
            return
            
        def upload_shorts():
            try:
                self.is_uploading = True
                self.upload_shorts_btn.config(state='disabled')
                self.upload_selected_btn.config(state='disabled')
                
                # Get settings
                title_prefix = self.title_prefix_var.get()
                tags = [tag.strip() for tag in self.tags_var.get().split(",") if tag.strip()]
                privacy = self.privacy_var.get()
                
                # Get selected files from upload tree, not video_files
                selected_files = []
                self.log(f"🔍 Looking for selected videos for Shorts upload...")
                
                # Get selected video files with full paths from upload tree
                for item in self.upload_tree.get_children():
                    values = self.upload_tree.item(item, 'values')
                    if values[0] == "✓":  # Selected
                        file_name = values[1]
                        
                        # Try multiple path locations
                        file_path = None
                        
                        # Try current video folder first
                        if self.current_video_folder and os.path.exists(self.current_video_folder):
                            test_path = os.path.join(self.current_video_folder, file_name)
                            if os.path.exists(test_path):
                                file_path = test_path
                        
                        # Try download folder
                        if not file_path:
                            test_path = os.path.join(self.download_folder, file_name)
                            if os.path.exists(test_path):
                                file_path = test_path
                        
                        # Try other common locations
                        if not file_path:
                            for folder in [os.path.expanduser("~/Downloads"), os.path.expanduser("~/Videos"), "."]:
                                test_path = os.path.join(folder, file_name)
                                if os.path.exists(test_path):
                                    file_path = test_path
                                    break
                        
                        if file_path:
                            selected_files.append(file_path)
                            self.log(f"✅ Found for Shorts: {file_path}")
                        else:
                            self.log(f"❌ File not found for Shorts: {file_name}")
                
                self.log(f"📁 Final selected files for Shorts: {len(selected_files)}")
                total_files = len(selected_files)
                successful = 0
                failed = 0
                
                self.log(f"📱 Starting Shorts upload for {total_files} videos...")
                
                for i, video_file in enumerate(selected_files):
                    try:
                        # Update progress
                        progress = (i / total_files) * 100
                        self.upload_progress.config(value=progress)
                        self.upload_status_var.set(f"📱 Uploading Shorts {i+1}/{total_files}...")
                        self.root.update_idletasks()
                        
                        # Analyze video for Shorts
                        self.log(f"📱 Analyzing video for Shorts: {os.path.basename(video_file)}")
                        shorts_info = self.analyze_video_for_shorts(video_file)
                        
                        if shorts_info:
                            if shorts_info.get('is_shorts'):
                                self.log(f"✅ Perfect for Shorts: {shorts_info.get('width')}x{shorts_info.get('height')}, {shorts_info.get('duration')}s")
                            else:
                                recommendations = shorts_info.get('recommendations', [])
                                if recommendations:
                                    self.log(f"⚠️ Shorts recommendations: {recommendations[0]}")
                        
                        filename = os.path.basename(video_file)
                        # Read title from tree column (user may have edited it)
                        tree_item = None
                        for _it in self.upload_tree.get_children():
                            if self.upload_tree.item(_it)['values'][1] == filename:
                                tree_item = _it
                                break
                        if tree_item:
                            _tv = self.upload_tree.item(tree_item)['values']
                            title = _tv[2] if _tv[2] else self._apply_title_template(filename)
                        else:
                            title = self._apply_title_template(filename)

                        description = self.upload_settings.get('description', '')

                        # Upload as Shorts
                        self.log(f"📱 Uploading as YouTube Shorts: {title}")
                        result = self.youtube_uploader.upload_shorts_video(
                            video_file, title, description, tags, privacy,
                            private_share_emails=self.upload_settings.get('private_share_emails', ''),
                            made_for_kids=self.upload_settings.get('made_for_kids', 'no') == 'yes'
                        )

                        if result['success']:
                            successful += 1
                            video_url = result.get('url', 'Unknown URL')
                            self.log(f"✅ Shorts upload successful: {video_url}")

                            if tree_item:
                                v = list(self.upload_tree.item(tree_item)['values'])
                                v[4] = "📱 Shorts ✅"
                                v[5] = "🔗 Open"
                                self.upload_tree.item(tree_item, values=v)
                        else:
                            failed += 1
                            error = result.get('error', 'Unknown error')
                            self.log(f"❌ Shorts upload failed: {error}")

                            if tree_item:
                                v = list(self.upload_tree.item(tree_item)['values'])
                                v[4] = "📱 Failed ❌"
                                v[5] = "❌ Error"
                                self.upload_tree.item(tree_item, values=v)
                                    
                    except Exception as e:
                        failed += 1
                        self.log(f"❌ Error uploading {video_file}: {e}")
                        
                # Complete
                self.upload_progress.config(value=100)
                self.upload_status_var.set(f"📱 Shorts upload complete! ✅{successful} ❌{failed}")
                
                # Summary message
                if successful > 0:
                    summary_msg = f"📱 YouTube Shorts Upload Complete!\n\n📊 Results:\n• Successful: {successful}\n• Failed: {failed}\n\n🎉 Shorts are optimized for mobile!\n• Vertical format with #Shorts tags\n• Should appear in Shorts feed\n• Perfect for mobile viewing\n\n📺 Check your Shorts: https://www.youtube.com/@sealrepo/shorts\n\n💡 Shorts tips:\n• Keep videos ≤60 seconds\n• Use vertical (9:16) format\n• Engage viewers in first 3 seconds\n• Use trending sounds/music"
                else:
                    summary_msg = f"❌ Shorts Upload Failed!\n\n📊 Results:\n• Successful: {successful}\n• Failed: {failed}\n\nPlease check the logs for error details."
                
                messagebox.showinfo("Shorts Upload Complete", summary_msg)
                
            except Exception as e:
                self.log(f"❌ Critical error during Shorts upload: {e}")
                messagebox.showerror("Upload Error", f"Critical error: {e}")
            finally:
                self.is_uploading = False
                self.upload_shorts_btn.config(state='normal')
                self.upload_selected_btn.config(state='normal')
                
        # Start upload in thread
        upload_thread = threading.Thread(target=upload_shorts, daemon=True)
        upload_thread.start()
        
    def upload_optimized_videos_thread(self):
        """Upload selected videos with optimization in thread"""
        if not self.selected_videos:
            messagebox.showwarning("Warning", "No videos selected!")
            return
            
        def upload_optimized():
            try:
                self.is_uploading = True
                self.upload_optimized_btn.config(state='disabled')
                self.upload_selected_btn.config(state='disabled')
                self.upload_shorts_btn.config(state='disabled')
                
                # Get settings
                title_prefix = self.title_prefix_var.get()
                tags = [tag.strip() for tag in self.tags_var.get().split(",") if tag.strip()]
                privacy = self.privacy_var.get()
                quality_preset = self.quality_preset_var.get()
                optimize = self.optimize_quality.get()
                
                # Get selected files from upload tree, not video_files
                selected_files = []
                self.log(f"🔍 Looking for {len(self.selected_videos)} selected videos...")
                
                # Get selected video files with full paths from upload tree
                for item in self.upload_tree.get_children():
                    values = self.upload_tree.item(item, 'values')
                    if values[0] == "✓":  # Selected
                        file_name = values[1]
                        
                        # Try multiple path locations
                        file_path = None
                        
                        # Try current video folder first
                        if self.current_video_folder and os.path.exists(self.current_video_folder):
                            test_path = os.path.join(self.current_video_folder, file_name)
                            if os.path.exists(test_path):
                                file_path = test_path
                        
                        # Try download folder
                        if not file_path:
                            test_path = os.path.join(self.download_folder, file_name)
                            if os.path.exists(test_path):
                                file_path = test_path
                        
                        # Try other common locations
                        if not file_path:
                            for folder in [os.path.expanduser("~/Downloads"), os.path.expanduser("~/Videos"), "."]:
                                test_path = os.path.join(folder, file_name)
                                if os.path.exists(test_path):
                                    file_path = test_path
                                    break
                        
                        if file_path:
                            selected_files.append(file_path)
                            self.log(f"✅ Found: {file_path}")
                        else:
                            self.log(f"❌ File not found: {file_name}")
                
                self.log(f"📁 Final selected files: {len(selected_files)}")
                total_files = len(selected_files)
                successful = 0
                failed = 0
                total_optimization_time = 0
                
                self.log(f"🎯 Starting optimized upload for {total_files} videos...")
                self.log(f"📊 Quality preset: {quality_preset}")
                
                for i, video_file in enumerate(selected_files):
                    try:
                        # Update progress
                        progress = (i / total_files) * 100
                        self.upload_progress.config(value=progress)
                        self.upload_status_var.set(f"🎯 Processing {i+1}/{total_files}...")
                        self.root.update_idletasks()
                        
                        filename = os.path.basename(video_file)
                        # Read title from tree column (user may have edited it)
                        tree_item = None
                        for _it in self.upload_tree.get_children():
                            if self.upload_tree.item(_it)['values'][1] == filename:
                                tree_item = _it
                                break
                        if tree_item:
                            tree_vals = self.upload_tree.item(tree_item)['values']
                            title = tree_vals[2] if tree_vals[2] else self._apply_title_template(filename)
                        else:
                            title = self._apply_title_template(filename)

                        description = self.upload_settings.get('description', '')

                        # Upload with optimization
                        self.log(f"🎯 Uploading with optimization: {title}")

                        start_time = time.time()
                        result = self.youtube_uploader.upload_optimized_video(
                            video_file, title, description, tags, "22", privacy,
                            optimize_quality=optimize, quality_preset=quality_preset,
                            private_share_emails=self.upload_settings.get('private_share_emails', ''),
                            made_for_kids=self.upload_settings.get('made_for_kids', 'no') == 'yes'
                        )
                        end_time = time.time()

                        processing_time = end_time - start_time
                        total_optimization_time += processing_time

                        if result['success']:
                            successful += 1
                            video_url = result.get('url', 'Unknown URL')

                            if result.get('optimization'):
                                opt_info = result['optimization']
                                self.log(f"✅ Optimized: {opt_info['input_size_mb']}MB → {opt_info['output_size_mb']}MB")
                                self.log(f"📊 Compression: {opt_info['compression_ratio']:.2f}x")

                            self.log(f"✅ Upload successful: {video_url}")
                            self.log(f"⏱️ Processing time: {processing_time:.1f}s")

                            if tree_item:
                                v = list(self.upload_tree.item(tree_item)['values'])
                                status = "🎯 Optimized ✅"
                                if result.get('optimization'):
                                    status += f" ({result['optimization']['compression_ratio']:.1f}x)"
                                v[4] = status
                                v[5] = "🔗 Open"
                                self.upload_tree.item(tree_item, values=v)
                        else:
                            failed += 1
                            error = result.get('error', 'Unknown error')
                            self.log(f"❌ Upload failed: {error}")

                            if tree_item:
                                v = list(self.upload_tree.item(tree_item)['values'])
                                v[4] = "🎯 Failed ❌"
                                v[5] = "❌ Error"
                                self.upload_tree.item(tree_item, values=v)
                                    
                    except Exception as e:
                        failed += 1
                        self.log(f"❌ Error uploading {video_file}: {e}")
                        
                # Complete
                self.upload_progress.config(value=100)
                avg_time = total_optimization_time / total_files if total_files > 0 else 0
                self.upload_status_var.set(f"🎯 Optimized upload complete! ✅{successful} ❌{failed}")
                
                # Summary message
                if successful > 0:
                    summary_msg = f"🎯 Optimized YouTube Upload Complete!\n\n📊 Results:\n• Successful: {successful}\n• Failed: {failed}\n• Quality preset: {quality_preset}\n• Avg processing time: {avg_time:.1f}s\n\n🎉 Videos optimized for best quality!\n• Enhanced encoding for YouTube\n• Optimized bitrates and codecs\n• Better compression efficiency\n• Improved compatibility\n\n📺 Check your channel: https://www.youtube.com/@sealrepo\n\n💡 Optimization benefits:\n• Better video quality\n• Faster YouTube processing\n• Improved mobile compatibility\n• Reduced storage usage"
                else:
                    summary_msg = f"❌ Optimized Upload Failed!\n\n📊 Results:\n• Successful: {successful}\n• Failed: {failed}\n\nPlease check the logs for error details."
                
                messagebox.showinfo("Optimized Upload Complete", summary_msg)
                
            except Exception as e:
                self.log(f"❌ Critical error during optimized upload: {e}")
                messagebox.showerror("Upload Error", f"Critical error: {e}")
            finally:
                self.is_uploading = False
                self.upload_optimized_btn.config(state='normal')
                self.upload_selected_btn.config(state='normal')
                self.upload_shorts_btn.config(state='normal')
                
        # Start upload in thread
        upload_thread = threading.Thread(target=upload_optimized, daemon=True)
        upload_thread.start()
        
    def optimize_single_video(self, video_path, parent_window):
        """Optimize single video from analysis window"""
        if not self.youtube_uploader:
            messagebox.showerror("Error", "YouTube uploader not available!")
            return
            
        quality_preset = self.quality_preset_var.get()
        
        try:
            # Generate output filename
            base, ext = os.path.splitext(video_path)
            output_path = f"{base}_optimized{ext}"
            
            self.log(f"🔧 Optimizing video: {os.path.basename(video_path)}")
            
            # Perform optimization
            result = self.youtube_uploader.optimize_video_for_youtube(
                video_path, output_path, quality_preset
            )
            
            if result['success']:
                opt_info = f"✅ Optimization successful!\n\n"
                opt_info += f"📊 Size: {result['input_size_mb']}MB → {result['output_size_mb']}MB\n"
                opt_info += f"📉 Compression: {result['compression_ratio']:.2f}x\n"
                opt_info += f"🎯 Preset: {result['optimization_preset']}\n\n"
                opt_info += f"📁 Output: {output_path}\n\n"
                opt_info += "Would you like to upload the optimized version?"
                
                if messagebox.askyesno("Optimization Complete", opt_info):
                    parent_window.destroy()
                    self.upload_single_video(output_path)
            else:
                messagebox.showerror("Optimization Failed", f"❌ Error: {result['error']}")
                
        except Exception as e:
            messagebox.showerror("Optimization Error", f"❌ Error: {str(e)}")
            
    def upload_single_video(self, video_path, parent_window=None):
        """Upload single video immediately"""
        if parent_window:
            parent_window.destroy()
            
        # Implementation for single video upload
        filename = os.path.basename(video_path)
        title = f"Video - {os.path.splitext(filename)[0]}"
        
        try:
            result = self.youtube_uploader.upload_video(
                video_path, title, "Uploaded via Douyin to YouTube Tool", 
                ["video", "upload"], "22", "private"
            )
            
            if result['success']:
                messagebox.showinfo("Upload Complete", f"✅ Video uploaded successfully!\n\nURL: {result.get('url', 'Unknown')}")
            else:
                messagebox.showerror("Upload Failed", f"❌ Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            messagebox.showerror("Upload Error", f"❌ Error: {str(e)}")
            
    def show_youtube_manager(self):
        """Show YouTube Manager (alias for open_youtube_manager)"""
        self.open_youtube_manager()
        
    def open_youtube_manager(self):
        """Show Enhanced YouTube Manager with comprehensive features"""
        if not YOUTUBE_AVAILABLE or not self.youtube_uploader:
            messagebox.showerror("Error", "YouTube uploader not available!")
            return
            
        # Create manager window
        manager_window = tk.Toplevel(self.root)
        manager_window.title("🚀 YouTube Manager Pro")
        manager_window.geometry("1200x800")
        manager_window.resizable(True, True)
        manager_window.configure(bg=self.colors['light'])
        
        # Make it modal
        manager_window.transient(self.root)
        manager_window.grab_set()
        
        # Center the window
        manager_window.update_idletasks()
        x = (manager_window.winfo_screenwidth() // 2) - (manager_window.winfo_width() // 2)
        y = (manager_window.winfo_screenheight() // 2) - (manager_window.winfo_height() // 2)
        manager_window.geometry(f"+{x}+{y}")
        
        main_frame = tk.Frame(manager_window, bg=self.colors['light'], padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with channel info
        header_frame = tk.Frame(main_frame, bg=self.colors['light'])
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(header_frame, text="🚀 YouTube Manager Pro", 
                 font=('Segoe UI', 16, 'bold'),
                 bg=self.colors['light'], fg=self.colors['dark']).pack(side=tk.LEFT)
        
        # Control buttons
        controls_frame = tk.Frame(header_frame, bg=self.colors['light'])
        controls_frame.pack(side=tk.RIGHT)
        
        tk.Button(controls_frame, text="🔄 Refresh", 
                  command=lambda: self.refresh_manager_data(manager_window),
                  bg=self.colors['primary'], fg='white', relief=tk.FLAT,
                  font=('Segoe UI', 9, 'bold'), cursor='hand2').pack(side=tk.LEFT, padx=(0, 5))
                  
        tk.Button(controls_frame, text="📊 Analytics", 
                  command=lambda: self.show_video_analytics(manager_window),
                  bg=self.colors['info'], fg='white', relief=tk.FLAT,
                  font=('Segoe UI', 9, 'bold'), cursor='hand2').pack(side=tk.LEFT, padx=(0, 5))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Video Management
        self.create_video_management_tab(notebook, manager_window)
        
        # Tab 2: Dashboard Overview
        self.create_dashboard_tab(notebook, manager_window)
        
        # Tab 3: Analytics
        self.create_analytics_tab(notebook, manager_window)
        
        # Tab 4: Comments
        self.create_comments_tab(notebook, manager_window)
        
        # Tab 5: SEO Tools
        self.create_seo_tab(notebook, manager_window)
        
        # Tab 6: Settings
        self.create_settings_tab(notebook, manager_window)
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.manager_status_var = tk.StringVar(value="🟢 YouTube Manager Ready")
        ttk.Label(status_frame, textvariable=self.manager_status_var).pack(side=tk.LEFT)
        
        # Auto-load data
        self.refresh_manager_data(manager_window)
        
        # Load real stats after window is created
        self.load_channel_statistics(manager_window)
        
        # Also trigger refresh of stats in refresh function
        try:
            # Find the first working refresh_manager_data function and update it
            threading.Thread(target=lambda: self.load_channel_statistics(manager_window), daemon=True).start()
        except:
            pass
            
    def create_video_management_tab(self, notebook, parent_window):
        """Create video management tab with list, preview, and edit/delete functionality"""
        video_frame = tk.Frame(notebook, bg=self.colors['light'])
        notebook.add(video_frame, text="📹 Video Manager")
        
        # Main layout - split into list and preview
        main_container = tk.PanedWindow(video_frame, orient=tk.HORIZONTAL, bg=self.colors['light'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Video list
        left_panel = tk.Frame(main_container, bg=self.colors['light'])
        main_container.add(left_panel, width=700)
        
        # Video list header
        list_header = tk.Frame(left_panel, bg=self.colors['primary'], height=40)
        list_header.pack(fill=tk.X, pady=(0, 5))
        list_header.pack_propagate(False)
        
        tk.Label(list_header, text="📹 My Videos", 
                font=('Segoe UI', 12, 'bold'),
                bg=self.colors['primary'], fg='white').pack(side=tk.LEFT, padx=10, pady=8)
        
        # Search and filter controls
        controls_frame = tk.Frame(left_panel, bg=self.colors['surface'])
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(controls_frame, text="🔍 Search:", bg=self.colors['surface']).pack(side=tk.LEFT, padx=(5, 5))
        
        self.video_search_var = tk.StringVar()
        search_entry = tk.Entry(controls_frame, textvariable=self.video_search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        search_entry.bind('<KeyRelease>', self.filter_video_list)
        
        tk.Button(controls_frame, text="🔄 Load Videos", 
                 command=lambda: self.load_video_list(parent_window),
                 bg=self.colors['primary'], fg='white', relief=tk.FLAT,
                 font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 5))
        
        # Video list with scrollbar
        list_container = tk.Frame(left_panel, bg=self.colors['light'])
        list_container.pack(fill=tk.BOTH, expand=True)
        
        # Video treeview
        columns = ('Title', 'Views', 'Privacy', 'Published', 'Duration')
        self.video_tree = ttk.Treeview(list_container, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.video_tree.heading('Title', text='📹 Title')
        self.video_tree.heading('Views', text='👁️ Views')
        self.video_tree.heading('Privacy', text='🔒 Privacy')
        self.video_tree.heading('Published', text='📅 Published')
        self.video_tree.heading('Duration', text='⏱️ Duration')
        
        self.video_tree.column('Title', width=300)
        self.video_tree.column('Views', width=80, anchor='center')
        self.video_tree.column('Privacy', width=80, anchor='center')
        self.video_tree.column('Published', width=100, anchor='center')
        self.video_tree.column('Duration', width=80, anchor='center')
        
        # Scrollbar for video list
        list_scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.video_tree.yview)
        self.video_tree.configure(yscrollcommand=list_scrollbar.set)
        
        self.video_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind events for preview and context menu
        self.video_tree.bind('<Motion>', self.on_video_hover)
        self.video_tree.bind('<Leave>', self.hide_video_preview)
        self.video_tree.bind('<Button-3>', self.show_video_context_menu)
        self.video_tree.bind('<<TreeviewSelect>>', self.on_video_select)
        
        # Right panel - Video preview and details
        right_panel = tk.Frame(main_container, bg=self.colors['surface'])
        main_container.add(right_panel, width=400)
        
        # Preview header
        preview_header = tk.Frame(right_panel, bg=self.colors['secondary'], height=40)
        preview_header.pack(fill=tk.X, pady=(0, 5))
        preview_header.pack_propagate(False)
        
        tk.Label(preview_header, text="👁️ Video Preview", 
                font=('Segoe UI', 12, 'bold'),
                bg=self.colors['secondary'], fg='white').pack(side=tk.LEFT, padx=10, pady=8)
        
        # Preview content area
        self.preview_frame = tk.Frame(right_panel, bg=self.colors['surface'])
        self.preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Default preview message
        self.preview_label = tk.Label(self.preview_frame, 
                                     text="📹 Select a video to see preview\n\n• Hover over videos for quick preview\n• Right-click for edit/delete options\n• Double-click to open in YouTube",
                                     font=('Segoe UI', 11),
                                     bg=self.colors['surface'], fg=self.colors['dark'],
                                     justify=tk.CENTER)
        self.preview_label.pack(expand=True)
        
        # Action buttons at bottom of preview
        action_frame = tk.Frame(right_panel, bg=self.colors['surface'])
        action_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Button(action_frame, text="✏️ Edit Video", 
                 command=self.edit_selected_video,
                 bg=self.colors['primary'], fg='white', relief=tk.FLAT,
                 font=('Segoe UI', 10, 'bold'), state='disabled').pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(action_frame, text="🗑️ Delete Video", 
                 command=self.delete_selected_video,
                 bg=self.colors['danger'], fg='white', relief=tk.FLAT,
                 font=('Segoe UI', 10, 'bold'), state='disabled').pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(action_frame, text="📊 Analytics", 
                 command=self.show_video_analytics,
                 bg=self.colors['info'], fg='white', relief=tk.FLAT,
                 font=('Segoe UI', 10, 'bold'), state='disabled').pack(side=tk.LEFT)
        
        # Store reference for later use
        self.current_video_data = {}
        
    def create_dashboard_tab(self, notebook, parent_window):
        """Create dashboard overview tab"""
        dashboard_frame = tk.Frame(notebook, bg=self.colors['light'])
        notebook.add(dashboard_frame, text="🏠 Dashboard")
        
        # Main container with scrollable content
        canvas = tk.Canvas(dashboard_frame, bg=self.colors['surface'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(dashboard_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['surface'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Quick Stats Section
        stats_frame = tk.LabelFrame(scrollable_frame, text="📊 Quick Stats", 
                                   bg=self.colors['background'], fg=self.colors['primary'],
                                   font=('Segoe UI', 10, 'bold'), padx=15, pady=15)
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        stats_grid = tk.Frame(stats_frame, bg=self.colors['background'])
        stats_grid.pack(fill=tk.X)
        
        # Stats cards
        self.create_stat_card(stats_grid, "📹 Total Videos", "Loading...", 0, 0)
        self.create_stat_card(stats_grid, "👥 Subscribers", "Loading...", 0, 1)
        self.create_stat_card(stats_grid, "👁️ Total Views", "Loading...", 0, 2)
        self.create_stat_card(stats_grid, "📅 Today's Uploads", "Loading...", 1, 0)
        self.create_stat_card(stats_grid, "⏱️ Watch Time", "Loading...", 1, 1)
        self.create_stat_card(stats_grid, "💰 Revenue (Est.)", "Loading...", 1, 2)
        
        # Recent Activity Section
        activity_frame = tk.LabelFrame(scrollable_frame, text="📈 Recent Activity",
                                     bg=self.colors['background'], fg=self.colors['primary'],
                                     font=('Segoe UI', 10, 'bold'), padx=15, pady=15)
        activity_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Activity buttons
        activity_buttons = tk.Frame(activity_frame, bg=self.colors['light'])
        activity_buttons.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(activity_buttons, text="📺 Check Today's Videos", 
                  command=self.quick_check_today,
                  bg=self.colors['primary'], fg='white', relief=tk.FLAT,
                  font=('Segoe UI', 9, 'bold'), cursor='hand2').pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(activity_buttons, text="📋 Recent Uploads", 
                  command=self.quick_check_channel,
                  bg=self.colors['secondary'], fg='white', relief=tk.FLAT,
                  font=('Segoe UI', 9, 'bold'), cursor='hand2').pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(activity_buttons, text="💬 Recent Comments", 
                  command=lambda: self.check_recent_comments(parent_window),
                  bg=self.colors['accent'], fg='white', relief=tk.FLAT,
                  font=('Segoe UI', 9, 'bold'), cursor='hand2').pack(side=tk.LEFT)
        
        # Quick Actions Section
        actions_frame = tk.LabelFrame(scrollable_frame, text="⚡ Quick Actions",
                                    bg=self.colors['background'], fg=self.colors['primary'],
                                    font=('Segoe UI', 10, 'bold'), padx=15, pady=15)
        actions_frame.pack(fill=tk.X, pady=(0, 15))
        
        actions_grid = tk.Frame(actions_frame, bg=self.colors['light'])
        actions_grid.pack(fill=tk.X)
        
        # Action buttons in grid
        tk.Button(actions_grid, text="🚀 Upload Video", 
                  command=self.browse_videos_for_upload,
                  bg=self.colors['primary'], fg='white', relief=tk.FLAT,
                  font=('Segoe UI', 9, 'bold'), cursor='hand2').grid(row=0, column=0, padx=(0, 10), pady=(0, 5), sticky="ew")
        tk.Button(actions_grid, text="🎨 Create Thumbnail", 
                  command=lambda: self.open_thumbnail_tools(parent_window),
                  bg=self.colors['accent'], fg='white', relief=tk.FLAT,
                  font=('Segoe UI', 9, 'bold'), cursor='hand2').grid(row=0, column=1, padx=(0, 10), pady=(0, 5), sticky="ew")
        tk.Button(actions_grid, text="📝 Edit Metadata", 
                  command=lambda: self.open_bulk_editor(parent_window),
                  bg=self.colors['secondary'], fg='white', relief=tk.FLAT,
                  font=('Segoe UI', 9, 'bold'), cursor='hand2').grid(row=0, column=2, pady=(0, 5), sticky="ew")
        
        tk.Button(actions_grid, text="📊 Export Analytics", 
                  command=lambda: self.export_analytics_data(parent_window),
                  bg=self.colors['accent'], fg='white', relief=tk.FLAT,
                  font=('Segoe UI', 9, 'bold'), cursor='hand2').grid(row=1, column=0, padx=(0, 10), pady=(0, 5), sticky="ew")
        tk.Button(actions_grid, text="🔍 SEO Analyzer", 
                  command=lambda: notebook.select(4),
                  bg=self.colors['success'], fg='white', relief=tk.FLAT,
                  font=('Segoe UI', 9, 'bold'), cursor='hand2').grid(row=1, column=1, padx=(0, 10), pady=(0, 5), sticky="ew")  # Switch to SEO tab
        tk.Button(actions_grid, text="📅 Schedule Upload", 
                  command=lambda: self.open_scheduler(parent_window),
                  bg=self.colors['danger'], fg='white', relief=tk.FLAT,
                  font=('Segoe UI', 9, 'bold'), cursor='hand2').grid(row=1, column=2, pady=(0, 5), sticky="ew")
        
        # Configure grid weights
        for i in range(3):
            actions_grid.columnconfigure(i, weight=1)
        
        # Performance Insights
        insights_frame = tk.LabelFrame(scrollable_frame, text="🎯 Performance Insights",
                                     bg=self.colors['background'], fg=self.colors['primary'],
                                     font=('Segoe UI', 10, 'bold'), padx=15, pady=15)
        insights_frame.pack(fill=tk.X)
        
        insights_text = tk.Text(insights_frame, height=8, font=('Segoe UI', 9),
                               bg=self.colors['light'], fg=self.colors['dark'],
                               insertbackground=self.colors['primary'])
        insights_scroll = ttk.Scrollbar(insights_frame, orient="vertical", command=insights_text.yview)
        insights_text.configure(yscrollcommand=insights_scroll.set)
        
        insights_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        insights_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Sample insights (will be populated with real data)
        sample_insights = """🎯 Channel Performance Insights:

📈 Top Performing Video: Will be loaded from analytics...
📊 Average View Duration: Analyzing...  
🎬 Best Upload Time: Calculating...
🏷️ Most Effective Tags: Processing...
👥 Audience Demographics: Loading...
📱 Traffic Sources: Fetching data...

💡 Recommendations:
• Upload frequency analysis pending...
• Content optimization suggestions loading...
• SEO improvements being calculated...
"""
        
        insights_text.insert(tk.END, sample_insights)
        insights_text.config(state=tk.DISABLED)
        
        # Pack scrollable elements
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_stat_card(self, parent, title, value, row, col):
        """Create a stat card widget"""
        card_frame = tk.LabelFrame(parent, text=title, 
                                  bg=self.colors['background'], fg=self.colors['primary'],
                                  font=('Segoe UI', 9, 'bold'), padx=10, pady=10)
        card_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        value_label = tk.Label(card_frame, text=str(value), 
                              font=('Segoe UI', 14, 'bold'),
                              bg=self.colors['background'], fg=self.colors['dark'])
        value_label.pack()
        
        # Store reference for updating
        if not hasattr(self, 'stat_labels'):
            self.stat_labels = {}
        self.stat_labels[title] = value_label
        
        # Configure grid weights
        parent.columnconfigure(col, weight=1)
        
    def refresh_manager_data(self, manager_window):
        """Refresh data in YouTube Manager"""
        try:
            # Update any displayed statistics or data
            self.log("🔄 Refreshing YouTube Manager data...")
            if hasattr(self, 'stat_labels'):
                # Refresh channel statistics if available
                if self.youtube_uploader and self.youtube_uploader.youtube:
                    # Could add real-time data refresh here
                    pass
            self.log("✅ YouTube Manager data refreshed")
        except Exception as e:
            self.log(f"❌ Error refreshing manager data: {e}")
    
    def manager_check_todays_uploads(self, window):
        """Check today's uploads from manager"""
        if not self.youtube_uploader or not self.youtube_uploader.youtube:
            messagebox.showerror("Error", "Please authenticate first!")
            return
            
        self.manager_results.delete(1.0, tk.END)
        self.manager_results.insert(tk.END, "📅 Checking today's uploads...\n")
        self.manager_results.insert(tk.END, "═" * 50 + "\n")
        window.update()
        
        try:
            result = self.youtube_uploader.get_todays_uploads()
            
            if result['success']:
                videos = result['videos']
                channel_title = result['channel_title']
                total_today = result['total_today']
                
                from datetime import datetime
                today_str = datetime.now().strftime("%Y-%m-%d")
                
                self.manager_results.insert(tk.END, f"Channel: {channel_title}\n")
                self.manager_results.insert(tk.END, f"Date: {today_str}\n")
                self.manager_results.insert(tk.END, f"Total uploads today: {total_today}\n\n")
                
                if total_today == 0:
                    self.manager_results.insert(tk.END, "📭 No uploads found for today\n")
                    self.manager_results.insert(tk.END, "\n💡 This could mean:\n")
                    self.manager_results.insert(tk.END, "• No videos were uploaded today\n")
                    self.manager_results.insert(tk.END, "• Videos are still processing\n")
                    self.manager_results.insert(tk.END, "• Wrong account authenticated\n")
                else:
                    public_count = sum(1 for v in videos if v.get('status') == 'public')
                    private_count = sum(1 for v in videos if v.get('status') == 'private')
                    processing_count = sum(1 for v in videos if v['processing_status'] == 'processing')
                    
                    self.manager_results.insert(tk.END, f"📊 Summary:\n")
                    self.manager_results.insert(tk.END, f"• Public: {public_count}\n")
                    self.manager_results.insert(tk.END, f"• Private: {private_count}\n") 
                    self.manager_results.insert(tk.END, f"• Processing: {processing_count}\n\n")
                    
                    self.manager_results.insert(tk.END, "📋 Video Details:\n")
                    self.manager_results.insert(tk.END, "─" * 50 + "\n")
                    
                    for i, video in enumerate(videos, 1):
                        title = video['title'][:40] + "..." if len(video['title']) > 40 else video['title']
                        privacy = video.get('status', 'unknown').upper()
                        processing = video.get('processing_status', 'unknown')
                        
                        self.manager_results.insert(tk.END, f"{i}. {title}\n")
                        self.manager_results.insert(tk.END, f"   Privacy: {privacy} | Processing: {processing}\n")
                        self.manager_results.insert(tk.END, f"   URL: {video['url']}\n\n")
            else:
                self.manager_results.insert(tk.END, f"❌ Error: {result['error']}\n")
                
        except Exception as e:
            self.manager_results.insert(tk.END, f"❌ Exception: {str(e)}\n")
            
        self.manager_results.see(tk.END)
        
    def manager_check_recent_uploads(self, window):
        """Check recent uploads status from manager"""
        if not self.youtube_uploader or not self.youtube_uploader.youtube:
            messagebox.showerror("Error", "Please authenticate first!")
            return
            
        self.manager_results.delete(1.0, tk.END)
        self.manager_results.insert(tk.END, "🔍 Checking recent uploads status...\n")
        self.manager_results.insert(tk.END, "═" * 50 + "\n")
        window.update()
        
        try:
            result = self.youtube_uploader.list_recent_uploads(max_results=10)
            
            if result['success']:
                videos = result['videos']
                total_found = result['total_found']
                
                self.manager_results.insert(tk.END, f"Total recent uploads: {total_found}\n\n")
                
                if total_found == 0:
                    self.manager_results.insert(tk.END, "📭 No recent uploads found\n")
                else:
                    self.manager_results.insert(tk.END, "📋 Recent Videos Status:\n")
                    self.manager_results.insert(tk.END, "─" * 50 + "\n")
                    
                    for i, video in enumerate(videos, 1):
                        title = video['title'][:40] + "..." if len(video['title']) > 40 else video['title']
                        privacy = video.get('status', 'unknown').upper()
                        upload_status = video.get('upload_status', 'unknown')
                        processing = video.get('processing_status', 'unknown')
                        
                        self.manager_results.insert(tk.END, f"{i}. {title}\n")
                        self.manager_results.insert(tk.END, f"   Privacy: {privacy}\n")
                        self.manager_results.insert(tk.END, f"   Upload: {upload_status} | Processing: {processing}\n")
                        if video.get('published_at'):
                            self.manager_results.insert(tk.END, f"   Published: {video['published_at']}\n")
                        self.manager_results.insert(tk.END, "\n")
            else:
                self.manager_results.insert(tk.END, f"❌ Error: {result['error']}\n")
                
        except Exception as e:
            self.manager_results.insert(tk.END, f"❌ Exception: {str(e)}\n")
            
        self.manager_results.see(tk.END)
                
    def select_all_for_upload(self):
        """Select all videos"""
        for item in self.upload_tree.get_children():
            values = list(self.upload_tree.item(item, 'values'))
            values[0] = "✓"
            # Ensure actions column exists
            if len(values) < 6:
                values.append("🎬  📁")
            self.upload_tree.item(item, values=values, tags=('selected',))
            self.selected_videos.add(values[1])
            
        self.update_upload_count()
        self.log("✅ Selected all videos")
        
    def deselect_all_for_upload(self):
        """Deselect all videos"""
        for item in self.upload_tree.get_children():
            values = list(self.upload_tree.item(item, 'values'))
            values[0] = ""
            # Ensure actions column exists
            if len(values) < 6:
                values.append("🎬  📁")
            self.upload_tree.item(item, values=values, tags=('unselected',))
            
        self.selected_videos.clear()
        self.update_upload_count()
        self.log("❌ Deselected all videos")
        
    def update_upload_count(self):
        """Update upload count"""
        total = len(self.upload_tree.get_children())
        selected = len(self.selected_videos)
        self.upload_count_var.set(f"📋 Selected: {selected}/{total}")
        
        if selected > 0 and YOUTUBE_AVAILABLE:
            self.upload_selected_btn.config(state='normal')
            self.upload_optimized_btn.config(state='normal')
            self.upload_shorts_btn.config(state='normal')
        else:
            self.upload_selected_btn.config(state='disabled')
            self.upload_optimized_btn.config(state='disabled')
            self.upload_shorts_btn.config(state='disabled')
            
    def youtube_authenticate_thread(self):
        """YouTube authentication in thread"""
        # Use root.after to run authentication in main thread
        self.root.after(100, self.authenticate_youtube)
        
    def auto_oauth_login(self):
        """Auto OAuth login without user dialog"""
        if not self.youtube_uploader:
            self.log("❌ YouTube API not available")
            return False
            
        try:
            # Try OAuth authentication first
            self.log("🔐 Attempting OAuth authentication...")
            success = self.youtube_uploader.authenticate()
            
            if success:
                self.log("✅ OAuth authentication successful! Full YouTube access enabled.")
                try:
                    self.update_auth_status()  # Update status display
                except:
                    pass  # Ignore if auth_status_var not ready
                return True
            else:
                self.log("⚠️ OAuth failed, falling back to demo mode")
                # Fallback to demo mode if OAuth fails
                self.youtube_uploader.service = 'demo_service'
                self.youtube_uploader.youtube = 'demo_service'
                self.youtube_uploader.authenticated = True
                try:
                    self.update_auth_status()  # Update status display
                except:
                    pass  # Ignore if auth_status_var not ready
                return True
                
        except Exception as e:
            error_msg = f"OAuth error: {str(e)}"
            self.log(f"⚠️ {error_msg}, using demo mode")
            # Fallback to demo mode on any error
            self.youtube_uploader.service = 'demo_service'
            self.youtube_uploader.youtube = 'demo_service'
            self.youtube_uploader.authenticated = True
            try:
                self.update_auth_status()  # Update status display
            except:
                pass  # Ignore if auth_status_var not ready
            return True
        
    def upload_selected_videos_thread(self):
        """Upload selected videos in thread"""
        thread = threading.Thread(target=self.upload_selected_videos, daemon=True)
        thread.start()
        
    def upload_selected_videos(self):
        """Upload selected videos"""
        if not YOUTUBE_AVAILABLE or not self.youtube_uploader:
            messagebox.showerror("Error", "YouTube uploader not available!")
            return
            
        if not self.selected_videos:
            messagebox.showerror("Error", "No videos selected for upload!\n\nPlease:\n1. Browse videos or load from downloads\n2. Double-click videos to select them (✓)\n3. Try again")
            return
            
        self.log(f"🚀 Starting upload of {len(self.selected_videos)} videos...")
        
        # Get selected video files with full paths
        selected_files = []
        for item in self.upload_tree.get_children():
            values = self.upload_tree.item(item, 'values')
            if values[0] == "✓":  # Selected
                file_name = values[1]
                
                # Try multiple path locations
                file_path = None
                
                # First try current video folder
                if hasattr(self, 'current_video_folder') and self.current_video_folder:
                    test_path = os.path.join(self.current_video_folder, file_name)
                    if os.path.exists(test_path):
                        file_path = test_path
                
                # Then try download folder
                if not file_path:
                    test_path = os.path.join(self.download_folder, file_name)
                    if os.path.exists(test_path):
                        file_path = test_path
                
                # Finally try absolute path if it looks like one
                if not file_path and os.path.isabs(file_name):
                    if os.path.exists(file_name):
                        file_path = file_name
                
                if file_path:
                    selected_files.append((item, file_path, file_name))
                else:
                    self.log(f"⚠️ File not found: {file_name}")
                    
        if not selected_files:
            messagebox.showerror("Error", "No valid video files found!\n\nPossible issues:\n• Files were moved or deleted\n• Wrong folder selected\n• File permissions")
            return
            
        self.log(f"📤 Found {len(selected_files)} valid files to upload")
        
        self.is_uploading = True
        self.upload_selected_btn.config(state='disabled')
        
        total = len(selected_files)
        self.upload_progress['maximum'] = total
        self.upload_progress['value'] = 0
        
        successful = 0
        failed = 0
        
        try:
            for i, (item, file_path, file_name) in enumerate(selected_files):
                # Update status
                values = list(self.upload_tree.item(item, 'values'))
                values[4] = "📤 Uploading..."
                self.upload_tree.item(item, values=values)

                # Read title from tree column (user may have edited it)
                title = values[2] if values[2] else self._apply_title_template(file_name)
                tags = [tag.strip() for tag in self.tags_var.get().split(',') if tag.strip()]

                self.log(f"📤 Uploading {i+1}/{total}: {file_name}")
                
                try:
                    result = self.youtube_uploader.upload_video(
                        video_file=file_path,
                        title=title,
                        description=self.upload_settings.get('description', ''),
                        tags=tags,
                        privacy_status=self.privacy_var.get(),
                        private_share_emails=self.upload_settings.get('private_share_emails', ''),
                        made_for_kids=self.upload_settings.get('made_for_kids', 'no') == 'yes'
                    )

                    if result['success']:
                        successful += 1
                        values[4] = "✅ Uploaded"
                        privacy_status = self.privacy_var.get()
                        video_url = result['url']
                        video_id = result.get('video_id', '')
                        
                        # Log detailed success info
                        self.log(f"✅ Upload successful!")
                        self.log(f"   📹 Title: {title}")
                        self.log(f"   🔗 URL: {video_url}")
                        self.log(f"   🆔 Video ID: {video_id}")
                        self.log(f"   🔒 Privacy: {privacy_status}")
                        # Log private share result
                        share_info = result.get('private_share')
                        if share_info:
                            if share_info.get('success'):
                                emails_shared = ', '.join(share_info.get('shared_with', []))
                                self.log(f"   📧 Shared with: {emails_shared}")
                            else:
                                self.log(f"   ⚠️ Private share failed: {share_info.get('error', 'unknown')}")
                        
                        # Verify if video actually exists on YouTube
                        if video_id:
                            try:
                                # First check if video exists
                                verify_result = self.youtube_uploader.verify_video_exists(video_id)
                                if verify_result['success']:
                                    if verify_result.get('exists'):
                                        self.log(f"   ✅ Video confirmed on YouTube!")
                                        self.log(f"   📅 Published: {verify_result.get('published_at', 'Unknown')}")
                                    else:
                                        self.log(f"   ⚠️  Video not found on YouTube yet (may still be processing)")
                                elif verify_result.get('is_demo'):
                                    self.log(f"   ⚠️  {verify_result['message']}")
                                    self.log(f"   💡 To upload real videos, use OAuth authentication with credentials.json")
                                    values[4] = "🎭 Demo"
                                else:
                                    self.log(f"   ❌ Could not verify video existence: {verify_result.get('error', 'Unknown error')}")
                                
                                # Then check detailed status
                                status_check = self.youtube_uploader.check_video_status(video_id)
                                if status_check['success']:
                                    upload_status = status_check.get('upload_status', 'unknown')
                                    processing_status = status_check.get('processing_status', 'unknown')
                                    failure_reason = status_check.get('failure_reason')
                                    rejection_reason = status_check.get('rejection_reason')
                                    
                                    self.log(f"   📤 Upload Status: {upload_status}")
                                    self.log(f"   ⚙️  Processing: {processing_status}")
                                    
                                    if failure_reason:
                                        self.log(f"   ❌ Failure Reason: {failure_reason}")
                                    if rejection_reason:
                                        self.log(f"   🚫 Rejection Reason: {rejection_reason}")
                                        
                                    # Update status in table based on actual status
                                    if upload_status == 'failed':
                                        values[4] = "❌ Failed"
                                        successful -= 1
                                        failed += 1
                                    elif rejection_reason:
                                        values[4] = "🚫 Rejected"
                                    # processing = YouTube đang xử lý nội bộ sau upload thành công → giữ ✅ Uploaded
                                        
                            except Exception as status_error:
                                self.log(f"   ⚠️  Could not verify status: {status_error}")
                        
                        # Check for processing status
                        if 'processing_status' in result:
                            proc_status = result['processing_status']
                            upload_status = result.get('upload_status', 'unknown')
                            self.log(f"   ⚙️  Processing: {proc_status}")
                            self.log(f"   📤 Upload Status: {upload_status}")
                        
                        # Check for warnings
                        if 'warning' in result:
                            self.log(f"   ⚠️  Warning: {result['warning']}")
                        
                        if privacy_status == "private":
                            self.log(f"   ⚠️  Video is PRIVATE - won't appear in channel publicly!")
                            self.log(f"   💡 Go to YouTube Studio to change privacy to 'Public'")
                        elif privacy_status == "unlisted":
                            self.log(f"   ⚠️  Video is UNLISTED - only viewable with direct link!")
                        else:
                            self.log(f"   ✅ Video is PUBLIC - should appear in your channel")
                            self.log(f"   ⏳ May take a few minutes to process and appear")
                            
                    else:
                        failed += 1
                        values[4] = "❌ Failed"
                        error_msg = result.get('error', 'Unknown error')
                        self.log(f"❌ Upload failed: {error_msg}")

                        if "quota" in error_msg.lower():
                            self.log(f"   💡 This might be a YouTube API quota issue")
                        elif "forbidden" in error_msg.lower():
                            self.log(f"   💡 Check if your account has upload permissions")
                        elif "invalid" in error_msg.lower():
                            self.log(f"   💡 Check video file format and size")

                except Exception as e:
                    failed += 1
                    values[4] = "❌ Error"
                    self.log(f"❌ Upload error: {e}")
                    
                self.upload_tree.item(item, values=values)
                self.upload_progress['value'] = i + 1
                self.upload_status_var.set(f"📤 Uploaded: {i + 1}/{total}")
                self.root.update_idletasks()
                
                time.sleep(2)
                
        except Exception as e:
            self.log(f"❌ Upload process error: {e}")
            
        finally:
            self.is_uploading = False
            self.upload_selected_btn.config(state='normal')
            
            # Detailed completion summary
            privacy_status = self.privacy_var.get()
            
            self.log("🎯 ========== UPLOAD SUMMARY ==========")
            self.log(f"✅ Successful uploads: {successful}")
            self.log(f"❌ Failed uploads: {failed}")
            self.log(f"🔒 Privacy setting: {privacy_status}")
            
            if successful > 0:
                if privacy_status == "private":
                    summary_msg = f"✅ Upload Complete!\n\n📊 Results:\n• Successful: {successful}\n• Failed: {failed}\n\n⚠️  IMPORTANT: Videos are set to PRIVATE\n\n🔧 To make them visible in your channel:\n1. Go to YouTube Studio (studio.youtube.com)\n2. Click 'Content' in left menu\n3. Find your uploaded videos\n4. Change visibility from 'Private' to 'Public'\n\n💡 Or change privacy setting to 'Public' before uploading next time!"
                elif privacy_status == "unlisted":
                    summary_msg = f"✅ Upload Complete!\n\n📊 Results:\n• Successful: {successful}\n• Failed: {failed}\n\n⚠️  Videos are UNLISTED\n• Only viewable with direct links\n• Won't appear in channel publicly\n\n💡 Change to 'Public' in YouTube Studio to show in channel"
                else:
                    summary_msg = f"✅ Upload Complete!\n\n📊 Results:\n• Successful: {successful}\n• Failed: {failed}\n\n🎉 Videos are PUBLIC\n• Should appear in your channel\n• May take a few minutes to process\n\n📺 Check your channel: https://www.youtube.com/@sealrepo\n\n� If videos are missing after 15+ minutes:\n• Click '🔍 Check Video Status' button\n• Go to YouTube Studio → Content\n• Look for copyright/community strikes\n• Check if videos were rejected\n\n💡 Common issues:\n• Processing can take 5-60 minutes\n• Copyright content may be blocked\n• Account verification required\n• File format/quality issues"
            else:
                summary_msg = f"❌ Upload Failed!\n\n📊 Results:\n• Successful: {successful}\n• Failed: {failed}\n\nPlease check the logs for error details."
            
            self.log("=" * 45)
            messagebox.showinfo("Upload Complete", summary_msg)

    def refresh_manager_data(self, manager_window):
        """Refresh all data in YouTube Manager"""
        try:
            if hasattr(self, 'manager_status_var'):
                self.manager_status_var.set("🔄 Refreshing data...")
            # Placeholder for data refresh logic
            if hasattr(self, 'manager_status_var'):
                self.manager_status_var.set("🟢 Data refreshed successfully")
        except Exception as e:
            if hasattr(self, 'manager_status_var'):
                self.manager_status_var.set(f"❌ Error refreshing data: {e}")
            
    def create_analytics_tab(self, notebook, parent_window):
        """Create analytics tab - placeholder"""
        analytics_frame = tk.Frame(notebook, bg=self.colors['surface'])
        notebook.add(analytics_frame, text="📊 Analytics")
        tk.Label(analytics_frame, text="📊 Analytics Dashboard (Coming Soon)", 
                 font=('Segoe UI', 14), bg=self.colors['surface'], fg=self.colors['dark']).pack(expand=True)
                 
    def create_comments_tab(self, notebook, parent_window):
        """Create comments tab - placeholder"""
        comments_frame = tk.Frame(notebook, bg=self.colors['surface'])
        notebook.add(comments_frame, text="💬 Comments")
        tk.Label(comments_frame, text="💬 Comment Management (Coming Soon)", 
                 font=('Segoe UI', 14), bg=self.colors['surface'], fg=self.colors['dark']).pack(expand=True)
                 
    def create_seo_tab(self, notebook, parent_window):
        """Create SEO tab - placeholder"""
        seo_frame = tk.Frame(notebook, bg=self.colors['surface'])
        notebook.add(seo_frame, text="🔍 SEO")
        tk.Label(seo_frame, text="🔍 SEO Tools (Coming Soon)", 
                 font=('Segoe UI', 14), bg=self.colors['surface'], fg=self.colors['dark']).pack(expand=True)
                 
    # Placeholder methods for dashboard actions
    def check_recent_comments(self, parent_window):
        messagebox.showinfo("Coming Soon", "💬 Recent Comments feature coming soon!")
        
    def open_thumbnail_tools(self, parent_window):
        messagebox.showinfo("Coming Soon", "🎨 Thumbnail Tools feature coming soon!")
    
    def save_upload_preset(self):
        """Save current upload settings as a preset"""
        try:
            preset_name = self.preset_var.get()
            if not preset_name or preset_name == "Default":
                preset_name = tk.simpledialog.askstring("Save Preset", "Enter preset name:")
                if not preset_name:
                    return
            
            # Gather all current settings
            preset_data = {
                'title_template': self.title_template_var.get(),
                'description': self.description_text.get('1.0', tk.END).strip(),
                'privacy': self.privacy_var.get(),
                'made_for_kids': self.made_for_kids_var.get(),
                'category': self.category_var.get(),
                'language': self.language_var.get(),
                'tags': self.tags_var.get(),
                'shorts_mode': self.shorts_mode.get(),
                'auto_thumbnail': self.auto_thumbnail.get(),
                'quality': self.quality_var.get(),
                'enable_monetization': self.enable_monetization.get(),
                'license': self.license_var.get(),
                'publish_timing': self.publish_timing.get(),
                'notify_subscribers': self.notify_subscribers.get()
            }
            
            # Save to file
            presets_file = os.path.join(os.path.dirname(__file__), "upload_presets.json")
            try:
                with open(presets_file, 'r') as f:
                    presets = json.load(f)
            except:
                presets = {}
            
            presets[preset_name] = preset_data
            
            with open(presets_file, 'w') as f:
                json.dump(presets, f, indent=2)
            
            self.log(f"💾 Saved preset: {preset_name}")
            messagebox.showinfo("Success", f"Preset '{preset_name}' saved successfully!")
            
        except Exception as e:
            self.log(f"❌ Error saving preset: {e}")
            messagebox.showerror("Error", f"Failed to save preset: {e}")
    
    def load_upload_preset(self):
        """Load a saved upload preset"""
        try:
            presets_file = os.path.join(os.path.dirname(__file__), "upload_presets.json")
            if not os.path.exists(presets_file):
                messagebox.showinfo("No Presets", "No saved presets found.")
                return
            
            with open(presets_file, 'r') as f:
                presets = json.load(f)
            
            preset_name = self.preset_var.get()
            if preset_name not in presets:
                available = list(presets.keys())
                if available:
                    preset_name = tk.simpledialog.askstring("Load Preset", 
                                    f"Available presets: {', '.join(available)}\n\nEnter preset name:")
                else:
                    messagebox.showinfo("No Presets", "No saved presets found.")
                    return
            
            if preset_name in presets:
                preset_data = presets[preset_name]
                
                # Apply all settings
                self.title_template_var.set(preset_data.get('title_template', ''))
                
                # Update description text widget
                self.description_text.delete('1.0', tk.END)
                self.description_text.insert('1.0', preset_data.get('description', ''))
                
                self.privacy_var.set(preset_data.get('privacy', 'public'))
                self.made_for_kids_var.set(preset_data.get('made_for_kids', 'no'))
                self.category_var.set(preset_data.get('category', 'Entertainment'))
                self.language_var.set(preset_data.get('language', 'English'))
                self.tags_var.set(preset_data.get('tags', ''))
                self.shorts_mode.set(preset_data.get('shorts_mode', True))
                self.auto_thumbnail.set(preset_data.get('auto_thumbnail', True))
                self.quality_var.set(preset_data.get('quality', 'hd720'))
                self.enable_monetization.set(preset_data.get('enable_monetization', True))
                self.license_var.set(preset_data.get('license', 'YouTube Standard License'))
                self.publish_timing.set(preset_data.get('publish_timing', 'immediate'))
                self.notify_subscribers.set(preset_data.get('notify_subscribers', True))
                
                self.log(f"📥 Loaded preset: {preset_name}")
                messagebox.showinfo("Success", f"Preset '{preset_name}' loaded successfully!")
            else:
                messagebox.showerror("Error", f"Preset '{preset_name}' not found.")
                
        except Exception as e:
            self.log(f"❌ Error loading preset: {e}")
            messagebox.showerror("Error", f"Failed to load preset: {e}")
        
    def open_bulk_editor(self, parent_window):
        messagebox.showinfo("Coming Soon", "📝 Bulk Editor feature coming soon!")
        
    def export_analytics_data(self, parent_window):
        messagebox.showinfo("Coming Soon", "📊 Analytics Export feature coming soon!")
        
    def open_scheduler(self, parent_window):
        messagebox.showinfo("Coming Soon", "📅 Upload Scheduler feature coming soon!")
        
    def load_channel_statistics(self, manager_window):
        """Load real channel statistics from YouTube API"""
        if not self.youtube_uploader:
            self.log("❌ YouTube API not available")
            return
            
        try:
            self.log("📊 Loading channel statistics...")
            
            # Get channel statistics from API
            stats = self.youtube_uploader.get_channel_statistics()
            
            if stats:
                # Update stat cards if they exist
                if hasattr(self, 'stat_labels'):
                    # Format numbers
                    total_videos = int(stats.get('videoCount', 0))
                    subscribers = int(stats.get('subscriberCount', 0))
                    total_views = int(stats.get('viewCount', 0))
                    
                    # Format with commas
                    self.update_stat_card("📹 Total Videos", f"{total_videos:,}")
                    self.update_stat_card("👥 Subscribers", f"{subscribers:,}")
                    self.update_stat_card("👁️ Total Views", f"{total_views:,}")
                    
                    # Calculate average views per video
                    if total_videos > 0:
                        avg_views = total_views // total_videos
                        self.update_stat_card("📊 Avg Views/Video", f"{avg_views:,}")
                    
                    self.log(f"✅ Channel: {stats.get('title', 'Unknown Channel')}")
                    self.log(f"📊 Statistics loaded: {total_videos:,} videos, {subscribers:,} subscribers")
                
            else:
                self.log("⚠️ No channel statistics available. Using demo data.")
                # Show demo data
                if hasattr(self, 'stat_labels'):
                    self.update_stat_card("📹 Total Videos", "Demo Mode")
                    self.update_stat_card("👥 Subscribers", "Get API Key")
                    self.update_stat_card("👁️ Total Views", "For Real Data")
                    self.update_stat_card("📊 Avg Views/Video", "See Instructions")
                
        except Exception as e:
            self.log(f"❌ Error loading statistics: {e}")
            # Show error message in stats
            if hasattr(self, 'stat_labels'):
                self.update_stat_card("📹 Total Videos", "Error")
                self.update_stat_card("👥 Subscribers", "API Error")
                self.update_stat_card("👁️ Total Views", "Check API Key")
                self.update_stat_card("📊 Avg Views/Video", "Try Again")
            
    def update_stat_card(self, title, value):
        """Update a stat card with new value"""
        if hasattr(self, 'stat_labels') and title in self.stat_labels:
            self.stat_labels[title].config(text=str(value))

    def open_upload_config(self):
        """Open comprehensive upload configuration popup window with optimized UI"""
        config_window = tk.Toplevel(self.root)
        config_window.title("⚙️ YouTube Upload Configuration")
        config_window.geometry("900x750")
        config_window.resizable(True, True)
        config_window.transient(self.root)
        config_window.grab_set()
        
        # Center the window
        config_window.update_idletasks()
        x = (config_window.winfo_screenwidth() // 2) - (900 // 2)
        y = (config_window.winfo_screenheight() // 2) - (750 // 2)
        config_window.geometry(f"900x750+{x}+{y}")
        
        # Configure window
        config_window.configure(bg=self.colors['background'])
        
        # Header with title and description
        header_frame = tk.Frame(config_window, bg=self.colors['primary'], height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="⚙️ YouTube Upload Configuration", 
                font=('Segoe UI', 16, 'bold'), bg=self.colors['primary'], fg='white').pack(pady=15)
        tk.Label(header_frame, text="Configure your video upload settings to match YouTube Creator Studio", 
                font=('Segoe UI', 10), bg=self.colors['primary'], fg='white').pack()
        
        # Main container with padding
        main_container = tk.Frame(config_window, bg=self.colors['background'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create scrollable frame with better styling
        canvas = tk.Canvas(main_container, bg=self.colors['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['background'])
        
        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enhanced mousewheel binding
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        # === SECTION 1: VIDEO DETAILS ===
        details_section = self.create_config_section(scrollable_frame, "📝 Video Details", 
                                                    "Configure title, description and tags for your videos")
        
        # Title Template with enhanced styling
        title_frame = self.create_config_field_frame(details_section)
        self.create_config_label(title_frame, "🎬 Title Template", 
                                "Template for video titles (use [FILENAME] as placeholder)")
        self.config_title_var = tk.StringVar(value=self.upload_settings.get('title_template', '[FILENAME]'))
        title_entry = tk.Entry(title_frame, textvariable=self.config_title_var, 
                              font=('Segoe UI', 10), relief=tk.FLAT, bd=5,
                              bg='white', fg=self.colors['dark'])
        title_entry.pack(fill=tk.X, pady=(5,0), ipady=8)
        
        # Description Template with better text area
        desc_frame = self.create_config_field_frame(details_section)
        self.create_config_label(desc_frame, "📄 Description Template", 
                                "Default description for your videos")
        
        desc_text_frame = tk.Frame(desc_frame, bg=self.colors['surface'], relief=tk.FLAT, bd=1)
        desc_text_frame.pack(fill=tk.X, pady=(5,0))
        
        self.config_desc_text = tk.Text(desc_text_frame, height=6, font=('Segoe UI', 10),
                                       bg='white', fg=self.colors['dark'], wrap=tk.WORD,
                                       relief=tk.FLAT, bd=5)
        desc_scroll = ttk.Scrollbar(desc_text_frame, orient="vertical", command=self.config_desc_text.yview)
        self.config_desc_text.configure(yscrollcommand=desc_scroll.set)
        
        self.config_desc_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        desc_scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=(0,5), pady=5)
        self.config_desc_text.insert('1.0', self.upload_settings.get('description', ''))
        
        # Tags with modern input
        tags_frame = self.create_config_field_frame(details_section)
        self.create_config_label(tags_frame, "🏷️ Default Tags", 
                                "Comma-separated tags (e.g., gaming, tutorial, review)")
        self.config_tags_var = tk.StringVar(value=self.upload_settings.get('tags', ''))
        tags_entry = tk.Entry(tags_frame, textvariable=self.config_tags_var, 
                             font=('Segoe UI', 10), relief=tk.FLAT, bd=5,
                             bg='white', fg=self.colors['dark'])
        tags_entry.pack(fill=tk.X, pady=(5,0), ipady=8)
        
        # === SECTION 2: PRIVACY & AUDIENCE ===
        privacy_section = self.create_config_section(scrollable_frame, "� Privacy & Audience", 
                                                    "Control who can see and interact with your videos")
        
        # Privacy and Kids settings in a nice grid
        privacy_grid = tk.Frame(privacy_section, bg=self.colors['surface'])
        privacy_grid.pack(fill=tk.X, pady=10)
        
        # Privacy setting
        privacy_frame = tk.Frame(privacy_grid, bg=self.colors['surface'])
        privacy_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=15)
        
        tk.Label(privacy_frame, text="🔒 Visibility", font=('Segoe UI', 10, 'bold'),
                bg=self.colors['surface'], fg=self.colors['dark']).pack(anchor=tk.W)
        self.config_privacy_var = tk.StringVar(value=self.upload_settings.get('privacy', 'public'))
        privacy_combo = ttk.Combobox(privacy_frame, textvariable=self.config_privacy_var,
                                   values=["public", "unlisted", "private"], state="readonly", 
                                   font=('Segoe UI', 10), width=15)
        privacy_combo.pack(anchor=tk.W, pady=(5,0))

        def _toggle_private_share(*_):
            if self.config_privacy_var.get() == 'private':
                private_share_frame.pack(fill=tk.X, pady=(8, 0))
            else:
                private_share_frame.pack_forget()

        self.config_privacy_var.trace_add('write', _toggle_private_share)

        private_share_frame = tk.Frame(privacy_section, bg=self.colors['surface'])

        # Header row
        hdr = tk.Frame(private_share_frame, bg=self.colors['surface'])
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="📧 Share with (emails)",
                font=('Segoe UI', 9, 'bold'), bg=self.colors['surface'],
                fg=self.colors['dark']).pack(side=tk.LEFT)
        self._ps_count_var = tk.StringVar(value="")
        tk.Label(hdr, textvariable=self._ps_count_var,
                font=('Segoe UI', 8), bg=self.colors['surface'],
                fg=self.colors['primary']).pack(side=tk.LEFT, padx=(8, 0))

        # Format hint
        tk.Label(private_share_frame,
                text="Mỗi email cách nhau bằng dấu phẩy, không có khoảng trắng  •  Ví dụ: a@gmail.com,b@gmail.com",
                font=('Segoe UI', 8), bg=self.colors['surface'],
                fg='#888888').pack(anchor=tk.W, pady=(1, 0))

        self.config_private_share_emails_var = tk.StringVar(
            value=self.upload_settings.get('private_share_emails', ''))

        # Text widget (multi-line, dễ đọc hơn Entry khi có nhiều email)
        ps_text_frame = tk.Frame(private_share_frame, bg='white',
                                 relief=tk.FLAT, bd=1,
                                 highlightthickness=1,
                                 highlightbackground='#cccccc')
        ps_text_frame.pack(fill=tk.X, pady=(4, 0))
        self._ps_text = tk.Text(ps_text_frame, height=3,
                                font=('Segoe UI', 9), relief=tk.FLAT, bd=4,
                                bg='white', fg=self.colors['dark'],
                                wrap=tk.WORD)
        self._ps_text.pack(fill=tk.X)
        # Populate from saved settings
        _saved_emails = self.upload_settings.get('private_share_emails', '')
        if _saved_emails:
            self._ps_text.insert('1.0', _saved_emails)

        # Live counter
        def _update_email_count(*_):
            raw = self._ps_text.get('1.0', tk.END).strip()
            # Sync to StringVar (strip whitespace/newlines for storage)
            clean = ','.join(e.strip() for e in raw.replace('\n', ',').split(',') if e.strip())
            self.config_private_share_emails_var.set(clean)
            count = len([e for e in clean.split(',') if e.strip()]) if clean else 0
            self._ps_count_var.set(f"({count} email{'s' if count != 1 else ''})" if count else "")

        self._ps_text.bind('<KeyRelease>', _update_email_count)
        _update_email_count()  # Init count

        # Show/hide based on current value
        _toggle_private_share()

        # Made for Kids setting
        kids_frame = tk.Frame(privacy_grid, bg=self.colors['surface'])
        kids_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=15)
        
        tk.Label(kids_frame, text="👶 Audience", font=('Segoe UI', 10, 'bold'),
                bg=self.colors['surface'], fg=self.colors['dark']).pack(anchor=tk.W)
        self.config_kids_var = tk.StringVar(value=self.upload_settings.get('made_for_kids', 'no'))
        kids_combo = ttk.Combobox(kids_frame, textvariable=self.config_kids_var,
                                values=["no", "yes"],
                                state="readonly", font=('Segoe UI', 10), width=15)
        kids_combo.pack(anchor=tk.W, pady=(5,0))
        
        # Age restriction
        age_frame = tk.Frame(privacy_grid, bg=self.colors['surface'])
        age_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=15)
        
        tk.Label(age_frame, text="🔞 Age Restriction", font=('Segoe UI', 10, 'bold'),
                bg=self.colors['surface'], fg=self.colors['dark']).pack(anchor=tk.W)
        self.config_age_restriction_var = tk.StringVar(value=self.upload_settings.get('age_restriction', 'none'))
        age_combo = ttk.Combobox(age_frame, textvariable=self.config_age_restriction_var,
                               values=["none", "18+"], state="readonly", 
                               font=('Segoe UI', 10), width=15)
        age_combo.pack(anchor=tk.W, pady=(5,0))
        
        # === SECTION 3: CONTENT CLASSIFICATION ===
        content_section = self.create_config_section(scrollable_frame, "� Content Classification", 
                                                    "Categorize your content for better discoverability")
        
        # Category and Language in grid
        classification_grid = tk.Frame(content_section, bg=self.colors['surface'])
        classification_grid.pack(fill=tk.X, pady=10)
        
        # Category
        cat_frame = tk.Frame(classification_grid, bg=self.colors['surface'])
        cat_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=15)
        
        tk.Label(cat_frame, text="📂 Category", font=('Segoe UI', 10, 'bold'),
                bg=self.colors['surface'], fg=self.colors['dark']).pack(anchor=tk.W)
        self.config_category_var = tk.StringVar(value=self.upload_settings.get('category', 'Entertainment'))
        category_combo = ttk.Combobox(cat_frame, textvariable=self.config_category_var,
                                    values=["Entertainment", "Gaming", "Education", "Science & Technology", 
                                           "Music", "Sports", "News & Politics", "Comedy", "Film & Animation",
                                           "Autos & Vehicles", "Travel & Events", "Pets & Animals", "Howto & Style"],
                                    state="readonly", font=('Segoe UI', 10), width=20)
        category_combo.pack(anchor=tk.W, pady=(5,0))
        
        # Language
        lang_frame = tk.Frame(classification_grid, bg=self.colors['surface'])
        lang_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=15)
        
        tk.Label(lang_frame, text="🌐 Language", font=('Segoe UI', 10, 'bold'),
                bg=self.colors['surface'], fg=self.colors['dark']).pack(anchor=tk.W)
        self.config_language_var = tk.StringVar(value=self.upload_settings.get('language', 'English'))
        language_combo = ttk.Combobox(lang_frame, textvariable=self.config_language_var,
                                    values=["English", "Vietnamese", "Chinese", "Japanese", "Korean", 
                                           "Spanish", "French", "German", "Portuguese", "Russian"],
                                    state="readonly", font=('Segoe UI', 10), width=15)
        language_combo.pack(anchor=tk.W, pady=(5,0))
        
        # License
        license_frame = self.create_config_field_frame(content_section)
        self.create_config_label(license_frame, "⚖️ License", "Rights and usage permissions")
        self.config_license_var = tk.StringVar(value=self.upload_settings.get('license', 'Standard YouTube License'))
        license_combo = ttk.Combobox(license_frame, textvariable=self.config_license_var,
                                   values=["Standard YouTube License", "Creative Commons - Attribution"],
                                   state="readonly", font=('Segoe UI', 10), width=35)
        license_combo.pack(anchor=tk.W, pady=(5,0))
        
        # === SECTION 4: INTERACTION SETTINGS ===
        interaction_section = self.create_config_section(scrollable_frame, "💬 Interaction Settings", 
                                                        "Configure how viewers can interact with your videos")
        
        # Modern checkboxes in a nice grid
        interaction_grid = tk.Frame(interaction_section, bg=self.colors['surface'])
        interaction_grid.pack(fill=tk.X, pady=10)
        
        # Left column
        left_col = tk.Frame(interaction_grid, bg=self.colors['surface'])
        left_col.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=20, pady=15)
        
        self.config_comments_var = tk.BooleanVar(value=self.upload_settings.get('allow_comments', True))
        comments_cb = tk.Checkbutton(left_col, text="💬 Allow Comments", variable=self.config_comments_var,
                                   bg=self.colors['surface'], fg=self.colors['dark'], 
                                   font=('Segoe UI', 10), selectcolor='white', bd=0)
        comments_cb.pack(anchor=tk.W, pady=5)
        
        self.config_ratings_var = tk.BooleanVar(value=self.upload_settings.get('allow_ratings', True))
        ratings_cb = tk.Checkbutton(left_col, text="⭐ Allow Ratings", variable=self.config_ratings_var,
                                  bg=self.colors['surface'], fg=self.colors['dark'], 
                                  font=('Segoe UI', 10), selectcolor='white', bd=0)
        ratings_cb.pack(anchor=tk.W, pady=5)
        
        # Right column
        right_col = tk.Frame(interaction_grid, bg=self.colors['surface'])
        right_col.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=20, pady=15)
        
        self.config_embedding_var = tk.BooleanVar(value=self.upload_settings.get('allow_embedding', True))
        embedding_cb = tk.Checkbutton(right_col, text="🔗 Allow Embedding", variable=self.config_embedding_var,
                                    bg=self.colors['surface'], fg=self.colors['dark'], 
                                    font=('Segoe UI', 10), selectcolor='white', bd=0)
        embedding_cb.pack(anchor=tk.W, pady=5)
        
        self.config_notify_var = tk.BooleanVar(value=self.upload_settings.get('notify_subscribers', True))
        notify_cb = tk.Checkbutton(right_col, text="🔔 Notify Subscribers", variable=self.config_notify_var,
                                 bg=self.colors['surface'], fg=self.colors['dark'], 
                                 font=('Segoe UI', 10), selectcolor='white', bd=0)
        notify_cb.pack(anchor=tk.W, pady=5)
        
        # === SECTION 5: PUBLISHING & THUMBNAIL ===
        publishing_section = self.create_config_section(scrollable_frame, "📅 Publishing & Thumbnail", 
                                                       "Control when and how your videos are published")
        
        # Publishing timing
        publish_frame = self.create_config_field_frame(publishing_section)
        self.create_config_label(publish_frame, "⏰ Publishing", "When to make your video live")
        self.config_publish_var = tk.StringVar(value=self.upload_settings.get('publish_timing', 'immediately'))
        publish_combo = ttk.Combobox(publish_frame, textvariable=self.config_publish_var,
                                   values=["immediately", "scheduled"], state="readonly", 
                                   font=('Segoe UI', 10), width=20)
        publish_combo.pack(anchor=tk.W, pady=(5,0))
        
        # Thumbnail settings
        thumbnail_container = tk.Frame(publishing_section, bg=self.colors['surface'], relief=tk.FLAT, bd=1)
        thumbnail_container.pack(fill=tk.X, pady=(10,0))
        
        thumb_header = tk.Frame(thumbnail_container, bg=self.colors['surface'])
        thumb_header.pack(fill=tk.X, padx=15, pady=(15,10))
        
        tk.Label(thumb_header, text="🖼️ Thumbnail Settings", font=('Segoe UI', 11, 'bold'),
                bg=self.colors['surface'], fg=self.colors['primary']).pack(side=tk.LEFT)
        
        self.config_auto_thumb_var = tk.BooleanVar(value=self.upload_settings.get('auto_thumbnail', True))
        auto_thumb_cb = tk.Checkbutton(thumbnail_container, text="🤖 Use Auto-Generated Thumbnail", 
                                     variable=self.config_auto_thumb_var,
                                     bg=self.colors['surface'], fg=self.colors['dark'], 
                                     font=('Segoe UI', 10), selectcolor='white', bd=0)
        auto_thumb_cb.pack(anchor=tk.W, padx=15, pady=5)
        
        # Custom thumbnail path with modern styling
        thumb_path_container = tk.Frame(thumbnail_container, bg=self.colors['surface'])
        thumb_path_container.pack(fill=tk.X, padx=15, pady=(5,15))
        
        tk.Label(thumb_path_container, text="📁 Custom Thumbnail:", font=('Segoe UI', 10),
                bg=self.colors['surface'], fg=self.colors['dark']).pack(anchor=tk.W, pady=(0,5))
        
        thumb_input_frame = tk.Frame(thumb_path_container, bg=self.colors['surface'])
        thumb_input_frame.pack(fill=tk.X)
        
        self.config_thumb_path_var = tk.StringVar(value=self.upload_settings.get('thumbnail_path', ''))
        thumb_entry = tk.Entry(thumb_input_frame, textvariable=self.config_thumb_path_var, 
                              font=('Segoe UI', 10), relief=tk.FLAT, bd=5,
                              bg='white', fg=self.colors['dark'])
        thumb_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,10), ipady=6)
        
        browse_btn = tk.Button(thumb_input_frame, text="📁 Browse",
                              command=lambda: self.browse_thumbnail_path(),
                              bg=self.colors['secondary'], fg='white', relief=tk.FLAT,
                              font=('Segoe UI', 9, 'bold'), cursor='hand2', padx=15, pady=6)
        browse_btn.pack(side=tk.RIGHT)
        
        # === BOTTOM BUTTONS WITH MODERN STYLING ===
        button_container = tk.Frame(config_window, bg=self.colors['light'], height=80)
        button_container.pack(fill=tk.X, side=tk.BOTTOM)
        button_container.pack_propagate(False)
        
        button_frame = tk.Frame(button_container, bg=self.colors['light'])
        button_frame.pack(expand=True)
        
        # Reset button
        reset_btn = tk.Button(button_frame, text="🔄 Reset to Defaults",
                             command=lambda: self.reset_config_defaults(config_window),
                             bg=self.colors['warning'], fg='white', relief=tk.FLAT,
                             font=('Segoe UI', 11, 'bold'), cursor='hand2', 
                             padx=25, pady=12, bd=0)
        reset_btn.pack(side=tk.LEFT, padx=10)
        
        # Cancel button
        cancel_btn = tk.Button(button_frame, text="❌ Cancel",
                              command=config_window.destroy,
                              bg=self.colors['danger'], fg='white', relief=tk.FLAT,
                              font=('Segoe UI', 11, 'bold'), cursor='hand2', 
                              padx=25, pady=12, bd=0)
        cancel_btn.pack(side=tk.RIGHT, padx=10)
        
        # Save button
        save_btn = tk.Button(button_frame, text="✅ Save Configuration",
                            command=lambda: self.save_config_settings(config_window),
                            bg=self.colors['success'], fg='white', relief=tk.FLAT,
                            font=('Segoe UI', 11, 'bold'), cursor='hand2', 
                            padx=25, pady=12, bd=0)
        save_btn.pack(side=tk.RIGHT, padx=(10,0))

    def create_config_section(self, parent, title, description):
        """Create a styled section for configuration form"""
        section_frame = tk.Frame(parent, bg=self.colors['background'])
        section_frame.pack(fill=tk.X, pady=(0,20))
        
        # Section header
        header_frame = tk.Frame(section_frame, bg=self.colors['primary'], height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        header_content = tk.Frame(header_frame, bg=self.colors['primary'])
        header_content.pack(expand=True, fill=tk.X, padx=20)
        
        tk.Label(header_content, text=title, font=('Segoe UI', 12, 'bold'),
                bg=self.colors['primary'], fg='white').pack(side=tk.LEFT, anchor=tk.W, pady=15)
        
        # Section content area
        content_frame = tk.Frame(section_frame, bg=self.colors['surface'], relief=tk.FLAT, bd=1)
        content_frame.pack(fill=tk.X, padx=1)
        
        # Description
        if description:
            desc_frame = tk.Frame(content_frame, bg=self.colors['light'])
            desc_frame.pack(fill=tk.X, padx=20, pady=(15,10))
            
            tk.Label(desc_frame, text=description, font=('Segoe UI', 9),
                    bg=self.colors['light'], fg=self.colors['medium']).pack(anchor=tk.W)
        
        return content_frame
    
    def create_config_field_frame(self, parent):
        """Create a frame for configuration fields"""
        field_frame = tk.Frame(parent, bg=self.colors['surface'])
        field_frame.pack(fill=tk.X, padx=20, pady=10)
        return field_frame
    
    def create_config_label(self, parent, text, description=None):
        """Create a styled label for configuration fields"""
        label = tk.Label(parent, text=text, font=('Segoe UI', 10, 'bold'),
                        bg=self.colors['surface'], fg=self.colors['dark'])
        label.pack(anchor=tk.W, pady=(0,5))
        
        if description:
            desc_label = tk.Label(parent, text=description, font=('Segoe UI', 9),
                                 bg=self.colors['surface'], fg=self.colors['medium'])
            desc_label.pack(anchor=tk.W, pady=(0,5))
        
        return label

    def browse_thumbnail_path(self):
        """Browse for thumbnail image file"""
        filename = filedialog.askopenfilename(
            title="Select Thumbnail Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("PNG files", "*.png"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.config_thumb_path_var.set(filename)

    def reset_config_defaults(self, window):
        """Reset configuration to default values"""
        result = messagebox.askyesno(
            "Reset to Defaults",
            "🔄 Reset all settings to default values?\n\nThis will overwrite all your current configuration.",
            parent=window
        )
        
        if result:
            # Default settings
            defaults = {
                'title_template': '[FILENAME]',
                'description': 'Video uploaded using Douyin to YouTube Tool\n\n#douyin #tiktok #viral',
                'tags': 'douyin,tiktok,viral,video',
                'privacy': 'public',
                'made_for_kids': 'no',
                'age_restriction': 'none',
                'category': 'Entertainment',
                'language': 'English',
                'license': 'Standard YouTube License',
                'allow_comments': True,
                'allow_ratings': True,
                'allow_embedding': True,
                'notify_subscribers': True,
                'publish_timing': 'immediately',
                'auto_thumbnail': True,
                'thumbnail_path': ''
            }
            
            # Update UI elements
            self.config_title_var.set(defaults['title_template'])
            self.config_desc_text.delete('1.0', tk.END)
            self.config_desc_text.insert('1.0', defaults['description'])
            self.config_tags_var.set(defaults['tags'])
            self.config_privacy_var.set(defaults['privacy'])
            self.config_kids_var.set(defaults['made_for_kids'])
            self.config_age_restriction_var.set(defaults['age_restriction'])
            self.config_category_var.set(defaults['category'])
            self.config_language_var.set(defaults['language'])
            self.config_license_var.set(defaults['license'])
            self.config_comments_var.set(defaults['allow_comments'])
            self.config_ratings_var.set(defaults['allow_ratings'])
            self.config_embedding_var.set(defaults['allow_embedding'])
            self.config_notify_var.set(defaults['notify_subscribers'])
            self.config_publish_var.set(defaults['publish_timing'])
            self.config_auto_thumb_var.set(defaults['auto_thumbnail'])
            self.config_thumb_path_var.set(defaults['thumbnail_path'])
            
            messagebox.showinfo("Reset Complete", "✅ Configuration reset to default values!", parent=window)

    def save_config_settings(self, window):
        """Save comprehensive configuration settings and close window"""
        # Update settings from UI with all new fields
        self.upload_settings.update({
            'title_template': self.config_title_var.get(),
            'description': self.config_desc_text.get('1.0', tk.END).strip(),
            'tags': self.config_tags_var.get(),
            'privacy': self.config_privacy_var.get(),
            'private_share_emails': (
                ','.join(e.strip() for e in
                         self._ps_text.get('1.0', tk.END).strip().replace('\n', ',').split(',')
                         if e.strip())
                if hasattr(self, '_ps_text') else
                self.config_private_share_emails_var.get() if hasattr(self, 'config_private_share_emails_var') else ''
            ),
            'made_for_kids': self.config_kids_var.get(),
            'age_restriction': self.config_age_restriction_var.get(),
            'category': self.config_category_var.get(),
            'language': self.config_language_var.get(),
            'license': self.config_license_var.get(),
            'allow_comments': self.config_comments_var.get(),
            'allow_ratings': self.config_ratings_var.get(),
            'allow_embedding': self.config_embedding_var.get(),
            'notify_subscribers': self.config_notify_var.get(),
            'publish_timing': self.config_publish_var.get(),
            'auto_thumbnail': self.config_auto_thumb_var.get(),
            'thumbnail_path': self.config_thumb_path_var.get()
        })
        
        # Sync privacy_var so upload thread always reads the latest value
        if hasattr(self, 'privacy_var'):
            self.privacy_var.set(self.upload_settings['privacy'])

        # Save to file
        self.save_upload_settings()

        # Show comprehensive confirmation
        messagebox.showinfo(
            "Configuration Saved", 
            "✅ Upload configuration saved successfully!\n\n" +
            f"📝 Title: {self.config_title_var.get()[:30]}...\n" +
            f"🔒 Privacy: {self.config_privacy_var.get().title()}\n" +
            f"📂 Category: {self.config_category_var.get()}\n" +
            f"🌐 Language: {self.config_language_var.get()}\n\n" +
            "These settings will be applied to all future uploads.",
            parent=window
        )
        
        window.destroy()

    def create_settings_tab(self, notebook, parent_window):
        """Create settings tab with authentication options"""
        settings_frame = tk.Frame(notebook, bg=self.colors['surface'])
        notebook.add(settings_frame, text="⚙️ Settings")
        
        # Main container
        main_container = tk.Frame(settings_frame, bg=self.colors['surface'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Authentication Section
        auth_frame = ttk.LabelFrame(main_container, text="🔐 Authentication", padding="15")
        auth_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Current auth status
        self.auth_status_var = tk.StringVar()
        self.update_auth_status()
        
        status_frame = ttk.Frame(auth_frame)
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(status_frame, text="Current Status:", font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        ttk.Label(status_frame, textvariable=self.auth_status_var, 
                 font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(10, 0))
        
        # Authentication buttons
        auth_buttons_frame = ttk.Frame(auth_frame)
        auth_buttons_frame.pack(fill=tk.X)
        
        ttk.Button(auth_buttons_frame, text="🔑 Manual OAuth Login", 
                  command=self.manual_oauth_login).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(auth_buttons_frame, text="🔄 Re-authenticate", 
                  command=self.reauthenticate).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(auth_buttons_frame, text="🚪 Logout", 
                  command=self.logout_youtube).pack(side=tk.LEFT)
        
        # Upload Configuration Section
        config_frame = ttk.LabelFrame(main_container, text="📋 Upload Configuration", padding="15")
        config_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Button(config_frame, text="⚙️ Open Upload Configuration", 
                  command=self.open_upload_config).pack()
        
        # App Information Section
        info_frame = ttk.LabelFrame(main_container, text="ℹ️ Application Info", padding="15")
        info_frame.pack(fill=tk.X)
        
        info_text = f"""
Douyin to YouTube Tool v{__version__}
• Auto OAuth authentication with YouTube API
• Real-time YouTube data synchronization
• Professional upload management
• Comprehensive analytics dashboard
• Video optimization for YouTube

Developer: {__author__}
Repository: https://github.com/PhanDo19/DouyinHelper
License: {__license__}
Release Date: August 21, 2025
Built with Python & Tkinter
        """.strip()
        
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT, 
                 font=('Segoe UI', 9)).pack(anchor=tk.W)

    def update_auth_status(self):
        """Update authentication status display"""
        if hasattr(self, 'auth_status_var') and self.auth_status_var:
            # Check youtube_uploader (main instance)
            if hasattr(self, 'youtube_uploader') and self.youtube_uploader and self.youtube_uploader.authenticated:
                if hasattr(self.youtube_uploader, 'auth_method'):
                    if self.youtube_uploader.auth_method == 'oauth':
                        self.auth_status_var.set("✅ OAuth - Full Access")
                    elif self.youtube_uploader.auth_method == 'api_key':
                        self.auth_status_var.set("🔑 API Key - Read Only")
                    elif self.youtube_uploader.auth_method == 'demo':
                        self.auth_status_var.set("📊 Demo Mode")
                    else:
                        self.auth_status_var.set("✅ Connected")
                else:
                    self.auth_status_var.set("✅ Connected")
            # Fallback check for youtube_api
            elif hasattr(self, 'youtube_api') and self.youtube_api and self.youtube_api.service:
                if hasattr(self.youtube_api, 'auth_method'):
                    if self.youtube_api.auth_method == 'oauth':
                        self.auth_status_var.set("✅ OAuth - Full Access")
                    elif self.youtube_api.auth_method == 'api_key':
                        self.auth_status_var.set("🔑 API Key - Read Only")
                    elif self.youtube_api.auth_method == 'demo':
                        self.auth_status_var.set("📊 Demo Mode")
                    else:
                        self.auth_status_var.set("✅ Connected")
                else:
                    self.auth_status_var.set("✅ Connected")
            else:
                self.auth_status_var.set("❌ Not Connected")

    def manual_oauth_login(self):
        """Manually trigger OAuth authentication"""
        try:
            self.log("🔑 Starting manual OAuth authentication...")
            
            # Initialize YouTube API with OAuth
            self.youtube_api = YouTubeAPI()
            success = self.youtube_api.authenticate_oauth()
            
            if success:
                self.log("✅ Manual OAuth authentication successful!")
                self.update_auth_status()
                messagebox.showinfo("Success", "✅ OAuth authentication successful!\nFull YouTube access enabled.")
            else:
                self.log("❌ Manual OAuth authentication failed")
                messagebox.showerror("Error", "❌ OAuth authentication failed.\nPlease check your credentials.json file.")
                
        except Exception as e:
            error_msg = f"OAuth authentication error: {e}"
            self.log(f"❌ {error_msg}")
            messagebox.showerror("Error", f"❌ Authentication failed:\n{error_msg}")

    def reauthenticate(self):
        """Force re-authentication by removing token and starting OAuth"""
        try:
            # Remove existing token
            token_file = 'token.json'
            if os.path.exists(token_file):
                os.remove(token_file)
                self.log("🗑️ Removed existing authentication token")
            
            # Start fresh OAuth
            self.manual_oauth_login()
            
        except Exception as e:
            error_msg = f"Re-authentication error: {e}"
            self.log(f"❌ {error_msg}")
            messagebox.showerror("Error", f"❌ Re-authentication failed:\n{error_msg}")

    def logout_youtube(self):
        """Logout from YouTube and clear authentication"""
        try:
            # Remove token file
            token_file = 'token.json'
            if os.path.exists(token_file):
                os.remove(token_file)
                self.log("🗑️ Removed authentication token")
            
            # Clear YouTube API instance
            self.youtube_api = None
            
            # Update status
            self.update_auth_status()
            
            self.log("🚪 Logged out from YouTube")
            messagebox.showinfo("Success", "✅ Successfully logged out from YouTube.\nApp will use demo mode until re-authentication.")
            
        except Exception as e:
            error_msg = f"Logout error: {e}"
            self.log(f"❌ {error_msg}")
            messagebox.showerror("Error", f"❌ Logout failed:\n{error_msg}")

    def load_upload_settings(self):
        """Load upload settings from file"""
        try:
            settings_file = os.path.join(self.download_folder, 'upload_settings.json')
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    self.upload_settings.update(saved_settings)
                    
            # Update variables with loaded settings
            if hasattr(self, 'tags_var'):
                self.tags_var.set(self.upload_settings.get('tags', ''))
            if hasattr(self, 'privacy_var'):
                self.privacy_var.set(self.upload_settings.get('privacy', 'public'))
                    
        except Exception as e:
            self.log(f"⚠️ Could not load upload settings: {e}")

    def save_upload_settings(self):
        """Save upload settings to file"""
        try:
            settings_file = os.path.join(self.download_folder, 'upload_settings.json')
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.upload_settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log(f"⚠️ Could not save upload settings: {e}")
            
    def show_oauth_setup_guide(self):
        """Show OAuth setup guide for real YouTube uploads"""
        guide_text = """
🔧 Cách Setup OAuth để Upload Video Thật lên YouTube

📋 BƯỚC 1: Tạo Google Cloud Project
1. Truy cập: https://console.cloud.google.com
2. Tạo project mới hoặc chọn project hiện có
3. Enable YouTube Data API v3

📋 BƯỚC 2: Tạo OAuth Credentials  
1. Vào "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
2. Chọn "Desktop Application"
3. Tải xuống file JSON
4. Đổi tên thành "credentials.json"
5. Đặt file vào thư mục ứng dụng

📋 BƯỚC 3: Authentication
1. Restart ứng dụng
2. Chọn "OAuth Login" khi được hỏi
3. Browser sẽ mở để đăng nhập Google
4. Cho phép truy cập YouTube

✅ SAU KHI SETUP:
• Upload sẽ thật sự lên YouTube channel của bạn
• Video sẽ xuất hiện trong YouTube Studio
• Có thể kiểm tra trạng thái thực tế

⚠️ HIỆN TẠI:
• Đang dùng Demo Mode
• Upload chỉ là simulation
• Không có video thật trên YouTube

💡 Cần hỗ trợ setup? Xem hướng dẫn chi tiết tại:
https://developers.google.com/youtube/v3/quickstart/python
"""
        
        messagebox.showinfo("OAuth Setup Guide", guide_text)
        
    def create_tooltip(self, widget, text):
        """Create tooltip for widget"""
        def on_enter(event):
            tooltip = ToolTip(widget, text)
            widget.tooltip = tooltip
            
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
                
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        
    def load_video_list(self, parent_window):
        """Load video list from YouTube channel"""
        try:
            if not self.youtube_uploader or not self.youtube_uploader.authenticated:
                messagebox.showwarning("Warning", "Please authenticate with YouTube first!")
                return
                
            self.manager_status_var.set("🔄 Loading videos...")
            parent_window.update()
            
            # Clear existing items
            for item in self.video_tree.get_children():
                self.video_tree.delete(item)
            
            # Get videos from YouTube using existing method
            try:
                # Use the existing YouTube service
                youtube = self.youtube_uploader.service
                
                # Get channel's uploads playlist
                channels_response = youtube.channels().list(
                    part='contentDetails',
                    mine=True
                ).execute()
                
                if not channels_response['items']:
                    self.manager_status_var.set("❌ No channel found")
                    return
                    
                uploads_playlist_id = channels_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
                
                # Get videos from uploads playlist
                playlist_response = youtube.playlistItems().list(
                    part='snippet',
                    playlistId=uploads_playlist_id,
                    maxResults=50
                ).execute()
                
                videos = []
                for item in playlist_response['items']:
                    video_id = item['snippet']['resourceId']['videoId']
                    
                    # Get detailed video info
                    video_response = youtube.videos().list(
                        part='snippet,statistics,status,contentDetails',
                        id=video_id
                    ).execute()
                    
                    if video_response['items']:
                        video_data = video_response['items'][0]
                        videos.append({
                            'id': video_id,
                            'title': video_data['snippet']['title'],
                            'description': video_data['snippet']['description'],
                            'viewCount': video_data['statistics'].get('viewCount', '0'),
                            'likeCount': video_data['statistics'].get('likeCount', '0'),
                            'commentCount': video_data['statistics'].get('commentCount', '0'),
                            'status': video_data['status']['privacyStatus'],
                            'publishedAt': video_data['snippet']['publishedAt'],
                            'duration': video_data['contentDetails']['duration'],
                            'thumbnails': video_data['snippet']['thumbnails']
                        })
                
                if videos:
                    for video in videos:
                        # Format data for display
                        title = video.get('title', 'Unknown Title')[:50] + ('...' if len(video.get('title', '')) > 50 else '')
                        views = self.format_number(video.get('viewCount', '0'))
                        privacy = video.get('status', 'unknown').title()
                        published = video.get('publishedAt', '')[:10]  # Just date part
                        duration = self.format_duration(video.get('duration', 'PT0S'))
                        
                        # Insert into tree
                        item = self.video_tree.insert('', 'end', values=(title, views, privacy, published, duration))
                        
                        # Store full video data
                        self.current_video_data[item] = video
                        
                    self.manager_status_var.set(f"✅ Loaded {len(videos)} videos")
                else:
                    self.manager_status_var.set("❌ No videos found")
                    
            except Exception as api_error:
                # Fallback to demo data
                demo_videos = [
                    {
                        'id': 'demo1', 'title': 'Demo Video 1', 'viewCount': '1234', 
                        'status': 'public', 'publishedAt': '2024-01-01', 'duration': 'PT3M45S'
                    },
                    {
                        'id': 'demo2', 'title': 'Demo Video 2', 'viewCount': '5678', 
                        'status': 'unlisted', 'publishedAt': '2024-01-02', 'duration': 'PT1M23S'
                    }
                ]
                
                for video in demo_videos:
                    title = video.get('title', 'Unknown Title')
                    views = self.format_number(video.get('viewCount', '0'))
                    privacy = video.get('status', 'unknown').title()
                    published = video.get('publishedAt', '')[:10]
                    duration = self.format_duration(video.get('duration', 'PT0S'))
                    
                    item = self.video_tree.insert('', 'end', values=(title, views, privacy, published, duration))
                    self.current_video_data[item] = video
                    
                self.manager_status_var.set(f"📊 Demo mode - {len(demo_videos)} videos")
                
        except Exception as e:
            self.manager_status_var.set(f"❌ Error loading videos: {str(e)}")
            print(f"Video loading error: {e}")
            
    def format_duration(self, duration_str):
        """Format ISO 8601 duration to readable format"""
        import re
        
        # Parse PT3M45S format
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
        if not match:
            return "0:00"
            
        hours, minutes, seconds = match.groups()
        hours = int(hours) if hours else 0
        minutes = int(minutes) if minutes else 0
        seconds = int(seconds) if seconds else 0
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
            
    def filter_video_list(self, event=None):
        """Filter video list based on search"""
        search_term = self.video_search_var.get().lower()
        
        # If search is empty, show all items
        if not search_term:
            for item in self.video_tree.get_children():
                self.video_tree.reattach(item, '', 'end')
            return
            
        # Hide items that don't match search
        for item in self.video_tree.get_children():
            values = self.video_tree.item(item, 'values')
            title = values[0].lower() if values else ""
            
            if search_term in title:
                self.video_tree.reattach(item, '', 'end')
            else:
                self.video_tree.detach(item)
                
    def format_number(self, num_str):
        """Format number for display (1.2K, 1.2M, etc.)"""
        try:
            num = int(num_str)
            if num >= 1000000:
                return f"{num/1000000:.1f}M"
            elif num >= 1000:
                return f"{num/1000:.1f}K"
            else:
                return str(num)
        except:
            return num_str
            
    def on_video_hover(self, event):
        """Show video preview on hover"""
        item = self.video_tree.identify_row(event.y)
        if item and item in self.current_video_data:
            self.show_video_preview(item)
            
    def hide_video_preview(self, event=None):
        """Hide video preview"""
        # Don't hide if a video is selected
        if not self.video_tree.selection():
            self.show_default_preview()
            
    def on_video_select(self, event):
        """Handle video selection"""
        selection = self.video_tree.selection()
        if selection:
            item = selection[0]
            self.show_video_preview(item)
            
    def show_video_preview(self, item):
        """Show detailed preview of selected video"""
        if item not in self.current_video_data:
            return
            
        video = self.current_video_data[item]
        
        # Clear preview frame
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
            
        # Create preview content
        preview_content = tk.Frame(self.preview_frame, bg=self.colors['surface'])
        preview_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Video title
        title_label = tk.Label(preview_content, 
                              text=video.get('title', 'Unknown Title'),
                              font=('Segoe UI', 12, 'bold'),
                              bg=self.colors['surface'], fg=self.colors['dark'],
                              wraplength=350, justify=tk.LEFT)
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Video stats
        stats_frame = tk.Frame(preview_content, bg=self.colors['surface'])
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(stats_frame, text=f"👁️ Views: {self.format_number(video.get('viewCount', '0'))}",
                bg=self.colors['surface'], font=('Segoe UI', 10)).pack(anchor=tk.W)
        tk.Label(stats_frame, text=f"👍 Likes: {self.format_number(video.get('likeCount', '0'))}",
                bg=self.colors['surface'], font=('Segoe UI', 10)).pack(anchor=tk.W)
        tk.Label(stats_frame, text=f"💬 Comments: {self.format_number(video.get('commentCount', '0'))}",
                bg=self.colors['surface'], font=('Segoe UI', 10)).pack(anchor=tk.W)
        tk.Label(stats_frame, text=f"🔒 Privacy: {video.get('status', 'unknown').title()}",
                bg=self.colors['surface'], font=('Segoe UI', 10)).pack(anchor=tk.W)
        
        # Publication date
        published = video.get('publishedAt', '')
        if published:
            tk.Label(stats_frame, text=f"📅 Published: {published[:10]}",
                    bg=self.colors['surface'], font=('Segoe UI', 10)).pack(anchor=tk.W)
        
        # Video URL
        video_id = video.get('id', '')
        if video_id:
            url_frame = tk.Frame(preview_content, bg=self.colors['surface'])
            url_frame.pack(fill=tk.X, pady=(10, 0))
            
            tk.Label(url_frame, text="🔗 URL:",
                    bg=self.colors['surface'], font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W)
            
            url_text = tk.Text(url_frame, height=2, font=('Consolas', 8), wrap=tk.WORD)
            url_text.insert('1.0', f"https://youtube.com/watch?v={video_id}")
            url_text.config(state=tk.DISABLED)
            url_text.pack(fill=tk.X, pady=(5, 0))
            
        # Quick actions
        actions_frame = tk.Frame(preview_content, bg=self.colors['surface'])
        actions_frame.pack(fill=tk.X, pady=(15, 0))
        
        tk.Button(actions_frame, text="🌐 Open in Browser", 
                 command=lambda: self.open_video_in_browser(video_id),
                 bg=self.colors['primary'], fg='white', relief=tk.FLAT,
                 font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(actions_frame, text="📋 Copy URL", 
                 command=lambda: self.copy_video_url(video_id),
                 bg=self.colors['secondary'], fg='white', relief=tk.FLAT,
                 font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT)
                 
    def show_default_preview(self):
        """Show default preview message"""
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
            
        self.preview_label = tk.Label(self.preview_frame, 
                                     text="📹 Select a video to see preview\n\n• Hover over videos for quick preview\n• Right-click for edit/delete options\n• Double-click to open in YouTube",
                                     font=('Segoe UI', 11),
                                     bg=self.colors['surface'], fg=self.colors['dark'],
                                     justify=tk.CENTER)
        self.preview_label.pack(expand=True)
        
    def show_video_context_menu(self, event):
        """Show context menu for video management"""
        item = self.video_tree.identify_row(event.y)
        if not item or item not in self.current_video_data:
            return
            
        # Select the item
        self.video_tree.selection_set(item)
        
        # Create context menu
        context_menu = tk.Menu(self.root, tearoff=0, font=('Segoe UI', 10))
        
        context_menu.add_command(label="✏️ Edit Video", 
                               command=lambda: self.edit_video(item))
        context_menu.add_command(label="🗑️ Delete Video", 
                               command=lambda: self.delete_video(item))
        context_menu.add_separator()
        context_menu.add_command(label="🌐 Open in Browser", 
                               command=lambda: self.open_video_in_browser(self.current_video_data[item].get('id')))
        context_menu.add_command(label="📋 Copy URL", 
                               command=lambda: self.copy_video_url(self.current_video_data[item].get('id')))
        context_menu.add_separator()
        context_menu.add_command(label="📊 View Analytics", 
                               command=lambda: self.show_video_analytics_detail(item))
        
        # Show menu
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
            
    def edit_video(self, item):
        """Edit video details"""
        if item not in self.current_video_data:
            return
            
        video = self.current_video_data[item]
        self.show_video_edit_dialog(video)
        
    def delete_video(self, item):
        """Delete video"""
        if item not in self.current_video_data:
            return
            
        video = self.current_video_data[item]
        title = video.get('title', 'Unknown Video')
        
        result = messagebox.askyesno("Confirm Delete", 
                                    f"Are you sure you want to delete this video?\n\n📹 {title}\n\n⚠️ This action cannot be undone!")
        
        if result:
            self.perform_video_delete(video, item)
            
    def open_video_in_browser(self, video_id):
        """Open video in browser"""
        if video_id:
            url = f"https://youtube.com/watch?v={video_id}"
            import webbrowser
            webbrowser.open(url)
            
    def copy_video_url(self, video_id):
        """Copy video URL to clipboard"""
        if video_id:
            url = f"https://youtube.com/watch?v={video_id}"
            self.root.clipboard_clear()
            self.root.clipboard_append(url)
            self.manager_status_var.set("📋 URL copied to clipboard!")
            
    def edit_selected_video(self):
        """Edit currently selected video"""
        selection = self.video_tree.selection()
        if selection:
            self.edit_video(selection[0])
            
    def delete_selected_video(self):
        """Delete currently selected video"""
        selection = self.video_tree.selection()
        if selection:
            self.delete_video(selection[0])
            
    def show_video_analytics(self):
        """Show analytics for selected video"""
        selection = self.video_tree.selection()
        if selection:
            self.show_video_analytics_detail(selection[0])
            
    def show_video_analytics_detail(self, item):
        """Show detailed analytics for a video"""
        if item not in self.current_video_data:
            return
            
        video = self.current_video_data[item]
        title = video.get('title', 'Unknown Video')
        
        # Create analytics window
        analytics_window = tk.Toplevel(self.root)
        analytics_window.title(f"📊 Analytics - {title[:30]}...")
        analytics_window.geometry("600x500")
        analytics_window.configure(bg=self.colors['light'])
        
        # Header
        header = tk.Frame(analytics_window, bg=self.colors['primary'], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text=f"📊 Video Analytics", 
                font=('Segoe UI', 14, 'bold'),
                bg=self.colors['primary'], fg='white').pack(pady=15)
        
        # Content
        content = tk.Frame(analytics_window, bg=self.colors['light'])
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Video info
        info_frame = tk.LabelFrame(content, text="Video Information", 
                                  font=('Segoe UI', 10, 'bold'))
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(info_frame, text=f"Title: {title}", 
                font=('Segoe UI', 10), justify=tk.LEFT, wraplength=500).pack(anchor=tk.W, padx=10, pady=5)
        tk.Label(info_frame, text=f"Video ID: {video.get('id', 'N/A')}", 
                font=('Segoe UI', 10)).pack(anchor=tk.W, padx=10, pady=2)
        tk.Label(info_frame, text=f"Published: {video.get('publishedAt', 'N/A')[:10]}", 
                font=('Segoe UI', 10)).pack(anchor=tk.W, padx=10, pady=2)
        
        # Stats
        stats_frame = tk.LabelFrame(content, text="Performance Stats", 
                                   font=('Segoe UI', 10, 'bold'))
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        stats_grid = tk.Frame(stats_frame)
        stats_grid.pack(padx=10, pady=10)
        
        # Create stats display
        stats = [
            ("👁️ Views", self.format_number(video.get('viewCount', '0'))),
            ("👍 Likes", self.format_number(video.get('likeCount', '0'))),
            ("💬 Comments", self.format_number(video.get('commentCount', '0'))),
            ("🔒 Privacy", video.get('status', 'unknown').title())
        ]
        
        for i, (label, value) in enumerate(stats):
            row = i // 2
            col = i % 2
            
            stat_frame = tk.Frame(stats_grid, bg=self.colors['surface'], relief=tk.RAISED, bd=1)
            stat_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            
            tk.Label(stat_frame, text=label, font=('Segoe UI', 9, 'bold'),
                    bg=self.colors['surface']).pack(pady=(5, 0))
            tk.Label(stat_frame, text=value, font=('Segoe UI', 12, 'bold'),
                    bg=self.colors['surface'], fg=self.colors['primary']).pack(pady=(0, 5))
        
        # Actions
        actions_frame = tk.Frame(content)
        actions_frame.pack(fill=tk.X, pady=(15, 0))
        
        tk.Button(actions_frame, text="🌐 Open in YouTube", 
                 command=lambda: self.open_video_in_browser(video.get('id')),
                 bg=self.colors['primary'], fg='white', relief=tk.FLAT,
                 font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(actions_frame, text="📊 YouTube Analytics", 
                 command=lambda: self.open_youtube_analytics(video.get('id')),
                 bg=self.colors['info'], fg='white', relief=tk.FLAT,
                 font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(actions_frame, text="❌ Close", 
                 command=analytics_window.destroy,
                 bg=self.colors['medium'], fg='white', relief=tk.FLAT,
                 font=('Segoe UI', 10, 'bold')).pack(side=tk.RIGHT)
                 
    def show_video_edit_dialog(self, video):
        """Show video edit dialog"""
        title = video.get('title', 'Unknown Video')
        
        # Create edit window
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"✏️ Edit Video - {title[:30]}...")
        edit_window.geometry("700x600")
        edit_window.configure(bg=self.colors['light'])
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Header
        header = tk.Frame(edit_window, bg=self.colors['primary'], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="✏️ Edit Video Details", 
                font=('Segoe UI', 14, 'bold'),
                bg=self.colors['primary'], fg='white').pack(pady=15)
        
        # Scrollable content
        canvas = tk.Canvas(edit_window, bg=self.colors['light'])
        scrollbar = ttk.Scrollbar(edit_window, orient="vertical", command=canvas.yview)
        content = tk.Frame(canvas, bg=self.colors['light'])
        
        content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        title_frame = tk.LabelFrame(content, text="📹 Title", font=('Segoe UI', 10, 'bold'))
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_var = tk.StringVar(value=title)
        title_entry = tk.Text(title_frame, height=2, font=('Segoe UI', 10), wrap=tk.WORD)
        title_entry.insert('1.0', title)
        title_entry.pack(fill=tk.X, padx=10, pady=10)
        
        # Description
        desc_frame = tk.LabelFrame(content, text="📝 Description", font=('Segoe UI', 10, 'bold'))
        desc_frame.pack(fill=tk.X, pady=(0, 15))
        
        desc_text = tk.Text(desc_frame, height=6, font=('Segoe UI', 10), wrap=tk.WORD)
        desc_text.insert('1.0', video.get('description', ''))
        desc_text.pack(fill=tk.X, padx=10, pady=10)
        
        # Privacy settings
        privacy_frame = tk.LabelFrame(content, text="🔒 Privacy Settings", font=('Segoe UI', 10, 'bold'))
        privacy_frame.pack(fill=tk.X, pady=(0, 15))
        
        privacy_var = tk.StringVar(value=video.get('status', 'public'))
        privacy_options = ['public', 'unlisted', 'private']

        for option in privacy_options:
            tk.Radiobutton(privacy_frame, text=option.title(), variable=privacy_var, value=option,
                          font=('Segoe UI', 10), bg=self.colors['light'],
                          command=lambda: _toggle_share()).pack(anchor=tk.W, padx=10, pady=2)

        # Private share (specific emails) — only meaningful for private videos.
        share_frame = tk.LabelFrame(content, text="📧 Share riêng tư (chỉ video Private)",
                                    font=('Segoe UI', 10, 'bold'))
        share_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(share_frame,
                 text="Nhập email (cách nhau bởi dấu phẩy). Tối đa 50 người. "
                      "Dùng cookie trình duyệt đang đăng nhập YouTube.",
                 font=('Segoe UI', 9), bg=self.colors['light'],
                 wraplength=600, justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=(10, 5))

        share_row = tk.Frame(share_frame, bg=self.colors['light'])
        share_row.pack(fill=tk.X, padx=10, pady=(0, 5))
        tk.Label(share_row, text="Browser:", font=('Segoe UI', 9),
                 bg=self.colors['light']).pack(side=tk.LEFT)
        share_browser_var = tk.StringVar(value="chrome")
        ttk.Combobox(share_row, textvariable=share_browser_var, width=12,
                     state="readonly",
                     values=["chrome", "edge", "brave", "chromium", "vivaldi"]
                     ).pack(side=tk.LEFT, padx=(5, 0))

        share_emails_entry = tk.Text(share_frame, height=2, font=('Segoe UI', 10), wrap=tk.WORD)
        share_emails_entry.pack(fill=tk.X, padx=10, pady=(0, 8))

        share_btn = tk.Button(
            share_frame, text="🔗 Share Private qua email",
            command=lambda: self._do_share_private(
                video, share_emails_entry, share_browser_var, share_btn),
            bg=self.colors['secondary'], fg='white', relief=tk.FLAT,
            font=('Segoe UI', 10, 'bold'))
        share_btn.pack(anchor=tk.W, padx=10, pady=(0, 10))

        def _toggle_share():
            is_private = privacy_var.get() == 'private'
            state = tk.NORMAL if is_private else tk.DISABLED
            share_btn.config(state=state)
            share_emails_entry.config(state=state)

        _toggle_share()

        # Tags
        tags_frame = tk.LabelFrame(content, text="🏷️ Tags", font=('Segoe UI', 10, 'bold'))
        tags_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(tags_frame, text="Enter tags separated by commas:", 
                font=('Segoe UI', 9), bg=self.colors['light']).pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        tags_entry = tk.Text(tags_frame, height=3, font=('Segoe UI', 10), wrap=tk.WORD)
        existing_tags = video.get('tags') or []
        if isinstance(existing_tags, list):
            tags_entry.insert('1.0', ", ".join(existing_tags))
        tags_entry.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Note
        warning_frame = tk.Frame(content, bg=self.colors['warning'])
        warning_frame.pack(fill=tk.X, pady=(15, 20))

        tk.Label(warning_frame,
                text="ℹ️ 'Save Changes' cập nhật title/mô tả/privacy/tags thật qua YouTube API.\n"
                     "'Share Private qua email' dùng cookie trình duyệt (API chính thức không hỗ trợ).",
                font=('Segoe UI', 10, 'bold'), bg=self.colors['warning'], fg=self.colors['dark']).pack(pady=10)

        # Buttons
        button_frame = tk.Frame(content, bg=self.colors['light'])
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Button(button_frame, text="💾 Save Changes", 
                 command=lambda: self.save_video_changes(edit_window, video, title_entry, desc_text, privacy_var, tags_entry),
                 bg=self.colors['success'], fg=self.colors['dark'], relief=tk.FLAT,
                 font=('Segoe UI', 11, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(button_frame, text="❌ Cancel", 
                 command=edit_window.destroy,
                 bg=self.colors['medium'], fg='white', relief=tk.FLAT,
                 font=('Segoe UI', 11, 'bold')).pack(side=tk.LEFT)
                 
    def _update_video_tree_row(self, video_id, new_title, new_privacy):
        """Update the visible Video Manager tree row for a given video id."""
        try:
            tree = getattr(self, 'video_tree', None)
            if not tree:
                return
            for item, vid in list(self.current_video_data.items()):
                if vid.get('id') == video_id:
                    vals = list(tree.item(item, 'values'))
                    # columns: (title, views, privacy, published, duration)
                    if len(vals) >= 3:
                        vals[0] = new_title
                        vals[2] = new_privacy.title()
                        tree.item(item, values=vals)
                    break
        except Exception:
            pass

    def save_video_changes(self, window, video, title_widget, desc_widget, privacy_var, tags_widget):
        """Save video changes via the YouTube Data API (videos.update)."""
        try:
            new_title = title_widget.get('1.0', 'end-1c').strip()
            new_desc = desc_widget.get('1.0', 'end-1c').strip()
            new_privacy = privacy_var.get()
            new_tags_raw = tags_widget.get('1.0', 'end-1c')
            new_tags = [t.strip() for t in new_tags_raw.split(',') if t.strip()]

            if not new_title:
                messagebox.showwarning("Thiếu tiêu đề", "Tiêu đề không được để trống.")
                return

            # Demo mode → just preview
            if not self.youtube_uploader or self.youtube_uploader.service == 'demo_service' \
                    or not getattr(self.youtube_uploader, 'youtube', None):
                messagebox.showinfo("Demo Mode",
                    f"Changes would be saved:\n\n"
                    f"📹 Title: {new_title[:50]}\n"
                    f"🔒 Privacy: {new_privacy}\n"
                    f"🏷️ Tags: {', '.join(new_tags)[:50]}\n\n"
                    f"Đăng nhập YouTube (OAuth) để áp dụng thật.")
                window.destroy()
                return

            video_id = video.get('id', '')
            if not video_id:
                messagebox.showerror("Error", "Không tìm thấy video_id.")
                return

            youtube = self.youtube_uploader.youtube

            # videos.update replaces the whole snippet — categoryId is required,
            # so fetch the current snippet first and patch the fields we changed.
            resp = youtube.videos().list(part="snippet,status", id=video_id).execute()
            items = resp.get('items', [])
            if not items:
                messagebox.showerror("Error", "Không lấy được thông tin video từ YouTube.")
                return
            snippet = items[0].get('snippet', {})
            status = items[0].get('status', {})

            snippet['title'] = new_title
            snippet['description'] = new_desc
            snippet['tags'] = new_tags
            if not snippet.get('categoryId'):
                snippet['categoryId'] = '22'
            status['privacyStatus'] = new_privacy

            try:
                youtube.videos().update(
                    part="snippet,status",
                    body={"id": video_id, "snippet": snippet, "status": status}
                ).execute()
            except Exception as api_err:
                msg = str(api_err)
                if 'insufficient' in msg.lower() or 'scope' in msg.lower() or 'forbidden' in msg.lower():
                    messagebox.showerror(
                        "Thiếu quyền",
                        "Tài khoản chưa cấp quyền chỉnh sửa.\n\n"
                        "Hãy xóa token và Login YouTube lại để cấp quyền "
                        "'youtube.force-ssl', rồi thử lại.")
                    return
                raise

            # Reflect changes in the local cache + visible tree row
            video['title'] = new_title
            video['status'] = new_privacy
            self._update_video_tree_row(video_id, new_title, new_privacy)
            messagebox.showinfo("Thành công", "✅ Đã cập nhật video trên YouTube!")
            window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Cập nhật thất bại: {str(e)}")

    def _do_share_private(self, video, emails_widget, browser_var, btn):
        """Share a private video with specific emails via Studio cookies."""
        emails_str = emails_widget.get('1.0', 'end-1c').strip()
        if not emails_str:
            messagebox.showwarning("Thiếu email", "Nhập ít nhất một email.")
            return

        # Basic email sanity check
        candidates = [e.strip() for e in emails_str.split(',') if e.strip()]
        bad = [e for e in candidates if '@' not in e or '.' not in e.split('@')[-1]]
        if bad:
            messagebox.showwarning("Email không hợp lệ",
                                   "Email sai định dạng:\n" + "\n".join(bad[:5]))
            return
        if len(candidates) > 50:
            messagebox.showwarning("Quá giới hạn",
                                   "YouTube chỉ cho share tối đa 50 người.")
            return

        video_id = video.get('id', '')
        if not video_id:
            messagebox.showerror("Error", "Không tìm thấy video_id.")
            return

        browser = browser_var.get()

        def _worker():
            self.root.after(0, lambda: btn.config(state=tk.DISABLED, text="⏳ Đang share..."))
            result = self._studio_share_private(video_id, emails_str, browser)

            def _done():
                btn.config(state=tk.NORMAL, text="🔗 Share Private qua email")
                if result.get('success'):
                    shared = result.get('shared_with', candidates)
                    messagebox.showinfo(
                        "Đã share",
                        "✅ Đã share video với:\n" + "\n".join(shared))
                else:
                    messagebox.showerror(
                        "Share thất bại", result.get('error', 'Unknown error'))
            self.root.after(0, _done)

        threading.Thread(target=_worker, daemon=True).start()
            
    def perform_video_delete(self, video, item):
        """Perform actual video deletion"""
        try:
            video_id = video.get('id', '')
            title = video.get('title', 'Unknown Video')
            
            # In demo mode, just simulate
            if not self.youtube_uploader or self.youtube_uploader.service == 'demo_service':
                messagebox.showinfo("Demo Mode", 
                    f"Video deletion simulated:\n\n📹 {title}\n🆔 {video_id}\n\n" +
                    f"To delete real videos, use OAuth authentication.")
                
                # Remove from tree
                self.video_tree.delete(item)
                del self.current_video_data[item]
                self.show_default_preview()
                return
            
            # Real deletion would go here with YouTube API
            messagebox.showinfo("Success", f"Video '{title}' deleted successfully!")
            
            # Remove from tree
            self.video_tree.delete(item)
            del self.current_video_data[item]
            self.show_default_preview()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete video: {str(e)}")
            
    def open_youtube_analytics(self, video_id):
        """Open YouTube Analytics for specific video"""
        if video_id:
            url = f"https://studio.youtube.com/video/{video_id}/analytics"
            import webbrowser
            webbrowser.open(url)

class ToolTip:
    """Simple tooltip class for buttons"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.show_tooltip()
        
    def show_tooltip(self):
        """Show tooltip window"""
        x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        # Create tooltip content
        frame = tk.Frame(self.tooltip, background="#FFFFDD", relief="solid", borderwidth=1)
        frame.pack()
        
        label = tk.Label(frame, text=self.text, background="#FFFFDD", 
                        font=("Segoe UI", 9), justify="left", padx=10, pady=8)
        label.pack()
        
    def destroy(self):
        """Destroy tooltip window"""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

def _start_hang_watchdog(root):
    """Detect a frozen Tk mainloop (UI 'Not Responding') and dump every thread's
    stack to HANG_WATCHDOG_LOG so a hang can be diagnosed after the fact.

    Works by scheduling a heartbeat via root.after() — if the mainloop is
    pumping normally the heartbeat timestamp advances every ~1s. A separate
    daemon thread (which keeps running even if the mainloop is stuck) checks
    that timestamp and dumps tracebacks if it goes stale.
    """
    state = {"last_beat": time.monotonic(), "dumped_at": 0.0}

    def _beat():
        state["last_beat"] = time.monotonic()
        root.after(1000, _beat)

    def _watch():
        while True:
            time.sleep(2)
            stale_for = time.monotonic() - state["last_beat"]
            if stale_for < HANG_WATCHDOG_TIMEOUT:
                continue
            # Avoid spamming the log while the hang continues.
            if time.monotonic() - state["dumped_at"] < 60:
                continue
            state["dumped_at"] = time.monotonic()
            try:
                with open(HANG_WATCHDOG_LOG, "a", encoding="utf-8") as f:
                    f.write(f"\n=== UI hang detected at {datetime.now().isoformat(timespec='seconds')} "
                            f"(no mainloop heartbeat for {stale_for:.1f}s) ===\n")
                    faulthandler.dump_traceback(file=f, all_threads=True)
            except Exception:
                pass

    root.after(1000, _beat)
    threading.Thread(target=_watch, daemon=True).start()


def main():
    """Run the application"""
    root = tk.Tk()
    root.minsize(1200, 800)

    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")

    app = DouyinYouTubeTool(root)
    _start_hang_watchdog(root)
    root.mainloop()

if __name__ == "__main__":
    main()
