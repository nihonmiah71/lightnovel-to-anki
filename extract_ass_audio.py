import os
import re
import csv
import hashlib
import sys
import tkinter as tk
from tkinter import filedialog
from pydub import AudioSegment
from difflib import SequenceMatcher
from datetime import datetime

# ---- CONFIGURATION ----
SENTENCE_COLUMN = 1  # Index 1 = Second column (where the example sentence is in your TSV)
MATCH_THRESHOLD = 0.45  # The baseline threshold from align87.py
LOG_FILE_NAME = "debug_missing_matches.log"
# -----------------------

def get_audio_quality_settings():
    """Prompts the user in the console to select the desired audio quality."""
    print("=" * 60)
    print(" SELECT AUDIO QUALITY")
    print("=" * 60)
    print(" [1] Best Quality (Lossless / Highest Bitrate - Stereo, 44.1kHz, 320k)")
    print(" [2] High Quality (Stereo, 44.1kHz, 192k)")
    print(" [3] Good Quality (Standard - Stereo, 44.1kHz, 128k)")
    print(" [4] Low Quality (Mono, 22.05kHz, 64k)")
    print(" [5] Lowest Quality (Very Compact - Mono, 22.05kHz, 24k)")
    print("=" * 60)
    
    while True:
        choice = input("Please select a quality level (1-5): ").strip()
        if choice in ["1", "2", "3", "4", "5"]:
            break
        print("Invalid input. Please enter a number from 1 to 5.")

    # Define quality profiles
    if choice == "1":
        return {"channels": 2, "frame_rate": 44100, "bitrate": "320k", "format": "mp3"}
    elif choice == "2":
        return {"channels": 2, "frame_rate": 44100, "bitrate": "192k", "format": "mp3"}
    elif choice == "3":
        return {"channels": 2, "frame_rate": 44100, "bitrate": "128k", "format": "mp3"}
    elif choice == "4":
        return {"channels": 1, "frame_rate": 22050, "bitrate": "64k", "format": "mp3"}
    elif choice == "5":
        return {"channels": 1, "frame_rate": 22050, "bitrate": "24k", "format": "mp3"}

def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=40, fill='█'):
    """Generates a visual progress bar in the console."""
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '░' * (length - filled_length)
    sys.stdout.write(f'\r{prefix} [{bar}] {percent}% {suffix}')
    sys.stdout.flush()
    if iteration == total:
        print()

