"""
Multimodal Vision Agent Integration.
Leverages Google Gemini Vision API for screenshot perception,
with seamless offline algorithmic fallback.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from PIL import Image
import config

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class MultimodalVisionAgent:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or config.GEMINI_API_KEY
        self.client = None
        if GENAI_AVAILABLE and self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                self.client = None

    def is_available(self) -> bool:
        return self.client is not None

    def analyze_chart_image(
        self,
        image_path: Path,
        asset_info: str = "Nifty 50 - 5 Min",
        capital_info: str = "Capital: ₹50,000, Max Risk: ₹1,000",
        context_info: str = "No major news"
    ) -> Optional[str]:
        """
        Sends chart screenshot directly to Gemini Multimodal Vision with the Master System Prompt.
        """
        if not self.is_available():
            return None

        prompt_text = f"""{config.MASTER_SYSTEM_PROMPT}

User Provided Context:
• Asset & Timeframe: {asset_info}
• Capital & Risk per Trade: {capital_info}
• Market Context / News: {context_info}

Please analyze this chart screenshot and respond strictly following the 6-Section Hinglish Structure.
"""
        try:
            pil_image = Image.open(image_path)
            response = self.client.models.generate_content(
                model=config.DEFAULT_MODEL,
                contents=[pil_image, prompt_text]
            )
            return response.text
        except Exception as e:
            # Try fallback model
            try:
                response = self.client.models.generate_content(
                    model=config.FALLBACK_MODEL,
                    contents=[pil_image, prompt_text]
                )
                return response.text
            except Exception as e2:
                print(f"Gemini Vision API error: {e2}")
                return None

