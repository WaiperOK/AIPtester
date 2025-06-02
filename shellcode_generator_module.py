# shellcode_generator_module.py
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

    title_font_family = text_font_to_use.cget("family") if text_font_to_use else "Arial"
    title_font_size = text_font_to_use.cget("size") + 4 if text_font_to_use else 14
    title_actual_font = font.Font(family=title_font_family, size=title_font_size, weight="bold")

    ttk.Label(frame, text="Генератор Шеллкодов (на базе AI)", font=title_actual_font).pack(pady=(0, 10),
                                                                                           anchor="center")

    input_frame = ttk.Frame(frame)
    input_frame.pack(fill="x", pady=5)

    row_idx = 0
    ttk.Label(input_frame, text="Payload (msfvenom):").grid(row=row_idx, column=0, sticky="w", padx=5, pady=2)
    sc_payload_type_combo = ttk.Combobox(input_frame, values=["windows/meterpreter/reverse_tcp",
                                                              "windows/x64/meterpreter/reverse_tcp",
                                                              "linux/x86/meterpreter/reverse_tcp",
                                                              "linux/x64/shell_reverse_tcp",
                                                              "osx/x64/shell_reverse_tcp",
                                                              "php/meterpreter/reverse_tcp",
                                                              "python/meterpreter/reverse_http",
                                                              "cmd/unix/reverse_python"], state="editable", width=45,
                                         font=text_font_to_use)
    sc_payload_type_combo.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew");
    sc_payload_type_combo.set("windows/meterpreter/reverse_tcp");
    row_idx += 1

    ttk.Label(input_frame, text="LHOST:").grid(row=row_idx, column=0, sticky="w", padx=5, pady=2);
    sc_lhost_entry = ttk.Entry(input_frame, width=45, font=text_font_to_use);
    sc_lhost_entry.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew");
    sc_lhost_entry.insert(0, "192.168.1.100");
    dynamic_font_widgets_list.append(sc_lhost_entry);
    row_idx += 1
    ttk.Label(input_frame, text="LPORT:").grid(row=row_idx, column=0, sticky="w", padx=5, pady=2);
    sc_lport_entry = ttk.Entry(input_frame, width=45, font=text_font_to_use);
    sc_lport_entry.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew");
    sc_lport_entry.insert(0, "4444");
    dynamic_font_widgets_list.append(sc_lport_entry);
    row_idx += 1
    ttk.Label(input_frame, text="Архитектура (Arch):").grid(row=row_idx, column=0, sticky="w", padx=5, pady=2);
    sc_arch_combo = ttk.Combobox(input_frame,
                                 values=["x86", "x64", "armle", "aarch64", "mipsle", "mipsbe", "cmd", "php", "python"],
                                 state="editable", width=45, font=text_font_to_use);
    sc_arch_combo.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew");
    sc_arch_combo.set("x86");
    row_idx += 1
    ttk.Label(input_frame, text="Формат вывода (-f):").grid(row=row_idx, column=0, sticky="w", padx=5, pady=2);
    sc_format_combo = ttk.Combobox(input_frame,
                                   values=["c", "python", "ruby", "raw", "hex", "js_le", "powershell", "exe", "elf",
                                           "macho", "asp", "war"], state="editable", width=45, font=text_font_to_use);
    sc_format_combo.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew");
    sc_format_combo.set("python");
    row_idx += 1
    ttk.Label(input_frame, text="Энкодер (-e, опционально):").grid(row=row_idx, column=0, sticky="w", padx=5, pady=2);
    sc_encoder_entry = ttk.Entry(input_frame, width=45, font=text_font_to_use);
    sc_encoder_entry.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew");
    sc_encoder_entry.insert(0, "x86/shikata_ga_nai");
    dynamic_font_widgets_list.append(sc_encoder_entry);
    row_idx += 1
    ttk.Label(input_frame, text="Плохие символы (-b, hex):").grid(row=row_idx, column=0, sticky="w", padx=5, pady=2);
    sc_badchars_entry = ttk.Entry(input_frame, width=45, font=text_font_to_use);
    sc_badchars_entry.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew");
    sc_badchars_entry.insert(0, "\\x00");
    dynamic_font_widgets_list.append(sc_badchars_entry);
    row_idx += 1
    ttk.Label(input_frame, text="NOP Sled (-n, опционально):").grid(row=row_idx, column=0, sticky="w", padx=5, pady=2);
    sc_nops_entry = ttk.Entry(input_frame, width=45, font=text_font_to_use);
    sc_nops_entry.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew");
    sc_nops_entry.insert(0, "0");
    dynamic_font_widgets_list.append(sc_nops_entry);
    row_idx += 1
    sc_null_free_var = tk.BooleanVar();
    sc_null_free_check = ttk.Checkbutton(input_frame, text="Null-free шеллкод", variable=sc_null_free_var);
    sc_null_free_check.grid(row=row_idx, column=1, sticky="w", padx=5, pady=2);
    row_idx += 1
    input_frame.columnconfigure(1, weight=1)
    sc_generate_button = ttk.Button(input_frame, text="Сгенерировать")
    sc_generate_button.grid(row=row_idx, column=0, columnspan=2, pady=10)
    results_control_frame = ttk.Frame(frame);
    results_control_frame.pack(fill="x", pady=(2, 2))

    def copy_results():
        content = sc_result_text.get("1.0", tk.END).strip()
        if content:
            try:
                tab_frame.clipboard_clear(); tab_frame.clipboard_append(content); status_setter("Шеллкод скопирован.")
            except tk.TclError as e_clip:
                status_setter(f"Ошибка буфера: {e_clip}"); messagebox.showwarning("Буфер обмена",
                                                                                  f"Не удалось: {e_clip}",
                                                                                  parent=tab_frame)
        else:
            status_setter("Нет текста для копирования.")

    copy_button = ttk.Button(results_control_frame, text="Копировать шеллкод", command=copy_results)
    copy_button.pack(side=tk.RIGHT, padx=0)
    sc_result_text = scrolledtext.ScrolledText(frame, height=10, bg=scrolledtext_bg, fg=scrolledtext_fg, wrap=tk.WORD,
                                               relief="solid", bd=1, font=text_font_to_use)
    dynamic_font_widgets_list.append(sc_result_text)
    sc_result_text.pack(fill="both", expand=True, pady=(0, 0))
    sc_result_text.insert(tk.END, "Ожидание генерации...\n")

    def _shellcode_thread_worker(params_dict):
        status_setter("Генерация шеллкода через AI...")
        sc_result_text.delete(1.0, tk.END)
        try:
            if not api_service or not hasattr(api_service, 'generate_shellcode'):
                sc_result_text.insert(tk.END,
                                      "AI сервис не инициализирован или метод 'generate_shellcode' не найден.\n");
                status_setter("Ошибка AI сервиса.");
                return
            result = api_service.generate_shellcode(params_dict)
            if isinstance(result, dict) and "error" in result:
                sc_result_text.insert(tk.END, f"Ошибка API: {result['error']}\n")
                if result.get("status_code"): sc_result_text.insert(tk.END, f"Status Code: {result['status_code']}\n")
            elif isinstance(result, dict) and result.get("status") == "success" and "shellcode_data" in result:
                sc_result_text.insert(tk.END, result["shellcode_data"])
            else:
                sc_result_text.insert(tk.END,
                                      f"Неожиданный ответ:\n{json.dumps(result, indent=2, ensure_ascii=False)}\n")
            status_setter("Генерация шеллкода завершена.")
        except Exception as e:
            detailed_error = traceback.format_exc(); sc_result_text.insert(tk.END,
                                                                           f"Ошибка: {str(e)}\n\n{detailed_error}\n"); status_setter(
                f"Ошибка генерации: {str(e)}")

    def run_generate_shellcode_command():
        params = {"payload": sc_payload_type_combo.get(), "lhost": sc_lhost_entry.get(), "lport": sc_lport_entry.get(),
                  "arch": sc_arch_combo.get(), "format": sc_format_combo.get(),
                  "encoder": sc_encoder_entry.get() or "None",
                  "badchars": sc_badchars_entry.get(), "nops": sc_nops_entry.get() or "0",
                  "null_free": sc_null_free_var.get()}
        if not all([params["payload"], params["lhost"], params["lport"], params["arch"],
                    params["format"]]): messagebox.showerror("Ошибка", "Основные поля должны быть заполнены.",
                                                             parent=tab_frame); return
        sc_generate_button.config(state=tk.DISABLED)

        def thread_target_wrapper():
            try:
                _shellcode_thread_worker(params)
            finally:
                if tab_frame.winfo_exists(): tab_frame.after(0, lambda: sc_generate_button.config(state=tk.NORMAL))

        threading.Thread(target=thread_target_wrapper, daemon=True).start()

    sc_generate_button.config(command=run_generate_shellcode_command)