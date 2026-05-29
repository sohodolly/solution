# Solution (working title)

> Interactive game platform for creating a digital phantom of a specific person based on real data: chats, voice messages, photos.

**Status:** Concept · MVP development until August 2026 · Private demo for investors

---

## 🧠 Concept

Solution lets users recreate a **digital double** of a person:
- Appearance based on photos (2D/3D)
- Communication style based on real chats (lexicon, tone, topics)
- Voice based on voice messages (future stage)

The product is positioned as an **interactive game with personalization elements** — not as a medical or psychological service.

### Unique Selling Proposition
- Chat style reconstruction via LLM fine-tuned on real conversations
- 3D face generation from photos (planned for stage 2)
- Voice cloning (planned for stage 2)
- Subscription + in-game economy (gifts, clothes, achievements)

---

## 🎯 Target Audience (Premium Segment)
- Willing to pay from $200/month
- Low price sensitivity
- High loyalty when engaged

---

## 🏗 Architecture & Development Stages

### Stage 1 (until August 2026) — text chat, 2D avatar, data collection
- Parse chats (Telegram, WhatsApp) → structured JSON (text + metadata for voice/photo)
- Local LLM (Llama 3 / Mistral) fine-tuned on the person’s style
- Web interface: chat, photo upload, 2D avatar
- No public subscription — closed demo for investors/team

**Tech stack:**
- Parser: Python (Telethon, Pyrogram)
- Backend: Python + FastAPI
- LLM inference: vLLM or llama.cpp
- Frontend: HTML/CSS/JS + WebSocket
- Storage: local encrypted files

### Stage 2 (autumn 2026 – spring 2027) — voice + 3D face + subscription
- Speech synthesis (TTS cloning from voice samples)
- 3D face generation from photo (DECA or similar)
- Subscription & in-game currency

### Stage 3 (2027–2028) — full 3D generation, video calls
- Automatic body & clothing generation
- Lip sync with voice
- International scaling

---

## 🔒 Privacy & Security

- **Encryption:** AES-256-GCM (client + server)
- Keys derived from user password (PBKDF2) — never stored in plaintext on server
- TLS 1.3 for all data in transit
- Access to production servers — limited to authorized members, fully logged
- All backups encrypted, stored offline

> All team members signed a 2‑year NDA.

---

## ⚖️ Legal Strategy (short version)

- Officially positioned as an **interactive game with personalization**
- Terms of Use explicitly state:
  - No medical or psychological services
  - All emotional consequences are the user’s responsibility
  - Subscription auto-renews, cancellable via personal account
  - In-game currency has no real-world value
  - Data collection only with explicit user consent

---

## 🗓 Roadmap to August 2026

| Period | Tasks |
|--------|-------|
| Apr–May | • Messengers parsing research (Telegram, WhatsApp)<br>• Parser → structured JSON<br>• Landing page + simple web chat<br>• Test JSON for one persona |
| June | • Local LLM integration (Llama 3 / Mistral)<br>• Backend (FastAPI) for web demo<br>• First end‑to‑end test: user → web → LLM → response |
| July | • Frontend improvements (avatar, basic animations)<br>• Video demo recording<br>• Investor presentation (focus on USP)<br>• Ethical public legend prepared |
| August | • Closed demo for potential investors<br>• Feedback collection & critical fixes<br>• Draft Terms of Use (with external lawyer)<br>• Waiting list & investment prep for stage 2 |

---

## ⚠️ Risks & Mitigation

| Risk | Mitigation |
|------|-------------|
| Delay of deadlines | Strict scope (text + 2D only), weekly syncs |
| Legal claims | Game wrapper, clear Terms of Use, external lawyer |
| Data breach | Encryption, limited access, NDA, logging |
| Team conflict | Fixed roles, open decision-making |
| High complexity of 3D | Stage 1 uses only 2D; 3D outsourced if needed |

---

## 📁 Repository structure (planned)
solution/
├── parser/ # Telegram/WhatsApp → JSON
├── backend/ # FastAPI + LLM inference
├── frontend/ # HTML/CSS/JS chat + 2D avatar
├── data/ # encrypted user data (gitignored)
├── docs/ # internal docs, Terms of Use drafts
└── README.md


---

## 👥 Team (public summary)

- **Project lead & web development** — strategy, parsing, coordination  
- **ML / Python** — ML pipelines, LLM + backend integration  
- **LLM & AI** — model selection, fine‑tuning, inference optimization  
- **Psychologist / ethics advisor** — risk assessment, public legend  
- **Generalist developer** — frontend, server admin, automation  

> Full roles and responsibilities defined internally. All members signed NDA.

---

## 🚀 Getting Started (for internal development)

> No public deployment yet. The following instructions are for team members.

1. Clone the repo  
2. Set up Python 3.11+ environment  
3. Install dependencies: `pip install -r requirements.txt`  
4. Run parser to generate JSON from exported chat  
5. Launch LLM inference server (vLLM/llama.cpp)  
6. Start FastAPI backend: `uvicorn main:app --reload`  
7. Open frontend `index.html`  

---

## 📄 License

Proprietary — all rights reserved.  
Not open for public use or redistribution without written permission.

---

## 📬 Contacts

For investors and partnership inquiries:  
*(contact information provided separately, not in public repo)*

---

*Last updated: March 26, 2026*
