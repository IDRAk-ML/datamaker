# import os
# import random
# import hashlib
# from datetime import datetime

# import pandas as pd
# import soundfile as sf  # noqa: F401  # (imported so you can post‑process audio later if desired)
# import streamlit as st
# from audio_recorder_streamlit import audio_recorder

# # -----------------------------------------------------------------------------
# # Constants & one‑time folder setup
# # -----------------------------------------------------------------------------

# DATA_DIR = "csvs_data"
# AUDIO_DIR = "audios"
# METADATA_FILE = os.path.join(AUDIO_DIR, "metadata.csv")

# os.makedirs(DATA_DIR, exist_ok=True)
# os.makedirs(AUDIO_DIR, exist_ok=True)

# # -----------------------------------------------------------------------------
# # Streamlit session‑state initialisation
# # -----------------------------------------------------------------------------

# def _init_session_state():
#     """Populate all keys the app will use so they always exist."""
#     defaults = {
#         "sentences": [],  # list of [text, domain, source_file, source_row]
#         "audio_bytes": None,
#         "current_sentence": None,
#         "current_domain": None,
#         "current_source_file": None,
#         "current_source_row": None,
#         "speaker": "",  # user‑supplied speaker id
#     }
#     for k, v in defaults.items():
#         if k not in st.session_state:
#             st.session_state[k] = v


# _init_session_state()

# # -----------------------------------------------------------------------------
# # Helpers for loading & saving
# # -----------------------------------------------------------------------------

# def load_sentences_into_session() -> None:
#     """Read every CSV in *csvs_data/* and cache rows in *st.session_state["sentences"]*.

#     Each element is `[text, domain, source_file, source_row]`.
#     """
#     if st.session_state["sentences"]:
#         return  # already loaded

#     sentences: list[list[str, str, str, int]] = []
#     for file_name in os.listdir(DATA_DIR):
#         if not file_name.lower().endswith(".csv"):
#             continue
#         file_path = os.path.join(DATA_DIR, file_name)
#         df = pd.read_csv(file_path)
#         if {"text", "domain"}.issubset(df.columns):
#             for idx, row in df.dropna(subset=["text", "domain"]).iterrows():
#                 sentences.append([row["text"], row["domain"], file_name, idx])
#     st.session_state["sentences"] = sentences


# def load_recorded_hashes() -> set[str]:
#     """Return set of *record_id* values already present in *metadata.csv*."""
#     if not os.path.exists(METADATA_FILE):
#         return set()
#     df = pd.read_csv(METADATA_FILE)
#     return set(df["record_id"].astype(str))


# def save_metadata(
#     *,
#     sentence: str,
#     domain: str,
#     filename: str,
#     speaker: str,
#     source_file: str,
#     source_row: int,
# ) -> None:
#     """Append a row to *metadata.csv* with the supplied information."""
#     record_id = hashlib.sha256(f"{sentence}{speaker}".encode()).hexdigest()

#     metadata = {
#         "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         "speaker": speaker,
#         "sentence": sentence,
#         "domain": domain,
#         "source_file": source_file,
#         "source_row": source_row,
#         "filename": filename,
#         "record_id": record_id,
#     }

#     if os.path.exists(METADATA_FILE):
#         df = pd.read_csv(METADATA_FILE)
#         df = pd.concat([df, pd.DataFrame([metadata])], ignore_index=True)
#     else:
#         df = pd.DataFrame([metadata])
#     df.to_csv(METADATA_FILE, index=False)


# # -----------------------------------------------------------------------------
# # UI pages
# # -----------------------------------------------------------------------------

# def upload_csv_page() -> None:
#     st.title("📄 Upload CSVs for Sentences")

#     uploaded_files = st.file_uploader(
#         "Upload one or more CSV files (must contain 'text' and 'domain' columns)",
#         type=["csv"],
#         accept_multiple_files=True,
#     )

#     if not uploaded_files:
#         st.info("No files selected yet.")
#         return

#     new_sentences: list[list[str, str, str, int]] = []
#     for uploaded_file in uploaded_files:
#         file_path = os.path.join(DATA_DIR, uploaded_file.name)
#         with open(file_path, "wb") as f:
#             f.write(uploaded_file.getbuffer())

#         df = pd.read_csv(file_path)
#         if {"text", "domain"}.issubset(df.columns):
#             for idx, row in df.dropna(subset=["text", "domain"]).iterrows():
#                 new_sentences.append([row["text"], row["domain"], uploaded_file.name, idx])
#             st.success(f"Uploaded ✓ {uploaded_file.name}")
#         else:
#             st.error(f"❌ {uploaded_file.name} missing required columns 'text' and/or 'domain'.")

