# Anki Audio Extraction Setup & Documentation

## Disclaimer

The python scripts will probably not run on your system unless you installed all the right packages, some of them might only be supported for older pyhton versions (Python 3.12), debug with AI and install the required packages as needed.

## Overview & Workflow Instructions

* **Select the cards** in the Anki browser you need the audio from. Make sure that all the mined sentences also appear in the target audio (for example, ensuring all selected cards belong to the same chapter for which the audio exists or was arranged).
* **Activate the injection extraction addon** and select "Extraction". Choose the field `Sentence Plain` in HTML format with no tags, and include the Note IDs (`nids`). Save the TSV file somewhere with a fitting name, for example in the same folder where the `.ass` subtitle file and the audio for the chapter are located (you can name the TSV after the chapter, for instance).
* **Confirm chronological order:** Ensure that the card on the first line in the created TSV is the sentence that chronologically appeared first in the light novel out of all the sentences you selected. The mined sentences in each line of the TSV should follow a chronological order (i.e., they appear successively in the text), otherwise the program might take longer to process.
* **Create a temporary directory** where you can temporarily save the extracted audio. As a suggestion, this could be in the same location where the newly created TSV file resides.
* **Run the Python script** `extract_ass_audio.py` and follow the on-screen instructions.
* **Locate the Anki media directory** (for example: `C:\Users\user\AppData\Roaming\Anki2\User 1\collection.media`) and move all the generated audio files from the temporary directory into this media directory.
* **Inject the audio back into Anki:** Select the exact same cards you selected earlier, activate the injection extraction addon again, and choose "Injection". For the fields you want to update, choose `Sound Back`. Select the TSV file that you exported earlier (which has now been modified by the script). Click "Yes" when prompted whether you want to match using the Note IDs (`nids`).
* The Anki cards will now successfully have the audio attached to the mined example sentences.

---

## Technical Documentation: extract_ass_audio.py

### Input / Output Perspective
* **Execution Environment:** Independent execution environment managed through cross-platform graphical user interface (`tkinter`) file explorer dialogs and an interactive terminal menu prompt.
* **Input Files & Location:**
    * **TSV / TXT File:** An exported Anki deck sheet containing target mined sentences. The location is picked manually via a file dialog.
    * **ASS Subtitle File:** The compiled Advanced SubStation Alpha template containing time-synced dialogue events.
    * **Master Audio File:** The full audio track matching the subtitle timeline (supported formats include `.m4a`, `.mp3`, `.wav`, and `.aac`).
* **Output Files & Location:**
    * **Updated TSV File:** Modifies the source TSV directly by appending or updating an `Audio` column with `[sound:audio_filename.mp3]` tags matching Anki's native reference format.
    * **Slicing Output Directory:** Generates cut audio segments inside a user-specified destination directory.
    * **Debug Error Log:** Generates a local `debug_missing_matches.log` file in the working directory tracking structural sentence mismatches.
* **Concrete Input Format:**
    * *TSV Format:* Tab-delimited spreadsheet lines. The sentence lookup column index defaults to index `1` (the second column).
    * *ASS File Format:* Structural sub-blocks parsing entries containing active dialogue markers (`●`) under the targeted `Text` rendering style layer.

### Core Architecture & Specifications

#### Functionality
This script automates slicing chapter-length master audio files into precise sentence-level `.mp3` clippings tailored for Anki card audio fields. It cross-references an Anki vocabulary export file (TSV) against a timed subtitle document (`.ass`), isolates corresponding audio frames, processes audio quality filters dynamically, and re-injects standard audio syntax directly back into the spreadsheet.

#### Operation
1. Launch the script via Python (`python extract_ass_audio.py`).
2. Pick an audio quality profile (1–5) via the command-line interface.
3. Locate the source files (TSV, ASS, Audio) and assign an output folder using the sequential popup windows.
4. The program tracks the matching process via an active visual progress bar. Any unmatched rows are logged out to `debug_missing_matches.log`.

#### Logic
* **Audio Profile Mapping:** Binds channels (mono/stereo), bitrates (`24k` up to `320k`), and sample rates (`22.05kHz` to `44.1kHz`) according to user performance selections.
* **Text Normalization Engine:** Strips structural HTML brackets, formatting markers (`\N`), visual timing tags (`●`), Japanese punctuation layouts, and maps Katakana sets over to Hiragana equivalence strings via an internal character translation matrix.
* **Chronological Dual-Horizon Search:**
    * *Primary Pointer:* Loops forward linearly through subtitle timestamps from the last confirmed match position to optimize parsing speeds for chronological script configurations.
    * *Secondary Fallback Loop:* Sweeps backward from the beginning of the timeline cache up to the index pointer if an instance lookup fails, handling non-sequential target selections gracefully.
* **Fuzzy String Match Matrix:** Validates strings via `SequenceMatcher` sliding window comparisons to robustly match cropped dialogue blocks against text segments.
* **Hash Serialization:** Generates clean, short file names using MD5 hex hashes (`audio_[10-char-hash].mp3`) built from the normalized sentence to avoid collisions or illegal characters.

#### Special Elements and Ideas
* **Direct Anki-Integration Framework:** Bridges structural media generation directly with spreadsheet fields. By parsing note IDs and updating matching columns in-place, it eliminates manual audio splitting workflows, providing immediate feedback loops when building customized immersion decks.
