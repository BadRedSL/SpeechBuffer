import pyaudio
import wave
import nemo.collections.asr as nemo_asr
import language_tool_python
import torch
import win32clipboard
import textblob as tb


class Recognition:

    def __init__(self):
        self.__CHUNK = 1024
        self.__FORMAT = pyaudio.paInt16
        self.__CHANNELS = 1
        self.__RATE = 16000
        self.__OUTPUT_FILENAME = "processed_audio.wav"
        self.__AUDIO_PATH = f"./{self.__OUTPUT_FILENAME}"

        self.__sber_quartzNet = nemo_asr.models.EncDecCTCModel.restore_from("./ZMv")
        self.__nemo_quartzNet = nemo_asr.models.ASRModel.from_pretrained(model_name="QuartzNet15x5Base-En")

        self.__correction_tool_ru = language_tool_python.LanguageTool('ru-RU')

        _, _, _, _, self.__apply_te = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                                     model='silero_te')

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

    def __recognize(self, language: str) -> str:
        files = [self.__AUDIO_PATH]
        if language == "ru":
            transcripts = self.__sber_quartzNet.transcribe(paths2audio_files=files)
        else:
            transcripts = self.__nemo_quartzNet.transcribe(paths2audio_files=files)
        print("* done transcribing")
        return transcripts[0]

    def __spelling_correction(self, text: str, language: str) -> str:
        if language == "ru":
            corrected_text = self.__correction_tool_ru.correct(text)
        else:
            tool = tb.TextBlob(text)
            corrected_text = tool.correct()
        print("* done spell correction")
        return corrected_text

    def __punctuation_correction(self, text: str, language: str) -> str:
        if language == "ru":
            text_with_punctuation = self.__apply_te(text.lower(), lan='ru')
        else:
            text_with_punctuation = self.__apply_te(text.lower(), lan='en')
        print("* done punctuation correction")
        return text_with_punctuation

    def recognize_speech(self, language: str) -> str:
        transcript = self.__recognize(language)
        corrected_text = self.__spelling_correction(transcript, language)
        text_with_punctuation = self.__punctuation_correction(corrected_text, language)
        print("* done speech recognize")
        return text_with_punctuation

    @staticmethod
    def copy_to_clipboard(text: str):
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
        print("* done copy to clipboard")


if __name__ == "__main__":
    recognition = Recognition()

    original_text_ru = "Худое, истощенное, желтоватое лицо его было все покрыто крупными морщинами, которые всегда" \
                       " казались так чистоплотно и старательно промыты, как кончики пальцев после бани."

    text_ru = "xудое истащенное желтаватое лицо его было все покрыто крупными морщинами которые всегда казались так" \
              " чистоплотна и старательно промыты, как кончики пальцев после бани"

    original_text_eng = "His thin, emaciated, yellowish face was all covered with large wrinkles, which always seemed" \
                        " to be so cleanly and diligently washed, like fingertips after a bath."

    text_eng = "his thin emaciated yellowish face was al covered with large wrinkles which always seemed" \
               " to be so clealy and diligently washed like fingertips after a bath"

    print(recognition._Recognition__spelling_correction(text_eng, "en"))
    print(recognition._Recognition__punctuation_correction(text_eng, "en"))