#     # extend cached list (avoid re‑reading disk until app restarts)
#     st.session_state["sentences"].extend(new_sentences)


# def record_voice_page() -> None:
#     st.title("🎤 Record Your Voice")

#     # Require speaker ID first
#     if not st.session_state["speaker"].strip():
#         st.error("👤 Please enter your speaker ID in the sidebar before recording.")
#         return
#     speaker = st.session_state["speaker"].strip()

#     # Load sentence list & previously recorded hashes
#     load_sentences_into_session()
#     sentences = st.session_state["sentences"]
#     recorded_hashes = load_recorded_hashes()

#     if not sentences:
#         st.warning("No sentences available! Please upload CSVs first.")
#         return

#     # Filter out sentences this speaker already recorded
#     available_sentences: list[list[str, str, str, int]] = [
#         (text, domain, src_file, src_row)
#         for text, domain, src_file, src_row in sentences
#         if hashlib.sha256(f"{text}{speaker}".encode()).hexdigest() not in recorded_hashes
#     ]

#     if not available_sentences:
#         st.success("🎉 You have recorded all available sentences for this speaker!")
#         return

#     # If no active sentence, pick one at random
#     if not st.session_state["current_sentence"]:
#         text, domain, src_file, src_row = random.choice(available_sentences)
#         st.session_state.update(
#             {
#                 "current_sentence": text,
#                 "current_domain": domain,
#                 "current_source_file": src_file,
#                 "current_source_row": src_row,
#             }
#         )

#     # Pull current values from session
#     text = st.session_state["current_sentence"]
#     domain = st.session_state["current_domain"]
#     src_file = st.session_state["current_source_file"]
#     src_row = st.session_state["current_source_row"]

#     # --- Display sentence & metadata ---
#     st.markdown("### 🗣️ Please say this sentence:")
#     st.markdown(f"> **{text}**")
#     st.markdown(f"**Domain:** {domain}")
#     st.caption(f"Source: {src_file} – row {src_row}")

#     # --- Record audio ---
#     st.write("🎙️ Press the record button to start/stop:")
#     audio_bytes = audio_recorder()
#     if audio_bytes:
#         st.session_state["audio_bytes"] = audio_bytes

#     # --- If a recording is present, let user listen/save/skip ---
#     if st.session_state["audio_bytes"] is not None:
#         st.success("✅ Recording finished! Listen below:")
#         st.audio(st.session_state["audio_bytes"], format="audio/wav")

#         save_col, skip_col = st.columns(2)

#         with save_col:
#             if st.button("💾 Save Recording"):
#                 timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#                 text_hash = hashlib.sha256(text.encode()).hexdigest()[:8]
#                 filename = f"{timestamp}_{speaker}_{text_hash}.wav"
#                 file_path = os.path.join(AUDIO_DIR, filename)

#                 # write bytes
#                 with open(file_path, "wb") as f:
#                     f.write(st.session_state["audio_bytes"])

#                 # save metadata row
#                 save_metadata(
#                     sentence=text,
#                     domain=domain,
#                     filename=filename,
#                     speaker=speaker,
#                     source_file=src_file,
#                     source_row=src_row,
#                 )

#                 st.success(f"🎉 Recording saved as {filename}")

#                 # Reset for next round
#                 for key in (
#                     "audio_bytes",
#                     "current_sentence",
#                     "current_domain",
#                     "current_source_file",
#                     "current_source_row",
#                 ):
#                     st.session_state[key] = None if key == "audio_bytes" else ""
#                 st.rerun()

#         with skip_col:
#             if st.button("⏭️ Skip Sentence"):
#                 st.warning("Skipped this sentence.")
#                 for key in (
#                     "audio_bytes",
#                     "current_sentence",
#                     "current_domain",
#                     "current_source_file",
#                     "current_source_row",
#                 ):
#                     st.session_state[key] = None if key == "audio_bytes" else ""
#                 st.rerun()


# # -----------------------------------------------------------------------------
# # Sidebar – speaker id & navigation
# # -----------------------------------------------------------------------------

# with st.sidebar:
#     st.session_state["speaker"] = st.text_input(
#         "Speaker ID / Name (required)",
#         value=st.session_state.get("speaker", ""),
#         placeholder="e.g. alice_01",
#         key="speaker_input",
#     )

