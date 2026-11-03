import customtkinter
import datetime
from db import (
    create_table,
    insert_task,
    update_task_status,
    select_tasks_by_date,
    delete_task,
)
from tkcalendar import Calendar
import sys
import os
import ctypes
from PIL import Image

# --- App Settings ---
customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("dark-blue")

APP_WIDTH = 320
APP_HEIGHT = 500
COLOR_BACKGROUND = "#1C1C1E"
COLOR_SECONDARY = "#2C2C2E"
COLOR_TEXT = "#FFFFFF"
COLOR_IOS_BLUE = "#0A84FF"
FONT_FAMILY = "Segoe UI"

FONT_SIZE_DATE = 14
FONT_SIZE_TASK = 14
FONT_SIZE_MESSAGE = 12


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        # Pega a pasta exata onde o app.py está salvo, e não a pasta de quem o chamou
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


class ToDoApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Focus")
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BACKGROUND)

        self.is_maximized = False
        self.stored_x = 0
        self.stored_y = 0
        self._calendar_open = False

        # Janela Frameless e presença na Barra
        self.overrideredirect(True)
        self.after(10, self.force_taskbar_presence)

        self.current_date = datetime.date.today()
        self.is_inbox_mode = False

        # --- Splash Screen ---
        self.splash_frame = customtkinter.CTkFrame(
            self, fg_color=COLOR_BACKGROUND, corner_radius=0
        )
        self.splash_frame.pack(fill="both", expand=True)

        try:
            logo_img = customtkinter.CTkImage(
                Image.open(resource_path("splash.png")), size=(320, 500)
            )
            self.splash_label = customtkinter.CTkLabel(
                self.splash_frame, text="", image=logo_img
            )
            self.splash_label.place(relx=0.5, rely=0.5, anchor="center")
        except:
            self.splash_label = customtkinter.CTkLabel(
                self.splash_frame,
                text="FOCUS",
                font=(FONT_FAMILY, 30, "bold"),
                text_color=COLOR_TEXT,
            )
            self.splash_label.pack(expand=True)

        self.after(1500, self.build_main_ui)

    def build_main_ui(self):
        self.splash_frame.destroy()
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Barra de Título
        self.title_bar = customtkinter.CTkFrame(
            self, fg_color=COLOR_BACKGROUND, corner_radius=0, height=45
        )
        self.title_bar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        self.title_bar.grid_columnconfigure(1, weight=1)

        self.app_name_label = customtkinter.CTkLabel(
            self.title_bar,
            text="Focus",
            font=(FONT_FAMILY, 26, "bold"),
            text_color=COLOR_TEXT,
        )
        self.app_name_label.grid(row=0, column=0, sticky="w", padx=15)

        self.app_name_label.bind("<Button-1>", self.start_move)
        self.app_name_label.bind("<B1-Motion>", self.do_move)
        self.title_bar.bind("<Button-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)

        self.btn_inbox = customtkinter.CTkButton(
            self.title_bar,
            text="Inbox",
            width=45,
            height=35,
            fg_color="transparent",
            hover_color=COLOR_SECONDARY,
            text_color=COLOR_TEXT,
            font=(FONT_FAMILY, 13, "bold"),
            command=self.toggle_inbox,
        )
        self.btn_inbox.grid(row=0, column=2)

        self.btn_minimize = customtkinter.CTkButton(
            self.title_bar,
            text="—",
            width=35,
            height=35,
            fg_color="transparent",
            hover_color=COLOR_SECONDARY,
            text_color=COLOR_TEXT,
            font=(FONT_FAMILY, 14, "bold"),
            command=self.minimize_window,
        )
        self.btn_minimize.grid(row=0, column=3)

        self.btn_maximize = customtkinter.CTkButton(
            self.title_bar,
            text="□",
            width=35,
            height=35,
            fg_color="transparent",
            hover_color=COLOR_SECONDARY,
            text_color=COLOR_TEXT,
            font=(FONT_FAMILY, 16, "bold"),
            command=self.toggle_maximize,
        )
        self.btn_maximize.grid(row=0, column=4)

        self.btn_close = customtkinter.CTkButton(
            self.title_bar,
            text="✕",
            width=35,
            height=35,
            fg_color="transparent",
            hover_color="#FF3B30",
            text_color=COLOR_TEXT,
            font=(FONT_FAMILY, 14, "bold"),
            command=self.destroy,
        )
        self.btn_close.grid(row=0, column=5, padx=(0, 5))

        # Header Frame
        self.header_frame = customtkinter.CTkFrame(
            self, fg_color=COLOR_BACKGROUND, corner_radius=0
        )
        self.header_frame.grid(
            row=1, column=0, columnspan=2, pady=(0, 0), padx=10, sticky="ew"
        )
        self.header_frame.grid_columnconfigure(1, weight=1)

        self.prev_day_button = customtkinter.CTkButton(
            self.header_frame,
            text="<",
            width=30,
            command=self.prev_day,
            fg_color="transparent",
            hover_color=COLOR_SECONDARY,
            text_color=COLOR_TEXT,
            font=(FONT_FAMILY, 14),
        )
        self.prev_day_button.grid(row=0, column=0, padx=(0, 5))

        self.date_label = customtkinter.CTkLabel(
            self.header_frame,
            text="",
            anchor="w",
            justify="left",
            cursor="hand2",
            font=(FONT_FAMILY, 14),
            text_color="#A0A0A5",
        )
        self.date_label.grid(row=0, column=1, sticky="ew")
        self.date_label.bind("<Button-1>", self.open_calendar_modal)

        self.next_day_button = customtkinter.CTkButton(
            self.header_frame,
            text=">",
            width=30,
            command=self.next_day,
            fg_color="transparent",
            hover_color=COLOR_SECONDARY,
            text_color=COLOR_TEXT,
            font=(FONT_FAMILY, 14),
        )
        self.next_day_button.grid(row=0, column=2, padx=(5, 0))

        self.progress_bar = customtkinter.CTkProgressBar(
            self.header_frame,
            height=3,
            fg_color=COLOR_SECONDARY,
            progress_color=COLOR_IOS_BLUE,
            corner_radius=0,
        )
        self.progress_bar.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(10, 5))

        # Tarefas Scroll
        self.task_scroll_frame = customtkinter.CTkScrollableFrame(
            self,
            fg_color=COLOR_BACKGROUND,
            corner_radius=0,
            scrollbar_button_color=COLOR_SECONDARY,
        )
        self.task_scroll_frame.grid(
            row=2, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="nsew"
        )
        self.task_scroll_frame.grid_columnconfigure(0, weight=1)

        # Input Frame
        self.input_frame = customtkinter.CTkFrame(
            self, fg_color=COLOR_BACKGROUND, corner_radius=0
        )
        self.input_frame.grid(
            row=3, column=0, columnspan=2, pady=(5, 10), padx=10, sticky="ew"
        )
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.task_entry = customtkinter.CTkEntry(
            self.input_frame,
            placeholder_text="Adicionar nova tarefa...",
            fg_color=COLOR_SECONDARY,
            text_color=COLOR_TEXT,
            border_width=0,
            corner_radius=5,
            font=(FONT_FAMILY, 14),
        )
        self.task_entry.grid(row=0, column=0, sticky="ew", ipady=5)
        self.task_entry.bind("<Return>", self.add_task_event)
        self.bind("<Key>", self.auto_focus_typing)

        create_table()
        self.update_date_display()
        self.load_tasks()

    def auto_focus_typing(self, event):
        if (
            getattr(self, "_calendar_open", False)
            or self.focus_get() == self.task_entry._entry
        ):
            return
        if (
            event.char
            and len(event.char) == 1
            and event.keysym not in ["Return", "BackSpace", "Escape", "Tab"]
        ):
            self.task_entry.focus_set()
            self.task_entry.insert("end", event.char)
            return "break"

    def toggle_inbox(self):
        self.is_inbox_mode = not self.is_inbox_mode
        if self.is_inbox_mode:
            self.btn_inbox.configure(text_color=COLOR_IOS_BLUE)
            self.prev_day_button.grid_remove()
            self.next_day_button.grid_remove()
            self.date_label.configure(text="Tarefas de Longo Prazo")
            self.date_label.unbind("<Button-1>")
            self.date_label.configure(cursor="arrow")
        else:
            self.btn_inbox.configure(text_color=COLOR_TEXT)
            self.prev_day_button.grid()
            self.next_day_button.grid()
            self.update_date_display()
            self.date_label.bind("<Button-1>", self.open_calendar_modal)
            self.date_label.configure(cursor="hand2")
        self.load_tasks()

    def force_taskbar_presence(self):
        # Essencial apenas para o app aparecer no Alt+Tab (mantido simples)
        hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
        style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
        style = (style & ~0x00000080) | 0x00040000
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, style)
        self.withdraw()
        self.deiconify()

    def minimize_window(self):
        hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
        ctypes.windll.user32.ShowWindow(hwnd, 6)

    def toggle_maximize(self):
        if self.is_maximized:
            self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}+{self.stored_x}+{self.stored_y}")
            self.btn_maximize.configure(text="□")
        else:
            self.stored_x = self.winfo_x()
            self.stored_y = self.winfo_y()
            # Maximização simples
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight() - 40
            self.geometry(f"{sw}x{sh}+0+0")
            self.btn_maximize.configure(text="❐")
        self.is_maximized = not self.is_maximized

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        if self.is_maximized:
            return
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def stop_move(self, event):
        self.x = None
        self.y = None

    def update_date_display(self):
        if self.is_inbox_mode:
            return
        day_of_week = self.current_date.strftime("%A")
        formatted_date = self.current_date.strftime("%d/%m/%Y")
        day_of_week_pt = {
            "Monday": "Segunda",
            "Tuesday": "Terça",
            "Wednesday": "Quarta",
            "Thursday": "Quinta",
            "Friday": "Sexta",
            "Saturday": "Sábado",
            "Sunday": "Domingo",
        }.get(day_of_week, day_of_week)
        self.date_label.configure(text=f"{day_of_week_pt}, {formatted_date}")

    def prev_day(self):
        self.current_date -= datetime.timedelta(days=1)
        self.update_date_display()
        self.load_tasks()

    def next_day(self):
        self.current_date += datetime.timedelta(days=1)
        self.update_date_display()
        self.load_tasks()

    def open_calendar_modal(self, event=None):
        if getattr(self, "_calendar_open", False):
            return
        self._calendar_open = True

        modal = customtkinter.CTkToplevel(self)
        modal.title("Data")
        modal.geometry("280x330")
        modal.attributes("-topmost", True)
        modal.configure(fg_color=COLOR_BACKGROUND)
        modal.overrideredirect(True)

        cal = Calendar(
            modal,
            selectmode="day",
            year=self.current_date.year,
            month=self.current_date.month,
            day=self.current_date.day,
            background=COLOR_BACKGROUND,
            foreground=COLOR_TEXT,
            headersbackground=COLOR_SECONDARY,
            headersforeground=COLOR_TEXT,
            bordercolor=COLOR_SECONDARY,
            normalbackground=COLOR_BACKGROUND,
            normalforeground=COLOR_TEXT,
            weekendbackground=COLOR_BACKGROUND,
            weekendforeground=COLOR_IOS_BLUE,
            othermonthforeground="#555555",
            othermonthbackground=COLOR_BACKGROUND,
        )
        cal.pack(pady=15, padx=15, fill="both", expand=True)

        def on_date_selected():
            self.current_date = datetime.date(
                cal.selection_get().year,
                cal.selection_get().month,
                cal.selection_get().day,
            )
            self.update_date_display()
            self.load_tasks()
            close_modal()

        def close_modal():
            self._calendar_open = False
            modal.destroy()

        btn_confirm = customtkinter.CTkButton(
            modal,
            text="Ir para a data",
            fg_color=COLOR_SECONDARY,
            hover_color=COLOR_IOS_BLUE,
            text_color=COLOR_TEXT,
            command=on_date_selected,
        )
        btn_confirm.pack(pady=(0, 10), padx=15, fill="x")
        btn_cancel = customtkinter.CTkButton(
            modal,
            text="Cancelar",
            fg_color="transparent",
            hover_color="#FF3B30",
            text_color="#555555",
            command=close_modal,
        )
        btn_cancel.pack(pady=(0, 15), padx=15, fill="x")

    def load_tasks(self):
        for widget in self.task_scroll_frame.winfo_children():
            widget.destroy()
        date_str = (
            "INBOX" if self.is_inbox_mode else self.current_date.strftime("%Y-%m-%d")
        )
        tasks = select_tasks_by_date(date_str)

        if not tasks:
            msg = (
                "Nenhuma tarefa de longo prazo."
                if self.is_inbox_mode
                else "Nenhuma tarefa para este dia."
            )
            customtkinter.CTkLabel(
                self.task_scroll_frame,
                text=msg,
                font=(FONT_FAMILY, FONT_SIZE_MESSAGE),
                text_color=COLOR_TEXT,
                anchor="w",
                justify="left",
            ).grid(row=0, column=0, pady=5, padx=0, sticky="ew")
            self.progress_bar.set(0)
            return

        completed_tasks = 0
        all_completed = True
        for i, task in enumerate(tasks):
            row_frame = customtkinter.CTkFrame(
                self.task_scroll_frame, fg_color="transparent"
            )
            row_frame.grid(row=i, column=0, sticky="ew", pady=(4, 4))
            row_frame.grid_columnconfigure(1, weight=1)  # Permite o texto expandir

            # 1. Apenas o Checkbox (sem texto)
            checkbox = customtkinter.CTkCheckBox(
                row_frame,
                text="",
                width=24,
                command=lambda t_id=task["id"], c_val=task[
                    "status"
                ]: self.toggle_task_status(t_id, c_val),
                onvalue=1,
                offvalue=0,
                fg_color=COLOR_IOS_BLUE,
                hover_color=COLOR_IOS_BLUE,
            )
            checkbox.grid(
                row=0, column=0, sticky="nw", pady=2
            )  # nw = alinhado no topo esquerdo

            if task["status"] == 1:
                checkbox.select()
                completed_tasks += 1
                txt_color = "#A0A0A5"  # Texto fica levemente cinza se concluído
            else:
                all_completed = False
                txt_color = COLOR_TEXT

            # 2. O Texto da Tarefa (com quebra de linha inteligente)
            task_label = customtkinter.CTkLabel(
                row_frame,
                text=task["descricao"],
                font=(FONT_FAMILY, FONT_SIZE_TASK),
                text_color=txt_color,
                justify="left",
                wraplength=205,  # Se o texto passar de 205 pixels, vai para a próxima linha
            )
            task_label.grid(row=0, column=1, sticky="w", padx=(5, 5))

            # Permite clicar no texto para marcar/desmarcar
            task_label.bind(
                "<Button-1>",
                lambda e, t_id=task["id"], c_val=task[
                    "status"
                ]: self.toggle_task_status(t_id, c_val),
            )

            # 3. Botão de Apagar
            customtkinter.CTkButton(
                row_frame,
                text="✕",
                width=24,
                height=24,
                fg_color="transparent",
                text_color="#555555",
                hover_color="#FF3B30",
                corner_radius=5,
                font=(FONT_FAMILY, 14, "bold"),
                command=lambda t_id=task["id"]: self.delete_task_event(t_id),
            ).grid(
                row=0, column=2, sticky="ne", padx=(5, 0)
            )  # ne = alinhado no topo direito

        self.progress_bar.set(completed_tasks / len(tasks))
        if tasks and all_completed:
            customtkinter.CTkLabel(
                self.task_scroll_frame,
                text="✅ Todas concluídas!",
                font=(FONT_FAMILY, FONT_SIZE_MESSAGE),
                text_color=COLOR_TEXT,
                anchor="w",
                justify="left",
            ).grid(row=len(tasks), column=0, pady=(10, 5), padx=0, sticky="ew")

    def toggle_task_status(self, task_id, current_status):
        update_task_status(task_id, 1 if current_status == 0 else 0)
        self.load_tasks()

    def delete_task_event(self, task_id):
        delete_task(task_id)
        self.load_tasks()

    def add_task_event(self, event=None):
        td = self.task_entry.get().strip()
        if td:
            insert_task(
                td,
                (
                    "INBOX"
                    if self.is_inbox_mode
                    else self.current_date.strftime("%Y-%m-%d")
                ),
            )
            self.task_entry.delete(0, "end")
            self.load_tasks()


if __name__ == "__main__":
    app = ToDoApp()
    app.mainloop()
