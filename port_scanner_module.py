# port_scanner_module.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import traceback
import json


def create_tab(tab_frame, api_service, selected_model_var, status_setter, theme_colors, dynamic_font_widgets_list):
    scrolledtext_bg = theme_colors.get("scrolledtext_bg", "#1e1e1e")
    scrolledtext_fg = theme_colors.get("scrolledtext_fg", "white")
    text_font_to_use = theme_colors.get("text_font")

    frame = ttk.Frame(tab_frame)
    frame.pack(fill="both", expand=True)

    top_frame = ttk.Frame(frame)
    top_frame.pack(fill="x", pady=(0, 5))

    ttk.Label(top_frame, text="Цель:").grid(row=0, column=0, sticky="w", padx=(0, 5), pady=2)
    ps_target_entry = ttk.Entry(top_frame, width=40, font=text_font_to_use)
    ps_target_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
    ps_target_entry.insert(0, "example.com")
    dynamic_font_widgets_list.append(ps_target_entry)

    ttk.Label(top_frame, text="Порты:").grid(row=1, column=0, sticky="w", padx=(0, 5), pady=2)
    ps_ports_entry = ttk.Entry(top_frame, width=40, font=text_font_to_use)
    ps_ports_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
    ps_ports_entry.insert(0, "80,443,22,8080")
    dynamic_font_widgets_list.append(ps_ports_entry)

    top_frame.columnconfigure(1, weight=1)

    ps_scan_button = ttk.Button(top_frame, text="Анализ (AI)")
    ps_scan_button.grid(row=0, column=2, rowspan=2, padx=5, pady=2, sticky="ns")

    results_control_frame = ttk.Frame(frame)
    results_control_frame.pack(fill="x", pady=(2, 2))

    def copy_results():
        content = ps_result_text.get("1.0", tk.END).strip()
        if content:
            try:
                tab_frame.clipboard_clear()
                tab_frame.clipboard_append(content)
                status_setter("Результаты скопированы в буфер обмена.")
            except tk.TclError as e_clip:
                status_setter(f"Ошибка буфера обмена: {e_clip}")
                messagebox.showwarning("Буфер обмена", f"Не удалось получить доступ к буферу обмена:\n{e_clip}",
                                       parent=tab_frame)
        else:
            status_setter("Нет текста для копирования.")

    copy_button = ttk.Button(results_control_frame, text="Копировать результаты", command=copy_results)
    copy_button.pack(side=tk.RIGHT, padx=0)

    ps_result_text = scrolledtext.ScrolledText(frame, height=15, bg=scrolledtext_bg, fg=scrolledtext_fg, wrap=tk.WORD,
                                               relief="solid", bd=1, font=text_font_to_use)
    dynamic_font_widgets_list.append(ps_result_text)
    ps_result_text.pack(fill="both", expand=True)

    def _port_scan_thread_worker(target, ports_str):
        status_setter(f"Анализ портов для {target} с помощью AI...")
        ps_result_text.delete(1.0, tk.END)
        scan_data_payload = {"target": target, "ports": ports_str}
        try:
            if not api_service or not hasattr(api_service, 'analyze_network'):
                ps_result_text.insert(tk.END,
                                      "Экземпляр AI сервиса не инициализирован или метод 'analyze_network' не найден.\n")
                status_setter("Ошибка AI сервиса.");
                return
            result = api_service.analyze_network(scan_data_payload)  # model_to_use убран
            if isinstance(result, dict) and "error" in result:
                ps_result_text.insert(tk.END, f"Ошибка API: {result['error']}\n")
                if result.get("status_code"): ps_result_text.insert(tk.END, f"Status Code: {result['status_code']}\n")
            elif result and isinstance(result, dict) and result.get("status") == "success" and "data" in result:
                data = result["data"]
                ps_result_text.insert(tk.END,
                                      f"Результаты анализа для {data.get('target', target)} (порты: {ports_str}):\n\n")
                ports_summary = data.get("ports_summary", {})
                if isinstance(ports_summary, dict):
                    for port, info in ports_summary.items():
                        if isinstance(info, dict):
                            ps_result_text.insert(tk.END,
                                                  f"Порт {port} ({info.get('service', 'N/A')}): {info.get('status', 'N/A')}\n")
                vulnerabilities_or_advice = data.get("vulnerabilities", [])
                if vulnerabilities_or_advice:
                    ps_result_text.insert(tk.END, "\nРекомендации/Анализ от AI:\n")
                    for item in vulnerabilities_or_advice: ps_result_text.insert(tk.END, f"- {item}\n")
                else:
                    ps_result_text.insert(tk.END, "AI не предоставил рекомендаций.\n")
            else:
                ps_result_text.insert(tk.END, f"Неожиданный ответ от API:\n{json.dumps(result, indent=2)}\n")
            status_setter(f"Анализ портов для {target} завершен.")
        except Exception as e:
            detailed_error = traceback.format_exc()
            ps_result_text.insert(tk.END, f"Ошибка: {str(e)}\n\n{detailed_error}")
            status_setter(f"Ошибка анализа: {str(e)}")

    def run_port_scan_command():
        target = ps_target_entry.get();
        ports = ps_ports_entry.get()
        if not target: messagebox.showerror("Ошибка", "Цель не указана.", parent=tab_frame); return
        ps_scan_button.config(state=tk.DISABLED)

        def thread_target_wrapper():
            try:
                _port_scan_thread_worker(target, ports)
            finally:
                if tab_frame.winfo_exists(): tab_frame.after(0, lambda: ps_scan_button.config(state=tk.NORMAL))

        threading.Thread(target=thread_target_wrapper, daemon=True).start()

    ps_scan_button.config(command=run_port_scan_command)