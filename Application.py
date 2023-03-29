from tkinter import Tk, Text, Button, Scrollbar, Frame
from Recognition import Recognition
import threading

is_recording = [False, ]


class Application:

    def __init__(self):
        self.__language = "ru"

        self.__window_height = 550
        self.__window_width = 400
        self.__frame_txt_height = 300
        self.__frame_btn_height = self.__window_height - self.__frame_txt_height
        self.__btn_height = 2
        self.__font = "Arial 12"

        self.__window = Tk()
        self.__window.title("SpeechBuffer")
        self.__window.geometry(f"{self.__window_width}x{self.__window_height}")

        self.__frame_txt = Frame(master=self.__window, borderwidth=1, relief="solid", height=self.__frame_txt_height)
        self.__frame_txt.pack(anchor="n", fill="both", padx=5, pady=5, expand=True)

        self.__frame_btn = Frame(master=self.__window, borderwidth=1, relief="solid", height=self.__frame_btn_height)
        self.__frame_btn.pack(anchor="s", fill="both", padx=5, pady=5, expand=True)

        self.__txt = Text(self.__frame_txt, font=self.__font)
        self.__txt.pack(anchor="center", fill="both", expand=True, side="top")

        self.__scroll = Scrollbar(master=self.__txt, orient="vertical", command=self.__txt.yview)
        self.__scroll.pack(side="right", fill="y")

        self.__btn_record = Button(master=self.__frame_btn, text="Запись", command=self.__clicked_btn_record,
                                   height=self.__btn_height)
        self.__btn_record.pack(anchor="center", fill="x", expand=True, side="bottom")

        self.__btn_stop_record = Button(master=self.__frame_btn, text="Стоп", command=self.__clicked_btn_stop_record,
                                        height=self.__btn_height, state="disabled")
        self.__btn_stop_record.pack(anchor="center", fill="x", expand=True, side="bottom", before=self.__btn_record)

        self.__btn_lang_ru = Button(master=self.__frame_btn, text="Русский", command=self.__clicked_btn_lang_ru,
                                    height=self.__btn_height, state="disabled")
        self.__btn_lang_ru.pack(anchor="center", fill="x", expand=True, side="bottom", before=self.__btn_stop_record)

        self.__btn_lang_eng = Button(master=self.__frame_btn, text="Английский", command=self.__clicked_btn_lang_eng,
                                     height=self.__btn_height)
        self.__btn_lang_eng.pack(anchor="center", fill="x", expand=True, side="bottom", before=self.__btn_lang_ru)

        self.__recognition = Recognition()
        self.__thread = threading.Thread()

    def __clicked_btn_record(self):
        self.__txt.delete(0.0, "end")
        self.__btn_record.config(state='disabled')
        self.__btn_stop_record.config(state='normal')
        global is_recording
        is_recording[0] = True
        self.__thread = threading.Thread(target=self.__recognition.record, args=(is_recording,))
        self.__thread.start()

    def __clicked_btn_stop_record(self):
        self.__txt.delete(0.0, "end")
        self.__btn_stop_record.config(state='disabled')
        self.__btn_record.config(state='normal')
        global is_recording
        is_recording[0] = False
        self.__thread.join()
        text = self.convert_speech_to_text()
        self.__txt.insert(0.0, text)

    def __clicked_btn_lang_ru(self):
        self.__language = "ru"
        self.__btn_lang_eng.config(state='normal')
        self.__btn_lang_ru.config(state='disabled')

    def __clicked_btn_lang_eng(self):
        self.__language = "eng"
        self.__btn_lang_eng.config(state='disabled')
        self.__btn_lang_ru.config(state='normal')

    def convert_speech_to_text(self) -> str:
        if self.__language == "ru":
            text = self.__recognition.recognize_speech_ru()
        else:
            text = "eng"
        self.__recognition.copy_to_clipboard(text)
        return text

    def run(self):
        self.__window.mainloop()
