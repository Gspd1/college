import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import random
import itertools
import time
import vlc
import os

vlc_path = r"C:\Program Files\VideoLAN\VLC"
os.add_dll_directory(vlc_path) #добавляет путь к каталогу поиска DLL для текущего процесса
#Это позволяет процессу искать файлы DLL в указанном каталоге при загрузке библиотек


def exit(): #выход из приложения
    player.stop() #остановка воспроизведения
    root.quit() #завершение программы

def open_help(): #открытие справки использования
    help_text = "Инструкция по использованию приложения:\n\n"
    help_text += "1. Нажмите 'Выбрать видео', чтобы загрузить видеофайл.\n"
    help_text += "2. Используйте кнопку '⏸' для паузы/воспроизведения.\n"
    help_text += "3. Используйте кнопку 'Плейлист' для управления списком воспроизведения.\n"
    help_text += "4. Для выхода используйте кнопку 'Выход'.\n"
    messagebox.showinfo("Помощь", help_text) #вывод окна с данными написанными слева и в функции сверху

def select_video(): #выбор видео при нажатии кнопки выбрать файл меню и его воспроизведение
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")]) #открывает диалоговое окно для выбора файла и возвращает путь к выбранному файлу в виде строки
    if file_path:
        load_and_play(file_path)

def pause(): #пауза/воспроизведение видео
    if player.is_playing():
        player.pause() #остановка воспроизведения
        pause_btn.config(text="▶️")
    else:
        player.play() #дальнейшее воспроизведение
        pause_btn.config(text="⏸️")

def update_playlist(): #обновление плейлиста при добавлении в него новых файлов
    if 'playlist_listbox' in globals():
        playlist_listbox.delete(0, tk.END) # удаление всех элементов из виджета listbox
        for i in playlist:
            playlist_listbox.insert(tk.END, i.split('/')[-1]) #добавление элементов в конец списка

def load_and_play(file_path): #загрузка одиночного видео
    player.stop()
    media = vlc_instance.media_new(file_path) #создание нового объекта медиа на основе указанного пути к файлу
    player.set_media(media) #установка медиаобъекта в медиаплеер
    set_player_ww()
    player.play()
    pause_btn.config(text="⏸️")
    time.sleep(0.1) #делает паузу между действиями в программе, останавливает выполнение потока на 100мс

def set_player_ww():
    player.set_hwnd(video_frame.winfo_id()) #позволяет привязать объект player к окну video_frame


def toggle_playlist_window(): #открывает/закрывает окно плейлиста
    global playlist_ww

    if playlist_ww and playlist_ww.winfo_exists():
        # Если окно существует - закрытие окна
        playlist_ww.destroy()
        playlist_ww = None
    else:
        # Создание новое окно плейлиста
        open_playlist_ww()

