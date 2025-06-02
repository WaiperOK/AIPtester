# sqli_tester_module.py
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

    main_label_font = ("Arial", text_font_to_use.cget("size") + 4, "bold")  # Заголовок чуть больше основного текста
    ttk.Label(frame, text="SQLi-тестер (AI ассистент)", font=main_label_font).pack(pady=(0, 10), anchor="center")

    input_frame = ttk.Frame(frame)
    input_frame.pack(fill="x", pady=5)

    current_row = 0
    ttk.Label(input_frame, text="Целевой URL:").grid(row=current_row, column=0, sticky="w", padx=5, pady=2)
    sqli_url_entry = ttk.Entry(input_frame, width=60, font=text_font_to_use)
    sqli_url_entry.grid(row=current_row, column=1, columnspan=2, padx=5, pady=2, sticky="ew")
    sqli_url_entry.insert(0, "http://testphp.vulnweb.com/listproducts.php?cat=1")
    dynamic_font_widgets_list.append(sqli_url_entry)
    current_row += 1

    ttk.Label(input_frame, text="Метод HTTP:").grid(row=current_row, column=0, sticky="w", padx=5, pady=2)
    sqli_method_combo = ttk.Combobox(input_frame, values=["GET", "POST"], state="readonly", width=10,
                                     font=text_font_to_use)
    sqli_method_combo.grid(row=current_row, column=1, padx=5, pady=2, sticky="w")
    sqli_method_combo.current(0)
    current_row += 1

    ttk.Label(input_frame, text="Параметры (для POST):").grid(row=current_row, column=0, sticky="w", padx=5, pady=2)
    sqli_params_entry = ttk.Entry(input_frame, width=60, font=text_font_to_use)
    sqli_params_entry.grid(row=current_row, column=1, columnspan=2, padx=5, pady=2, sticky="ew")
    dynamic_font_widgets_list.append(sqli_params_entry)
    current_row += 1

    ttk.Label(input_frame, text="Cookies:").grid(row=current_row, column=0, sticky="w", padx=5, pady=2)
    sqli_cookies_entry = ttk.Entry(input_frame, width=60, font=text_font_to_use)
    sqli_cookies_entry.grid(row=current_row, column=1, columnspan=2, padx=5, pady=2, sticky="ew")
    dynamic_font_widgets_list.append(sqli_cookies_entry)
    current_row += 1

    ttk.Label(input_frame, text="Тип/Уровень теста API:").grid(row=current_row, column=0, sticky="w", padx=5, pady=2)
    sqli_test_type_combo = ttk.Combobox(input_frame, values=[
        "Basic Boolean", "Error Based", "Time Based", "Union Based (Generic)"
    ], state="readonly", width=30, font=text_font_to_use)
    sqli_test_type_combo.grid(row=current_row, column=1, padx=5, pady=2, sticky="w")
    sqli_test_type_combo.current(0)
    current_row += 1
    input_frame.columnconfigure(1, weight=1)

    sqli_test_button = ttk.Button(input_frame, text="Получить план теста (AI)")
    sqli_test_button.grid(row=current_row, column=0, columnspan=3, pady=10)

    results_control_frame = ttk.Frame(frame);
    results_control_frame.pack(fill="x", pady=(2, 2))

    def copy_results():
        content = sqli_result_text.get("1.0", tk.END).strip()
        if content:
            try:
                tab_frame.clipboard_clear(); tab_frame.clipboard_append(content); status_setter("План SQLi скопирован.")
            except tk.TclError as e_clip:
                status_setter(f"Ошибка буфера: {e_clip}"); messagebox.showwarning("Буфер обмена",
                                                                                  f"Не удалось: {e_clip}",
                                                                                  parent=tab_frame)
        else:
            status_setter("Нет текста для копирования.")

    copy_button = ttk.Button(results_control_frame, text="Копировать план", command=copy_results)
    copy_button.pack(side=tk.RIGHT, padx=0)

    sqli_result_text = scrolledtext.ScrolledText(frame, height=15, bg=scrolledtext_bg, fg=scrolledtext_fg, wrap=tk.WORD,
                                                 relief="solid", bd=1, font=text_font_to_use)
    dynamic_font_widgets_list.append(sqli_result_text)
    sqli_result_text.pack(fill="both", expand=True, pady=(0, 0))
    sqli_result_text.insert(tk.END, "Ожидание запуска...\nAI поможет составить план тестирования SQLi.\n")

    def _sqli_test_thread_worker(url, method, params_str, cookies_str, test_type):
        status_setter(f"Получение плана SQLi для {url}...")
        sqli_result_text.delete(1.0, tk.END)

        api_call_params = {"url": url, "method": method, "data": params_str if method == "POST" else None,
                           "cookies": cookies_str, "test_type": test_type}
        try:
            if not api_service or not hasattr(api_service, 'perform_sqli_test'):
                sqli_result_text.insert(tk.END,
                                        "Экземпляр AI сервиса не инициализирован или метод 'perform_sqli_test' не найден.\n")
                status_setter("Ошибка AI сервиса.");
                return

            result = api_service.perform_sqli_test(api_call_params)  # model_to_use убран

            if isinstance(result, dict) and "error" in result:
                sqli_result_text.insert(tk.END, f"\nОшибка API: {result['error']}\n")
                if result.get("status_code"): sqli_result_text.insert(tk.END, f"Status Code: {result['status_code']}\n")
            elif isinstance(result, dict) and result.get("status") == "success" and "sqli_plan" in result:
                sqli_result_text.insert(tk.END, "\n--- План тестирования SQLi от AI ---\n")
                sqli_result_text.insert(tk.END, result["sqli_plan"])
                if result.get("log"): sqli_result_text.insert(tk.END, f"\nЛог AI: {result['log']}\n")
            else:
                sqli_result_text.insert(tk.END,
                                        f"\nНеожиданный ответ от API:\n{json.dumps(result, indent=2, ensure_ascii=False)}\n")
            status_setter("Получение плана SQLi завершено.")
        except Exception as e:
            detailed_error = traceback.format_exc()
            sqli_result_text.insert(tk.END, f"\nКритическая ошибка: {str(e)}\n\n{detailed_error}\n")
            status_setter(f"SQLi-тестер: Критическая ошибка: {str(e)}")

    def run_sqli_test_command():
        url = sqli_url_entry.get();
        method = sqli_method_combo.get();
        params_str = sqli_params_entry.get()
        cookies_str = sqli_cookies_entry.get();
        test_type = sqli_test_type_combo.get()
        if not url: messagebox.showerror("Ошибка", "URL не указан.", parent=tab_frame); return
        sqli_test_button.config(state=tk.DISABLED)

        def thread_target_wrapper():
            try:
                _sqli_test_thread_worker(url, method, params_str, cookies_str, test_type)
            finally:
                if tab_frame.winfo_exists():
                    tab_frame.after(0, lambda: sqli_test_button.config(state=tk.NORMAL))

        threading.Thread(target=thread_target_wrapper, daemon=True).start()

    sqli_test_button.config(command=run_sqli_test_command)