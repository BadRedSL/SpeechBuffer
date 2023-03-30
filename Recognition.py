import pyaudio
import wave
import nemo.collections.asr as nemo_asr
import language_tool_python
import torch
import win32clipboard


class Recognition:

    def __init__(self):
        self.__CHUNK = 1024
        self.__FORMAT = pyaudio.paInt16
        self.__CHANNELS = 1
        self.__RATE = 16000
        self.__OUTPUT_FILENAME = "processed_audio.wav"
        self.__AUDIO_PATH = f"./{self.__OUTPUT_FILENAME}"

        self.__sber_quartzNet = nemo_asr.models.EncDecCTCModel.restore_from("./ZMv")

    def record(self, is_recording: list[bool,]):
        p = pyaudio.PyAudio()

        stream = p.open(format=self.__FORMAT,
                        channels=self.__CHANNELS,
                        rate=self.__RATE,
                        input=True,
                        frames_per_buffer=self.__CHUNK)

        print("* recording")

        frames = []

        while is_recording[0]:
            data = stream.read(self.__CHUNK)
            frames.append(data)

        print("* done recording")

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(self.__OUTPUT_FILENAME, 'wb')
        wf.setnchannels(self.__CHANNELS)
        wf.setsampwidth(p.get_sample_size(self.__FORMAT))
        wf.setframerate(self.__RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

    def __recognize_ru(self) -> str:
        files = [self.__AUDIO_PATH]
        transcripts = self.__sber_quartzNet.transcribe(paths2audio_files=files)
        print("* done transcribing")
        return transcripts[0]

    @staticmethod
    def __spelling_correction_ru(text: str) -> str:
        tool = language_tool_python.LanguageTool('ru-RU')
        corrected_text = tool.correct(text)
        print("* done spell correction")
        return corrected_text

    @staticmethod
    def __punctuation_correction_ru(text: str) -> str:
        model, example_texts, languages, punct, apply_te = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                                                          model='silero_te')
        text_with_punctuation = apply_te(text.lower(), lan='ru')
        print("* done punctuation correction")
        return text_with_punctuation

    def recognize_speech_ru(self) -> str:
        transcript = self.__recognize_ru()
        corrected_text = self.__spelling_correction_ru(transcript)
        text_with_punctuation = self.__punctuation_correction_ru(corrected_text)
        print("* done speech recognize")
        return text_with_punctuation

    @staticmethod
    def copy_to_clipboard(text: str):
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
        print("* done copy to clipboard")
