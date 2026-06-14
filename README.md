# Anki Audio Extraction Setup & Documentation

## Overview & Workflow Instructions

* Select the cards in the anki browser you need the audio from, make sure that all the mined sentences also appear in the target audio (for example one all the mined sentences (cards that are selcted) are in the same chapter (for which the audio exists or was arranged))[cite: 9]
* Activate the injection extraction addon and select extraction, and the field "Sentence Plain" in html format with no tags and also with the nids[cite: 9]. Save the tsv somewhere with a fitting name, for example in the same folder where the .ass subtitle file for the chapter and the audio for the chapter is alos located (you then can also name the tsv after the chapter for example)[cite: 9]
* Confirm that the card on the first line in the created tsv is the sentence that chronologicaly appeared first in the lightnovel from all the sentences you selected and the mined sentences in each line of the tsv follow a chronological order, i.e. they also appear successively in the text(otherwise the program might take longer)[cite: 9]
* Create a temporary directroy where you can save the audio also at some location but as a suggestion it could be also in the same location where the just created tsv is[cite: 9]
* Run the python script and follow the instructions extract_ass_audio.py[cite: 9]
* Locate the anki media directory, for example in my case it would be "C:\Users\user\AppData\Roaming\Anki2\User 1\collection.media", move all the audio files from the temporary directory into the media directory[cite: 9]
* Select the same cards you selected earlier again and activate the injection extraction addon again and choose injection, choose for the fields you want to update "Sound Back", select the tsv file that you exported earlier and has beeen modified now again, click yes when you are prompted whether you want to match with the nids[cite: 9].
* The anki cards now have the audio for the mined example sentences[cite: 9]

---

## Technical Documentation: extract_ass_audio.py

### Input / Output Perspective
* **Execution Environment:** Independent execution environment managed through cross-platform graphical user interface (`tkinter`) file explorer dialogs and an interactive terminal menu prompt[cite: 9].
* **Input Files & Location:**
    * **TSV / TXT File:** An exported Anki deck sheet containing target mined sentences[cite: 9]. Location is picked manually via a file dialog[cite: 9].
    * **ASS Subtitle File:** The compiled Advanced SubStation Alpha template containing time-synced dialogue events[cite: 9].
    * **Master Audio File:** The full audio track matching the subtitle timeline (supported formats include `.m4a`, `.mp3`, `.wav`, and `.aac`)[cite: 9].
* **Output Files & Location:**
    * **Updated TSV File:** Modifies the source TSV directly by appending or updating an `Audio` column with `[sound:audio_filename.mp3]` tags matching Anki's native reference format[cite: 9].
    * **Slicing Output Directory:** Generates cut audio segments inside a user-specified destination directory[cite: 9].
    * **Debug Error Log:** Generates a local `debug_missing_matches.log` file in the working directory tracking structural sentence mismatches[cite: 9].
* **Concrete Input Format:**
    * *TSV Format:* Tab-delimited spreadsheet lines[cite: 9]. The sentence lookup column index defaults to index `1` (the second column)[cite: 9].
    * *ASS File Format:* Structural sub-blocks parsing entries containing active dialogue markers (`●`) under the targeted `Text` rendering style layer[cite: 9].

### Core Architecture & Specifications

#### Functionality
This script automates slicing chapter-length master audio files into precise sentence-level `.mp3` clippings tailored for Anki card audio fields[cite: 9]. It cross-references an Anki vocabulary export file (TSV) against a timed subtitle document (`.ass`), isolates corresponding audio frames, processes audio quality filters dynamically, and re-injects standard audio syntax directly back into the spreadsheet[cite: 9].

#### Operation
1. Launch the script via Python[cite: 9].
2. Pick an audio quality profile (1–5) via the command-line interface[cite: 9].
3. Locate the source files (TSV, ASS, Audio) and assign an output folder using the sequential popup windows[cite: 9].
4. The program tracks the matching process via an active visual progress bar[cite: 9]. Any unmatched rows are logged out to `debug_missing_matches.log`[cite: 9].

#### Logic
* **Audio Profile Mapping:** Binds channels (mono/stereo), bitrates (`24k` up to `320k`), and sample rates (`22.05kHz` to `44.1kHz`) according to user performance selections[cite: 9].
* **Text Normalization Engine:** Strips structural HTML brackets, formatting markers (`\N`), visual timing tags (`●`), Japanese punctuation layouts, and maps Katakana sets over to Hiragana equivalence strings via an internal character translation matrix[cite: 9].
* **Chronological Dual-Horizon Search:**
    * *Primary Pointer:* Loops forward linearly through subtitle timestamps from the last confirmed match position to optimize parsing speeds for chronological script configurations[cite: 9].
    * *Secondary Fallback Loop:* Sweeps backward from the beginning of the timeline cache up to the index pointer if an instance lookup fails, handling non-sequential target selections gracefully[cite: 9].
* **Fuzzy String Match Matrix:** Validates strings via `SequenceMatcher` sliding window comparisons to robustly match cropped dialogue blocks against text segments[cite: 9].
* **Hash Serialization:** Generates clean, short file names using MD5 hex hashes (`audio_[10-char-hash].mp3`) built from the normalized sentence to avoid collisions or illegal characters[cite: 9].

#### Special Elements and Ideas
* **Direct Anki-Integration Framework:** Bridges structural media generation directly with spreadsheet fields. By parsing note IDs and updating matching columns in-place, it eliminates manual audio splitting workflows, providing immediate feedback loops when building customized immersion decks[cite: 9].
