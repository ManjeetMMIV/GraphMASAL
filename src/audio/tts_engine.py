import os
import asyncio
import edge_tts

async def generate_audio_file(text: str, output_path: str, voice: str = "en-IN-NeerjaNeural"):
    """
    Generates an MP3 file using edge-tts asynchronously.
    """
    # ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)
    return output_path
