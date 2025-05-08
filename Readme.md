
# Voice‑Recorder Streamlit App

A lightweight web tool for collecting high‑quality speech data per sentence, per speaker. Upload a corpus of prompts (text + domain), record each prompt exactly once for each speaker, and download structured metadata in one click.

**Live demo** → [https://asrtraining.idrakanywhere.com/](https://asrtraining.idrakanywhere.com/)

---

## ✨ Key features

| Feature                     | Details                                                                                                                                         |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **CSV upload**              | Drag‑and‑drop multiple CSV files containing **`text`** and **`domain`** columns. Rows are merged into one queue.                                |
| **Speaker tracking**        | Enter a speaker ID in the sidebar; the app guarantees each *speaker × sentence* pair is recorded only once.                                     |
| **In‑browser recorder**     | Uses `audio_recorder_streamlit` to capture microphone audio—no external tools needed.                                                           |
| **Instant playback & save** | Listen before you commit. Saved WAV files are named with timestamp + speaker + hash.                                                            |
| **Rich metadata**           | Every save appends a row to `audios/metadata.csv` (timestamp, speaker, sentence, domain, source‑file, row number, filename, SHA‑256 record ID). |
| **Progress awareness**      | Prompts that are already recorded by the current speaker are automatically skipped on reload.                                                   |
| **Metadata viewer**         | Built‑in page to filter metadata by speaker and download the subset as CSV.                                                                     |

---

## 🏁 Quick start (local)

```bash
# 1. Clone
git clone <repo‑url> voice‑recorder
cd voice‑recorder

# 2. Create env & install deps
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Run
streamlit run voice_recorder_app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

### Requirements

* Python ≥ 3.9
* **Packages** (also in `requirements.txt`)

  * `streamlit`
  * `pandas`
  * `soundfile`
  * `audio_recorder_streamlit`

If `soundfile` complains about libsndfile, install it via your OS package manager (e.g. `brew install libsndfile` or `apt-get install libsndfile1`).

---

## 🖥️ Using the web demo

1. Go to **Upload CSVs** and add your prompt files.
   *Required columns:* `text`, `domain` (anything else is ignored).
2. In the sidebar, enter a **Speaker ID** (e.g. `alice_01`).
3. Switch to **Record Data**. A sentence appears—read it, click the **record** mic, click again to stop.
4. **Save Recording** (or **Skip**). The next prompt auto‑loads until all are done.
5. View your work in **Metadata** → filter by speaker if needed, download CSV.

> **Note:** The public demo is ephemeral. For production collection you should self‑host or add authentication.

---

## 🗂 Project structure

```
voice_recorder_app.py   # main Streamlit script
csvs_data/              # uploaded prompt files (*.csv)
audios/                 # recorded WAVs + metadata
└── metadata.csv        # grows with each save
```

`metadata.csv` schema:

| column        | type | description                               |
| ------------- | ---- | ----------------------------------------- |
| `timestamp`   | str  | yyyy‑mm‑dd HH\:MM\:SS (server local time) |
| `speaker`     | str  | ID typed in sidebar                       |
| `sentence`    | str  | the full text prompt                      |
| `domain`      | str  | domain column from CSV                    |
| `source_file` | str  | CSV filename prompt came from             |
| `source_row`  | int  | row index inside that CSV                 |
| `filename`    | str  | WAV filename saved under `audios/`        |
| `record_id`   | str  | SHA‑256 of `speaker+sentence`             |

---

## 🛠️ Extending the app

| Idea                     | Hint                                                                  |
| ------------------------ | --------------------------------------------------------------------- |
| **Progress bar**         | `len(recorded)/len(total)` per speaker.                               |
| **Waveform/level meter** | Use `streamlit-webrtc` or render with `matplotlib`.                   |
| **Database backend**     | Swap CSV for SQLite or PostgreSQL for concurrency.                    |
| **Authentication**       | Protect uploads & recordings with Streamlit Cloud secrets or a proxy. |

PRs & suggestions welcome!

---

## 📄 License

MIT. See `LICENSE` for details.
