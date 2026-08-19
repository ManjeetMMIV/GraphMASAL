import uuid
from pathlib import Path
from fastapi import HTTPException
from pydantic import BaseModel
from src.api.dependencies import get_neo4j_connection

# Resolve REPO_ROOT properly
REPO_ROOT = Path(__file__).resolve().parents[3]

class LectureRequest(BaseModel):
    student_id: str
    session_id: str
    concept_name: str

class PPTRequest(BaseModel):
    student_id: str
    session_id: str
    concept_name: str
    custom_prompt: str = ""

async def generate_lecture_logic(req: LectureRequest):
    conn = get_neo4j_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Neo4j credentials are missing.")
    try:
        from src.agents.lecturer_agent import LecturerAgent
        from src.audio.tts_engine import generate_audio_file
        
        agent = LecturerAgent(conn)
        script = agent.generate_script(req.concept_name, req.student_id)
        
        if not script:
            raise HTTPException(status_code=500, detail="Failed to generate script.")
            
        filename = f"{uuid.uuid4().hex[:8]}.mp3"
        audio_dir = REPO_ROOT / "public" / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)
        audio_path = audio_dir / filename
        
        await generate_audio_file(script, str(audio_path))
        
        return {"status": "ok", "audio_url": f"/audio/{filename}", "script": script}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

def generate_ppt_logic(req: PPTRequest):
    conn = get_neo4j_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Neo4j credentials are missing.")
    try:
        from src.agents.ppt_agent import PPTAgent
        from src.presentation.ppt_engine import PPTEngine
        
        agent = PPTAgent(conn)
        slides_json = agent.generate_slides_json(req.concept_name, req.student_id, req.custom_prompt)
        
        if not slides_json:
            raise HTTPException(status_code=500, detail="Failed to generate slide content.")
            
        engine = PPTEngine(output_dir=str(REPO_ROOT / "public" / "presentations"))
        url_path = engine.generate_presentation(slides_json, filename_prefix=req.concept_name)
        
        return {"status": "ok", "ppt_url": url_path}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
