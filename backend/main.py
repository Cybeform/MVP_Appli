# backend/main.py

import os
import uuid
import datetime
import json

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware


from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from fastapi import FastAPI, Depends, Body
from auth import validate_code, verify_token


from meeting_transcription import (
    start_recording,
    stop_recording,
    transcribe_with_progress,
)

# —————————————————————————————————————————
# App & CORS
# —————————————————————————————————————————

app = FastAPI()

# --- 1) Validation du code ---
@app.post("/validate-code")
def api_validate_code(code: str = Body(..., embed=True)):
    token = validate_code(code)
    return {"token": token}

# Monte le dossier "static" pour servir favicon.ico et autres assets
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")),
    name="static",
)

# Juste après vos imports et avant vos autres routes, ajoutez :
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    # renvoie le fichier static/favicon.ico sans passer par le proxy CRA
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "favicon.ico"))


origins = [
    "https://jazzy-truffle-4ada47.netlify.app",
    "https://6835df33c3c24a844b437e2b--jazzy-truffle-4ada47.netlify.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://mvpappli-production.up.railway.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # autorise ce(s) domaine(s)
    allow_credentials=True,
    allow_methods=["*"],         # GET, POST, OPTIONS…
    allow_headers=["*"],         # Content-Type, Authorization…
)

# —————————————————————————————————————————
# Stockage en mémoire des enregistrements
# —————————————————————————————————————————

# Structure: { id: { wav: str, docx: str | None, date: datetime, duration: str | None } }
RECORDINGS = {}

# —————————————————————————————————————————
# 1) Démarrage / arrêt de l’enregistrement live
# —————————————————————————————————————————

@app.post("/api/start-recording", dependencies=[Depends(verify_token)])
async def api_start():
    rec_id = str(uuid.uuid4())
    wav_path = os.path.join("recordings", f"{rec_id}.wav")
    os.makedirs("recordings", exist_ok=True)
    RECORDINGS[rec_id] = {
        "wav": wav_path,
        "docx": None,
        "date": datetime.datetime.utcnow(),
        "duration": None
    }
    start_recording(output_file=wav_path)
    return {"id": rec_id}


@app.post("/api/stop-recording", dependencies=[Depends(verify_token)])
async def api_stop(id: str):
    rec = RECORDINGS.get(id)
    if not rec:
        raise HTTPException(404, "ID inconnu")
    stop_recording()
    rec["duration"] = "∞"
    return {"id": id}


# —————————————————————————————————————————
# 2) Upload d’un fichier audio existant
# —————————————————————————————————————————

@app.post("/api/upload", dependencies=[Depends(verify_token)])
async def api_upload(file: UploadFile = File(...)):
    rec_id = str(uuid.uuid4())
    wav_path = os.path.join("recordings", f"{rec_id}.wav")
    os.makedirs("recordings", exist_ok=True)
    content = await file.read()
    with open(wav_path, "wb") as f:
        f.write(content)
    RECORDINGS[rec_id] = {
        "wav": wav_path,
        "docx": None,
        "date": datetime.datetime.utcnow(),
        "duration": None
    }
    return {"id": rec_id}


# —————————————————————————————————————————
# 3) Liste des enregistrements
# —————————————————————————————————————————

@app.get("/api/recordings", dependencies=[Depends(verify_token)])
async def api_list():
    out = []
    for rec_id, meta in sorted(RECORDINGS.items(),
                               key=lambda x: x[1]["date"],
                               reverse=True):
        out.append({
            "id": rec_id,
            "title": f"Réunion {rec_id[:8]}",
            "date": meta["date"].strftime("%Y-%m-%d %H:%M"),
            "duration": meta["duration"] or "?"
        })
    return JSONResponse(out)


# —————————————————————————————————————————
# 4) SSE pour progression de génération du rapport
# —————————————————————————————————————————

@app.get("/api/generate-report-stream/{id}", dependencies=[Depends(verify_token)])
def generate_report_stream(id: str):
    rec = RECORDINGS.get(id)
    if not rec or not os.path.exists(rec["wav"]):
        raise HTTPException(404, "Enregistrement introuvable")

    def event_generator():
        gen = transcribe_with_progress(rec["wav"])
        while True:
            try:
                # on récupère un événement de progression
                progress = next(gen)
                yield f"data: {json.dumps(progress)}\n\n"
            except StopIteration as stop:
                # fin normale du générateur : on récupère le path
                _, _, docx_path = stop.value
                rec["docx"] = docx_path
                done_event = {"phase": "done", "path": docx_path}
                yield f"data: {json.dumps(done_event)}\n\n"
                break
            except Exception as e:
                # toute autre erreur : on la signale au client
                err = {"phase": "error", "message": str(e)}
                yield f"data: {json.dumps(err)}\n\n"
                break

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# —————————————————————————————————————————
# 5) Téléchargement du rapport final
# —————————————————————————————————————————

@app.get("/api/download-report/{id}", dependencies=[Depends(verify_token)])
def download_report(id: str):
    rec = RECORDINGS.get(id)
    if not rec or not rec.get("docx") or not os.path.exists(rec["docx"]):
        raise HTTPException(404, "Rapport introuvable")
    return FileResponse(
        path=rec["docx"],
        filename=f"report-{id}.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


# —————————————————————————————————————————
# 6) Alias routes sans "/api" pour compatibilité
# —————————————————————————————————————————

@app.post("/start-recording", include_in_schema=False)
async def start_recording_root():
    return await api_start()

@app.post("/stop-recording", include_in_schema=False)
async def stop_recording_root(id: str):
    return await api_stop(id)

@app.post("/upload", include_in_schema=False)
async def upload_root(file: UploadFile = File(...)):
    return await api_upload(file)

@app.get("/recordings", include_in_schema=False)
async def recordings_root():
    return await api_list()

@app.get("/generate-report-stream/{id}", include_in_schema=False)
def generate_report_stream_root(id: str):
    return generate_report_stream(id)

@app.get("/download-report/{id}", include_in_schema=False)
def download_report_root(id: str):
    return download_report(id)
