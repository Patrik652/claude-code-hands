"""
Gemini Vision Analyzer for Claude Vision Hands
Integrates Google Gemini 2.5 Flash API with automatic fallback
"""

import os
import io
import json
import base64
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
import logging

import google.generativeai as genai
from PIL import Image
import paddleocr
from paddleocr import PaddleOCR
import yaml

# Setup logging
logger = logging.getLogger(__name__)

class GeminiVisionAnalyzer:
    """
    AI-powered vision analyzer using Gemini 2.5 Flash
    with automatic fallback to local OCR
    """
    
    def __init__(self, config_path: str = "config/ai_models.yaml"):
        """Initialize Gemini analyzer with configuration"""
        self.config = self._load_config(config_path)
        self.api_key = os.getenv('GEMINI_API_KEY', '')
        
        # Quota management
        self.daily_requests = 0
        self.daily_limit = self.config.get('gemini', {}).get('daily_limit', 250)
        self.last_reset = datetime.now()
        self.request_history = []
        
        # Initialize Gemini if API key available
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                self.gemini_available = True
                logger.info("Gemini API initialized successfully")
            except Exception as e:
                logger.warning(f"Gemini initialization failed: {e}")
                self.gemini_available = False
        else:
            self.gemini_available = False
            logger.warning("No Gemini API key found, using fallback OCR")
        
        # Initialize fallback OCR
        self.paddle_ocr = PaddleOCR(
            use_angle_cls=True,
            lang='en',
            show_log=False
        )
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        
        # Default configuration
        return {
            'gemini': {
                'model': 'gemini-2.5-flash',
                'daily_limit': 250,
                'requests_per_minute': 10,
                'context_window': 1048576
            },
            'fallback': {
                'primary': 'paddleocr',
                'secondary': 'tesseract'
            },
            'retry': {
                'max_attempts': 3,
                'backoff_factor': 2,
                'max_delay': 30
            }
        }
    
    def _reset_daily_quota_if_needed(self):
        """Reset daily quota at midnight"""
        now = datetime.now()
        if now.date() > self.last_reset.date():
            self.daily_requests = 0
            self.request_history = []
            self.last_reset = now
            logger.info("Daily quota reset")
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        self._reset_daily_quota_if_needed()
        
        # Check daily limit
        if self.daily_requests >= self.daily_limit:
            logger.warning(f"Daily limit reached: {self.daily_requests}/{self.daily_limit}")
            return False
        
        # Check per-minute limit
        now = datetime.now()
        recent_requests = [
            req for req in self.request_history 
            if (now - req).seconds < 60
        ]
        
        rpm_limit = self.config.get('gemini', {}).get('requests_per_minute', 10)
        if len(recent_requests) >= rpm_limit:
            logger.warning(f"Rate limit reached: {len(recent_requests)} requests in last minute")
            return False
        
        return True
    
    def analyze_screenshot(
        self, 
        screenshot: Image.Image, 
        prompt: Optional[str] = None,
        detect_elements: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze screenshot using Gemini or fallback OCR
        
        Args:
            screenshot: PIL Image object
            prompt: Custom prompt for analysis
            detect_elements: Whether to detect UI elements
        
        Returns:
            Dictionary with analysis results
        """
        # Try Gemini first if available and within limits
        if self.gemini_available and self._check_rate_limit():
            result = self._analyze_with_gemini(screenshot, prompt, detect_elements)
            if result['success']:
                return result
        
        # Fallback to local OCR
        return self._analyze_with_ocr(screenshot)
    
    def _analyze_with_gemini(
        self, 
        screenshot: Image.Image,
        prompt: Optional[str],
        detect_elements: bool
    ) -> Dict[str, Any]:
        """Analyze using Gemini API"""
        try:
            # Default prompt for UI analysis
            if prompt is None:
                prompt = """Analyze this screenshot and identify:
                1. All clickable elements (buttons, links, icons)
                2. Text input fields and their labels
                3. Important text content
                4. Layout structure
                5. Current state/context of the interface
                
                Format response as JSON with sections for each element type."""
            
            # Add element detection instruction
            if detect_elements:
                prompt += "\nInclude bounding boxes in format: [x, y, width, height] for each element."
            
            # Convert image for Gemini
            img_byte_arr = io.BytesIO()
            screenshot.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            # Call Gemini API with retry logic
            for attempt in range(self.config['retry']['max_attempts']):
                try:
                    response = self.model.generate_content([prompt, screenshot])
                    
                    # Update quota tracking
                    self.daily_requests += 1
                    self.request_history.append(datetime.now())
                    
                    # Parse response
                    analysis = self._parse_gemini_response(response.text)
                    
                    return {
                        'success': True,
                        'provider': 'gemini',
                        'model': 'gemini-2.5-flash',
                        'analysis': analysis,
                        'raw_text': response.text,
                        'elements': analysis.get('elements', []),
                        'quota': {
                            'used': self.daily_requests,
                            'limit': self.daily_limit,
                            'remaining': self.daily_limit - self.daily_requests
                        },
                        'timestamp': datetime.now().isoformat()
                    }
                    
                except Exception as e:
                    if attempt < self.config['retry']['max_attempts'] - 1:
                        delay = min(
                            self.config['retry']['backoff_factor'] ** attempt,
                            self.config['retry']['max_delay']
                        )
                        logger.warning(f"Gemini attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                        time.sleep(delay)
                    else:
                        logger.error(f"Gemini analysis failed after {attempt + 1} attempts: {e}")
                        break
            
        except Exception as e:
            logger.error(f"Gemini analysis error: {e}")
        
        return {'success': False, 'error': 'Gemini analysis failed'}
    
    def _parse_gemini_response(self, response_text: str) -> dict:
        """Parse Gemini response into structured format"""
        try:
            # Try to parse as JSON first
            if response_text.strip().startswith('{'):
                return json.loads(response_text)
        except:
            pass
        
        # Parse text response into structured format
        analysis = {
            'elements': [],
            'text_content': [],
            'layout': {},
            'context': ''
        }
        
        # Extract different types of elements
        lines = response_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect sections
            if 'button' in line.lower() or 'click' in line.lower():
                current_section = 'buttons'
            elif 'input' in line.lower() or 'field' in line.lower():
                current_section = 'inputs'
            elif 'text' in line.lower() or 'label' in line.lower():
                current_section = 'text'
            
            # Extract elements based on section
            if current_section and ':' in line:
                element_text = line.split(':', 1)[1].strip()
                element = {
                    'type': current_section,
                    'text': element_text,
                    'confidence': 0.9  # High confidence for Gemini
                }
                
                # Try to extract coordinates if present
                if '[' in line and ']' in line:
                    try:
                        coords_str = line[line.find('['):line.find(']')+1]
                        coords = json.loads(coords_str)
                        element['bbox'] = coords
                    except:
                        pass
                
                analysis['elements'].append(element)
        
        # Set context
        analysis['context'] = response_text[:500] if len(response_text) > 500 else response_text
        
        return analysis
    
    def _analyze_with_ocr(self, screenshot: Image.Image) -> Dict[str, Any]:
        """Fallback analysis using PaddleOCR"""
        try:
            # Convert PIL Image to numpy array
            import numpy as np
            img_array = np.array(screenshot)
            
            # Run OCR
            result = self.paddle_ocr.ocr(img_array, cls=True)
            
            # Parse OCR results
            elements = []
            all_text = []
            
            for line in result[0] if result else []:
                bbox, (text, confidence) = line
                
                # Convert bbox format
                x_coords = [p[0] for p in bbox]
                y_coords = [p[1] for p in bbox]
                
                element = {
                    'type': 'text',
                    'text': text,
                    'confidence': confidence,
                    'bbox': [
                        min(x_coords),
                        min(y_coords),
                        max(x_coords) - min(x_coords),
                        max(y_coords) - min(y_coords)
                    ]
                }
                
                elements.append(element)
                all_text.append(text)
            
            # Try to identify element types based on text
            for element in elements:
                text_lower = element['text'].lower()
                if any(word in text_lower for word in ['button', 'click', 'submit', 'cancel', 'ok']):
                    element['type'] = 'button'
                elif any(word in text_lower for word in ['input', 'enter', 'type', 'password', 'email']):
                    element['type'] = 'input'
            
            return {
                'success': True,
                'provider': 'paddleocr',
                'analysis': {
                    'elements': elements,
                    'text_content': all_text,
                    'context': f"Found {len(elements)} text elements via OCR"
                },
                'elements': elements,
                'raw_text': '\n'.join(all_text),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"OCR analysis error: {e}")
            return {
                'success': False,
                'provider': 'paddleocr',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def find_element(self, screenshot: Image.Image, element_text: str) -> Optional[Dict[str, Any]]:
        """Find specific element in screenshot"""
        analysis = self.analyze_screenshot(screenshot)
        
        if not analysis.get('success'):
            return None
        
        # Search for element by text
        for element in analysis.get('elements', []):
            if element_text.lower() in element.get('text', '').lower():
                return element
        
        return None
    
    def get_clickable_elements(self, screenshot: Image.Image) -> List[Dict[str, Any]]:
        """Get all clickable elements from screenshot"""
        analysis = self.analyze_screenshot(
            screenshot,
            prompt="Identify all clickable elements (buttons, links, icons) with their positions."
        )
        
        if not analysis.get('success'):
            return []
        
        # Filter for clickable elements
        clickable_types = ['button', 'link', 'icon', 'clickable']
        return [
            element for element in analysis.get('elements', [])
            if element.get('type', '').lower() in clickable_types
        ]
    
    def get_input_fields(self, screenshot: Image.Image) -> List[Dict[str, Any]]:
        """Get all input fields from screenshot"""
        analysis = self.analyze_screenshot(
            screenshot,
            prompt="Identify all input fields and text areas with their labels and positions."
        )
        
        if not analysis.get('success'):
            return []
        
        # Filter for input elements
        input_types = ['input', 'textfield', 'textarea', 'field']
        return [
            element for element in analysis.get('elements', [])
            if element.get('type', '').lower() in input_types
        ]
    
    def get_status(self) -> Dict[str, Any]:
        """Get current analyzer status"""
        self._reset_daily_quota_if_needed()
        
        return {
            'gemini_available': self.gemini_available,
            'quota': {
                'used': self.daily_requests,
                'limit': self.daily_limit,
                'remaining': max(0, self.daily_limit - self.daily_requests),
                'reset_time': (self.last_reset + timedelta(days=1)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                ).isoformat()
            },
            'fallback_available': True,
            'current_provider': 'gemini' if (self.gemini_available and self._check_rate_limit()) else 'paddleocr'
        }


# Example usage and testing
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create analyzer
    analyzer = GeminiVisionAnalyzer()
    
    # Get status
    status = analyzer.get_status()
    print("Analyzer Status:", json.dumps(status, indent=2))
    
    # Test with a screenshot
    # screenshot = Image.open("test_screenshot.png")
    # result = analyzer.analyze_screenshot(screenshot)
    # print("Analysis Result:", json.dumps(result, indent=2))