def log_failed_match(row_idx, raw_sentence, normalized_sentence, ass_blocks):
    """Writes clean and useful debug information to the log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    scored_blocks = []

    for block in ass_blocks:
        matcher = SequenceMatcher(None, normalized_sentence, block['text'])
        ratio = matcher.ratio()
        scored_blocks.append({'block': block, 'ratio': ratio})
    
    scored_blocks.sort(key=lambda x: x['ratio'], reverse=True)
    top_matches = scored_blocks[:3]
    
    with open(LOG_FILE_NAME, "a", encoding="utf-8") as log_file:
        log_file.write("="*80 + "\n")
        log_file.write(f"[{timestamp}] NO MATCH FOUND FOR ROW {row_idx}\n")
        log_file.write("="*80 + "\n")
        log_file.write(f"Original TSV Text: {raw_sentence}\n")
        log_file.write(f"Normalized TSV Text: {normalized_sentence}\n\n")
        log_file.write("Top 3 most similar ASS blocks in chapter:\n")
        log_file.write(f"{'Start Time':<12} | {'Ratio':<6} | {'Normalized ASS Text'}\n")
        log_file.write("-" * 80 + "\n")
        
        for item in top_matches:
            block = item['block']
            ratio = item['ratio']
            total_secs = block['start'] / 1000
            h = int(total_secs // 3600)
            m = int((total_secs % 3600) // 60)
            s = int(total_secs % 60)
            ms = int(block['start'] % 1000)
            time_str = f"{h:01d}:{m:02d}:{s:02d}.{ms//10:02d}"
            log_file.write(f"{time_str:<12} | {ratio:.4f} | {block['text']}\n")
        log_file.write("\n\n")

def select_files_via_explorer():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    print("Please select your TSV file...")
    tsv_path = filedialog.askopenfilename(
        title="1. Select TSV File",
        filetypes=[("TSV Files", "*.tsv *.txt"), ("All Files", "*.*")]
    )
    if not tsv_path:
        return None, None, None, None

    print("Please select your ASS subtitle file...")
    ass_path = filedialog.askopenfilename(
        title="2. Select ASS Subtitle File",
        filetypes=[("ASS Subtitles", "*.ass"), ("All Files", "*.*")]
    )
    if not ass_path:
        return None, None, None, None

    print("Please select your M4A audio file...")
    media_path = filedialog.askopenfilename(
        title="3. Select M4A Audio File",
        filetypes=[("Audio Files", "*.m4a *.mp3 *.wav *.aac"), ("All Files", "*.*")]
    )
    if not media_path:
        return None, None, None, None

    print("Please select the output directory for the audio cuts (or create a new one)...")
    output_dir = filedialog.askdirectory(
        title="4. Select Audio Output Directory"
    )
    if not output_dir:
        return None, None, None, None

    return tsv_path, ass_path, media_path, output_dir

def ass_time_to_ms(time_str):
    try:
        parts = time_str.strip().split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds_parts = parts[2].split('.')
        seconds = int(seconds_parts[0])
        
        frac_str = seconds_parts[1]
        if len(frac_str) == 2:
            ms = int(frac_str) * 10
        elif len(frac_str) == 3:
            ms = int(frac_str)
        else:
            ms = int(frac_str[:3].ljust(3, '0'))
            
        return (hours * 3600 + minutes * 60 + seconds) * 1000 + ms
    except Exception:
        return None

def normalize_text(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\{[^}]+\}', '', text)
    text = re.sub(r'\\N', '', text)
    text = re.sub(r'\\n', '', text)
    text = text.replace('●', '')
    
    text = re.sub(r'[\s+、。！？「」『』()（）.,!?\-=_+*⑨<>█░…·•\"\'’]', '', text)
    
    katakana = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポァィゥェォッャュョ"
    hiragana = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんがぎぐげござじずぜぞだづづでどばびぶべぼぱぴぷぺぽぁぃぅぇぉっゃゅょ"
    
    trans = str.maketrans(katakana, hiragana)
    text = text.translate(trans)
    
    return text.strip()

def window_search_match(tsv_text, ass_text, min_ratio=0.55):
    if not tsv_text or not ass_text:
        return False
        
    if len(ass_text) <= len(tsv_text):
        return SequenceMatcher(None, tsv_text, ass_text).ratio() >= MATCH_THRESHOLD

    window_size = len(tsv_text)
    best_ratio = 0.0
    
    for i in range(len(ass_text) - window_size + 1):
        sub_str = ass_text[i:i+window_size]
        ratio = SequenceMatcher(None, tsv_text, sub_str).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            if best_ratio >= 0.80:
                return True
                
    return best_ratio >= min_ratio

def is_single_block_match(tsv_sentence, block):
    """Checks if a TSV line matches a single ASS segment."""
    if SequenceMatcher(None, tsv_sentence, block['text']).ratio() >= MATCH_THRESHOLD:
        return True
    if tsv_sentence in block['text'] or block['text'] in tsv_sentence:
        return True
    if window_search_match(tsv_sentence, block['text'], min_ratio=0.50):
        return True
    return False

def parse_ass_file(ass_path):
    """Parses the .ass file and automatically merges overlapping/simultaneous lines."""
    temp_blocks = {}
    if not os.path.exists(ass_path):
        return []

    with open(ass_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if line.startswith("Dialogue:"):
                parts = line.split(",", 9)
                if len(parts) == 10:
                    start_str = parts[1]
                    end_str = parts[2]
                    style = parts[3].strip()
                    text_content = parts[9]
                    
                    if style.lower() == 'text' and '●' in text_content:
                        start_ms = ass_time_to_ms(start_str)
                        end_ms = ass_time_to_ms(end_str)
                        
                        if start_ms is not None and end_ms is not None:
                            time_key = (start_ms, end_ms)
                            if time_key in temp_blocks:
                                temp_blocks[time_key] += " " + text_content
                            else:
                                temp_blocks[time_key] = text_content
    
    blocks = []
    for (start_ms, end_ms), raw_text in temp_blocks.items():
        blocks.append({
            'start': start_ms,
            'end': end_ms,
            'text': normalize_text(raw_text)
        })
    blocks.sort(key=lambda x: x['start'])  # Ensure chronological sorting
    return blocks

def main():
    # Ask for audio quality settings at the very beginning
    quality = get_audio_quality_settings()
    
    tsv_path, ass_path, media_path, output_dir = select_files_via_explorer()
    if not tsv_path:
        print("Operation cancelled.")
        return

    os.makedirs(output_dir, exist_ok=True)
    
    print("\nLoading subtitles (ASS)...")
    ass_blocks = parse_ass_file(ass_path)
    if not ass_blocks:
        print("No active text blocks found. Aborting.")
        return
    
    print(f"Successfully loaded {len(ass_blocks)} merged subtitle segments.")
    
    print("Loading main audio file (M4A)...")
    try:
        full_audio = AudioSegment.from_file(media_path)
    except Exception as e:
        print(f"Error loading audio file: {e}")
        return

    generated_audios_cache = {}
    rows = []
    with open(tsv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter='\t')
        try:
            header = next(reader)
        except StopIteration:
            return
        for row in reader:
            rows.append(row)

    if 'Audio' in header:
        audio_idx = header.index('Audio')
    else:
        header.append('Audio')
        audio_idx = len(header) - 1
        for row in rows:
            row.append('')

    print("\nProcessing TSV rows and cutting audio...")
    failed_matches_count = 0
    total_rows = len(rows)

    # Initial progress bar setup
    print_progress_bar(0, total_rows, prefix='Progress:', suffix=f'(0/{total_rows} rows)', length=40)

    # Chronological search pointer
    last_match_index = 0
    num_ass_blocks = len(ass_blocks)

    for i, row in enumerate(rows):
        current_row_num = i + 2  # For accurate error reporting (+2 due to header)
        
        if len(row) <= SENTENCE_COLUMN:
            print_progress_bar(i + 1, total_rows, prefix='Progress:', suffix=f'({i + 1}/{total_rows} rows)', length=40)
            continue
            
        raw_sentence = row[SENTENCE_COLUMN]
        normalized_tsv_sentence = normalize_text(raw_sentence)
        
        if not normalized_tsv_sentence:
            print_progress_bar(i + 1, total_rows, prefix='Progress:', suffix=f'({i + 1}/{total_rows} rows)', length=40)
            continue

        if normalized_tsv_sentence in generated_audios_cache:
            row[audio_idx] = f"[sound:{generated_audios_cache[normalized_tsv_sentence]}]"
            print_progress_bar(i + 1, total_rows, prefix='Progress:', suffix=f'({i + 1}/{total_rows} rows)', length=40)
            continue

        found_block = None
        found_at_idx = -1

        # 1. Chronological Search: Look forward from the last known position
        for idx in range(last_match_index, num_ass_blocks):
            if is_single_block_match(normalized_tsv_sentence, ass_blocks[idx]):
                found_block = ass_blocks[idx]
                found_at_idx = idx
                break

        # 2. Fallback Search: If nothing found forward, scan missed section from the beginning
        if found_block is None and last_match_index > 0:
            for idx in range(0, last_match_index):
                if is_single_block_match(normalized_tsv_sentence, ass_blocks[idx]):
                    found_block = ass_blocks[idx]
                    found_at_idx = idx
                    break

        # If no match was found at all
        if found_block is None:
            sys.stdout.write("\n")
            print(f"Row {current_row_num}: No match found for '{raw_sentence[:20]}...' (Logged to file)")
            log_failed_match(current_row_num, raw_sentence, normalized_tsv_sentence, ass_blocks)
            failed_matches_count += 1
            print_progress_bar(i + 1, total_rows, prefix='Progress:', suffix=f'({i + 1}/{total_rows} rows)', length=40)
            continue

        # Update pointer to the found position for the next iteration
        last_match_index = found_at_idx
        
        start_time = found_block['start']
        end_time = found_block['end']
        
        text_hash = hashlib.md5(normalized_tsv_sentence.encode('utf-8')).hexdigest()[:10]
        audio_filename = f"audio_{text_hash}.mp3"
        output_path = os.path.join(output_dir, audio_filename)

        if not os.path.exists(output_path):
            audio_segment = full_audio[start_time:end_time]
            
            # Dynamic adjustment based on user selection
            audio_segment = audio_segment.set_channels(quality["channels"])
            audio_segment = audio_segment.set_frame_rate(quality["frame_rate"])
            
            audio_segment.export(
                output_path, 
                format=quality["format"], 
                bitrate=quality["bitrate"]
            )

        generated_audios_cache[normalized_tsv_sentence] = audio_filename
        row[audio_idx] = f"[sound:{audio_filename}]"
        
        # Update progress bar
        print_progress_bar(i + 1, total_rows, prefix='Progress:', suffix=f'({i + 1}/{total_rows} rows)', length=40)

    with open(tsv_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(header)
        writer.writerows(rows)

    print(f"\n=== EXPORT SUCCESSFUL ===")
    print(f"The TSV file has been completely updated.")
    print(f"Number of unmatched rows: {failed_matches_count}")
    if failed_matches_count > 0:
        print(f"You can find detailed information in the file: {LOG_FILE_NAME}")

if __name__ == "__main__":
    main()