import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import threading
import os
import traceback
from typing import Union, Optional
from tkinter import font

from api_integration import AI_SERVICES, PREDEFINED_MODELS, BaseAIService

import port_scanner_module
import hash_cracker_module
import osint_module
import exploit_generator_module
import api_tester_gui_module
import sqli_tester_module
import shellcode_generator_module
import xss_generator_module
import pentest_plan_generator_module

class PentestToolkitApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ElitePentest AI Toolkit (Multi-AI Enhanced)")
        self.root.geometry("1350x980")
        self.root.configure(bg="#1e1e1e")

        text_widget_classes = ["Entry", "Text", "TEntry"]
        for wc in text_widget_classes:
            self.root.bind_class(wc, "<Button-3>", self._show_text_context_menu)
            self.root.bind_class(wc, "<Button-2>", self._show_text_context_menu)

        self.default_font_family = "Arial"
        self.current_font_size = 10
        self.text_widgets_font = font.Font(family=self.default_font_family, size=self.current_font_size)
        self.dynamic_font_widgets = []

        self.config = self.load_config()
        self.current_ai_provider_name = tk.StringVar(value=self.config.get("current_ai_provider", "Gemini"))
        default_models_for_current_provider = PREDEFINED_MODELS.get(self.current_ai_provider_name.get(), [""])
        initial_model_val = self.config.get("current_model", default_models_for_current_provider[0] if default_models_for_current_provider else "")
        is_ollama = self.current_ai_provider_name.get() == "Ollama-local"
        available_provider_models = PREDEFINED_MODELS.get(self.current_ai_provider_name.get(), [])
        if not is_ollama and available_provider_models:
            if initial_model_val not in available_provider_models:
                initial_model_val = available_provider_models[0] if available_provider_models else ""
        elif is_ollama:
            if not initial_model_val and not available_provider_models:
                initial_model_val = "Имя_модели_Ollama (введите)"
        elif not available_provider_models:
            initial_model_val = ""
        self.current_ai_model_name = tk.StringVar(value=initial_model_val)
        self.api_service: Optional[BaseAIService] = None

        self.setup_styles()
        self.setup_gui()
        self._update_gui_for_provider_and_model()

        self.theme_colors = {"scrolledtext_bg": self.scrolledtext_bg, "scrolledtext_fg": self.scrolledtext_fg,
                             "text_font": self.text_widgets_font}
        self.setup_tabs()
        self.root.after(200, self.check_api_status)

    def _show_text_context_menu(self, event):
        widget = event.widget
        context_menu = tk.Menu(widget, tearoff=0)
        can_copy = False
        can_cut = False
        can_paste = False
        can_delete = False
        is_readonly_or_disabled = False
        try:
            state = widget.cget("state")
            if state == tk.DISABLED or state == 'readonly':
                is_readonly_or_disabled = True
        except tk.TclError:
            if isinstance(widget, tk.Text) and widget.cget("state") == tk.DISABLED:
                is_readonly_or_disabled = True
        try:
            if widget.selection_get():
                can_copy = True
            if not is_readonly_or_disabled:
                can_cut = True
                can_delete = True
        except tk.TclError:
            pass
        try:
            if widget.clipboard_get():
                if not is_readonly_or_disabled:
                    can_paste = True
        except tk.TclError:
            pass
        if can_cut:
            context_menu.add_command(label="Вырезать", command=lambda w=widget: w.event_generate("<<Cut>>"))
        if can_copy:
            context_menu.add_command(label="Копировать", command=lambda w=widget: w.event_generate("<<Copy>>"))
        if can_paste:
            context_menu.add_command(label="Вставить", command=lambda w=widget: w.event_generate("<<Paste>>"))
        if can_delete:
            def delete_selection():
                try:
                    if widget.tag_ranges(tk.SEL):
                        widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                    elif widget.selection_present():
                        widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                except tk.TclError:
                    pass
            context_menu.add_command(label="Удалить", command=delete_selection)
        can_select_all = False
        if isinstance(widget, (tk.Entry, ttk.Entry)) and widget.get():
            can_select_all = True
        elif isinstance(widget, tk.Text) and widget.get("1.0", tk.END).strip():
            can_select_all = True
        if can_select_all:
            if context_menu.index(tk.END) is not None:
                context_menu.add_separator()
            def select_all():
                if isinstance(widget, (tk.Entry, ttk.Entry)):
                    widget.select_range(0, tk.END)
                    widget.icursor(tk.END)
                elif isinstance(widget, tk.Text):
                    widget.tag_add(tk.SEL, "1.0", tk.END)
                    widget.mark_set(tk.INSERT, "1.0")
                    widget.see(tk.INSERT)
                widget.focus_set()
            context_menu.add_command(label="Выделить всё", command=select_all)
        if context_menu.index(tk.END) is not None:
            context_menu.tk_popup(event.x_root, event.y_root)

    def _apply_font_to_widgets(self):
        print(f"Применение шрифта: {self.text_widgets_font.cget('family')} {self.text_widgets_font.cget('size')}")
        for widget in self.dynamic_font_widgets:
            if widget and widget.winfo_exists():
                try:
                    widget.configure(font=self.text_widgets_font)
                except tk.TclError as e:
                    print(f"Не удалось применить шрифт к {widget}: {e}")
        self.style.configure("TEntry", font=self.text_widgets_font)
        self.style.configure("TCombobox", font=self.text_widgets_font)
        self.style.configure("TLabel", font=self.text_widgets_font)
        self.style.configure("TButton", font=self.text_widgets_font)
        self.style.configure("TNotebook.Tab", font=self.text_widgets_font)

    def increase_font_size(self):
        self.current_font_size += 1
        self.current_font_size = min(self.current_font_size, 20)
        self.text_widgets_font.configure(size=self.current_font_size)
        self._apply_font_to_widgets()
        self.status_var.set(f"Размер шрифта: {self.current_font_size}")

    def decrease_font_size(self):
        self.current_font_size -= 1
        self.current_font_size = max(self.current_font_size, 7)
        self.text_widgets_font.configure(size=self.current_font_size)
        self._apply_font_to_widgets()
        self.status_var.set(f"Размер шрифта: {self.current_font_size}")

    def _initialize_api_service(self):
        provider_name = self.current_ai_provider_name.get()
        all_api_keys = self.config.get("api_keys", {})
        api_key_for_provider = all_api_keys.get(provider_name)
        service_class_name = AI_SERVICES.get(provider_name)
        selected_model_str = self.current_ai_model_name.get()

        if service_class_name:
            # Динамически импортируем модуль и получаем класс
            try:
                import importlib
                api_module = importlib.import_module("api_integration")
                service_class = getattr(api_module, service_class_name)
                self.api_service = service_class(api_key_for_provider, model_name=selected_model_str)
                print(f"Инициализирован сервис: {provider_name} ({'ключ есть' if api_key_for_provider else 'ключа нет'}, модель: '{selected_model_str}')")
            except (ImportError, AttributeError) as e:
                print(f"ПРЕДУПРЕЖДЕНИЕ: Не удалось найти или импортировать класс для AI '{provider_name}': {e}")
                self.api_service = None
        else:
            print(f"ПРЕДУПРЕЖДЕНИЕ: Не найден класс для AI '{provider_name}'")
            self.api_service = None

    def setup_styles(self):
        self.style = ttk.Style()
        try:
            self.style.theme_use('clam')
        except tk.TclError:
            print("Тема 'clam' не найдена.")

        self.style.configure("TFrame", background="#252526")
        self.style.configure("TLabel", background="#252526", foreground="white", font=self.text_widgets_font)
        self.style.configure("TButton", background="#333333", foreground="white", padding=5, font=self.text_widgets_font)
        self.style.map("TButton", background=[('active', '#555555'), ('disabled', '#2a2a2a')])
        self.style.configure("TEntry", fieldbackground="#333333", foreground="white", insertbackground="white", font=self.text_widgets_font)
        self.style.configure("TCombobox", fieldbackground="#333333", foreground="white", selectbackground='#333333', arrowcolor="white", font=self.text_widgets_font)
        self.style.map('TCombobox', fieldbackground=[('readonly', '#333333'), ('disabled', '#2a2a2a')])
        self.style.configure("TNotebook", background="#252526", tabmargins=[2, 5, 2, 0])
        self.style.configure("TNotebook.Tab", background="#333", foreground="white", padding=[10, 5], lightcolor="#252526", bordercolor="#252526", font=self.text_widgets_font)
        self.style.map("TNotebook.Tab", background=[("selected", "#0057b8")], foreground=[("selected", "white")])
        self.scrolledtext_bg = "#1e1e1e"
        self.scrolledtext_fg = "white"

    def load_config(self):
        default_provider = "Gemini"
        default_models_for_gemini = PREDEFINED_MODELS.get(default_provider, [""])
        default_gemini_model = default_models_for_gemini[0] if default_models_for_gemini else ""
        default_config = {"api_keys": {p: "" for p in AI_SERVICES.keys()}, "current_ai_provider": default_provider,
                          "current_model": default_gemini_model, "theme": "dark", "font_size": 10}
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                config_data = json.load(f)
            loaded_api_keys = config_data.get("api_keys", {})
            for pk in AI_SERVICES.keys():
                loaded_api_keys.setdefault(pk, "")
            config_data["api_keys"] = loaded_api_keys
            config_data.setdefault("current_ai_provider", default_provider)
            prov = config_data["current_ai_provider"]
            models = PREDEFINED_MODELS.get(prov, [""])
            def_model = models[0] if models else ""
            curr_model = config_data.get("current_model", def_model)
            is_ollama_no_predefined = prov == "Ollama-local" and not models
            if not is_ollama_no_predefined and models and curr_model not in models:
                curr_model = def_model
            config_data["current_model"] = curr_model
            config_data.setdefault("theme", "dark")
            self.current_font_size = config_data.get("font_size", 10)
            self.text_widgets_font.configure(size=self.current_font_size)  # Устанавливаем загруженный размер шрифта
            return config_data
        except FileNotFoundError:
            print("config.json не найден.")
            self.text_widgets_font.configure(size=self.current_font_size)
            return default_config
        except Exception as e:
            print(f"Ошибка config.json({e}).")
            self.text_widgets_font.configure(size=self.current_font_size)
            return default_config

    def _save_current_selection_to_config(self):
        print("Обновление self.config и сохранение...")
        self.config["current_ai_provider"] = self.current_ai_provider_name.get()
        self.config["current_model"] = self.current_ai_model_name.get()
        self.config["font_size"] = self.current_font_size
        current_provider = self.current_ai_provider_name.get()
        if hasattr(self, 'api_key_entry'):
            current_key_in_gui = self.api_key_entry.get()
            if "api_keys" not in self.config or not isinstance(self.config.get("api_keys"), dict):
                self.config["api_keys"] = {p: "" for p in AI_SERVICES.keys()}
            self.config["api_keys"][current_provider] = current_key_in_gui
        self.save_config()

    def save_config(self):
        try:
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            print("Конфигурация сохранена.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить config.json:{e}", parent=self.root)

    def _update_gui_for_provider_and_model(self):
        provider_name = self.current_ai_provider_name.get()
        api_key_val = self.config.get("api_keys", {}).get(provider_name, "")
        if hasattr(self, 'api_key_entry'):
            self.api_key_entry.delete(0, tk.END)
            self.api_key_entry.insert(0, api_key_val)
        models_list = PREDEFINED_MODELS.get(provider_name, [])
        if hasattr(self, 'ai_model_combo'):
            self.ai_model_combo['values'] = models_list
            current_model_str = self.current_ai_model_name.get()
            if provider_name == "Ollama-local":
                self.ai_model_combo.config(state="normal")
                if not current_model_str or "Имя_модели_Ollama" in current_model_str:
                    self.current_ai_model_name.set("Имя_модели_Ollama (введите)")
            else:
                self.ai_model_combo.config(state="readonly")
                if models_list:
                    if current_model_str not in models_list:
                        self.current_ai_model_name.set(models_list[0])
                else:
                    self.current_ai_model_name.set("")
        self._initialize_api_service()

    def on_provider_selected(self, event=None):
        print(f"Выбран AI: {self.current_ai_provider_name.get()}")
        self._update_gui_for_provider_and_model()
        self._save_current_selection_to_config()
        self.check_api_status()

    def on_model_selected(self, event=None):
        print(f"Модель: '{self.current_ai_model_name.get()}' для '{self.current_ai_provider_name.get()}'")
        self._initialize_api_service()
        self._save_current_selection_to_config()
        self.check_api_status()

    def setup_gui(self):
        top_controls_frame = ttk.Frame(self.root, padding="5 5 5 5")
        top_controls_frame.pack(fill="x", padx=10, pady=5)
        row0_frame = ttk.Frame(top_controls_frame)
        row0_frame.pack(fill="x")
        ttk.Label(row0_frame, text="AI Провайдер:").pack(side=tk.LEFT, padx=(0, 5))
        self.ai_provider_combo = ttk.Combobox(row0_frame, textvariable=self.current_ai_provider_name,
                                              values=list(AI_SERVICES.keys()), state="readonly", width=15,
                                              font=self.text_widgets_font)
        self.ai_provider_combo.pack(side=tk.LEFT, padx=5)
        self.ai_provider_combo.bind("<<ComboboxSelected>>", self.on_provider_selected)
        ttk.Label(row0_frame, text="Модель:").pack(side=tk.LEFT, padx=(10, 5))
        self.ai_model_combo = ttk.Combobox(row0_frame, textvariable=self.current_ai_model_name, state="readonly",
                                           width=25, font=self.text_widgets_font)
        self.ai_model_combo.pack(side=tk.LEFT, padx=5, fill="x", expand=True)
        self.ai_model_combo.bind("<<ComboboxSelected>>", self.on_model_selected)
        self.ai_model_combo.bind("<Return>", self.on_model_selected)
        self.api_status_label = ttk.Label(row0_frame, text="Статус API: -", anchor="w", width=30,
                                          font=self.text_widgets_font)
        self.api_status_label.pack(side=tk.LEFT, padx=10)
        self.dynamic_font_widgets.append(self.api_status_label)
        row1_frame = ttk.Frame(top_controls_frame)
        row1_frame.pack(fill="x", pady=5)
        ttk.Label(row1_frame, text="API Ключ (для AI):").pack(side=tk.LEFT, padx=(0, 5))
        self.api_key_entry = ttk.Entry(row1_frame, width=50, font=self.text_widgets_font)
        self.api_key_entry.pack(side=tk.LEFT, padx=5, fill="x", expand=True)
        self.dynamic_font_widgets.append(self.api_key_entry)
        self.save_key_button = ttk.Button(row1_frame, text="Сохранить ключ",
                                          command=self.save_api_key_for_selected_provider)
        self.save_key_button.pack(side=tk.LEFT, padx=5)
        font_button_frame = ttk.Frame(row1_frame)
        font_button_frame.pack(side=tk.LEFT, padx=10)
        ttk.Button(font_button_frame, text="A+", command=self.increase_font_size, width=3).pack(side=tk.LEFT)
        ttk.Button(font_button_frame, text="A-", command=self.decrease_font_size, width=3).pack(side=tk.LEFT, padx=(2, 0))
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        self.status_var = tk.StringVar(value="Готов")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w", padding="5 2 5 2",
                               font=self.text_widgets_font)
        status_bar.pack(fill="x", padx=10, pady=(0, 5), side="bottom")
        self.dynamic_font_widgets.append(status_bar)

    def get_status_setter(self):
        return self.status_var.set

    def setup_tabs(self):
        tabs_config = [("Сканер портов", port_scanner_module.create_tab),
                       ("Взлом хэшей", hash_cracker_module.create_tab),
                       ("OSINT-разведка", osint_module.create_tab),
                       ("Эксплойт-генератор", exploit_generator_module.create_tab),
                       ("API-тестер GUI", api_tester_gui_module.create_tab),
                       ("SQLi-тестер", sqli_tester_module.create_tab),
                       ("Генератор Шеллкодов", shellcode_generator_module.create_tab),
                       ("XSS-Генератор", xss_generator_module.create_tab),
                       ("План Пентеста (AI)", pentest_plan_generator_module.create_tab)]
        for i in reversed(range(self.notebook.index("end"))):
            self.notebook.forget(i)
        for name, create_tab_function in tabs_config:
            tab_frame = ttk.Frame(self.notebook, padding="10 10 10 10")
            self.notebook.add(tab_frame, text=name)
            api_to_pass = None if name == "API-тестер GUI" else self.api_service
            create_tab_function(tab_frame, api_to_pass, self.current_ai_model_name, self.get_status_setter(),
                                self.theme_colors, self.dynamic_font_widgets)

    def save_api_key_for_selected_provider(self):
        provider_name = self.current_ai_provider_name.get()
        api_key = self.api_key_entry.get()
        if "api_keys" not in self.config or not isinstance(self.config.get("api_keys"), dict):
            self.config["api_keys"] = {p: "" for p in AI_SERVICES.keys()}
        self.config["api_keys"][provider_name] = api_key
        self._save_current_selection_to_config()
        if self.api_service and hasattr(self.api_service, 'update_api_key') and callable(self.api_service.update_api_key):
            self.api_service.update_api_key(api_key)
        else:
            self._initialize_api_service()
        self.check_api_status()
        messagebox.showinfo("Ключ сохранен", f"API ключ для {provider_name} сохранен.", parent=self.root)

    def _check_api_status_worker(self, current_provider_name_for_thread: str):
        import time
        time.sleep(0.1)
        if self.api_service and hasattr(self.api_service, 'is_configured') and self.api_service.is_configured():
            return True, f"API ({current_provider_name_for_thread}): Сконфигурирован"
        elif self.api_service and hasattr(self.api_service, 'api_key') and self.api_service.api_key:
            return False, f"API ({current_provider_name_for_thread}): Ошибка конфигурации"
        else:
            return False, f"API ({current_provider_name_for_thread}): Ключ отсутствует"

    def _update_api_status_ui(self, success: bool, message: str, provider_name_str: str):
        if self.root.winfo_exists():
            if success:
                self.api_status_label.config(text=message, foreground="#4CAF50")
            else:
                self.api_status_label.config(text=message, foreground="#F44336")
            self.status_var.set(f"Проверка статуса {provider_name_str} API завершена.")

    def check_api_status(self):
        if not hasattr(self, 'api_status_label') or not self.api_status_label.winfo_exists():
            return
        provider_name_str = self.current_ai_provider_name.get()
        self.status_var.set(f"Проверка статуса {provider_name_str} API...")
        self.api_status_label.config(text="API: Проверка...", foreground="#FFC107")

        def worker(provider_name_arg: str):
            if not self.root.winfo_exists():
                return
            success, message = self._check_api_status_worker(provider_name_arg)
            if self.root.winfo_exists():
                self.root.after(0, self._update_api_status_ui, success, message, provider_name_arg)

        threading.Thread(target=worker, args=(provider_name_str,), daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    try:
        app = PentestToolkitApp(root)
        root.mainloop()
    except Exception as e:
        detailed_error = traceback.format_exc()
        print(f"Критическая ошибка: {detailed_error}")
        parent_window = root if root.winfo_exists() else None
        messagebox.showerror("Критическая ошибка", f"Не удалось запустить:\n{e}\n\n{detailed_error}", parent=parent_window)