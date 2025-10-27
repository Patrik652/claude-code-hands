"""
Integration helper for adding Gemini analyzer to vision-mcp server
Add this import and initialization to your vision-mcp/server.py
"""

# Add to imports section:
from analyzers.gemini_analyzer import GeminiVisionAnalyzer

# Add to initialization:
gemini_analyzer = GeminiVisionAnalyzer(config_path="../config/ai_models.yaml")

# Add new MCP tool:
@server.tool()
async def analyze_with_ai(
    prompt: str = "Analyze this screenshot",
    use_fallback: bool = True
) -> dict:
    """
    Analyze current screenshot using AI (Gemini or fallback OCR)
    """
    screenshot = capture_screen()  # Your existing capture function
    result = gemini_analyzer.analyze_screenshot(
        screenshot, 
        prompt=prompt
    )
    return result

# Add element finder tool:
@server.tool()
async def find_ui_element(element_text: str) -> dict:
    """
    Find UI element by text using AI vision
    """
    screenshot = capture_screen()
    element = gemini_analyzer.find_element(screenshot, element_text)
    if element:
        return {
            "found": True,
            "element": element
        }
    return {"found": False}

# Add status tool:
@server.tool()
async def ai_status() -> dict:
    """
    Get AI analyzer status and quota
    """
    return gemini_analyzer.get_status()