#     page = st.selectbox("Go to", ("Upload CSVs", "Record Data"), key="page_select")

# # -----------------------------------------------------------------------------
# # Page router
# # -----------------------------------------------------------------------------

# if page == "Upload CSVs":
#     upload_csv_page()
# elif page == "Record Data":
#     record_voice_page()
import os
import random
import hashlib
from datetime import datetime

import pandas as pd
import soundfile as sf  # noqa: F401
import streamlit as st
from audio_recorder_streamlit import audio_recorder

# -----------------------------------------------------------------------------
# Constants & folder setup
# -----------------------------------------------------------------------------

DATA_DIR = "csvs_data"
AUDIO_DIR = "audios"
METADATA_FILE = os.path.join(AUDIO_DIR, "metadata.csv")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# Session‑state initialisation
# -----------------------------------------------------------------------------

def _init_session_state():
    """Populate all keys the app will use so they always exist."""
    defaults = {
        "sentences": [],  # list[ text, domain, source_file, source_row ]
        "audio_bytes": None,
        "current_sentence": None,
        "current_domain": None,
        "current_source_file": None,
        "current_source_row": None,
        "speaker": "",  # user‑supplied speaker id
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init_session_state()

# -----------------------------------------------------------------------------
# Helpers for loading & saving
# -----------------------------------------------------------------------------

def load_sentences_into_session() -> None:
    """Read every CSV in *csvs_data/* and cache rows in session."""
    if st.session_state["sentences"]:
        return
    sentences: list[list[str, str, str, int]] = []
    for file_name in os.listdir(DATA_DIR):
        if not file_name.lower().endswith(".csv"):
            continue
        file_path = os.path.join(DATA_DIR, file_name)
        df = pd.read_csv(file_path)
        if {"text", "domain"}.issubset(df.columns):
            for idx, row in df.dropna(subset=["text", "domain"]).iterrows():
                sentences.append([row["text"], row["domain"], file_name, idx])
    st.session_state["sentences"] = sentences


def load_recorded_hashes() -> set[str]:
    if not os.path.exists(METADATA_FILE):
        return set()
    df = pd.read_csv(METADATA_FILE)
    return set(df["record_id"].astype(str))


def save_metadata(*, sentence: str, domain: str, filename: str, speaker: str, source_file: str, source_row: int) -> None:
    record_id = hashlib.sha256(f"{sentence}{speaker}".encode()).hexdigest()
    metadata = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "speaker": speaker,
        "sentence": sentence,
        "domain": domain,
        "source_file": source_file,
        "source_row": source_row,
        "filename": filename,
        "record_id": record_id,
    }
    if os.path.exists(METADATA_FILE):
        df = pd.read_csv(METADATA_FILE)
        df = pd.concat([df, pd.DataFrame([metadata])], ignore_index=True)
    else:
        df = pd.DataFrame([metadata])
    df.to_csv(METADATA_FILE, index=False)

# -----------------------------------------------------------------------------
# Page 1 – Upload CSVs
# -----------------------------------------------------------------------------

