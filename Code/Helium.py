import numpy as np
import soundfile as sf
import pyworld as pw
import torch
import torch.nn.functional as F

def voice2hel(audio):
    fs = 16000
    formant_multiplier = 1.2
    audio = input_wav(audio.astype(float), fs, formant_multiplier)
    return audio
def input_wav(audio, fs, formant_multiplier):
    f0, sp, ap = pw.wav2world(audio, fs)
    sp = envelope_stretch(sp, formant_multiplier)

    audio = pw.synthesize(f0, sp, ap, fs)
    audio = audio.astype(np.float32)
    return audio
def envelope_stretch(sp, formant_multiplier):
    sp = sp.transpose()
    sp = torch.FloatTensor(sp).unsqueeze(0)

    n_rows = sp.shape[-2]
    sp = F.interpolate(sp.unsqueeze(1), size=(int(n_rows * formant_multiplier), sp.shape[-1])).squeeze(1)
    sp = sp[:, :n_rows, :]

    sp = sp.squeeze(0).numpy().astype(np.float64)
    sp = np.ascontiguousarray(sp.transpose())
    return sp