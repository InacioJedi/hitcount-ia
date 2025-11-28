import { useEffect, useRef, useState } from "react";
import { Play, Pause, RotateCcw, TimerReset } from "lucide-react";

const STREAM_URL = "http://127.0.0.1:8000/stream";
const HITS_URL = "http://127.0.0.1:8000/hits";

export default function App() {

  // ----------- Placar vindos do backend -----------
  const [verde, setVerde] = useState(0); // lado_verde
  const [vermelho, setVermelho] = useState(0); // lado_vermelho

  // ----------- Cronômetro -----------
  const [seconds, setSeconds] = useState(120);
  const [running, setRunning] = useState(false);
  const timerRef = useRef(null);

  const tick = () => {
    setSeconds((prev) => {
      if (prev <= 0) {
        clearInterval(timerRef.current);
        setRunning(false);
        return 0;
      }
      return prev - 1;
    });
  };

  // 🔥 sincronizado com o backend /play
  const start = async () => {
    if (running) return;
    try {
      await fetch("http://127.0.0.1:8000/play");
    } catch (e) {
      console.error("Erro ao chamar /play:", e);
    }
    timerRef.current = setInterval(tick, 1000);
    setRunning(true);
  };

  // 🔥 sincronizado com o backend /pause
  const pause = async () => {
    try {
      await fetch("http://127.0.0.1:8000/pause");
    } catch (e) {
      console.error("Erro ao chamar /pause:", e);
    }
    clearInterval(timerRef.current);
    setRunning(false);
  };

  // 🔥 sincronizado com o backend /reset (zera vídeo, timer e hits)
  const reset = async () => {
    try {
      await fetch("http://127.0.0.1:8000/reset");
    } catch (e) {
      console.error("Erro ao chamar /reset:", e);
    }
    clearInterval(timerRef.current);
    setRunning(false);
    setSeconds(120);
    // os hits vão zerar sozinhos pelo /hits
  };

  // ----------- Atualiza hits a cada 200ms -----------
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(HITS_URL);
        const data = await res.json();

        setVerde(data.lado_verde ?? 0);
        setVermelho(data.lado_vermelho ?? 0);

      } catch (error) {
        console.error("Erro ao buscar hits:", error);
      }
    }, 200);

    return () => clearInterval(interval);
  }, []);

  // 🔥 chama /start uma vez só pra preparar o backend pausado
  useEffect(() => {
    fetch("http://127.0.0.1:8000/start").catch(() => {});
  }, []);

  // Formatação do cronômetro
  const fmt = (s) =>
    `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(
      2,
      "0"
    )}`;

  // ======================= UI COMPLETA =======================

  return (
    <div className="min-h-screen bg-neutral-950 flex flex-col items-center px-6 py-4"
      style={{ color: "#ffffff" }}
    >

      {/* ======================== PLACAR ======================== */}
      <div className="w-full max-w-6xl mb3">
        <div className="
          w-full flex items-center justify-between
          bg-neutral-900/70 backdrop-blur-xl
          rounded-3xl px-10 py-6 shadow-[0_0_40px_-10px_rgba(0,0,0,0.7)]
          border border-neutral-800
        ">

          {/* 🟥 VERMELHO */}
          <div className="flex flex-col items-center">
            <span className="text-sm tracking-[0.25em] uppercase text-red-400/70">
              Robô Vermelho
            </span>
            <span className="text-[90px] font-bold leading-none text-red-400 drop-shadow-[0_0_12px_rgba(255,0,0,0.4)]">
              {vermelho}
            </span>
            <span className="text-xs tracking-[0.3em] uppercase opacity-60">
              HITS
            </span>
          </div>

          {/* CRONÔMETRO */}
          <div className="flex flex-col items-center gap-3">
            <span className="text-xs tracking-[0.25em] uppercase opacity-70 flex items-center gap-2">
              <TimerReset size={16} /> Cronômetro
            </span>

            <span className="
              text-7xl font-bold tabular-nums leading-none
              text-cyan-300 drop-shadow-[0_0_10px_rgba(0,200,255,0.5)]
            ">
              {fmt(seconds)}
            </span>

            <div className="flex gap-4 mt-2">

              {!running ? (
                <button
                  onClick={start}
                  className="
                    flex items-center gap-2 px-6 py-2
                    rounded-full text-sm font-semibold
                    bg-cyan-600 hover:bg-cyan-500
                    shadow-lg shadow-cyan-500/30
                    border border-cyan-300/60 transition
                  "
                >
                  <Play size={16} /> Iniciar
                </button>
              ) : (
                <button
                  onClick={pause}
                  className="
                    flex items-center gap-2 px-6 py-2
                    rounded-full text-sm font-semibold
                    bg-amber-600 hover:bg-amber-500
                    shadow-lg shadow-amber-500/30
                    border border-amber-300/60 transition
                  "
                >
                  <Pause size={16} /> Pausar
                </button>
              )}

              <button
                onClick={reset}
                className="
                  flex items-center gap-2 px-6 py-2
                  rounded-full text-sm font-medium
                  border border-neutral-500
                  bg-neutral-800 hover:bg-neutral-700
                  transition
                "
              >
                <RotateCcw size={16} /> Reset
              </button>
            </div>
          </div>

          {/* 🟩 VERDE */}
          <div className="flex flex-col items-center">
            <span className="text-sm tracking-[0.25em] uppercase text-green-400/70">
              Robô Verde
            </span>
            <span className="text-[90px] font-bold leading-none text-green-400 drop-shadow-[0_0_12px_rgba(0,255,0,0.4)]">
              {verde}
            </span>
            <span className="text-xs tracking-[0.3em] uppercase opacity-60">
              HITS
            </span>
          </div>

        </div>
      </div>

      {/* ======================== VÍDEO ======================== */}
      <div className="w-full max-w-6xl mt-3">
        <div className="
          bg-neutral-900/70 backdrop-blur-xl
          rounded-3xl p-4 shadow-[0_0_40px_-10px_rgba(0,0,0,0.7)]
          border border-neutral-800
        ">
          <div className="text-sm mb-2 opacity-70 tracking-wide">
            Visão Superior — IA de Identificação de Robôs
          </div>

          <div className="w-full h-[480px] rounded-2xl overflow-hidden bg-black shadow-inner">
            <img
              src={STREAM_URL}
              alt="stream"
              className="w-full h-full object-contain"
            />
          </div>
        </div>
      </div>

    </div>
  );
}