def open_playlist_ww(): #открытие плейлиста
    def del_vids(): #удаление выбранных видео в плейлисте
        selected = playlist_listbox.curselection() #возвращает кортеж индексов выбранных элементов
        for i in reversed(selected): #перебирает элементы последовательности в обратном порядке.
            # Последовательность в данном случае это индексы видео
            del playlist[i] # удаления элемента из списка по индексу
        update_playlist()

    def add_vids(): #добавление видео в плейлист
        files = filedialog.askopenfilenames(filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")])
        if files:
            playlist.extend(files) #добавление новых элементов из окна проводника в конец уже имеющегося плейлиста
            update_playlist()

    def save_vids():  # сохранение плейлиста как текстового файла
        filepath = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[
            ("Text files", "*.txt")])  # defaultextension это автоматическое задание расширения файлов для сохранения
        if filepath: #если вообще что нибудь выбрано
            try:
                with open(filepath, 'w',
                          encoding='utf-8') as output:  # контекст.менеджер; 1-путь к файлу, 2-режим открытия(w значит для записи), 3-кодировка; c сохранением в пер-ю filepath
                    #открывает файл и возвращает объект, представляющий его
                    for i in playlist: #для видео в плейлисте
                        print(i, file=output)  # запись в файл
                messagebox.showinfo("Сохранено", 'Ваш плейлист сохранен')
            except:
                messagebox.showerror("Ошибка", "Не выбран путь для сохранения файла")

    def load_playlist(): #загрузка плейлиста из памяти компьютера как текстового файла
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f: #r это read
                    loaded_paths = [line.strip() for line in f.readlines() if line.strip()]
                    #line.strip() для удаления символов переноса (\n)
                    playlist.clear() #удаляет уже имеющиеся видео в плейлисте
                    playlist.extend(loaded_paths) #добавление элементы из txt файлав в конец плейлиста, т.е. друг за другом
                    update_playlist() #обновление плейлиста при добавлении в него новых файлов
                messagebox.showinfo("Успешно", "Плейлист загружен.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить плейлист:\n{e}")

    def play_some(index): #для кнопки 'воспроизвести' в окне плейлиста
        if 0 <= index and index < len(playlist):
            file_path = playlist[index]
            load_and_play(file_path) #загрузка и проигрывание видео

    def play_selected(): #если видео выбрано, проигрывание начинается с выбранного видео
        if not playlist:
            messagebox.showinfo("Плейлист пуст", "Сначала добавьте видео в плейлист.")
            return
        selected = playlist_listbox.curselection()
        if selected:
            start_index = selected[0]  # индекс выбранного видео в плейлисте
        else:
            start_index = 0

        def play_next(index): #запуск след. видео в плейлисте
            if 0 <= index < len(playlist):
                play_some(index)
            else:
                play_some(0)


        def check_video_end(): #проверка окончания видео
            nonlocal start_index #nonlocal значит не является локальной, но она и не является глобальной в общем смысле
            if player.get_length() > 0: # продолжительность текущего медиафайла в мс
                if player.get_state() == vlc.State.Ended: #а это так, возвращает текущее состояние проигрывателя
                    if playlist_auto: #глобальная переменная
                        next_index = (start_index + 1) % len(playlist)
                        start_index = next_index
                        play_next(next_index)
            root.after(1000, check_video_end) #запуск функции через определённый промежуток времени (чтобы все успело обновиться,закрыться, открыться (в общем), чтобы не возникало ошибок)

        play_next(start_index)
        root.after(1000, check_video_end) #запуск функции через определённый промежуток времени


    global playlist_ww
    playlist_ww = tk.Toplevel(master=root,bg='darkolivegreen')
    playlist_ww.title("Плейлист")
    playlist_ww.geometry("400x300")

    global playlist_listbox
    playlist_listbox = tk.Listbox(master=playlist_ww,bg='darkolivegreen') #листбокс для видео
    playlist_listbox.pack(fill="both", expand=True, padx=10, pady=10)

    btn_frame = tk.Frame(master=playlist_ww, bg='darkolivegreen')
    btn_frame.pack(pady=5)

    add_btn = tk.Button(master=btn_frame, text="Добавить", command=add_vids)
    add_btn.grid(row=0, column=0, padx=5)

    del_btn = tk.Button(master=btn_frame, text="Удалить", command=del_vids)
    del_btn.grid(row=0, column=1, padx=5)

    save_btn = tk.Button(master=btn_frame, text="Сохранить", command=save_vids)
    save_btn.grid(row=0, column=2, padx=5)

    load_btn = tk.Button(master=btn_frame, text="Загрузить", command=load_playlist)
    load_btn.grid(row=0, column=3, padx=5)

    play_btn = tk.Button(master=btn_frame, text="Воспроизвести", command=play_selected)
    play_btn.grid(row=0, column=4, padx=5)

    update_playlist()

