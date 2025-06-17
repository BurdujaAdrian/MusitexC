from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import subprocess
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/run")
async def run_code(request: Request):
    data = await request.json()
    editor_content = data.get("content", "")
    with open("code.txt", "w", encoding="utf-8") as f:
        f.write(editor_content)
    return {"status": "saved", "length": len(editor_content)}

@app.post("/api/compile")
async def compile_code():
    midi_file = "output.mid"
    try:
        result = subprocess.run(
            ["python", "../python_stuff/compiler.py", "code.txt", midi_file],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return JSONResponse(
                status_code=400,
                content={"error": result.stderr, "output.txt": result.stdout}
            )
        if os.path.exists(midi_file):
            return FileResponse(midi_file, media_type="audio/midi", filename=midi_file)
        else:
            return JSONResponse(
                status_code=500,
                content={"error": "MIDI file was not created.", "output.txt": result.stdout}
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        ) 