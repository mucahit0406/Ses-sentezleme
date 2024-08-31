import torch
from TTS.api import TTS
from playsound import playsound
import concurrent.futures
import queue
import logging

# Log seviyesini ayarla
logging.getLogger('TTS').setLevel(logging.ERROR)

device = "cuda" if torch.cuda.is_available() else "cpu"

print("Şu an oluşturuluyor")

# TTS modelini yükleme
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

# Giriş metni
text = "Metin Girin "
sentences = text.split('.')

# Ses sentezi ve oynatımını işlemek için bir kuyruk oluştur
audio_queue = queue.Queue()

def synthesize_and_enqueue(sentence, speaker_wav, language, index):
    if sentence.strip():  # Boş olmayan cümleleri işle
        print(f"Processing sentence: {sentence}")
        file_path = f"sentez_{index}.wav"
        tts.tts_to_file(text=sentence, speaker_wav=speaker_wav, language=language, file_path=file_path)
        audio_queue.put(file_path)

def play_audio():
    while True:
        file_path = audio_queue.get()
        if file_path is None:  # Kuyrukta None varsa işlemi sonlandır
            break
        playsound(file_path)

# Ses oynatma iş parçacığı oluştur
player_thread = concurrent.futures.ThreadPoolExecutor().submit(play_audio)

# Her cümleyi sentezleyip kuyruğa ekle
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [executor.submit(synthesize_and_enqueue, sentence, "sentezlenecekses.wav", "tr", i) for i, sentence in enumerate(sentences)]#istediğiniz kişinin sesinden olabildiğince tüm harflerin bulunduğu bir ses kaydı ekleyin nekadar gürültüsüz bir ses koyarsanız sonuçlar okadar iyi olacaktır
    concurrent.futures.wait(futures)

# Kuyruğa None ekle ve oynatıcı iş parçacığının bitmesini bekle
audio_queue.put(None)
player_thread.result()

print("Tüm sesler işlendi ve çalındı.")
