"""
Лабораторная работа №4
«Модель доступа Белла-ЛаПадула»

К дискреционной матрице доступа из лабы №3 добавляется мандатная часть:
  PrivilegesUser[N]   - уровень допуска пользователя (0 - 3)
  PrivilegesObject[M] - гриф (уровень секретности) объекта (0 - 3)
  PrivilegesBuffer    - гриф данных, лежащих в буфере обмена программы

Правила (по методичке):
  * доступ к объекту J есть, только если P[I,J] != 0 И PrivilegesUser[I] >= PrivilegesObject[J]
    (нельзя читать «вверх» - no read up);
  * «Копировать» (6) доступно, если PrivilegesUser[I] > PrivilegesObject[J];
    при копировании запоминается гриф объекта -> PrivilegesBuffer;
  * «Вставить» (5) доступно, если PrivilegesBuffer < PrivilegesObject[J]
    (данные можно переносить только «вверх» - no write down).

Запуск:  python Lab_4\\lab4.py
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

RIGHTS = {0: "нет прав", 1: "чтение", 2: "модификация"}
LEVELS = ["0 НЕСЕКРЕТНО", "1 КОНФИДЕНЦИАЛЬНО", "2 СЕКРЕТНО", "3 СОВ. СЕКРЕТНО"]

# ---------------------------------------------------------------------------
# 1. Исходные данные
# ---------------------------------------------------------------------------
Users = ["Администратор", "Иванов", "Петров", "Сидоров"]
PrivilegesUser = [3, 2, 1, 0]                  # допуск каждого пользователя

object_names = ["Объект 1", "Объект 2", "Объект 3", "Объект 4"]
Object = [
    "Пример 1: объявление о субботнике",
    "Пример 2: список сотрудников с телефонами",
    "Пример 3: план модернизации серверной",
    "Пример 4: ключи шифрования каналов связи",
]
PrivilegesObject = [0, 1, 2, 3]                # гриф каждого объекта

#      адм  об1 об2 об3 об4
P = [
    [1,   2,  2,  2,  2],   # Администратор (сов. секретно) - всё
    [0,   2,  2,  2,  1],   # Иванов (секретно): к об.4 право чтения ЕСТЬ, но допуска не хватает
    [0,   1,  2,  2,  0],   # Петров (конфиденциально): к об.3 право есть, допуска нет
    [0,   2,  1,  0,  0],   # Сидоров (несекретно)
]

# Буфер обмена программы (отдельный от системного буфера Windows)
buffer_text = None
PrivilegesBuffer = None


def admins_count():
    return sum(1 for row in P if row[0] == 1)


# ---------------------------------------------------------------------------
# 2. Главная форма
# ---------------------------------------------------------------------------
class MainForm:
    def __init__(self, root):
        self.root = root
        root.title("Модель Белла-ЛаПадула")
        root.minsize(620, 330)

        top = ttk.Frame(root, padding=10)
        top.pack(fill="x")
        ttk.Label(top, text="Пользователь", font=("Segoe UI", 12)).pack(side="left")
        self.user_cb = ttk.Combobox(top, state="readonly", width=20)              # 1
        self.user_cb.pack(side="left", padx=10)
        self.user_cb.bind("<<ComboboxSelected>>", lambda e: self.on_user_selected())
        self.admin_btn = ttk.Button(top, text="Редактировать права доступа",      # 2
                                    command=self.open_editor)
        self.admin_btn.pack(side="left", padx=10)

        box = ttk.LabelFrame(root, text="Объект", padding=10)
        box.pack(fill="both", expand=True, padx=10)

        self.obj_list = tk.Listbox(box, width=20, height=10, exportselection=False)  # 3
        self.obj_list.pack(side="left", fill="y")
        self.obj_list.bind("<<ListboxSelect>>", lambda e: self.on_object_selected())

        right = ttk.Frame(box)
        right.pack(side="left", fill="both", expand=True, padx=(10, 0))
        self.text = tk.Text(right, width=45, height=8, wrap="word")              # 4
        self.text.pack(fill="both", expand=True)
        self.text.bind("<KeyRelease>", lambda e: self.save_object())
        # Запрещаем системные Ctrl+C / Ctrl+X / Ctrl+V: иначе секретный текст
        # можно было бы вынести в обход правил модели через буфер Windows.
        for ev in ("<<Copy>>", "<<Cut>>", "<<Paste>>"):
            self.text.bind(ev, lambda e: "break")

        btns = ttk.Frame(right)
        btns.pack(fill="x", pady=(8, 0))
        self.paste_btn = ttk.Button(btns, text="Вставить", command=self.paste)   # 5
        self.paste_btn.pack(side="left", expand=True)
        self.copy_btn = ttk.Button(btns, text="Копировать", command=self.copy)   # 6
        self.copy_btn.pack(side="left", expand=True)

        self.buffer_lbl = ttk.Label(root, padding=(10, 5, 10, 0))
        self.buffer_lbl.pack(fill="x")
        self.status = ttk.Label(root, padding=(10, 2, 10, 8), foreground="#555")
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
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", value)
        self.text.config(state="normal" if editable else "disabled",
                         background="white" if editable else "#eeeeee")

    @staticmethod
    def enable(btn, flag):
        btn.state(["!disabled"] if flag else ["disabled"])

    def update_buffer_label(self):
        if buffer_text is None:
            self.buffer_lbl.config(text="Буфер: пусто")
        else:
            short = buffer_text if len(buffer_text) <= 40 else buffer_text[:40] + "…"
            self.buffer_lbl.config(
                text=f"Буфер: «{short}»   (гриф буфера: {LEVELS[PrivilegesBuffer]})")

    def refresh(self):
        old_user, old_obj = self.current_user(), self.current_object()
        self.user_cb["values"] = Users
        if Users:
            self.user_cb.current(old_user if old_user is not None and old_user < len(Users) else 0)
        self.obj_list.delete(0, "end")
        for j, name in enumerate(object_names):
            self.obj_list.insert("end", f"{name}  [гриф {PrivilegesObject[j]}]")
        if old_obj is not None and old_obj < len(object_names):
            self.obj_list.selection_set(old_obj)
        self.on_user_selected()

    # ---- (1) выбран пользователь -------------------------------------------
    def on_user_selected(self):
        I = self.current_user()
        self.enable(self.admin_btn, I is not None and P[I][0] == 1)
        self.on_object_selected()

    # ---- (3) выбран объект: здесь вся логика модели ------------------------
    def on_object_selected(self):
        self.update_buffer_label()
        I, J = self.current_user(), self.current_object()
        if I is None or J is None:
            self.show_text("", editable=False)
            self.enable(self.copy_btn, False)
            self.enable(self.paste_btn, False)
            self.status.config(text="Выберите пользователя и объект")
            return

        right = P[I][J + 1]
        pu, po = PrivilegesUser[I], PrivilegesObject[J]

        # --- доступ к значению (дискреционная + мандатная проверка)
        if right == 0 or pu < po:
            self.show_text("", editable=False)
            reason = "нет права в матрице P" if right == 0 else "допуск ниже грифа (no read up)"
            access = f"ДОСТУП ЗАПРЕЩЁН: {reason}"
        elif right == 1:
            self.show_text(Object[J], editable=False)
            access = "только чтение"
        else:
            self.show_text(Object[J], editable=True)
            access = "чтение и модификация"
        has_access = right != 0 and pu >= po

        # --- кнопка 6 «Копировать»: PrivilegesUser[I] > PrivilegesObject[J]
        can_copy = has_access and pu > po
        # --- кнопка 5 «Вставить»:  PrivilegesBuffer < PrivilegesObject[J]
        can_paste = (buffer_text is not None and right == 2 and has_access
                     and PrivilegesBuffer < po)
        self.enable(self.copy_btn, can_copy)
        self.enable(self.paste_btn, can_paste)

        self.status.config(text=f"Допуск: {LEVELS[pu]}  |  Гриф: {LEVELS[po]}  |  "
                                f"P = {right} ({RIGHTS[right]})  →  {access}")

    # ---- (4) редактирование -------------------------------------------------
    def save_object(self):
        I, J = self.current_user(), self.current_object()
        if (I is not None and J is not None and P[I][J + 1] == 2
                and PrivilegesUser[I] >= PrivilegesObject[J]):
            Object[J] = self.text.get("1.0", "end-1c")

    # ---- (6) Копировать -----------------------------------------------------
    def copy(self):
        global buffer_text, PrivilegesBuffer
        J = self.current_object()
        sel = self.text.tag_ranges("sel")
        # копируется выделенный фрагмент, а если ничего не выделено - весь текст
        fragment = self.text.get(sel[0], sel[1]) if sel else self.text.get("1.0", "end-1c")
        buffer_text = fragment
        PrivilegesBuffer = PrivilegesObject[J]        # запоминаем гриф источника
        self.on_object_selected()

    # ---- (5) Вставить -------------------------------------------------------
    def paste(self):
        self.text.insert("insert", buffer_text)       # в позицию курсора
        self.save_object()                            # результат -> Object[J]
        self.on_object_selected()

    def open_editor(self):
        MatrixEditor(self.root, on_change=self.refresh)


# ---------------------------------------------------------------------------
# 3. Форма редактирования матрицы доступа и матриц привилегий
# ---------------------------------------------------------------------------
class MatrixEditor:
    def __init__(self, parent, on_change):
        self.on_change = on_change
        self.win = tk.Toplevel(parent)
        self.win.title("Редактирование прав доступа и привилегий")
        self.win.transient(parent)
        self.win.grab_set()

        self.grid_frame = ttk.Frame(self.win, padding=10)
        self.grid_frame.pack(fill="both", expand=True)

        btns = ttk.Frame(self.win, padding=(10, 0, 10, 10))
        btns.pack(fill="x")
        ttk.Button(btns, text="+ Пользователь", command=self.add_user).pack(side="left")
        ttk.Button(btns, text="+ Объект", command=self.add_object).pack(side="left", padx=5)
        ttk.Button(btns, text="Закрыть", command=self.win.destroy).pack(side="right")
        ttk.Label(self.win, padding=(10, 0, 10, 10), foreground="#555",
                  text="Адм.: 1 - может редактировать.  Права: 0 - нет, 1 - чтение, "
                       "2 - модификация.  Уровни: 0 - несекретно … 3 - сов. секретно.").pack(fill="x")
        self.build()

    def build(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()
        g = self.grid_frame
        bold = ("Segoe UI", 9, "bold")
        n_obj = len(object_names)

        # строка 0 - названия объектов
        ttk.Label(g, text="Пользователь", font=bold).grid(row=0, column=0, padx=4)
        ttk.Label(g, text="Допуск", font=bold).grid(row=0, column=1, padx=4)
        ttk.Label(g, text="Адм.", font=bold).grid(row=0, column=2, padx=4)
        for j, name in enumerate(object_names):
            head = ttk.Frame(g)
            head.grid(row=0, column=j + 3, padx=4)
            ttk.Label(head, text=name, font=bold).pack(side="left")
            ttk.Button(head, text="✕", width=2,
                       command=lambda j=j: self.delete_object(j)).pack(side="left")

        # строка 1 - PrivilegesObject (гриф объектов)
        ttk.Label(g, text="Гриф объекта →", foreground="#a33").grid(row=1, column=0,
                                                                   columnspan=3, sticky="e")
        for j in range(n_obj):
            cb = ttk.Combobox(g, values=["0", "1", "2", "3"], width=3, state="readonly")
            cb.set(str(PrivilegesObject[j]))
            cb.grid(row=1, column=j + 3, pady=(0, 6))
            cb.bind("<<ComboboxSelected>>",
                    lambda e, j=j, cb=cb: self.set_obj_level(j, int(cb.get())))

        # строки пользователей: имя, PrivilegesUser, P[i][0..M]
        for i, user in enumerate(Users):
            r = i + 2
            ttk.Label(g, text=user).grid(row=r, column=0, sticky="w", padx=4, pady=2)
            lv = ttk.Combobox(g, values=["0", "1", "2", "3"], width=3, state="readonly")
            lv.set(str(PrivilegesUser[i]))
            lv.grid(row=r, column=1, padx=4)
            lv.bind("<<ComboboxSelected>>",
                    lambda e, i=i, cb=lv: self.set_user_level(i, int(cb.get())))
            for col in range(n_obj + 1):
                values = ["0", "1"] if col == 0 else ["0", "1", "2"]
                cb = ttk.Combobox(g, values=values, width=3, state="readonly")
                cb.set(str(P[i][col]))
                cb.grid(row=r, column=col + 2, padx=4, pady=2)
                cb.bind("<<ComboboxSelected>>",
                        lambda e, i=i, col=col, cb=cb: self.set_right(i, col, int(cb.get())))
            ttk.Button(g, text="✕", width=2,
                       command=lambda i=i: self.delete_user(i)).grid(row=r, column=n_obj + 3)

    def changed(self):
        self.build()
        self.on_change()

    def set_right(self, i, col, value):
        if col == 0 and value == 0 and P[i][0] == 1 and admins_count() == 1:
            messagebox.showwarning("Нельзя", "Должен остаться хотя бы один администратор.",
                                   parent=self.win)
        else:
            P[i][col] = value
        self.changed()

    def set_user_level(self, i, value):
        PrivilegesUser[i] = value
        self.changed()

    def set_obj_level(self, j, value):
        PrivilegesObject[j] = value
        self.changed()

    def add_user(self):
        name = simpledialog.askstring("Новый пользователь", "Имя пользователя:", parent=self.win)
        if name:
            Users.append(name)
            PrivilegesUser.append(0)
            P.append([0] * (len(object_names) + 1))
            self.changed()

    def delete_user(self, i):
        if P[i][0] == 1 and admins_count() == 1:
            messagebox.showwarning("Нельзя", "Нельзя удалить последнего администратора.",
                                   parent=self.win)
            return
        Users.pop(i)
        PrivilegesUser.pop(i)
        P.pop(i)
        self.changed()

    def add_object(self):
        name = simpledialog.askstring("Новый объект", "Название объекта:",
                                      initialvalue=f"Объект {len(object_names) + 1}",
                                      parent=self.win)
        if name:
            object_names.append(name)
            Object.append("")
            PrivilegesObject.append(0)
            for row in P:
                row.append(0)
            self.changed()

    def delete_object(self, j):
        object_names.pop(j)
        Object.pop(j)
        PrivilegesObject.pop(j)
        for row in P:
            row.pop(j + 1)
        self.changed()


if __name__ == "__main__":
    root = tk.Tk()
    MainForm(root)
    root.mainloop()
