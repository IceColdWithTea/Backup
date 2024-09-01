import tkinter as tk
import os
import shutil
from tkinter import ttk
from tkinter import filedialog
from tkcalendar import Calendar
from datetime import datetime, timedelta
from tkinter import messagebox
import babel.numbers
import configparser


# Конфиг
config_file = 'config.ini'
config = configparser.ConfigParser()


# Загрузка конфига
def load_config():
    if os.path.exists(config_file):
        config.read(config_file)
        entry_folder.insert(0, config.get('Folders', 'entry_data_folder', fallback=''))
        backup_folder.insert(0, config.get('Folders', 'backup_data_folder', fallback=''))


# Сохранение конфига
def save_config():
    if not config.has_section('Folders'):
        config.add_section('Folders')
    config.set('Folders', 'entry_data_folder', entry_folder.get())
    config.set('Folders', 'backup_data_folder', backup_folder.get())
    with open(config_file, 'w') as configfile:
        config.write(configfile)


# Проверка даты
def week_info():
    try:
        start_date = datetime.strptime(start_date_button.cget("text"), "%d.%m.%y")
        end_date = datetime.strptime(end_date_button.cget("text"), "%d.%m.%y")

        if end_date < start_date:
            messagebox.showerror("Ошибка", "Начальная дата старше конечной.")
            return False

        first_monday = start_date + timedelta(days=(7 - start_date.weekday())) if start_date.weekday() != 0 else start_date
        last_monday = end_date - timedelta(days=end_date.weekday())

        if first_monday > last_monday:
            messagebox.showerror("Ошибка", "Период меньше недели")
        else:
            count_monday = ((last_monday - first_monday).days // 7) + 1
            messagebox.showinfo("Информация", f"Недели: {count_monday}")
            return True
    finally:
        return


# Основная функция
def execute_backup():
    action = action_name.get()
    file_types = [file_types for file_types, c in file_types_dict.items() if c.get()]
    entry_data_folder = entry_folder.get()
    backup_data_folder = backup_folder.get()

    try:
        start_date_text = datetime.strptime(start_date_button.cget("text"), "%d.%m.%y")
        end_date_text = datetime.strptime(end_date_button.cget("text"), "%d.%m.%y")
    except ValueError:
        messagebox.showerror("Ошибка", "Не выбрана начальная или конечная дата.")
        return

    if not file_types:
        messagebox.showerror("Ошибка", "Не выбраны типы файлов.")
        return
    if not entry_data_folder:
        messagebox.showerror("Ошибка", "Не указана исходная папка.")
        return
    if not backup_data_folder:
        messagebox.showerror("Ошибка", "Не указана папка для резервного копирования.")
        return

    for window_dir, dirs, files in os.walk(entry_data_folder):
        for file in files:
            if any(file.endswith(ext) for ext in file_types):
                file_name, file_extension = os.path.splitext(file)
                if file != 'password.txt':
                    parts = file_name.split('-')
                    if len(parts) == 2:
                        file_date_str = parts[1]
                        try:
                            file_date = datetime.strptime(file_date_str, "%y%m%d")
                            if not (start_date_text <= file_date <= end_date_text):
                                continue
                        except ValueError:
                            continue     
                src_path = os.path.join(window_dir, file)
                dest_path = os.path.join(backup_data_folder, os.path.relpath(window_dir, entry_data_folder))
                os.makedirs(dest_path, exist_ok=True)

                if action == 'copy':
                    shutil.copy(src_path, dest_path)
                    print(f"Copied {file} to {dest_path}")
                elif action == 'move':
                    shutil.move(src_path, dest_path)
                    print(f"Moved {file} to {dest_path}")
                elif action == 'delete':
                    os.remove(src_path)
                    print(f"Deleted {file}")


# Допполнительные функции -----------------------------------------------------
# Возвращает папку в которой хранятся данные
def select_entry_folder():
    selected_folder = filedialog.askdirectory()
    entry_folder.delete(0, tk.END)
    entry_folder.insert(0, selected_folder)
    save_config()


# Возвращает папку в которую нужно все перенести
def select_backup_folder():
    selected_folder = filedialog.askdirectory()
    backup_folder.delete(0, tk.END)
    backup_folder.insert(0, selected_folder)
    save_config()


# Календарь и даты ------------------------------------------------------------
def choose_start_date():
    open_calendar(set_start_date)


def choose_end_date():
    open_calendar(set_end_date)


# Открытие календаря
def open_calendar(callback):
    window.update_idletasks()
    main_window_x = window.winfo_x()
    main_window_y = window.winfo_y()
    main_window_width = window.winfo_width()

    calendar_window = tk.Toplevel(window)
    calendar_window.grab_set()
    calendar_window.transient(window)

    calendar_window.geometry(f'+{main_window_x + main_window_width}+{main_window_y}')

    calendar = Calendar(calendar_window, selectmode='day', locale='ru_RU')
    calendar.pack(pady=10)
    ttk.Button(calendar_window, text="OK", command=lambda: select_date(calendar, callback, calendar_window)).pack(pady=10)


# Выбор даты и ее получение
def select_date(calendar, callback, calendar_window):
    callback(calendar.selection_get())
    calendar_window.destroy()


# Установка стартовой выбранной даты
def set_start_date(date):
    start_date_button.config(text=datetime.strftime(date, '%d.%m.%y'))
    if start_date_button.cget("text") != "Выбор даты" and end_date_button.cget("text") != "Выбор даты":
        week_info()


# Установка конечной выбранной даты
def set_end_date(date):
    end_date_button.config(text=datetime.strftime(date, '%d.%m.%y'))
    if start_date_button.cget("text") != "Выбор даты" and end_date_button.cget("text") != "Выбор даты":
        week_info()


# Настройка основного окна ----------------------------------------------------

window = tk.Tk()
window.title('AKBackup')
window.geometry('400x550')
window.resizable(False, False)


# Настройка интерфейса --------------------------------------------------------
# Вкладка действие
actions = ttk.LabelFrame(window, text='Действие', padding=(15, 10))
actions.pack(fill='x', pady=10)

action_name = tk.StringVar()
action_name.set('copy')
ttk.Radiobutton(actions, text='Копировать',
                variable=action_name, value='copy').pack(anchor=tk.W)
ttk.Radiobutton(actions, text='Переместить',
                variable=action_name, value='move').pack(anchor=tk.W)
ttk.Radiobutton(actions, text='Удалить',
                variable=action_name, value='delete').pack(anchor=tk.W)


# Вкладка данные
data_name = ttk.LabelFrame(window, text='Данные', padding=(15, 10))
data_name.pack(fill='x', pady=10)

file_types_dict = {
    ".sbin": tk.BooleanVar(value=True),
    ".bin": tk.BooleanVar(value=True),
    ".log": tk.BooleanVar(),
    "password.txt": tk.BooleanVar()
}

for name, var in file_types_dict.items():
    ttk.Checkbutton(data_name, text=name, variable=var).pack(anchor=tk.W)


# Вкладка путь
way_name = ttk.LabelFrame(window, text='Пути', padding=(15, 10))
way_name.pack(fill='x', pady=10)

tk.Label(way_name, text='Папка AutoGRAPH').grid(row=0, column=0, sticky=tk.W)
entry_folder = ttk.Entry(way_name, width=30)
entry_folder.grid(row=0, column=1)
ttk.Button(way_name, text='Обзор...', command=select_entry_folder).grid(row=0, column=2, padx=5)

ttk.Label(way_name, text='Резервная папка').grid(row=1, column=0, sticky=tk.W)
backup_folder = ttk.Entry(way_name, width=30)
backup_folder.grid(row=1, column=1)
ttk.Button(way_name, text='Обзор...', command=select_backup_folder).grid(row=1, column=2, padx=5)


# Вкладка даты
period_name = ttk.LabelFrame(window, text='Период', padding=(15, 10))
period_name.pack(fill='x', pady=10)

ttk.Label(period_name, text='С:').grid(row=0, column=0)
start_date_button = ttk.Button(period_name, text='Выбор даты', command=choose_start_date)
start_date_button.grid(row=0, column=1, padx=10)

ttk.Label(period_name, text="По:").grid(row=0, column=2)
end_date_button = ttk.Button(period_name, text="Выбор даты", command=choose_end_date)
end_date_button.grid(row=0, column=3, padx=10)


# Выполнить
execute_name = ttk.Frame(window)
execute_name.pack(pady=20)
ttk.Button(execute_name, text='Выполнить', command=execute_backup).pack()

load_config()

window.mainloop()
