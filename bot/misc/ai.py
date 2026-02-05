
from vosk import Model, KaldiRecognizer
import wave, json, os


def recognizeaudio(path):
    # Укажите путь до распакованной модели
    model_path = r"bot/misc/vosk-model-small-ru-0.22"
    model = Model(model_path)

    wf = wave.open(path, "rb")
    rec = KaldiRecognizer(model, wf.getframerate())

    text = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            text.append(res.get("text", ""))

    res = json.loads(rec.FinalResult())
    text.append(res.get("text", ""))

    return(" ".join(text))