def upload_csv_page() -> None:
    st.title("📄 Upload CSVs for Sentences")

    uploaded_files = st.file_uploader(
        "Upload one or more CSV files (must contain 'text' and 'domain' columns)",
        type=["csv"],
        accept_multiple_files=True,
    )

    if not uploaded_files:
        st.info("No files selected yet.")
        return

    new_sentences: list[list[str, str, str, int]] = []
    for uploaded_file in uploaded_files:
        file_path = os.path.join(DATA_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        df = pd.read_csv(file_path)
        if {"text", "domain"}.issubset(df.columns):
            for idx, row in df.dropna(subset=["text", "domain"]).iterrows():
                new_sentences.append([row["text"], row["domain"], uploaded_file.name, idx])
            st.success(f"Uploaded ✓ {uploaded_file.name}")
        else:
            st.error(f"❌ {uploaded_file.name} missing required columns 'text' and/or 'domain'.")

    st.session_state["sentences"].extend(new_sentences)

# -----------------------------------------------------------------------------
# Page 2 – Record Voice
# -----------------------------------------------------------------------------

def record_voice_page() -> None:
    st.title("🎤 Record Your Voice")

    if not st.session_state["speaker"].strip():
        st.error("👤 Please enter your speaker ID in the sidebar before recording.")
        return
    speaker = st.session_state["speaker"].strip()

    load_sentences_into_session()
    sentences = st.session_state["sentences"]
    recorded_hashes = load_recorded_hashes()

    if not sentences:
        st.warning("No sentences available! Please upload CSVs first.")
        return

    available_sentences = [
        (text, domain, src_file, src_row)
        for text, domain, src_file, src_row in sentences
        if hashlib.sha256(f"{text}{speaker}".encode()).hexdigest() not in recorded_hashes
    ]

    if not available_sentences:
        st.success("🎉 You have recorded all available sentences for this speaker!")
        return

    if not st.session_state["current_sentence"]:
        text, domain, src_file, src_row = random.choice(available_sentences)
        st.session_state.update(
            {
                "current_sentence": text,
                "current_domain": domain,
                "current_source_file": src_file,
                "current_source_row": src_row,
            }
        )

    text = st.session_state["current_sentence"]
    domain = st.session_state["current_domain"]
    src_file = st.session_state["current_source_file"]
    src_row = st.session_state["current_source_row"]

    st.markdown("### 🗣️ Please say this sentence:")
    st.markdown(f"> **{text}**")
    st.markdown(f"**Domain:** {domain}")
    st.caption(f"Source: {src_file} – row {src_row}")

    st.write("🎙️ Press the record button to start/stop:")
    audio_bytes = audio_recorder(pause_threshold=10.0,energy_threshold=(-1.0, 1.0),)
    if audio_bytes:
        st.session_state["audio_bytes"] = audio_bytes

    if st.session_state["audio_bytes"] is not None:
        st.success("✅ Recording finished! Listen below:")
        st.audio(st.session_state["audio_bytes"], format="audio/wav")

        save_col, skip_col = st.columns(2)
        with save_col:
            if st.button("💾 Save Recording"):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                text_hash = hashlib.sha256(text.encode()).hexdigest()[:8]
                filename = f"{timestamp}_{speaker}_{text_hash}.wav"
                file_path = os.path.join(AUDIO_DIR, filename)
                with open(file_path, "wb") as f:
                    f.write(st.session_state["audio_bytes"])
                save_metadata(
                    sentence=text,
                    domain=domain,
                    filename=filename,
                    speaker=speaker,
                    source_file=src_file,
                    source_row=src_row,
                )
                st.success(f"🎉 Recording saved as {filename}")
                for key in (
                    "audio_bytes",
                    "current_sentence",
                    "current_domain",
                    "current_source_file",
                    "current_source_row",
                ):
                    st.session_state[key] = None if key == "audio_bytes" else ""
                st.rerun()
        with skip_col:
            if st.button("⏭️ Skip Sentence"):
                st.warning("Skipped this sentence.")
                for key in (
                    "audio_bytes",
                    "current_sentence",
                    "current_domain",
                    "current_source_file",
                    "current_source_row",
                ):
                    st.session_state[key] = None if key == "audio_bytes" else ""
                st.rerun()

# -----------------------------------------------------------------------------
# Page 3 – Show Audio Metadata
# -----------------------------------------------------------------------------

def show_metadata_page() -> None:
    st.title("📑 Audio Metadata")

    if not os.path.exists(METADATA_FILE):
        st.info("No recordings yet.")
        return

    df = pd.read_csv(METADATA_FILE)
    if df.empty:
        st.info("No recordings yet.")
        return

    speakers = ["All"] + sorted(df["speaker"].dropna().unique().tolist())
    selected_speaker = st.selectbox("Filter by speaker", speakers)
    if selected_speaker != "All":
        df = df[df["speaker"] == selected_speaker]

    st.dataframe(df, use_container_width=True)

    csv_bytes = df.to_csv(index=False).encode()
    st.download_button("Download filtered CSV", csv_bytes, "metadata_filtered.csv", mime="text/csv")

# -----------------------------------------------------------------------------
# Sidebar – speaker id & navigation
# -----------------------------------------------------------------------------

with st.sidebar:
    st.session_state["speaker"] = st.text_input(
        "Speaker ID / Name (required)",
        value=st.session_state.get("speaker", ""),
        placeholder="e.g. alice_01",
        key="speaker_input",
    )
    page = st.selectbox("Go to", ("Upload CSVs", "Record Data", "Metadata"), key="page_select")

# -----------------------------------------------------------------------------
# Page router
# -----------------------------------------------------------------------------

if page == "Upload CSVs":
    upload_csv_page()
elif page == "Record Data":
    record_voice_page()
else:  # Metadata
    show_metadata_page()
