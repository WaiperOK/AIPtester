# hash_cracker_module.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
import traceback


def create_tab(tab_frame, api_service, selected_model_var, status_setter, theme_colors, dynamic_font_widgets_list):
    scrolledtext_bg = theme_colors.get("scrolledtext_bg", "#1e1e1e")
    scrolledtext_fg = theme_colors.get("scrolledtext_fg", "white")
    text_font_to_use = theme_colors.get("text_font")

    frame = ttk.Frame(tab_frame)
    frame.pack(fill="both", expand=True)
    top_frame = ttk.Frame(frame)
    top_frame.pack(fill="x", pady=(0, 10))

    ttk.Label(top_frame, text="Хэш:").grid(row=0, column=0, sticky="w", padx=(0, 5), pady=2)
    hc_hash_entry = ttk.Entry(top_frame, width=50, font=text_font_to_use)
    hc_hash_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
    dynamic_font_widgets_list.append(hc_hash_entry)

    ttk.Label(top_frame, text="Доп. инфо (user_info):").grid(row=1, column=0, sticky="w", padx=(0, 5), pady=2)
    hc_userinfo_entry = ttk.Entry(top_frame, width=50, font=text_font_to_use)
    hc_userinfo_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
    dynamic_font_widgets_list.append(hc_userinfo_entry)

    top_frame.columnconfigure(1, weight=1)

    hc_crack_button = ttk.Button(top_frame, text="Анализ взлома хэша (AI)")
    hc_crack_button.grid(row=0, column=2, rowspan=2, padx=5, pady=2, sticky="ns")

    results_control_frame = ttk.Frame(frame);
    results_control_frame.pack(fill="x", pady=(2, 2))

    def copy_results():
        content = hc_result_text.get("1.0", tk.END).strip()
        if content:
            try:
                tab_frame.clipboard_clear(); tab_frame.clipboard_append(content); status_setter(
                    "Рекомендации скопированы.")
            except tk.TclError as e_clip:
                status_setter(f"Ошибка буфера: {e_clip}"); messagebox.showwarning("Буфер обмена",
                                                                                  f"Не удалось: {e_clip}",
                                                                                  parent=tab_frame)
        else:
            status_setter("Нет текста для копирования.")

    copy_button = ttk.Button(results_control_frame, text="Копировать рекомендации", command=copy_results)
    copy_button.pack(side=tk.RIGHT, padx=0)

    hc_result_text = scrolledtext.ScrolledText(frame, height=15, bg=scrolledtext_bg, fg=scrolledtext_fg, wrap=tk.WORD,
                                               relief="solid", bd=1, font=text_font_to_use)
    dynamic_font_widgets_list.append(hc_result_text)
    hc_result_text.pack(fill="both", expand=True)
    hc_result_text.insert(tk.END, "AI предоставит рекомендации по взлому хэша, но не выполнит сам взлом.\n")

    def _hash_crack_thread_worker(hash_value, user_info):
        status_setter(f"Анализ взлома хэша {hash_value[:20]}... с помощью AI")
        hc_result_text.delete(1.0, tk.END)
        try:
            if not api_service or not hasattr(api_service, 'crack_hash'):
                hc_result_text.insert(tk.END, "AI сервис не инициализирован или метод 'crack_hash' не найден.\n");
                status_setter("Ошибка AI сервиса.");
                return
            result = api_service.crack_hash(hash_value, user_info=user_info)  # model_to_use убран
            if isinstance(result, dict) and "error" in result:
                hc_result_text.insert(tk.END, f"Ошибка API: {result['error']}\n")
                if result.get("status_code"): hc_result_text.insert(tk.END, f"Status Code: {result['status_code']}\n")
            elif isinstance(result, dict) and result.get("status") == "success" and "crack_guidance" in result:
                hc_result_text.insert(tk.END, "Рекомендации по взлому хэша от AI:\n\n");
                hc_result_text.insert(tk.END, result["crack_guidance"])
            else:
                hc_result_text.insert(tk.END,
                                      f"API не вернуло ожидаемый результат:\n{json.dumps(result, indent=4, ensure_ascii=False)}\n")
            status_setter(f"Анализ взлома хэша {hash_value[:20]}... завершен.")
        except Exception as e:
            detailed_error = traceback.format_exc()
            hc_result_text.insert(tk.END, f"Ошибка: {str(e)}\n\n{detailed_error}");
            status_setter(f"Ошибка анализа: {str(e)}")

    def run_hash_crack_command():
        hash_value = hc_hash_entry.get();
        user_info = hc_userinfo_entry.get()
        if not hash_value: messagebox.showerror("Ошибка", "Хэш не указан.", parent=tab_frame); return
        hc_crack_button.config(state=tk.DISABLED)

        def thread_target_wrapper():
            try:
                _hash_crack_thread_worker(hash_value, user_info or None)
            finally:
                if tab_frame.winfo_exists(): tab_frame.after(0, lambda: hc_crack_button.config(state=tk.NORMAL))

        threading.Thread(target=thread_target_wrapper, daemon=True).start()

    hc_crack_button.config(command=run_hash_crack_command)