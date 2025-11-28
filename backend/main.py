from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import time
import json

from detector import CamWorker, Latest
from hit_state import HitState

app = FastAPI(title="HitCount IA", version="1.0")

# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# PATHS DO PROJETO
# -----------------------------
VIDEO_SRC = r"C:\Users\inaci\Desktop\TCC CORRETO\data\luta.mp4"
WEIGHTS = r"C:\Users\inaci\Desktop\TCC CORRETO\runs\detect\train_duas_cores\weights\best.pt"
HITS_FILE = r"C:\Users\inaci\Desktop\TCC CORRETO\data\hits_rotulados.json"

# -----------------------------
# ESTADOS
# -----------------------------
latest = Latest()
hit_state = HitState()
worker: CamWorker | None = None


def create_worker(conf: float = 0.5):
    """
    Cria um novo worker, já pausado no frame inicial,
    com hits resetados e mapa de hits carregado.
    """
    global worker, hit_state

    hit_state.reset()

    try:
        with open(HITS_FILE, "r", encoding="utf-8") as f:
            hits_list = json.load(f)  # lista de {frame, robot}
        print(f"[OK] Arquivo de hits carregado: {len(hits_list)} entradas")
    except Exception as e:
        print("[ERRO] Falha ao ler hits_rotulados.json:", e)
        hits_list = []

    worker = CamWorker(
        src=VIDEO_SRC,
        latest=latest,
        weights=WEIGHTS,
        conf=conf,
        hit_state=hit_state,
        hits_map=hits_list,
    )
    worker.paused = True  # começa pausado
    worker.start()


# -----------------------------
# START → apenas cria o worker pausado
# -----------------------------
@app.get("/start")
def start(conf: float = 0.5):
    global worker
    if worker is None:
        create_worker(conf)
        return {"started": True, "paused": True}
    return {"running": True, "paused": worker.paused}


# -----------------------------
# PLAY → libera o loop (sync com timer no front)
# -----------------------------
@app.get("/play")
def play():
    global worker
    if worker is None:
        create_worker(0.5)
    worker.paused = False
    return {"playing": True}


# -----------------------------
# PAUSE → congela o avanço de frames
# -----------------------------
@app.get("/pause")
def pause():
    global worker
    if worker is not None:
        worker.paused = True
        return {"paused": True}
    return {"paused": False, "reason": "no worker"}


# -----------------------------
# RESET → para tudo, zera hits, volta pro frame inicial
# -----------------------------
@app.get("/reset")
def reset(conf: float = 0.5):
    global worker, latest

    if worker is not None:
        worker.stop()
        worker = None

    # limpa frame atual
    latest.set(None)

    # recria worker pausado e zera hits
    create_worker(conf)
    return {"reset": True}


# -----------------------------
# STOP (se precisar encerrar geral)
# -----------------------------
@app.get("/stop")
def stop():
    global worker
    if worker:
        worker.stop()
        worker = None
    hit_state.reset()
    latest.set(None)
    return {"stopped": True}


# -----------------------------
# STREAM (MJPEG)
# -----------------------------
def mjpeg_stream():
    while True:
        frame = latest.get()

        if frame is None:
            time.sleep(0.01)
            continue

        ok, jpg = cv2.imencode(".jpg", frame)
        if not ok:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            jpg.tobytes() +
            b"\r\n"
        )


@app.get("/stream")
def stream():
    return StreamingResponse(
        mjpeg_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


# -----------------------------
# /hits → usado pelo frontend
# -----------------------------
@app.get("/hits")
def get_hits():
    return hit_state.get_counts()


# -----------------------------
# /debug_frame
# -----------------------------
@app.get("/debug_frame")
def debug_frame():
    frame = latest.get()
    if frame is None:
        return {"status": "no frame"}

    try:
        h, w, c = frame.shape
        return {"status": "ok", "shape": [h, w, c]}
    except:
        return {"status": "ok", "shape": "unknown"}


@app.get("/")
def root():
    return {"status": "backend alive"}
