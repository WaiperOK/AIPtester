# api_tester_gui_module.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
import requests
import traceback


def create_tab(tab_frame, api_service_unused, selected_model_var_unused, status_setter, theme_colors,
               dynamic_font_widgets_list):
    scrolledtext_bg = theme_colors.get("scrolledtext_bg", "#1e1e1e")
    scrolledtext_fg = theme_colors.get("scrolledtext_fg", "white")
    text_font_to_use = theme_colors.get("text_font")

    frame = ttk.Frame(tab_frame)
    frame.pack(fill="both", expand=True)

    input_frame = ttk.Frame(frame)
    input_frame.pack(fill="x", pady=(0, 5))

    ttk.Label(input_frame, text="URL:").grid(row=0, column=0, sticky="w", padx=(0, 5), pady=2)
    apit_url_entry = ttk.Entry(input_frame, width=60, font=text_font_to_use)
    apit_url_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=2, sticky="ew")
    apit_url_entry.insert(0, "https://jsonplaceholder.typicode.com/todos/1")
    dynamic_font_widgets_list.append(apit_url_entry)

    ttk.Label(input_frame, text="Метод:").grid(row=1, column=0, sticky="w", padx=(0, 5), pady=2)
    apit_method_combo = ttk.Combobox(input_frame, width=10, font=text_font_to_use, values=[
        "GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"
    ], state="readonly")
    apit_method_combo.grid(row=1, column=1, padx=5, pady=2, sticky="w")
    apit_method_combo.current(0)

    apit_send_button = ttk.Button(input_frame, text="Отправить запрос")
    apit_send_button.grid(row=1, column=2, padx=5, pady=2, sticky="e")

    input_frame.columnconfigure(1, weight=1)

    paned_window_req = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
    paned_window_req.pack(fill="both", expand=True, pady=5)

    headers_frame = ttk.Labelframe(paned_window_req, text="Заголовки запроса (Ключ:Значение, 1 на строку)", padding=5)
    apit_headers_text = scrolledtext.ScrolledText(headers_frame, height=6, bg=scrolledtext_bg, fg=scrolledtext_fg,
                                                  relief="solid", bd=1, wrap=tk.WORD, font=text_font_to_use)
    apit_headers_text.pack(fill="both", expand=True)
    apit_headers_text.insert(tk.END, "Content-Type: application/json\nUser-Agent: ElitePentestAIToolkit/1.0")
    dynamic_font_widgets_list.append(apit_headers_text)
    paned_window_req.add(headers_frame, weight=1)

    body_frame = ttk.Labelframe(paned_window_req, text="Тело запроса", padding=5)
    apit_body_text = scrolledtext.ScrolledText(body_frame, height=6, bg=scrolledtext_bg, fg=scrolledtext_fg,
                                               relief="solid", bd=1, wrap=tk.WORD, font=text_font_to_use)
    apit_body_text.pack(fill="both", expand=True)
    dynamic_font_widgets_list.append(apit_body_text)
    paned_window_req.add(body_frame, weight=1)

    response_main_frame = ttk.Labelframe(frame, text="Ответ от сервера", padding=5)
    response_main_frame.pack(fill="both", expand=True, pady=(5, 0))

    apit_status_label = ttk.Label(response_main_frame, text="Статус: -", font=text_font_to_use)
    apit_status_label.pack(fill="x")
    dynamic_font_widgets_list.append(apit_status_label)

    paned_window_resp = ttk.PanedWindow(response_main_frame, orient=tk.HORIZONTAL)
    paned_window_resp.pack(fill="both", expand=True, pady=5)  # <--- ИСПРАВЛЕНО ЗДЕСЬ

    resp_headers_frame = ttk.Labelframe(paned_window_resp, text="Заголовки ответа", padding=5)
    apit_resp_headers_text = scrolledtext.ScrolledText(resp_headers_frame, height=6, bg=scrolledtext_bg,
                                                       fg=scrolledtext_fg, relief="solid", bd=1, wrap=tk.WORD,
                                                       font=text_font_to_use)
    apit_resp_headers_text.pack(fill="both", expand=True)
    dynamic_font_widgets_list.append(apit_resp_headers_text)
    paned_window_resp.add(resp_headers_frame, weight=1)

    resp_body_frame = ttk.Labelframe(paned_window_resp, text="Тело ответа", padding=5)
    body_copy_frame = ttk.Frame(resp_body_frame)
    body_copy_frame.pack(fill="x", pady=(0, 2))  # Размещаем фрейм для кнопки сверху

    apit_resp_body_text = scrolledtext.ScrolledText(resp_body_frame, height=8, bg=scrolledtext_bg, fg=scrolledtext_fg,
                                                    relief="solid", bd=1, wrap=tk.WORD, font=text_font_to_use)
    apit_resp_body_text.pack(fill="both", expand=True)  # Текстовое поле заполняет оставшееся место в resp_body_frame
    dynamic_font_widgets_list.append(apit_resp_body_text)
    paned_window_resp.add(resp_body_frame, weight=1)

    def copy_response_body():
        content = apit_resp_body_text.get("1.0", tk.END).strip()
        if content:
            try:
                tab_frame.clipboard_clear()
                tab_frame.clipboard_append(content)
                status_setter("Тело ответа скопировано.")
            except tk.TclError as e_clip:
                status_setter(f"Ошибка буфера: {e_clip}")
                messagebox.showwarning("Буфер обмена", f"Не удалось получить доступ к буферу обмена:\n{e_clip}",
                                       parent=tab_frame)
        else:
            status_setter("Нет текста для копирования.")

    copy_btn_body = ttk.Button(body_copy_frame, text="Копировать тело", command=copy_response_body, width=15)
    copy_btn_body.pack(side=tk.RIGHT)  # Кнопка копирования для тела ответа

    def update_ui(callback, *args, **kwargs):
        if tab_frame.winfo_exists():
            tab_frame.after(0, lambda cb=callback, a=args, kw=kwargs: cb(*a, **kw))

    def _api_test_thread_worker(url, method, headers_str, body_str):
        update_ui(status_setter, f"Отправка {method} запроса на {url}...")
        update_ui(apit_status_label.config, text="Статус: Отправка...")
        update_ui(apit_resp_headers_text.delete, "1.0", tk.END)
        update_ui(apit_resp_body_text.delete, "1.0", tk.END)
        parsed_headers = {}
        if headers_str:
            for line in headers_str.split('\n'):
                if ':' in line:
                    key_val = line.split(':', 1);
                    parsed_headers[key_val[0].strip()] = key_val[1].strip() if len(key_val) > 1 else ""
        try:
            response = requests.request(method.upper(), url, headers=parsed_headers,
                                        data=body_str.encode('utf-8') if body_str and method.upper() in ["POST", "PUT",
                                                                                                         "PATCH"] else None,
                                        timeout=30)
            update_ui(apit_status_label.config, text=f"Статус: {response.status_code} {response.reason}")
            resp_headers_pretty = "\n".join([f"{k}: {v}" for k, v in response.headers.items()])
            update_ui(apit_resp_headers_text.insert, tk.END, resp_headers_pretty)
            try:
                json_response = response.json(); update_ui(apit_resp_body_text.insert, tk.END,
                                                           json.dumps(json_response, indent=4, ensure_ascii=False))
            except json.JSONDecodeError:
                update_ui(apit_resp_body_text.insert, tk.END, response.text)
            update_ui(status_setter, f"Запрос {method} на {url} ({response.status_code}).")
        except requests.exceptions.Timeout:
            update_ui(apit_status_label.config, text="Статус: Таймаут"); update_ui(apit_resp_body_text.insert, tk.END,
                                                                                   "Таймаут."); update_ui(status_setter,
                                                                                                          "Ошибка: Таймаут.")
        except requests.exceptions.RequestException as e:
            de = traceback.format_exc(); update_ui(apit_status_label.config,
                                                   text=f"Статус: Ошибка ({type(e).__name__})"); update_ui(
                apit_resp_body_text.insert, tk.END, f"Ошибка запроса:\n{str(e)}\n\n{de}"); update_ui(status_setter,
                                                                                                     f"Ошибка запроса: {str(e)}")
        except Exception as e:
            de = traceback.format_exc(); update_ui(apit_status_label.config,
                                                   text=f"Статус: Ошибка приложения ({type(e).__name__})"); update_ui(
                apit_resp_body_text.insert, tk.END, f"Ошибка: {str(e)}\n\n{de}"); update_ui(status_setter,
                                                                                            f"Внутренняя ошибка: {str(e)}")

    def run_api_test_request_command():
        url = apit_url_entry.get();
        method = apit_method_combo.get();
        headers_str = apit_headers_text.get("1.0", tk.END).strip();
        body_str = apit_body_text.get("1.0", tk.END).strip()
        if not url: messagebox.showerror("Ошибка", "URL не указан.", parent=tab_frame);return
        if not method: messagebox.showerror("Ошибка", "Метод HTTP не выбран.", parent=tab_frame);return
        apit_send_button.config(state=tk.DISABLED)

        def thread_target_wrapper():
            try:
                _api_test_thread_worker(url, method, headers_str, body_str)
            finally:
                if tab_frame.winfo_exists(): tab_frame.after(0, lambda: apit_send_button.config(state=tk.NORMAL))

        threading.Thread(target=thread_target_wrapper, daemon=True).start()

    apit_send_button.config(command=run_api_test_request_command)