"""
AI Video Analysis Service
Handles video transcription and AI-powered annotation generation
"""

import os
import subprocess
import time
from datetime import datetime
from typing import List, Dict, Optional
import tempfile
import json
import base64

# OpenAI imports
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

# Whisper imports (local model)
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    whisper = None

# CV2 for frame extraction
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    cv2 = None


class AIAnalyzer:
    """AI-powered video analysis service"""
    
    def __init__(self, api_key: str = None, use_enhanced: bool = True):
        """
        Initialize AI Analyzer
        
        Args:
            api_key: OpenAI API key (required for full analysis)
            use_enhanced: If True, use OpenAI API for visual analysis; if False, audio only
        """
        self.api_key = api_key
        self.use_enhanced = use_enhanced and api_key is not None
        
        if not api_key:
            print("⚠️  Warning: No OpenAI API key provided. Visual analysis disabled.")
        
        # Initialize OpenAI client if available
        if self.use_enhanced and OPENAI_AVAILABLE:
            self.openai_client = OpenAI(api_key=api_key)
        else:
            self.openai_client = None
        
        # Load local Whisper model (lazy loading)
        self.whisper_model = None
        
    def _load_whisper_model(self, model_size: str = "small"):
        """Lazy load Whisper model"""
        if not WHISPER_AVAILABLE:
            raise Exception("Whisper library not available. Install with: pip install openai-whisper")
        
        if self.whisper_model is None:
            print(f"Loading Whisper {model_size} model...")
            self.whisper_model = whisper.load_model(model_size)
            print("Whisper model loaded successfully")
        
        return self.whisper_model
    
    def extract_audio(self, video_path: str, output_path: str = None) -> str:
        """
        Extract audio from video file
        
        Args:
            video_path: Path to video file
            output_path: Optional output path for audio file
            
        Returns:
            Path to extracted audio file
        """
        if output_path is None:
            output_path = tempfile.mktemp(suffix='.wav')
        
        try:
            # Use FFmpeg to extract audio
            command = [
                'ffmpeg',
                '-i', video_path,
                '-vn',  # No video
                '-acodec', 'pcm_s16le',  # PCM 16-bit
                '-ar', '16000',  # 16kHz sample rate
                '-ac', '1',  # Mono
                '-y',  # Overwrite output file
                output_path
            ]
            
            subprocess.run(command, check=True, capture_output=True)
            return output_path
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to extract audio: {e.stderr.decode()}")
        except FileNotFoundError:
            raise Exception("FFmpeg not found. Please install FFmpeg.")
    
    def transcribe_local(self, audio_path: str) -> Dict:
        """
        Transcribe audio using local Whisper model
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary with transcription results
        """
        start_time = time.time()
        
        model = self._load_whisper_model()
        result = model.transcribe(audio_path)
        
        processing_time = time.time() - start_time
        
        return {
            'text': result['text'],
            'segments': result.get('segments', []),
            'language': result.get('language', 'en'),
            'method': 'local_whisper',
            'processing_time': processing_time
        }
    
    def transcribe_api(self, audio_path: str) -> Dict:
        """
        Transcribe audio using OpenAI Whisper API
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary with transcription results
        """
        if not self.openai_client:
            raise Exception("OpenAI client not initialized")
        
        start_time = time.time()
        
        with open(audio_path, 'rb') as audio_file:
            response = self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["segment"]
            )
        
        processing_time = time.time() - start_time
        
        # Extract segments if available
        segments = []
        if hasattr(response, 'segments') and response.segments:
            # Convert segment objects to dicts for JSON serialization
            for seg in response.segments:
                segments.append({
                    'text': seg.text if hasattr(seg, 'text') else str(seg),
                    'start': seg.start if hasattr(seg, 'start') else 0,
                    'end': seg.end if hasattr(seg, 'end') else 0
                })
            print(f"✅ Extracted {len(segments)} segments from Whisper API")
        else:
            print("⚠️ No segments returned from Whisper API")
        
        return {
            'text': response.text,
            'segments': segments,
            'language': response.language if hasattr(response, 'language') else 'en',
            'method': 'openai_api',
            'processing_time': processing_time
        }
    
    def extract_frames(self, video_path: str, num_frames: int = 10) -> List[str]:
        """
        Extract frames from video at regular intervals
        
        Args:
            video_path: Path to video file
            num_frames: Number of frames to extract (default 10)
            
        Returns:
            List of base64-encoded frame images
        """
        if not CV2_AVAILABLE:
            print("⚠️  Warning: OpenCV not available. Frame extraction skipped.")
            return []
        
        try:
            video = cv2.VideoCapture(video_path)
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = video.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0
            
            # Calculate frame intervals (extract frames evenly throughout video)
            frame_interval = max(1, total_frames // num_frames)
            
            frames_base64 = []
            frame_count = 0
            extracted_count = 0
            
            print(f"Extracting {num_frames} frames from video (duration: {duration:.1f}s)...")
            
            while video.isOpened() and extracted_count < num_frames:
                ret, frame = video.read()
                if not ret:
                    break
                
                # Extract frame at intervals
                if frame_count % frame_interval == 0:
                    # Resize frame to reduce data size (max 800px width)
                    height, width = frame.shape[:2]
                    if width > 800:
                        scale = 800 / width
                        new_width = 800
                        new_height = int(height * scale)
                        frame = cv2.resize(frame, (new_width, new_height))
                    
                    # Encode frame to JPEG
                    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                    
                    # Convert to base64
                    frame_base64 = base64.b64encode(buffer).decode('utf-8')
                    frames_base64.append(frame_base64)
                    extracted_count += 1
                    
                    print(f"  Frame {extracted_count}/{num_frames} extracted (at {frame_count/fps:.1f}s)")
                
                frame_count += 1
            
            video.release()
            print(f"✅ Extracted {len(frames_base64)} frames successfully")
            return frames_base64
            
        except Exception as e:
            print(f"❌ Frame extraction error: {str(e)}")
            return []
    
    def extract_frames_every_n_seconds(
        self, 
        video_path: str, 
        interval_seconds: int = 2
    ) -> List[str]:
        """
        Extract frames at regular time intervals
        
        Args:
            video_path: Path to video file
            interval_seconds: Extract a frame every N seconds (default: 2)
            
        Returns:
            List of base64-encoded frame images
        """
        if not CV2_AVAILABLE:
            print("⚠️  Warning: OpenCV not available. Frame extraction skipped.")
            return []
        
        try:
            video = cv2.VideoCapture(video_path)
            fps = video.get(cv2.CAP_PROP_FPS)
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            print(f"Extracting frames every {interval_seconds} seconds from {duration:.1f}s video...")
            
            # Calculate how many frames to extract
            num_frames = int(duration / interval_seconds) + 1
            print(f"  → Will extract ~{num_frames} frames")
            
            frames_base64 = []
            
            for frame_idx in range(num_frames):
                # Calculate timestamp for this frame
                timestamp = frame_idx * interval_seconds
                if timestamp > duration:
                    break
                
                # Seek to the timestamp
                frame_number = int(timestamp * fps)
                video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                
                ret, frame = video.read()
                if not ret:
                    continue
                
                # Resize frame to reduce data size (max 800px width)
                height, width = frame.shape[:2]
                if width > 800:
                    scale = 800 / width
                    new_width = 800
                    new_height = int(height * scale)
                    frame = cv2.resize(frame, (new_width, new_height))
                
                # Encode frame to JPEG
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                
                # Convert to base64
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                frames_base64.append(frame_base64)
                
                print(f"  Frame {frame_idx+1} extracted at {timestamp:.1f}s")
            
            video.release()
            print(f"✅ Extracted {len(frames_base64)} frames (every {interval_seconds}s)")
            return frames_base64
            
        except Exception as e:
            print(f"❌ Frame extraction error: {str(e)}")
            return []
    
    def extract_key_frames(
        self, 
        video_path: str, 
        transcript_segments: List[Dict],
        num_frames: int = 15
    ) -> List[str]:
        """
        Extract frames at KEY moments identified from transcript
        
        Args:
            video_path: Path to video file
            transcript_segments: Whisper transcript segments with timestamps
            num_frames: Number of frames to extract (default 15)
            
        Returns:
            List of base64-encoded frame images at key moments
        """
        if not CV2_AVAILABLE:
            print("⚠️  Warning: OpenCV not available. Frame extraction skipped.")
            return []
        
        try:
            video = cv2.VideoCapture(video_path)
            fps = video.get(cv2.CAP_PROP_FPS)
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            print(f"Smart frame extraction from {duration:.1f}s video with {len(transcript_segments)} segments...")
            
            # Strategy: Combine transcript-based + evenly-spaced frames
            key_timestamps = []
            
            # 1. Extract frames at beginning of each transcript segment (up to 10)
            if transcript_segments:
                segment_times = [seg.get('start', 0) for seg in transcript_segments[:10]]
                key_timestamps.extend(segment_times)
                print(f"  → {len(segment_times)} frames at transcript segments")
            
            # 2. Add evenly distributed frames to ensure full coverage
            interval = duration / max(1, num_frames - len(key_timestamps))
            for i in range(num_frames - len(key_timestamps)):
                time_point = i * interval
                if time_point not in key_timestamps:
                    key_timestamps.append(time_point)
            
            # Sort and limit to num_frames
            key_timestamps = sorted(set(key_timestamps))[:num_frames]
            print(f"  → Total: {len(key_timestamps)} key moments identified")
            
            frames_base64 = []
            
            for idx, timestamp in enumerate(key_timestamps):
                # Seek to the timestamp
                frame_number = int(timestamp * fps)
                video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                
                ret, frame = video.read()
                if not ret:
                    continue
                
                # Resize frame to reduce data size (max 800px width)
                height, width = frame.shape[:2]
                if width > 800:
                    scale = 800 / width
                    new_width = 800
                    new_height = int(height * scale)
                    frame = cv2.resize(frame, (new_width, new_height))
                
                # Encode frame to JPEG
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                
                # Convert to base64
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                frames_base64.append(frame_base64)
                
                print(f"  Frame {idx+1}/{len(key_timestamps)} extracted at {timestamp:.1f}s")
            
            video.release()
            print(f"✅ Extracted {len(frames_base64)} frames at key moments")
            return frames_base64
            
        except Exception as e:
            print(f"❌ Key frame extraction error: {str(e)}")
            return []
    
    def analyze_frames_with_vision(
        self,
        frames_base64: List[str],
        best_practices: List[Dict],
        video_category: str = None
    ) -> List[Dict]:
        """
        Analyze video frames using GPT-4 Vision
        
        Args:
            frames_base64: List of base64-encoded frame images
            best_practices: List of best practice criteria
            video_category: Optional category for focused analysis
            
        Returns:
            List of visual observation annotations
        """
        if not self.openai_client:
            print("⚠️  Warning: OpenAI client not initialized. Vision analysis skipped.")
            return []
        
        if not frames_base64:
            print("⚠️  Warning: No frames provided. Vision analysis skipped.")
            return []
        
        # Filter practices for visual aspects
        visual_practices = [
            p for p in best_practices 
            if any(keyword in p.get('description', '').lower() 
                   for keyword in ['positioning', 'materials', 'eye level', 'facing', 
                                   'visual', 'body language', 'gesture', 'physical',
                                   'ready', 'organized', 'environment', 'setup'])
        ]
        
        if video_category:
            visual_practices = [p for p in visual_practices if p.get('category') == video_category]
        
        practices_text = "\n".join([
            f"- {p['title']}: {p['description']}"
            for p in visual_practices[:15]  # Limit to 15 for prompt size
        ])
        
        print(f"Analyzing {len(frames_base64)} frames with GPT-4 Vision...")
        
        # Prepare messages with multiple images (send up to 15 frames for detailed analysis)
        # For every-2-second extraction, send more frames for better coverage
        if len(frames_base64) > 15:
            sample_frames = frames_base64[::max(1, len(frames_base64)//15)][:15]
        else:
            sample_frames = frames_base64
        
        image_content = []
        for i, frame_b64 in enumerate(sample_frames):
            image_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{frame_b64}",
                    "detail": "low"  # Use low detail for faster processing
                }
            })
        
        prompt = f"""You are analyzing teaching session video frames for evidence of visual teaching practices.

Teaching Category: {video_category if video_category else 'general'}

Visual Best Practices to Look For:
{practices_text}

Analyze the provided video frames and identify:
1. Teacher positioning (eye level, facing student, proximity)
2. Materials readiness and organization
3. Student engagement indicators
4. Physical prompts or gestures
5. Environmental setup

For each observation, provide:
- practice_title: The exact practice name from the list above
- description: What you observe in the frames
- is_positive: Whether it's correctly implemented (true) or needs improvement (false)
- frame_numbers: Which frames show this (e.g., "frames 1-3")
- confidence: Your confidence level (0.0-1.0)

You MUST respond with a JSON object with this EXACT structure:
{{
  "visual_observations": [
    {{
      "practice_title": "string",
      "description": "string",
      "is_positive": true/false,
      "frame_numbers": "string",
      "confidence": 0.0-1.0
    }}
  ]
}}

The top-level key MUST be "visual_observations".
"""
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert educational analyst specializing in observing teaching techniques through video."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt}
                ] + image_content
            }
        ]
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=2000,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            observations = result.get('visual_observations', [])
            print(f"✅ GPT-4 Vision generated {len(observations)} visual observations")
            return observations
            
        except Exception as e:
            print(f"❌ Vision analysis error: {str(e)}")
            return []
    
    def analyze_transcript(
        self,
        transcript: str,
        best_practices: List[Dict],
        video_category: str = None
    ) -> List[Dict]:
        """
        Analyze transcript using GPT-4 to identify teaching practices
        
        Args:
            transcript: Video transcript text
            best_practices: List of best practice criteria
            video_category: Optional category to focus analysis
            
        Returns:
            List of identified annotations
        """
        if not self.openai_client:
            raise Exception("OpenAI client not initialized")
        
        # Filter best practices by category if provided
        if video_category:
            practices = [p for p in best_practices if p.get('category') == video_category]
        else:
            practices = best_practices
        
        # Create prompt
        practices_text = "\n".join([
            f"- {p['title']}: {p['description']}"
            for p in practices
        ])
        
        prompt = f"""You are an expert in evidence-based teaching practices for children with autism. 
Analyze this video transcript and identify instances of the following teaching practices:

{practices_text}

For each practice you identify, provide:
1. The practice title (exact match from list above)
2. A specific quote or description from the transcript
3. Whether it's a positive example (correctly implemented) or negative (needs improvement)
4. A brief comment explaining why

Transcript:
{transcript}

You MUST respond with a JSON object with this EXACT structure:
{{
  "annotations": [
    {{
      "practice_title": "string",
      "quote": "string",
      "is_positive": true/false,
      "comment": "string",
      "confidence": 0.0-1.0
    }}
  ]
}}

The top-level key MUST be "annotations" (not "results" or anything else).
"""
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",  # Changed from gpt-4 to gpt-4o-mini (supports JSON mode, faster, cheaper)
            messages=[
                {"role": "system", "content": "You are an expert educational analyst specializing in autism intervention techniques."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        try:
            result = json.loads(response.choices[0].message.content)
            return result.get('annotations', [])
        except json.JSONDecodeError:
            return []
    
    def analyze_video(
        self,
        video_path: str,
        best_practices: List[Dict],
        video_category: str = None,
        use_enhanced: bool = None
    ) -> Dict:
        """
        Complete video analysis pipeline
        
        Args:
            video_path: Path to video file
            best_practices: List of best practice criteria
            video_category: Optional category for focused analysis
            use_enhanced: Override default enhanced setting
            
        Returns:
            Dictionary with analysis results
        """
        if use_enhanced is None:
            use_enhanced = self.use_enhanced
        
        results = {
            'video_path': video_path,
            'category': video_category,
            'timestamp': datetime.utcnow().isoformat(),
            'method': 'enhanced' if use_enhanced else 'local'
        }
        
        try:
            # Step 1: Extract audio
            print("Extracting audio...")
            audio_path = self.extract_audio(video_path)
            results['audio_extracted'] = True
            
            # Step 2: Transcribe
            print("Transcribing audio...")
            if use_enhanced:
                transcript_result = self.transcribe_api(audio_path)
            else:
                transcript_result = self.transcribe_local(audio_path)
            
            results['transcript'] = transcript_result
            
            # Step 3: Extract video frames (if enhanced mode)
            visual_annotations = []
            if use_enhanced and self.openai_client and CV2_AVAILABLE:
                print("Extracting video frames every 2 seconds...")
                
                # Extract frames every 2 seconds throughout the video
                frames = self.extract_frames_every_n_seconds(
                    video_path, 
                    interval_seconds=2  # Frame every 2 seconds
                )
                results['frames_extracted'] = len(frames)
                
                if frames:
                    print("Analyzing frames with GPT-4 Vision...")
                    visual_annotations = self.analyze_frames_with_vision(
                        frames,
                        best_practices,
                        video_category
                    )
                    results['visual_annotations'] = visual_annotations
            else:
                results['frames_extracted'] = 0
                results['visual_annotations'] = []
            
            # Step 4: Analyze transcript with GPT-4 (if enhanced mode and OpenAI available)
            transcript_annotations = []
            if use_enhanced and self.openai_client:
                print("Analyzing transcript with GPT-4...")
                transcript_annotations = self.analyze_transcript(
                    transcript_result['text'],
                    best_practices,
                    video_category
                )
            
            # Combine transcript and visual annotations
            results['annotations'] = transcript_annotations + visual_annotations
            print(f"✅ Total annotations: {len(results['annotations'])} ({len(transcript_annotations)} from transcript, {len(visual_annotations)} from vision)")
            
            if not use_enhanced:
                results['note'] = "AI analysis requires enhanced mode with OpenAI API key"
            
            # Cleanup
            if os.path.exists(audio_path):
                os.remove(audio_path)
            
            results['status'] = 'success'
            
        except Exception as e:
            results['status'] = 'error'
            results['error'] = str(e)
        
        return results
    
    def generate_annotations_from_segments(
        self,
        segments: List[Dict],
        video_id: int
    ) -> List[Dict]:
        """
        Convert transcript segments into timestamped annotations
        
        Args:
            segments: Whisper transcript segments
            video_id: Video ID
            
        Returns:
            List of annotation objects ready for database
        """
        annotations = []
        
        for segment in segments:
            annotations.append({
                'video_id': video_id,
                'start_time': segment.get('start', 0),
                'end_time': segment.get('end', 0),
                'comment': segment.get('text', ''),
                'annotation_type': 'ai_generated',
                'status': 'draft',
                'practice_category': 'general'
            })
        
        return annotations

