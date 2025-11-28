# 🤖 HitCount IA — Sistema de Detecção de Robôs e Contagem Automática de Hits em Combates

Projeto de TCC desenvolvido para automatizar a **detecção de robôs de combate** e a **contabilização de hits** utilizando visão computacional, redes neurais e um painel de controle em tempo real no navegador.

O sistema integra:

- 🧠 **IA (YOLOv8)** treinada para identificar robôs e reconhecer impactos (hits)  
- 🎥 **Processamento de vídeo em tempo real** (visão superior ou câmeras gravadas)  
- 🌐 **Backend FastAPI** para stream e cálculo de hits  
- ⚡ **Frontend React + Vite + Tailwind** com placar, cronômetro e vídeo ao vivo  

---

## 📌 Sumário

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Tecnologias Utilizadas](#tecnologias-utilizadas)
4. [Como Executar o Projeto](#como-executar-o-projeto)
   - [Backend (Python/FastAPI)](#backend)
   - [Frontend (React/Vite)](#frontend)
5. [Fluxo de Funcionamento](#fluxo-de-funcionamento)
6. [Modelos de IA](#modelos-de-ia)
7. [Estrutura de Pastas](#estrutura-de-pastas)
8. [Contribuição](#contribuição)
9. [Licença](#licença)

---

# 📘 **Visão Geral**

O **HitCount IA** foi desenvolvido para solucionar um problema real em competições de robôs:  
a dificuldade de contabilizar impactos com precisão durante o combate.

A solução utiliza **inteligência artificial** para rastrear os robôs e identificar hits automaticamente, exibindo tudo em um painel simples e profissional, com:

- Contagem de hits em tempo real  
- Placar dos dois robôs (Verde x Vermelho)  
- Cronômetro sincronizado com o vídeo  
- Stream ou vídeo local  
- Interface moderna e responsiva  

---

# 🏗️ Arquitetura do Sistema

┌────────────────────┐ HTTP ┌─────────────────────┐
│ YOLOv8 Detector │ <───────────────> │ Frontend React │
│ (Python + FastAPI) │ API / Stream │ (Placar + Cronômetro) │
└────────────────────┘ └─────────────────────┘
▲
│ Processamento de vídeo
▼
Arquivo .mp4 ou câmera

# 🛠️ Tecnologias Utilizadas

### **Backend**
- Python 3.11
- FastAPI
- OpenCV
- Ultralytics YOLOv8
- WebSocket / Streaming MJPEG

### **Frontend**
- React + Vite
- TailwindCSS
- Lucide Icons
- Polling e sincronização com backend

---

# 🚀 Como Executar o Projeto

## 🔧 Backend

### 1️⃣ Criar ambiente virtual
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
2️⃣ Instalar dependências

pip install -r requirements.txt
3️⃣ Executar o backend

uvicorn main:app --reload
Backend sobe por padrão em:

http://127.0.0.1:8000
🎨 Frontend
1️⃣ Instalar dependências
cd frontend
npm install
2️⃣ Rodar o servidor
npm run dev
Frontend normalmente roda em:
http://localhost:5173
🔄 Fluxo de Funcionamento
Backend abre o vídeo (câmera ou arquivo)

YOLO detecta posição dos robôs

HitState.py calcula hits com base em distância, aceleração e colisões

Frontend exibe hits e placar

Cronômetro sincroniza com o backend (opcional)

Painel mostra a luta em tempo real

🧠 Modelos de IA
O sistema utiliza dois modelos YOLOv8:

Detector — identifica cada robô no frame

Classificador de Hits — reconhece impactos

Dataset criado com rotulagem manual

Treinamentos feitos em GPUs Colab

Os arquivos .pt não são incluídos no repositório por tamanho.

📁 Estrutura de Pastas
TCC_CORRETO/
│
├── backend/
│   ├── data/
│   │   ├── hits_rotulados.json
│   │   ├── robo_vermelho_ref.png
│   │   ├── robo_azul_ref.png
│   ├── detector.py
│   ├── hit_state.py
│   ├── main.py
│   ├── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── index.css
│   │   ├── main.jsx
│   ├── public/
│   ├── package.json
│   ├── tailwind.config.js
│
└── README.md
🤝 Contribuição
Pull requests são bem-vindos!
Sugestões de melhorias na IA, UX do painel ou otimizações do backend são especialmente úteis.

📜 Licença
Distribuído sob MIT License.

🎖️ Créditos
Projeto desenvolvido por Inácio Felipe Tomazelli — Engenharia de Software
Universidade Católica de Santa Catarina
Equipe WickedBotz 🤖🔥
