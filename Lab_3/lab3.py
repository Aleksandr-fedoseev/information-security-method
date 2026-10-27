"""
Лабораторная работа №3
«Модели дискреционного управления доступом Харрисона-Руззо-Ульмана»

Реализация матричной модели доступа:
  Users[N]      - список пользователей (субъекты)
  Object[M]     - значения объектов (строки)
  P[N][M+1]     - матрица прав доступа:
                    P[i][0]       - админ. право редактировать матрицу (0 / 1)
                    P[i][j], j>=1 - права i-го пользователя к j-му объекту
                                    (0 - нет прав, 1 - чтение, 2 - модификация)

Запуск:  python Lab_3\\lab3.py   (нужен только стандартный Python, tkinter встроен)
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

RIGHTS = {0: "нет прав", 1: "чтение", 2: "модификация"}

# ---------------------------------------------------------------------------
# 1. Исходные данные
# ---------------------------------------------------------------------------
Users = ["Администратор", "Иванов", "Петров", "Сидоров"]

object_names = ["Объект 1", "Объект 2", "Объект 3"]          # подписи в списке
Object = [                                                   # значения объектов
    "Пример 1: приказ по предприятию",
    "Пример 2: список сотрудников отдела",
    "Пример 3: отчёт о финансовых результатах",
]

#      адм  об1 об2 об3
P = [
    [1,   2,  2,  2],   # Администратор - может всё
    [0,   1,  2,  0],   # Иванов  - читает об.1, меняет об.2, об.3 не видит
    [0,   0,  1,  2],   # Петров  - об.1 не видит, читает об.2, меняет об.3
    [1,   1,  0,  1],   # Сидоров - админ матрицы, но сам только читает
]


def admins_count():
    """Сколько пользователей имеют право редактировать матрицу доступа."""
    return sum(1 for row in P if row[0] == 1)


# ---------------------------------------------------------------------------
# 2. Главная форма
# ---------------------------------------------------------------------------
class MainForm:
    def __init__(self, root):
        self.root = root
        root.title("Модель Харрисона-Руззо-Ульмана")
        root.minsize(560, 300)

        # --- верхняя строка: (1) выбор пользователя, (2) кнопка администратора
        top = ttk.Frame(root, padding=10)
        top.pack(fill="x")
        ttk.Label(top, text="Пользователь", font=("Segoe UI", 12)).pack(side="left")

        self.user_cb = ttk.Combobox(top, state="readonly", width=20)          # 1
        self.user_cb.pack(side="left", padx=10)
        self.user_cb.bind("<<ComboboxSelected>>", lambda e: self.on_user_selected())

        self.admin_btn = ttk.Button(top, text="Редактировать права доступа",  # 2
                                    command=self.open_editor)
        self.admin_btn.pack(side="left", padx=10)

        # --- блок «Объект»: (3) список объектов, (4) поле значения
        box = ttk.LabelFrame(root, text="Объект", padding=10)
        box.pack(fill="both", expand=True, padx=10)

        self.obj_list = tk.Listbox(box, width=20, height=10, exportselection=False)  # 3
        self.obj_list.pack(side="left", fill="y")
        self.obj_list.bind("<<ListboxSelect>>", lambda e: self.on_object_selected())

        self.text = tk.Text(box, width=45, height=10, wrap="word")            # 4
        self.text.pack(side="left", fill="both", expand=True, padx=(10, 0))
        # любое нажатие клавиши в поле - сразу сохраняем значение в Object[J]
        self.text.bind("<KeyRelease>", lambda e: self.save_object())

        # --- строка состояния: показывает, какие права сработали
        self.status = ttk.Label(root, padding=(10, 5), foreground="#555")
        self.status.pack(fill="x")

        self.refresh()

    # ---- вспомогательные функции -------------------------------------------
    def current_user(self):
        i = self.user_cb.current()
        return i if 0 <= i < len(Users) else None

    def current_object(self):
        sel = self.obj_list.curselection()
        return sel[0] if sel else None

    def show_text(self, value, editable):
        """Вывести значение в поле 4 и сделать его доступным/недоступным."""
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", value)
        self.text.config(state="normal" if editable else "disabled",
                         background="white" if editable else "#eeeeee")

    # ---- перерисовка формы после изменения матрицы ------------------------
    def refresh(self):
        old_user, old_obj = self.current_user(), self.current_object()

        self.user_cb["values"] = Users
        if Users:
            self.user_cb.current(old_user if old_user is not None and old_user < len(Users) else 0)
        else:
            self.user_cb.set("")

        self.obj_list.delete(0, "end")
        for name in object_names:
            self.obj_list.insert("end", name)
        if old_obj is not None and old_obj < len(object_names):
            self.obj_list.selection_set(old_obj)

        self.on_user_selected()

    # ---- (1) выбран пользователь I -----------------------------------------
    def on_user_selected(self):
        I = self.current_user()
        # Если P[I, 0] = 0, то кнопка 2 недоступна
        if I is not None and P[I][0] == 1:
            self.admin_btn.state(["!disabled"])
        else:
            self.admin_btn.state(["disabled"])
        self.on_object_selected()

    # ---- (3) выбран объект J -----------------------------------------------
    def on_object_selected(self):
        I, J = self.current_user(), self.current_object()
        if I is None or J is None:
            self.show_text("", editable=False)
            self.status.config(text="Выберите пользователя и объект")
            return

        right = P[I][J + 1]          # столбец 0 - админ. права, объекты с 1
        if right == 0:               # нет прав: поле недоступно, значение скрыто
            self.show_text("", editable=False)
        elif right == 1:             # чтение: значение видно, поле недоступно
            self.show_text(Object[J], editable=False)
        else:                        # модификация: значение видно, поле доступно
            self.show_text(Object[J], editable=True)

        self.status.config(text=f"P[{Users[I]}, {object_names[J]}] = {right} "
                                f"({RIGHTS[right]})")

    # ---- (4) редактирование значения ---------------------------------------
    def save_object(self):
        I, J = self.current_user(), self.current_object()
        if I is not None and J is not None and P[I][J + 1] == 2:
            Object[J] = self.text.get("1.0", "end-1c")

    # ---- (2) форма редактирования матрицы ----------------------------------
    def open_editor(self):
        MatrixEditor(self.root, on_change=self.refresh)


# ---------------------------------------------------------------------------
# 3. Форма редактирования матрицы доступа
#    - добавление / удаление пользователей
#    - добавление / удаление объектов
#    - назначение и изменение прав доступа
# ---------------------------------------------------------------------------
class MatrixEditor:
    def __init__(self, parent, on_change):
        self.on_change = on_change
        self.win = tk.Toplevel(parent)
        self.win.title("Редактирование матрицы доступа")
        self.win.transient(parent)
        self.win.grab_set()            # модальное окно

        self.grid_frame = ttk.Frame(self.win, padding=10)
        self.grid_frame.pack(fill="both", expand=True)

        btns = ttk.Frame(self.win, padding=(10, 0, 10, 10))
        btns.pack(fill="x")
        ttk.Button(btns, text="+ Пользователь", command=self.add_user).pack(side="left")
        ttk.Button(btns, text="+ Объект", command=self.add_object).pack(side="left", padx=5)
        ttk.Button(btns, text="Закрыть", command=self.win.destroy).pack(side="right")

        ttk.Label(self.win, padding=(10, 0, 10, 10), foreground="#555",
                  text="Адм.: 1 - может редактировать матрицу.  "
                       "Права к объекту: 0 - нет, 1 - чтение, 2 - модификация.  "
                       "✕ - удалить строку/столбец.").pack(fill="x")
        self.build()

    def build(self):
        """Перестроить таблицу P заново (после любого изменения)."""
        for w in self.grid_frame.winfo_children():
            w.destroy()
        g = self.grid_frame

        # заголовок
        ttk.Label(g, text="Пользователь", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, padx=4)
        ttk.Label(g, text="Адм.", font=("Segoe UI", 9, "bold")).grid(row=0, column=1, padx=4)
        for j, name in enumerate(object_names):
            head = ttk.Frame(g)
            head.grid(row=0, column=j + 2, padx=4)
            ttk.Label(head, text=name, font=("Segoe UI", 9, "bold")).pack(side="left")
            ttk.Button(head, text="✕", width=2,
                       command=lambda j=j: self.delete_object(j)).pack(side="left")

        # строки матрицы
        for i, user in enumerate(Users):
            ttk.Label(g, text=user).grid(row=i + 1, column=0, sticky="w", padx=4, pady=2)
            for col in range(len(object_names) + 1):
                values = ["0", "1"] if col == 0 else ["0", "1", "2"]
                cb = ttk.Combobox(g, values=values, width=3, state="readonly")
                cb.set(str(P[i][col]))
                cb.grid(row=i + 1, column=col + 1, padx=4, pady=2)
                cb.bind("<<ComboboxSelected>>",
                        lambda e, i=i, col=col, cb=cb: self.set_right(i, col, int(cb.get())))
            ttk.Button(g, text="✕", width=2,
                       command=lambda i=i: self.delete_user(i)).grid(row=i + 1,
                                                                     column=len(object_names) + 2)

    # ---- операции над матрицей ---------------------------------------------
    def changed(self):
        self.build()
        self.on_change()

    def set_right(self, i, col, value):
        # нельзя оставить систему без единого администратора
        if col == 0 and value == 0 and P[i][0] == 1 and admins_count() == 1:
            messagebox.showwarning("Нельзя", "Должен остаться хотя бы один администратор.",
                                   parent=self.win)
        else:
            P[i][col] = value          # enter / delete right into M[s, o]
        self.changed()

    def add_user(self):                # create subject s
        name = simpledialog.askstring("Новый пользователь", "Имя пользователя:", parent=self.win)
        if name:
            Users.append(name)
            P.append([0] * (len(object_names) + 1))   # по умолчанию - никаких прав
            self.changed()

    def delete_user(self, i):          # destroy subject s
        if P[i][0] == 1 and admins_count() == 1:
            messagebox.showwarning("Нельзя", "Нельзя удалить последнего администратора.",
                                   parent=self.win)
            return
        Users.pop(i)
        P.pop(i)
        self.changed()

    def add_object(self):              # create object o
        name = simpledialog.askstring("Новый объект", "Название объекта:",
                                      initialvalue=f"Объект {len(object_names) + 1}",
                                      parent=self.win)
        if name:
            object_names.append(name)
            Object.append("")
            for row in P:
                row.append(0)          # новый столбец прав, у всех 0
            self.changed()

    def delete_object(self, j):        # destroy object o
        object_names.pop(j)
        Object.pop(j)
        for row in P:
            row.pop(j + 1)
        self.changed()


if __name__ == "__main__":
    root = tk.Tk()
    MainForm(root)
    root.mainloop()
