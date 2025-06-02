# osint_module.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
import traceback


def create_tab(tab_frame, api_service, selected_model_var, status_setter, theme_colors, dynamic_font_widgets_list):
    scrolledtext_bg = theme_colors.get("scrolledtext_bg", "#1e1e1e")
    scrolledtext_fg = theme_colors.get("scrolledtext_fg", "white")
    text_font_to_use = theme_colors.get("text_font")

    frame = ttk.Frame(tab_frame);
    frame.pack(fill="both", expand=True)
    top_frame = ttk.Frame(frame);
    top_frame.pack(fill="x", pady=(0, 10))

    ttk.Label(top_frame, text="Цель OSINT:").grid(row=0, column=0, sticky="w", padx=(0, 5), pady=2)
    osint_target_entry = ttk.Entry(top_frame, width=40, font=text_font_to_use)
    osint_target_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
    dynamic_font_widgets_list.append(osint_target_entry)

    ttk.Label(top_frame, text="Тип поиска:").grid(row=1, column=0, sticky="w", padx=(0, 5), pady=2)
    osint_type_combo = ttk.Combobox(top_frame, width=37, font=text_font_to_use, values=[
        "person", "email", "domain", "ip_address", "phone_number", "username", "company"
    ], state="readonly")
    osint_type_combo.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
    if osint_type_combo["values"]: osint_type_combo.current(0)
    # dynamic_font_widgets_list.append(osint_type_combo) # Обычно для Combobox не нужно

    top_frame.columnconfigure(1, weight=1)
    osint_search_button = ttk.Button(top_frame, text="Начать OSINT (AI)")
    osint_search_button.grid(row=0, column=2, rowspan=2, padx=5, pady=2, sticky="ns")

    results_control_frame = ttk.Frame(frame);
    results_control_frame.pack(fill="x", pady=(2, 2))

    def copy_results():
        content = osint_result_text.get("1.0", tk.END).strip()
        if content:
            try:
                tab_frame.clipboard_clear(); tab_frame.clipboard_append(content); status_setter(
                    "Результаты OSINT скопированы.")
            except tk.TclError as e_clip:
                status_setter(f"Ошибка буфера: {e_clip}"); messagebox.showwarning("Буфер обмена",
                                                                                  f"Не удалось: {e_clip}",
                                                                                  parent=tab_frame)
        else:
            status_setter("Нет текста для копирования.")

    copy_button = ttk.Button(results_control_frame, text="Копировать результаты", command=copy_results)
    copy_button.pack(side=tk.RIGHT, padx=0)

    osint_result_text = scrolledtext.ScrolledText(frame, height=15, bg=scrolledtext_bg, fg=scrolledtext_fg,
                                                  wrap=tk.WORD, relief="solid", bd=1, font=text_font_to_use)
    dynamic_font_widgets_list.append(osint_result_text)
    osint_result_text.pack(fill="both", expand=True)

    def _osint_thread_worker(target_param, search_type_param):
        status_setter(f"OSINT по '{target_param}' (тип: {search_type_param}) с AI...")
        osint_result_text.delete(1.0, tk.END)
        try:
            if not api_service or not hasattr(api_service, 'osint_search'):
                osint_result_text.insert(tk.END, "AI сервис не инициализирован или метод 'osint_search' не найден.\n");
                status_setter("Ошибка AI сервиса.");
                return
            result = api_service.osint_search(target_param, search_type_param)  # model_to_use убран
            if isinstance(result, dict) and "error" in result:
                osint_result_text.insert(tk.END, f"Ошибка API: {result['error']}\n")
                if result.get("status_code"): osint_result_text.insert(tk.END,
                                                                       f"Status Code: {result['status_code']}\n")
            elif isinstance(result, dict) and result.get("status") == "success" and "osint_data" in result:
                osint_result_text.insert(tk.END, f"Результаты OSINT для '{target_param}' ({search_type_param}):\n\n");
                osint_result_text.insert(tk.END, result["osint_data"])
            else:
                osint_result_text.insert(tk.END,
                                         f"API не вернуло результат:\n{json.dumps(result, indent=4, ensure_ascii=False)}\n")
            status_setter(f"OSINT по '{target_param}' завершен.")
        except Exception as e:
            detailed_error = traceback.format_exc()
            osint_result_text.insert(tk.END, f"Ошибка OSINT: {str(e)}\n\n{detailed_error}");
            status_setter(f"Ошибка OSINT: {str(e)}")

    def run_osint_search_command():
        target = osint_target_entry.get();
        search_type = osint_type_combo.get()
        if not target: messagebox.showerror("Ошибка", "Цель OSINT не указана.", parent=tab_frame); return
        osint_search_button.config(state=tk.DISABLED)

        def thread_target_wrapper():
            try:
                _osint_thread_worker(target, search_type)
            finally:
                if tab_frame.winfo_exists(): tab_frame.after(0, lambda: osint_search_button.config(state=tk.NORMAL))

        threading.Thread(target=thread_target_wrapper, daemon=True).start()

    osint_search_button.config(command=run_osint_search_command)