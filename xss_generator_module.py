# xss_generator_module.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
import traceback
from tkinter import font


def create_tab(tab_frame, api_service, selected_model_var, status_setter, theme_colors, dynamic_font_widgets_list):
    scrolledtext_bg = theme_colors.get("scrolledtext_bg", "#1e1e1e")
    scrolledtext_fg = theme_colors.get("scrolledtext_fg", "white")
    text_font_to_use = theme_colors.get("text_font")

    frame = ttk.Frame(tab_frame)
    frame.pack(fill="both", expand=True)

    # Используем text_font_to_use, если он есть, или стандартный шрифт для заголовка
    title_font_family = text_font_to_use.cget("family") if text_font_to_use else "Arial"
    title_font_size = text_font_to_use.cget("size") + 4 if text_font_to_use else 14  # Заголовок чуть больше
    title_actual_font = font.Font(family=title_font_family, size=title_font_size, weight="bold")

    ttk.Label(frame, text="XSS-Генератор (на базе AI)", font=title_actual_font).pack(pady=(0, 10), anchor="center")

    input_frame = ttk.Frame(frame)
    input_frame.pack(fill="x", pady=5)

    row_idx = 0
    ttk.Label(input_frame, text="Контекст XSS:").grid(row=row_idx, column=0, sticky="w", padx=5, pady=2)
    xss_context_combo = ttk.Combobox(input_frame, values=[
        "HTML тег", "HTML атрибут (без кавычек)", "HTML атрибут (в двойных кавычках)",
        "HTML атрибут (в одинарных кавычках)", "JavaScript строковый литерал",
        "URL параметр/путь"
    ], state="readonly", width=50, font=text_font_to_use)
    xss_context_combo.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew");
    xss_context_combo.current(0);
    row_idx += 1

    ttk.Label(input_frame, text="Шаблон Payload:").grid(row=row_idx, column=0, sticky="w", padx=5, pady=2)
    xss_payload_template_combo = ttk.Combobox(input_frame, values=[
        "Custom (see JS field)", "<script>JS</script>", "<img src=x onerror=JS>",
        "<svg onload=JS>", "<a href='javascript:JS'>Click</a>",
        "\" onmouseover=JS data-dummy=\"", "' onmouseover=JS data-dummy='"
    ], state="readonly", width=50, font=text_font_to_use)
    xss_payload_template_combo.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew");
    xss_payload_template_combo.current(0);
    row_idx += 1

    ttk.Label(input_frame, text="Свой JavaScript (JS):").grid(row=row_idx, column=0, sticky="w", padx=5, pady=2)
    xss_custom_js_entry = ttk.Entry(input_frame, width=50, font=text_font_to_use)
    xss_custom_js_entry.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew");
    xss_custom_js_entry.insert(0, "alert(document.domain)");
    dynamic_font_widgets_list.append(xss_custom_js_entry);
    row_idx += 1

    ttk.Label(input_frame, text="Обработчик события:").grid(row=row_idx, column=0, sticky="w", padx=5, pady=2)
    xss_event_handler_combo = ttk.Combobox(input_frame,
                                           values=["None", "onerror", "onload", "onmouseover", "onclick", "onfocus",
                                                   "onblur"], state="readonly", width=50, font=text_font_to_use)
    xss_event_handler_combo.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew");
    xss_event_handler_combo.current(0);
    row_idx += 1

    ttk.Label(input_frame, text="Кодирование/Обфускация:").grid(row=row_idx, column=0, sticky="w", padx=5, pady=2)
    xss_encoding_combo = ttk.Combobox(input_frame, values=["None", "HTML Entities (decimal)", "HTML Entities (hex)",
                                                           "URL Encode (все символы)", "String.fromCharCode",
                                                           "eval(String.fromCharCode)", "Простые JS эскейпы (\\xHH)"],
                                      state="readonly", width=50, font=text_font_to_use)
    xss_encoding_combo.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew");
    xss_encoding_combo.current(0);
    row_idx += 1

    input_frame.columnconfigure(1, weight=1)
    xss_generate_button = ttk.Button(input_frame, text="Сгенерировать XSS")
    xss_generate_button.grid(row=row_idx, column=0, columnspan=2, pady=10)

    results_area_frame = ttk.Frame(frame)
    results_area_frame.pack(fill="both", expand=True, pady=(5, 0))
    results_control_frame_xss = ttk.Frame(results_area_frame)
    results_control_frame_xss.pack(fill="x", pady=(0, 2))

    xss_result_text = scrolledtext.ScrolledText(results_area_frame, height=10, bg=scrolledtext_bg, fg=scrolledtext_fg,
                                                wrap=tk.WORD, relief="solid", bd=1, font=text_font_to_use)
    dynamic_font_widgets_list.append(xss_result_text)

    def copy_xss_results():
        content = xss_result_text.get("1.0", tk.END).strip()
        if content:
            try:
                tab_frame.clipboard_clear(); tab_frame.clipboard_append(content); status_setter(
                    "XSS Payload скопирован.")
            except tk.TclError as e_clip:
                status_setter(f"Ошибка буфера: {e_clip}"); messagebox.showwarning("Буфер обмена",
                                                                                  f"Не удалось: {e_clip}",
                                                                                  parent=tab_frame)
        else:
            status_setter("Нет XSS Payload для копирования.")

    copy_button_xss = ttk.Button(results_control_frame_xss, text="Копировать XSS", command=copy_xss_results)
    copy_button_xss.pack(side=tk.RIGHT, padx=0)
    xss_result_text.pack(fill="both", expand=True)
    xss_result_text.insert(tk.END, "Ожидание генерации XSS...\n")

    def _xss_thread_worker(context, payload_template, custom_js, event_handler, encoding):
        status_setter("Генерация XSS через AI...")
        xss_result_text.delete(1.0, tk.END)
        params = {"context": context, "payload_template": payload_template, "custom_js": custom_js,
                  "event_handler": event_handler, "encoding": encoding}
        try:
            if not api_service or not hasattr(api_service, 'generate_xss_payload'):
                xss_result_text.insert(tk.END,
                                       "AI сервис не инициализирован или метод 'generate_xss_payload' не найден.\n");
                status_setter("Ошибка AI сервиса.");
                return
            result = api_service.generate_xss_payload(params)
            if isinstance(result, dict) and "error" in result:
                xss_result_text.insert(tk.END, f"Ошибка API: {result['error']}\n")
                if result.get("status_code"): xss_result_text.insert(tk.END, f"Status Code: {result['status_code']}\n")
            elif isinstance(result, dict) and result.get("status") == "success" and "xss_payload" in result:
                xss_result_text.insert(tk.END, result["xss_payload"])
            else:
                xss_result_text.insert(tk.END,
                                       f"Неожиданный ответ:\n{json.dumps(result, indent=2, ensure_ascii=False)}\n")
            status_setter("Генерация XSS завершена.")
        except Exception as e:
            detailed_error = traceback.format_exc(); xss_result_text.insert(tk.END,
                                                                            f"Ошибка: {str(e)}\n\n{detailed_error}\n"); status_setter(
                f"Ошибка XSS: {str(e)}")

    def run_generate_xss_command():
        params_list = [xss_context_combo.get(), xss_payload_template_combo.get(), xss_custom_js_entry.get(),
                       xss_event_handler_combo.get(), xss_encoding_combo.get()]
        xss_generate_button.config(state=tk.DISABLED)

        def thread_target_wrapper():
            try:
                _xss_thread_worker(*params_list)
            finally:
                if tab_frame.winfo_exists(): tab_frame.after(0, lambda: xss_generate_button.config(state=tk.NORMAL))

        threading.Thread(target=thread_target_wrapper, daemon=True).start()

    xss_generate_button.config(command=run_generate_xss_command)