#!/usr/bin/env python3
"""
Vision MCP Server - Oči pre Claude Code
MIT License - Open Source
"""

import asyncio
import base64
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from io import BytesIO

# Core dependencies
import numpy as np
from PIL import Image, ImageGrab, ImageDraw
import mss
import cv2
from paddleocr import PaddleOCR

# MCP dependencies
from fastmcp import FastMCP, Context
from fastmcp.tools import Tool
from pydantic import BaseModel, Field

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env")

# AI Analyzer
from analyzers.gemini_analyzer import GeminiVisionAnalyzer

# Initialize MCP server
app = FastMCP("vision-mcp")

# Initialize OCR engine (lazy loading)
ocr_engine = None

def get_ocr_engine():
    """Lazy load OCR engine for better startup performance"""
    global ocr_engine
    if ocr_engine is None:
        ocr_engine = PaddleOCR(
            use_angle_cls=True,
            lang='en',
            show_log=False,
            use_gpu=True if cv2.cuda.getCudaEnabledDeviceCount() > 0 else False
        )
    return ocr_engine

# Safety and configuration
MAX_SCREENSHOT_SIZE = 4096  # Max dimension
SCREENSHOT_QUALITY = 85  # JPEG quality
CACHE_DIR = Path.home() / ".claude-vision-cache"
CACHE_DIR.mkdir(exist_ok=True)

