import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = "data.json"

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("План тренировок")
        self.root.geometry("900x600")
        
        self.data_list = []
        self.load_json()
        

        style = ttk.Style()
        style.theme_use('clam')
        

        frame_in = ttk.LabelFrame(root, text="Добавить тренировку", padding=10)
        frame_in.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(frame_in, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=0, padx=5)
        self.e_date = ttk.Entry(frame_in, width=12)
        self.e_date.grid(row=0, column=1, padx=5)
        self.e_date.insert(0, datetime.now().strftime("%d.%m.%Y"))
        
        ttk.Label(frame_in, text="Тип:").grid(row=0, column=2, padx=5)
        types = ["Бег", "Плавание", "Зал", "Йога", "Велосипед"]
        self.c_type = ttk.Combobox(frame_in, values=types, width=10)
        self.c_type.grid(row=0, column=3, padx=5)
        self.c_type.current(0)
        
        ttk.Label(frame_in, text="Минуты:").grid(row=0, column=4, padx=5)
        self.e_mins = ttk.Entry(frame_in, width=5)
        self.e_mins.grid(row=0, column=5, padx=5)
        
        btn_add = ttk.Button(frame_in, text="ДОБАВИТЬ", command=self.add_item)
        btn_add.grid(row=0, column=6, padx=10)


        frame_f = ttk.Frame(root)
        frame_f.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(frame_f, text="Фильтр по типу:").pack(side='left', padx=5)
        self.v_filter_type = tk.StringVar(value="Все")
        cb_filter = ttk.Combobox(frame_f, textvariable=self.v_filter_type, 
                                 values=["Все", "Бег", "Плавание", "Зал", "Йога", "Велосипед"], width=10)
        cb_filter.pack(side='left', padx=5)
        cb_filter.bind("<<ComboboxSelected>>", self.update_view)
        
        ttk.Label(frame_f, text="По дате:").pack(side='left', padx=(20,5))
        self.e_filter_date = ttk.Entry(frame_f, width=10)
        self.e_filter_date.pack(side='left', padx=5)
        self.e_filter_date.bind("<KeyRelease>", self.update_view)
        
        btn_reset = ttk.Button(frame_f, text="Сброс", command=self.reset_filters)
        btn_reset.pack(side='right', padx=5)


        tree_frame = ttk.Frame(root)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        cols = ("date", "type", "mins")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings")
        self.tree.heading("date", text="Дата")
        self.tree.heading("type", text="Тип")
        self.tree.heading("mins", text="Минуты")
        
        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        
        self.tree.bind("<Button-3>", self.on_right_click)


        frame_bot = ttk.Frame(root)
        frame_bot.pack(fill='x', padx=10, pady=5)
        self.lbl_status = ttk.Label(frame_bot, text="Записей: 0")
        self.lbl_status.pack(side='left')
        btn_save = ttk.Button(frame_bot, text="Сохранить JSON", command=self.save_json)
        btn_save.pack(side='right')
        
        self.update_view()

    def get_input(self):
        d = self.e_date.get().strip()
        t = self.c_type.get()
        m = self.e_mins.get().strip()
        
        if not d or not m:
            return None
            
        try:
            datetime.strptime(d, "%d.%m.%Y")
        except:
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ДД.ММ.ГГГГ")
            return None
            
        try:
            mins_val = int(m)
            if mins_val <= 0: raise ValueError
        except:
            messagebox.showerror("Ошибка", "Длительность должна быть положительным числом")
            return None
            
        return {"date": d, "type": t, "mins": mins_val}

    def add_item(self):
        item = self.get_input()
        is_valid = item is not None
        
        if is_valid:
            self.data_list.append(item)
            self.save_json()
            self.update_view()
            self.e_mins.delete(0, 'end')

    def update_view(self, event=None):
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        f_type = self.v_filter_type.get()
        f_date = self.e_filter_date.get().strip().lower()
        
        shown = 0
        for row in self.data_list:
            ok_type = (f_type == "Все") or (row["type"] == f_type)
            ok_date = True
            if f_date:
                ok_date = f_date in row["date"].lower()
                
            if ok_type and ok_date:
                self.tree.insert("", "end", values=(row["date"], row["type"], row["mins"]))
                shown += 1
                
        self.lbl_status.config(text=f"Всего: {len(self.data_list)} | Показано: {shown}")

    def reset_filters(self):
        self.v_filter_type.set("Все")
        self.e_filter_date.delete(0, 'end')
        self.update_view()

    def save_json(self):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data_list, f, indent=4, ensure_ascii=False)

    def load_json(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    txt = f.read().strip()
                    if txt:
                        self.data_list = json.loads(txt)
                    else:
                        self.data_list = []
            except:
                self.data_list = []
        else:
            self.data_list = []

    def on_right_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id:
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Удалить", command=lambda: self.del_item(item_id))
            menu.post(event.x_root, event.y_root)

    def del_item(self, iid):
        vals = self.tree.item(iid, "values")
        d, t, m = vals[0], vals[1], int(vals[2])
        
        idx_to_del = -1
        for i, x in enumerate(self.data_list):
            if x["date"] == d and x["type"] == t and x["mins"] == m:
                idx_to_del = i
                break
                
        if idx_to_del != -1:
            del self.data_list[idx_to_del]
            self.save_json()
            self.update_view()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()