def format_time(ms): #форматирование времени из мс в с (или с и ч если видео длинное)
    if ms is None or ms < 0:
        return "00:00"
    else:
        seconds = ms // 1000
        if seconds < 3600:
            mins = int(seconds // 60)
            secs = int(seconds % 60)
            return f'{mins:02d}:{secs:02d}'  # 02d -форматир-е
        else:
            hours = int(seconds // 3600)
            mins = int((seconds - 3600 * hours) // 60)
            secs = int((seconds - 3600 * hours) % 60)
            return f'{hours:02d}{mins:02d}:{secs:02d}'

def upd_slider(): #обновление слайдера времени видео
    if player.get_length() > 0:
        length = player.get_length()
        current = player.get_time() #текущее время воспроизведения
        slider.config(to=100) #100 это проценты отображения длительности, т.е. 100 проц длительности
        slider.set(current * 100 / length)
        curr_time.config(text=format_time(current))
        dur_time.config(text=format_time(length))
    else:
        curr_time.config(text="00:00")
        dur_time.config(text="00:00")

    root.after(500, upd_slider) #запуск функции через определённый промежуток времени


def slider_change(event): #изменение положения ползунка слайдера при дергании его мышкой
    if player.get_length()>0:
        current_time = int(slider.get()*player.get_length()/100)
        player.set_time(current_time)

def play_random(): #рандомный порядок воспроизведения
    global shuffled_iterator
    if not playlist: #если плейлист не создан
        messagebox.showinfo("Ошибка","Плейлист пуст")
        return

    shuffled = playlist.copy() # создаёт новый список с теми же элементами, что и оригинальный, но сохраняет свою идентичность в памяти
    #изменения в новом списке не влияют на оригинальный, и наоборот (если пользователь захочет отключить рандомный порядок)
    random.shuffle(shuffled)
    shuffled_iterator = itertools.cycle(shuffled) #cycle это бесконечный итератор

    def play_next_random(): #запуск след видео в рандомном порядке
        path = next(shuffled_iterator)
        load_and_play(path)

    def check_video_end(): #проверка окончания видео для плейлиста
        if player.get_length() > 0:
            if player.get_state() == vlc.State.Ended: #если воспроизводимое видео окончилось
                play_next_random() #играем следующее
        root.after(1000, check_video_end) #запуск функции через определённый промежуток времени

    play_next_random()
    root.after(1000, check_video_end)



def repeat():
    global repeat_current
    repeat_current = not repeat_current #смена состояния репита
    repeat_btn.config(relief=tk.SUNKEN if repeat_current else tk.RAISED)

def playlist_mod():
    global playlist_auto
    playlist_auto = not playlist_auto
    if playlist:
        enable_playlist_btn.config(text="Откл. плейлист" if playlist_auto else "Вкл. плейлист")
    else:
        messagebox.showinfo('Ошибка', 'Плейлист не создан')


def setup_vlc_events(): #обрабатывает ивент завершения видео, вызывает on_end_reached
    event_manager = player.event_manager() #для обнаружения окончания воспроизведения медиафайла или изменения состояния медиа
    event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, on_end_reached)
    #позволяет зарегистрировать уведомление о событии и связать его с функцией обратного вызова (обработчиком события)

def on_end_reached(event): #проверка на окончание для рестарта одного видео
    if repeat_current:
        root.after(100, restart_video)

def restart_video():
    try:
        player.stop()
        player.set_time(0) #установка значения времени
        player.play()
    except Exception as e: #обработка ошибок на всякий случай
        print(f"Ошибка при перезапуске видео: {e}")
        messagebox.showerror("Ошибка", f"Не удалось перезапустить видео: {e}")

def volume_change(val): #изменение громкости звука
    volume = int(float(val))
    player.audio_set_volume(volume) #настройка громкости, число от 0 до 100


root = tk.Tk()
root.title('Видеоплеер')
root.iconbitmap(default="illustration2.ico")
root.geometry("1000x600+170-100")
root.configure(bg='darkolivegreen')
root.minsize(800,600)

#глобальные переменные
playlist = []
playlist_auto = True #сигнализатор нажатия кнопки
repeat_current = False #сигнализатор повтора текущего трека
playlist_ww = None  # Для отслеживания окна плейлиста

video_frame = tk.Frame(root, bg="black") #фрейм для видео
video_frame.pack(expand=True, fill="both")

vlc_instance = vlc.Instance() #создаёт экземпляр (объект) библиотеки VLC
player = vlc_instance.media_player_new() #создаёт новый объект видеоплеера, связанный с экземпляром библиотеки VLC
setup_vlc_events() #присоединение обработчиков событий к объекту EventManager медиаплеера
player.audio_set_volume(80)

# Ползунок и время
slider_frame = tk.Frame(master=root,bg='darkolivegreen')
slider_frame.pack(pady=10)

curr_time = tk.Label(slider_frame, text="00:00", width=5, font=("Arial", 10),bg='darkolivegreen')
curr_time.pack(side=tk.LEFT, padx=5)

slider = tk.Scale(slider_frame, from_=0, to=100, orient="horizontal", length=600, sliderlength=20, showvalue=False,bg='darkolivegreen')
slider.pack(side=tk.LEFT, padx=5)
slider.bind("<ButtonRelease-1>", slider_change) #buttonrelease -событие, которое срабатывает, когда кнопка мыши отпущена (левая кнопка)

dur_time = tk.Label(slider_frame, text="00:00", width=5, font=("Arial", 10),bg='darkolivegreen')
dur_time.pack(side=tk.LEFT, padx=5)


btn_frame = tk.Frame(master=root,bg='darkolivegreen')
btn_frame.pack(pady=10)

pause_btn = tk.Button(btn_frame, text="⏸️", command=pause)
pause_btn.grid(row=0, column=1, padx=5)

playlist_btn = tk.Button(btn_frame, text="Плейлист", command=toggle_playlist_window)
playlist_btn.grid(row=0, column=3, padx=5)

random_btn = tk.Button(btn_frame, text="Случайный порядок", command=play_random)
random_btn.grid(row=0, column=5, padx=5)

repeat_btn = tk.Button(btn_frame, text="Повтор 1 дорожки", command=repeat)
repeat_btn.grid(row=0, column=6, padx=5)

enable_playlist_btn = tk.Button(btn_frame, text="Откл. плейлист", command=playlist_mod)
enable_playlist_btn.grid(row=0, column=4, padx=5)

volume_slider = tk.Scale(master=slider_frame,from_=100,to=0,orient="vertical",length=50, sliderlength=10, command=volume_change,bg='darkolivegreen')
volume_slider.set(80) #автом-ки громкость =80
volume_slider.pack(side=tk.RIGHT,padx=5)

menubar = tk.Menu(master=root)

media_menu = tk.Menu(master=menubar, tearoff=0)
media_menu.add_command(label="Выбрать файл",command=select_video)
media_menu.add_command(label='Выход',command=exit)

help_menu = tk.Menu(master=menubar,tearoff=0)
help_menu.add_command(label='Справка пользования',command=open_help)

menubar.add_cascade(label='Медиа',menu=media_menu)
menubar.add_cascade(label='Помощь',menu=help_menu)

root.config(menu=menubar)

upd_slider()

root.mainloop() #запускает цикл обработки событий окна для взаимодействия с пользователем