# Logging
def log_action(action: str, details: Dict[str, Any]):
    """Log all vision actions for debugging"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details
    }
    log_file = CACHE_DIR / f"vision_log_{datetime.now().strftime('%Y%m%d')}.jsonl"
    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

# Helper functions
def image_to_base64(image: Image.Image, format: str = "PNG") -> str:
    """Convert PIL Image to base64 string"""
    buffer = BytesIO()
    image.save(buffer, format=format, quality=SCREENSHOT_QUALITY if format == "JPEG" else None)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def resize_if_needed(image: Image.Image) -> Image.Image:
    """Resize image if too large"""
    width, height = image.size
    if width > MAX_SCREENSHOT_SIZE or height > MAX_SCREENSHOT_SIZE:
        ratio = min(MAX_SCREENSHOT_SIZE / width, MAX_SCREENSHOT_SIZE / height)
        new_size = (int(width * ratio), int(height * ratio))
        return image.resize(new_size, Image.Resampling.LANCZOS)
    return image

# MCP Tools

@app.tool()
async def capture_screen(
    monitor: Optional[int] = None,
    format: str = "PNG"
) -> Dict[str, Any]:
    """
    Capture full screen or specific monitor

    Args:
        monitor: Monitor number (0-based), None for all monitors
        format: Image format (PNG or JPEG)

    Returns:
        Dictionary with base64 encoded image and metadata
    """
    try:
        with mss.mss() as sct:
            if monitor is not None:
                # Specific monitor
                monitor_info = sct.monitors[monitor + 1]  # mss uses 1-based indexing
            else:
                # All monitors
                monitor_info = sct.monitors[0]

            # Capture screenshot
            screenshot = sct.grab(monitor_info)

            # Convert to PIL Image
            image = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

            # Resize if needed
            image = resize_if_needed(image)

            # Save to cache
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            cache_file = CACHE_DIR / f"screen_{timestamp}.png"
            image.save(cache_file)

            # Log action
            log_action("capture_screen", {
                "monitor": monitor,
                "size": image.size,
                "cached": str(cache_file)
            })

            return {
                "image": image_to_base64(image, format),
                "width": image.width,
                "height": image.height,
                "timestamp": timestamp,
                "cached_path": str(cache_file),
                "monitor": monitor
            }

    except Exception as e:
        log_action("capture_screen_error", {"error": str(e)})
        raise Exception(f"Screen capture failed: {str(e)}")

@app.tool()
async def capture_region(
    x: int,
    y: int,
    width: int,
    height: int,
    format: str = "PNG"
) -> Dict[str, Any]:
    """
    Capture specific region of screen

    Args:
        x, y: Top-left corner coordinates
        width, height: Region dimensions
        format: Image format

    Returns:
        Dictionary with base64 encoded image and metadata
    """
    try:
        with mss.mss() as sct:
            region = {"left": x, "top": y, "width": width, "height": height}
            screenshot = sct.grab(region)

            # Convert to PIL Image
            image = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

            # Save to cache
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            cache_file = CACHE_DIR / f"region_{timestamp}.png"
            image.save(cache_file)

            # Log action
            log_action("capture_region", {
                "region": region,
                "cached": str(cache_file)
            })

            return {
                "image": image_to_base64(image, format),
                "region": region,
                "timestamp": timestamp,
                "cached_path": str(cache_file)
            }

    except Exception as e:
        log_action("capture_region_error", {"error": str(e)})
        raise Exception(f"Region capture failed: {str(e)}")

@app.tool()
async def find_element(
    template_path: str,
    confidence: float = 0.8,
    screenshot: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Find UI element using template matching

    Args:
        template_path: Path to template image
        confidence: Matching confidence threshold (0-1)
        screenshot: Optional base64 screenshot, captures new if not provided

    Returns:
        Dictionary with element position or None if not found
    """
    try:
        # Get screenshot
        if screenshot:
            # Decode provided screenshot
            img_data = base64.b64decode(screenshot)
            nparr = np.frombuffer(img_data, np.uint8)
            screen = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        else:
            # Capture new screenshot
            result = await capture_screen()
            img_data = base64.b64decode(result["image"])
            nparr = np.frombuffer(img_data, np.uint8)
            screen = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Load template
        template = cv2.imread(template_path)
        if template is None:
            raise ValueError(f"Template not found: {template_path}")

        # Convert to grayscale for matching
        screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        # Perform template matching
        result = cv2.matchTemplate(screen_gray, template_gray, cv2.TM_CCOEFF_NORMED)

        # Find best match
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= confidence:
            # Found match
            h, w = template_gray.shape
            x, y = max_loc
            center_x = x + w // 2
            center_y = y + h // 2

            # Draw rectangle on debug image
            debug_img = screen.copy()
            cv2.rectangle(debug_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Save debug image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            debug_file = CACHE_DIR / f"match_{timestamp}.png"
            cv2.imwrite(str(debug_file), debug_img)

            # Log action
            log_action("find_element", {
                "template": template_path,
                "found": True,
                "confidence": float(max_val),
                "position": [center_x, center_y],
                "debug": str(debug_file)
            })

            return {
                "found": True,
                "x": center_x,
                "y": center_y,
                "confidence": float(max_val),
                "bbox": {"x": x, "y": y, "width": w, "height": h},
                "debug_image": str(debug_file)
            }
        else:
            # Not found
            log_action("find_element", {
                "template": template_path,
                "found": False,
                "best_confidence": float(max_val)
            })
            return None

    except Exception as e:
        log_action("find_element_error", {"error": str(e)})
        raise Exception(f"Element search failed: {str(e)}")

@app.tool()
async def extract_text(
    x: Optional[int] = None,
    y: Optional[int] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    screenshot: Optional[str] = None,
    language: str = "en"
) -> Dict[str, Any]:
    """
    Extract text from screen using OCR

    Args:
        x, y, width, height: Optional region (extracts from full screen if not provided)
        screenshot: Optional base64 screenshot
        language: OCR language

    Returns:
        Dictionary with extracted text and confidence scores
    """
    try:
        # Get screenshot or region
        if screenshot:
            img_data = base64.b64decode(screenshot)
            image = Image.open(BytesIO(img_data))
        elif x is not None and y is not None and width and height:
            result = await capture_region(x, y, width, height)
            img_data = base64.b64decode(result["image"])
            image = Image.open(BytesIO(img_data))
        else:
            result = await capture_screen()
            img_data = base64.b64decode(result["image"])
            image = Image.open(BytesIO(img_data))

        # Convert to numpy array for PaddleOCR
        img_array = np.array(image)

        # Run OCR
        ocr = get_ocr_engine()
        result = ocr.ocr(img_array, cls=True)

        # Process results
        extracted_text = []
        all_text = []

        if result and result[0]:
            for line in result[0]:
                text = line[1][0]
                confidence = line[1][1]
                bbox = line[0]

                extracted_text.append({
                    "text": text,
                    "confidence": float(confidence),
                    "bbox": bbox
                })
                all_text.append(text)

        # Log action
        log_action("extract_text", {
            "region": {"x": x, "y": y, "width": width, "height": height},
            "lines_extracted": len(extracted_text)
        })

        return {
            "full_text": " ".join(all_text),
            "lines": extracted_text,
            "total_lines": len(extracted_text),
            "average_confidence": np.mean([l["confidence"] for l in extracted_text]) if extracted_text else 0
        }

    except Exception as e:
        log_action("extract_text_error", {"error": str(e)})
        raise Exception(f"Text extraction failed: {str(e)}")

@app.tool()
async def wait_for_element(
    template_path: str,
    timeout: int = 10,
    check_interval: float = 0.5,
    confidence: float = 0.8
) -> Optional[Dict[str, Any]]:
    """
    Wait for UI element to appear

    Args:
        template_path: Path to template image
        timeout: Maximum wait time in seconds
        check_interval: Time between checks
        confidence: Matching confidence threshold

    Returns:
        Element position when found or None if timeout
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        result = await find_element(template_path, confidence)
        if result:
            return result
        await asyncio.sleep(check_interval)

    log_action("wait_for_element", {
        "template": template_path,
        "timeout_reached": True
    })

    return None

@app.tool()
async def get_screen_info() -> Dict[str, Any]:
    """
    Get information about available screens

    Returns:
        Dictionary with screen configuration
    """
    try:
        with mss.mss() as sct:
            monitors = []
            for i, monitor in enumerate(sct.monitors[1:], 1):  # Skip virtual monitor
                monitors.append({
                    "index": i - 1,
                    "x": monitor["left"],
                    "y": monitor["top"],
                    "width": monitor["width"],
                    "height": monitor["height"]
                })

            return {
                "primary_screen": {
                    "width": sct.monitors[0]["width"],
                    "height": sct.monitors[0]["height"]
                },
                "monitors": monitors,
                "total_monitors": len(monitors)
            }

    except Exception as e:
        log_action("get_screen_info_error", {"error": str(e)})
        raise Exception(f"Screen info failed: {str(e)}")

# Health check
@app.tool()
async def health_check() -> Dict[str, Any]:
    """
    Check vision system health

    Returns:
        System status and capabilities
    """
    try:
        # Test screen capture
        screen_test = await capture_screen()
        screen_ok = screen_test is not None

        # Test OCR
        ocr_ok = get_ocr_engine() is not None

        # Check GPU
        gpu_available = cv2.cuda.getCudaEnabledDeviceCount() > 0

        # Cache status
        cache_files = list(CACHE_DIR.glob("*"))
        cache_size = sum(f.stat().st_size for f in cache_files) / (1024 * 1024)  # MB

        return {
            "status": "healthy" if screen_ok and ocr_ok else "degraded",
            "capabilities": {
                "screen_capture": screen_ok,
                "ocr": ocr_ok,
                "gpu_acceleration": gpu_available,
                "opencv_version": cv2.__version__
            },
            "cache": {
                "directory": str(CACHE_DIR),
                "files": len(cache_files),
                "size_mb": round(cache_size, 2)
            },
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Cleanup function
@app.tool()
async def cleanup_cache(
    older_than_hours: int = 24
) -> Dict[str, Any]:
    """
    Clean up old cache files

    Args:
        older_than_hours: Delete files older than this

    Returns:
        Cleanup statistics
    """
    try:
        cutoff_time = time.time() - (older_than_hours * 3600)
        deleted_count = 0
        freed_space = 0

        for file in CACHE_DIR.glob("*"):
            if file.stat().st_mtime < cutoff_time:
                freed_space += file.stat().st_size
                file.unlink()
                deleted_count += 1

        return {
            "deleted_files": deleted_count,
            "freed_space_mb": round(freed_space / (1024 * 1024), 2),
            "cache_directory": str(CACHE_DIR)
        }

    except Exception as e:
        log_action("cleanup_cache_error", {"error": str(e)})
        raise Exception(f"Cache cleanup failed: {str(e)}")

# Initialize AI Analyzer (lazy loading)
gemini_analyzer = None

def get_gemini_analyzer():
    """Lazy load Gemini analyzer"""
    global gemini_analyzer
    if gemini_analyzer is None:
        config_path = Path(__file__).parent.parent.parent / "config" / "ai_models.yaml"
        gemini_analyzer = GeminiVisionAnalyzer(config_path=str(config_path))
    return gemini_analyzer

# AI-Powered MCP Tools

@app.tool()
async def analyze_screen_ai(
    prompt: str = "Analyze this screenshot and identify all UI elements",
    use_fallback: bool = True
) -> Dict[str, Any]:
    """
    AI-powered screen analysis using Gemini 2.5 Flash

    Args:
        prompt: Analysis question/prompt
        use_fallback: Use PaddleOCR fallback if quota exceeded

    Returns:
        AI analysis with identified elements and insights
    """
    try:
        # Capture screenshot
        screen_data = await capture_screen()
        img_data = base64.b64decode(screen_data["image"])
        screenshot = Image.open(BytesIO(img_data))

        # Get analyzer
        analyzer = get_gemini_analyzer()

        # Analyze with AI
        result = analyzer.analyze_screenshot(screenshot, prompt=prompt)

        # Log action
        log_action("analyze_screen_ai", {
            "prompt": prompt,
            "provider": result.get("provider", "unknown"),
            "quota_used": result.get("quota_used", 0)
        })

        return result

    except Exception as e:
        log_action("analyze_screen_ai_error", {"error": str(e)})
        return {
            "success": False,
            "error": str(e),
            "fallback_available": use_fallback
        }

@app.tool()
async def find_element_ai(
    element_description: str,
    screenshot: Optional[str] = None
) -> Dict[str, Any]:
    """
    Find UI element using AI vision (semantic search)

    Args:
        element_description: Description of element to find (e.g., "submit button", "login field")
        screenshot: Optional base64 screenshot, captures new if not provided

    Returns:
        Element location and details if found
    """
    try:
        # Get screenshot
        if screenshot:
            img_data = base64.b64decode(screenshot)
            image = Image.open(BytesIO(img_data))
        else:
            screen_data = await capture_screen()
            img_data = base64.b64decode(screen_data["image"])
            image = Image.open(BytesIO(img_data))

        # Get analyzer
        analyzer = get_gemini_analyzer()

        # Find element
        element = analyzer.find_element(image, element_description)

        # Log action
        log_action("find_element_ai", {
            "description": element_description,
            "found": element is not None
        })

        if element:
            return {
                "found": True,
                "element": element,
                "description": element_description
            }
        else:
            return {
                "found": False,
                "description": element_description,
                "message": "Element not found"
            }

    except Exception as e:
        log_action("find_element_ai_error", {"error": str(e)})
        return {
            "found": False,
            "error": str(e)
        }

@app.tool()
async def ai_status() -> Dict[str, Any]:
    """
    Get AI analyzer status, quota usage, and capabilities

    Returns:
        Status information including quota, provider, and capabilities
    """
    try:
        analyzer = get_gemini_analyzer()
        status = analyzer.get_status()

        return {
            "status": "healthy",
            "analyzer": status,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Main entry point
if __name__ == "__main__":
    # Print startup info
    print("🎯 Vision MCP Server starting...")
    print(f"📁 Cache directory: {CACHE_DIR}")
    print(f"🖥️ Display: {os.environ.get('DISPLAY', 'Not set')}")

    # Check dependencies
    try:
        import mss
        import cv2
        from paddleocr import PaddleOCR
        print("✅ All dependencies loaded")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        sys.exit(1)

    # Check AI analyzer
    try:
        analyzer = get_gemini_analyzer()
        print(f"🤖 AI Analyzer: {analyzer.gemini_available and 'Gemini Ready' or 'Fallback OCR Only'}")
    except Exception as e:
        print(f"⚠️ AI Analyzer: {e}")

    # Run server
    print("🚀 Server ready on stdio")
    app.run()
