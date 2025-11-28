import threading
import time
import cv2
import numpy as np
from ultralytics import YOLO


# -------------------- FRAME BUFFER --------------------
class Latest:
    def __init__(self):
        self.frame = None
        self.lock = threading.Lock()

    def set(self, f):
        with self.lock:
            self.frame = f

    def get(self):
        with self.lock:
            return None if self.frame is None else self.frame.copy()


# -------------------- TRACKER + HITS --------------------
class CamWorker(threading.Thread):
    def __init__(
        self,
        src,
        latest: Latest,
        weights: str,
        conf: float,
        hit_state=None,
        hits_map=None,
        detections_callback=None
    ):
        super().__init__(daemon=True)

        self.src = src
        self.latest = latest
        self.conf = conf
        self.hit_state = hit_state
        self.detections_callback = detections_callback

        self.stop_flag = False
        self.paused = True  # 👉 começa PAUSADO

        # YOLO GPU
        self.model = YOLO(weights)
        try:
            self.model.to("cuda")
        except Exception as e:
            print("[WARNING] GPU indisponível → rodando na CPU:", e)

        # =============================
        # 🔥 PROCESSAR hits_rotulados.json
        # hits_map = lista de dicts:
        # { "frame": 170, "robot": "vermelho" }
        # =============================
        self.hit_events = {}      # {frame:int -> [lado_vermelho/lado_verde, ...]}
        if hits_map:
            for item in hits_map:
                f = int(item["frame"])
                # ATENÇÃO: mapeamento que você aprovou (bateu 3x19 certo)
                # robot "vermelho" → lado_verde
                # robot "azul"     → lado_vermelho
                if item["robot"] == "vermelho":
                    side = "lado_verde"
                else:
                    side = "lado_vermelho"
                self.hit_events.setdefault(f, []).append(side)

            print("[OK] Hits carregados:", len(self.hit_events))

        # marca quais hits já foram disparados
        self.fired_hits = set()

        # TRACKING
        self.track = {
            "lado_vermelho": {"center": None, "xyxy": None, "miss": 0},
            "lado_verde": {"center": None, "xyxy": None, "miss": 0},
        }

        self.initialized = False
        self.max_miss = 12
        self.frame_idx = 0

    # -----------------------------------------------------
    @staticmethod
    def smooth(old, new, alpha=0.25):
        if old is None:
            return new
        return (
            old[0] * (1 - alpha) + new[0] * alpha,
            old[1] * (1 - alpha) + new[1] * alpha,
        )

    @staticmethod
    def dist(a, b):
        return float(np.linalg.norm(np.subtract(a, b)))

    # -----------------------------------------------------
    def update_track(self, name, det):
        cx, cy = det["center"]
        x1, y1, x2, y2 = det["xyxy"]

        t = self.track[name]
        t["center"] = self.smooth(t["center"], (cx, cy))
        t["xyxy"] = (x1, y1, x2, y2)
        t["miss"] = 0

    # -----------------------------------------------------
    def update_tracks(self, dets):
        if len(dets) == 0:
            for name in self.track:
                self.track[name]["miss"] += 1
            return

        # ---- Inicialização ----
        if not self.initialized and len(dets) >= 2:
            left, right = sorted(dets[:2], key=lambda d: d["center"][0])
            self.update_track("lado_vermelho", left)
            self.update_track("lado_verde", right)
            self.initialized = True
            return

        if not self.initialized:
            return

        vr_center = self.track["lado_vermelho"]["center"]
        vg_center = self.track["lado_verde"]["center"]

        assigned = {"lado_vermelho": False, "lado_verde": False}

        if len(dets) == 1:
            d = dets[0]
            cx, cy = d["center"]

            d_r = self.dist((cx, cy), vr_center)
            d_g = self.dist((cx, cy), vg_center)

            if d_r <= d_g:
                self.update_track("lado_vermelho", d)
                assigned["lado_vermelho"] = True
            else:
                self.update_track("lado_verde", d)
                assigned["lado_verde"] = True

        else:
            d0, d1 = dets[:2]
            c0, c1 = d0["center"], d1["center"]

            # custo de associação
            d0_r = self.dist(c0, vr_center)
            d1_r = self.dist(c1, vr_center)
            d0_g = self.dist(c0, vg_center)
            d1_g = self.dist(c1, vg_center)

            cost1 = d0_r + d1_g
            cost2 = d0_g + d1_r

            if cost1 <= cost2:
                self.update_track("lado_vermelho", d0)
                self.update_track("lado_verde", d1)
            else:
                self.update_track("lado_vermelho", d1)
                self.update_track("lado_verde", d0)

            assigned["lado_vermelho"] = True
            assigned["lado_verde"] = True

        # incrementar miss de quem não recebeu detecção
        for name in self.track:
            if not assigned[name]:
                self.track[name]["miss"] += 1

    # -----------------------------------------------------
    # 🔥 CONTAGEM DE HITS COM TOLERÂNCIA ±3 FRAMES
    #    MAS CADA HIT SÓ CONTA UMA VEZ
    # -----------------------------------------------------
    def apply_hits_for_frame(self):
        if not self.hit_state:
            return

        for frame_hit, sides in self.hit_events.items():
            if frame_hit in self.fired_hits:
                continue

            # tolerância para compensar variação de FPS
            if abs(self.frame_idx - frame_hit) <= 3:
                for side in sides:
                    self.hit_state.add_hit(side)
                self.fired_hits.add(frame_hit)

    # -----------------------------------------------------
    def stop(self):
        self.stop_flag = True

    # -----------------------------------------------------
    def run(self):
        cap = cv2.VideoCapture(self.src)
        self.frame_idx = 0

        if not cap.isOpened():
            print("[ERRO] Não conseguiu abrir o vídeo:", self.src)
            return

        print("[OK] Vídeo carregado:", self.src)

        while not self.stop_flag:
            # PAUSADO → não avança frame
            if self.paused:
                time.sleep(0.03)
                continue

            ok, frame = cap.read()
            if not ok:
                break

            # YOLO GPU
            results = self.model(
                frame, conf=self.conf, imgsz=960, verbose=False, device="cuda"
            )

            dets = []
            for r in results:
                for b in r.boxes:
                    x1, y1, x2, y2 = map(int, b.xyxy[0].tolist())
                    cx = (x1 + x2) / 2
                    cy = (y1 + y2) / 2
                    dets.append({"xyxy": (x1, y1, x2, y2), "center": (cx, cy)})

            dets = sorted(dets, key=lambda d: d["center"][0]) if dets else dets
            self.update_tracks(dets)

            # desenhar caixas idênticas
            for name, t in self.track.items():
                if t["xyxy"] and t["miss"] <= self.max_miss:
                    x1, y1, x2, y2 = t["xyxy"]
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)

            # aplica hits rotulados
            self.apply_hits_for_frame()

            # envia ao stream
            self.latest.set(frame)

            cv2.waitKey(1)
            self.frame_idx += 1

        cap.release()
