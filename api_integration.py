# api_integration.py
import traceback
import json
import os
import requests
import time

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    from openai import OpenAI, APIConnectionError, RateLimitError, APIStatusError, APIError
except ImportError:
    OpenAI = None
    APIConnectionError = RateLimitError = APIStatusError = APIError = Exception

try:
    import anthropic
    from anthropic import Anthropic, APIConnectionError as AnthropicConnectionError, \
        RateLimitError as AnthropicRateLimitError, APIStatusError as AnthropicStatusError
except ImportError:
    anthropic = None
    Anthropic = AnthropicConnectionError = AnthropicRateLimitError = AnthropicStatusError = None


AI_SERVICES = {
    "Gemini": "GeminiAIService",
    "OpenAI": "OpenAIAIService",
    "Claude": "ClaudeAIService",
    "DeepSeek": "DeepSeekAIService",
    "Ollama-local": "OllamaLocalService",
    "Grok": "GrokAIService"
}

PREDEFINED_MODELS = {
    "Gemini": [
        "gemini-1.0-pro",
        "gemini-1.5-pro-latest",
        "gemini-1.5-flash-latest",
        "gemini-2.0-pro",
        "gemini-2.5-pro",
        "gemini-2.0-flash",
        "gemini-2.5-flash"
    ],
    "OpenAI": [
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo"
    ],
    "Claude": [
        "claude-3-5-sonnet-20241022",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229"
    ],
    "DeepSeek": [
        "DeepSeek-V3-0324",
        "DeepSeek-R1-0528"
    ],
    "Ollama-local": [],
    "Grok": [
        "grok-3",
        "grok-3-mini"

    ]
}

_GEMINI_API_CONFIGURED_GLOBALLY_WITH_KEY = None


def ensure_gemini_api_configured(api_key):
    global _GEMINI_API_CONFIGURED_GLOBALLY_WITH_KEY
    if _GEMINI_API_CONFIGURED_GLOBALLY_WITH_KEY != api_key:
        if not api_key or genai is None:
            _GEMINI_API_CONFIGURED_GLOBALLY_WITH_KEY = None
            return False
        try:
            genai.configure(api_key=api_key)
            _GEMINI_API_CONFIGURED_GLOBALLY_WITH_KEY = api_key
            print("Gemini API: Глобальная конфигурация ОК.")
            return True
        except Exception as e:
            print(f"Gemini API: Ошибка глобальной конфигурации: {e}")
            _GEMINI_API_CONFIGURED_GLOBALLY_WITH_KEY = None
            return False
    return True


class BaseAIService:
    def __init__(self, api_key=None, model_name=None):
        self.api_key = api_key
        self.model_name = model_name
        self.is_api_configured = False
        print(f"Инициализация {self.__class__.__name__} (ключ: {'Есть' if api_key else 'Нет'}, модель: {model_name})")

    def is_configured(self):
        return self.is_api_configured

    def update_api_key(self, api_key):
        self.api_key = api_key
        self._configure_service()

    def _configure_service(self):
        self.is_api_configured = False
        print(f"ПРЕДУПРЕЖДЕНИЕ: _configure_service не реализован для {self.__class__.__name__}")

    def set_model(self, model_name):
        self.model_name = model_name
        self._configure_service()

    def generate_text_content(self, prompt_text, temperature=0.7, top_p=1.0, top_k=40):
        return {"error": f"{type(self).__name__} generate_text_content не реализован."}

    def generate_xss_payload(self, params):
        return self.generate_text_content(self._create_xss_prompt(params))

    def generate_shellcode(self, params):
        return self.generate_text_content(self._create_shellcode_prompt(params), temperature=0.5)

    def perform_sqli_test(self, params):
        return self.generate_text_content(self._create_sqli_analysis_prompt(params))

    def osint_search(self, target, search_type):
        return self.generate_text_content(self._create_osint_prompt(target, search_type))

    def generate_exploit(self, vuln_type):
        return self.generate_text_content(self._create_exploit_code_prompt(vuln_type), temperature=0.6)

    def analyze_network(self, scan_data_dict):
        return self.generate_text_content(self._create_network_analysis_prompt(scan_data_dict))

    def crack_hash(self, hash_value, user_info=None):
        return self.generate_text_content(self._create_hash_crack_guidance_prompt(hash_value, user_info))

    def generate_pentest_plan(self, params):
        return self.generate_text_content(self._create_detailed_pentest_plan_prompt(params), temperature=0.6, top_k=50)

    def explain_text(self, text_to_explain, context=""):
        prompt = f"Объясни следующий текст {context}:\n\n---\n{text_to_explain}\n---\n\nОбъяснение должно быть подробным и понятным."
        return self.generate_text_content(prompt, temperature=0.5)

    def _create_xss_prompt(self, params):
        prompt = f"Сгенерируй XSS payload. Контекст: {params.get('context', 'HTML тег')}. "
        prompt += f"Желаемое действие (JavaScript): {params.get('custom_js', 'alert(\"XSS\")')}. "
        if 'event_handler' in params and params['event_handler'] != 'None':
            prompt += f"Обработчик: {params['event_handler']}. "
        if 'encoding' in params and params['encoding'] != 'None':
            prompt += f"Кодирование: {params['encoding']}. "
        if 'payload_template' in params and params['payload_template'] != 'Custom (see JS field)':
            prompt += f"Шаблон: {params['payload_template']}. "
        return prompt + "Только payload, без markdown и пояснений."

    def _create_shellcode_prompt(self, params):
        prompt = f"Команда msfvenom или шеллкод:\nPayload: {params.get('payload')}\nLHOST: {params.get('lhost')}\nLPORT: {params.get('lport')}\nАрхитектура: {params.get('arch', 'x86')}\nФормат: {params.get('format')}\n"
        if params.get('badchars'):
            prompt += f"Badchars: {params.get('badchars')}\n"
        if params.get('encoder') and params['encoder'] != 'None':
            prompt += f"Энкодер: {params['encoder']}\n"
        if params.get('nops') and str(params.get('nops', 0)).isdigit() and int(params.get('nops', 0)) > 0:
            prompt += f"NOP: {params.get('nops')}\n"
        if params.get('null_free'):
            prompt += "Null-free.\n"
        return prompt + "Только команда/шеллкод, без markdown и пояснений."

    def _create_sqli_analysis_prompt(self, params):
        return f"План тестирования SQLi для URL={params.get('url')}, метод {params.get('method')}, POST data '{params.get('data', '')}', cookies '{params.get('cookies', '')}', тип теста '{params.get('test_type', '')}'. Векторы, нагрузки. Без выполнения, только план."

    def _create_osint_prompt(self, target, search_type):
        return f"OSINT: Цель='{target}', Тип='{search_type}'. Ключевая публичная информация, структурировано."

    def _create_exploit_code_prompt(self, vuln_type):
        return f"Сгенерируй концептуальный пример кода или шаблон эксплойта (PoC) для уязвимости типа '{vuln_type}'. Если возможно, предоставь рабочий (но безопасный для демонстрации, например, вызывающий calc.exe или создающий файл) фрагмент кода на Python, C, или псевдокоде. Укажи основные части: подготовка payload, определение смещений (если применимо), метод доставки. Если прямой код невозможен, предоставь четкую структуру и ключевые функции. Избегай общих описаний, фокусируйся на практической структуре эксплойта. Не включай предупреждений об этике."

    def _create_network_analysis_prompt(self, scan_data_dict):
        return f"Хост '{scan_data_dict.get('target')}', открыты порты '{scan_data_dict.get('ports')}'. Следующие шаги анализа безопасности? Сервисы, уязвимости? Краткие рекомендации."

    def _create_hash_crack_guidance_prompt(self, hash_value, user_info=None):
        prompt = f"Хэш: '{hash_value}'. "
        if user_info:
            prompt += f"Контекст: '{user_info}'. "
        return prompt + "Популярные методы и инструменты для взлома. Шаги."

    def _create_detailed_pentest_plan_prompt(self, params):
        prompt = "Создай **чрезвычайно детальный, всеобъемлющий и профессиональный план проведения тестирования на проникновение**.\n\n"
        prompt += f"**1. Введение и Управленческое резюме:**\n   - Описание проекта.\n   - Цели: {params.get('objectives', 'Определить уязвимости, оценить риск, дать рекомендации.')}\n\n"
        prompt += f"**2. Область Тестирования (Scope):**\n   - Цели: {params.get('scope', 'Не указана')}\n   - Исключения.\n\n"
        prompt += f"**3. Тип Тестирования и Методологии:**\n   - Тип: {params.get('pentest_type', 'Комплексный')}. (Black/White/Grey Box).\n   - Методология: {params.get('methodology', 'PTES/OWASP')}.\n\n"
        prompt += f"**4. Информация о Цели:**\n   - Тех. стек: {params.get('target_info', 'Будет определено.')}\n\n"
        prompt += f"**5. Ограничения и Правила:**\n   - Временные рамки: {params.get('constraints', 'Согласовать.')}\n   - Запреты.\n\n"
        prompt += "**6. Детальные Этапы Тестирования:**\n   **6.1. Разведка:** Пассивный/активный сбор, инструменты.\n   **6.2. Сканирование и Анализ уязвимостей:** Авто/ручное, инструменты.\n   **6.3. Эксплуатация:** Проверка, Metasploit, пароли.\n   **6.4. Пост-Эксплуатация:** Привилегии, сбор данных, анализ сети, закрепление.\n   **6.5. Анализ и Документирование:** Классификация, описание, рекомендации.\n   **6.6. Отчет:** Резюме, тех. детали.\n   **6.7. Очистка.**\n\n"
        prompt += "**7. Инструментарий:** Список.\n\n**8. Отчетность:** Регулярность, формат.\n\n**9. Временные Рамки (Фазы):** Подготовка, Разведка, Сканирование, Эксплуатация, Пост-эксплуатация, Отчетность, Презентация.\n\n**10. Команда (если есть):** Роли.\n\nПлан должен быть практичным, структурированным (markdown)."
        return prompt


class GeminiAIService(BaseAIService):
    def __init__(self, api_key, model_name='gemini-1.5-pro-latest'):  # Изменяем дефолт на актуальную модель
        super().__init__(api_key, model_name)
        self.model_instance = None
        self._configure_service()

    def _configure_service(self):
        if not self.api_key or genai is None:
            print(
                "ПРЕДУПРЕЖДЕНИЕ (GeminiAIService): API ключ не предоставлен или библиотека 'google-generativeai' не установлена.")
            self.model_instance = None
            self.is_api_configured = False
            return
        if not ensure_gemini_api_configured(self.api_key):
            self.model_instance = None
            self.is_api_configured = False
            return
        try:
            print(f"GeminiAIService: Попытка инстанцирования модели '{self.model_name}'...")
            self.model_instance = genai.GenerativeModel(self.model_name)
            self.is_api_configured = True
            print(f"GeminiAIService: Успешно создан инстанс модели '{self.model_name}'.")
        except Exception as e:
            print(
                f"ОШИБКА (GeminiAIService): Не удалось создать инстанс '{self.model_name}': {e}\n{traceback.format_exc()}")
            self.model_instance = None
            self.is_api_configured = False

    def update_model(self, new_model_name):
        """Обновляет модель, переинициализируя model_instance."""
        if self.model_name != new_model_name:
            self.model_name = new_model_name
            self._configure_service()

    def generate_text_content(self, prompt_text, temperature=0.7, top_p=1.0, top_k=40):
        if not self.is_configured() or not self.model_instance:
            if self.api_key and not self.model_instance:
                self._configure_service()
            if not self.model_instance:
                return {"error": f"Gemini ('{self.model_name}'): не удалось создать инстанс.", "status_code": 503}

        print(
            f"GeminiAIService: Промпт (модель: {self.model_instance.model_name}, {len(prompt_text)} симв): {prompt_text[:80]}...")
        try:
            gen_config = genai.types.GenerationConfig(
                candidate_count=1,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k
            )
            response = self.model_instance.generate_content(prompt_text, generation_config=gen_config)

            if hasattr(response, 'text') and response.text:
                return {"status": "success", "text_response": response.text}

            if hasattr(response, 'parts') and response.parts:
                ft = "".join([p.text for p in response.parts if hasattr(p, 'text')])
                if ft:
                    return {"status": "success", "text_response": ft}

            if hasattr(response, 'candidates') and response.candidates and hasattr(response.candidates[0],
                                                                                   'content') and hasattr(
                    response.candidates[0].content, 'parts') and response.candidates[0].content.parts:
                ft = "".join([p.text for p in response.candidates[0].content.parts if hasattr(p, 'text')])
                if ft:
                    return {"status": "success", "text_response": ft}

            if hasattr(response, 'prompt_feedback') and hasattr(response.prompt_feedback, 'block_reason'):
                bm = getattr(response.prompt_feedback, 'block_reason_message', "N/A")
                return {"error": f"Контент заблокирован: {response.prompt_feedback.block_reason}. {bm}",
                        "status_code": "GEMINI_CONTENT_BLOCKED"}

            print(f"Gemini API: Не извлечен текст. Ответ: {response}")
            return {"error": "Не удалось извлечь текст от Gemini."}

        except Exception as e:
            error_msg = f"Ошибка генерации Gemini ({self.model_instance.model_name if self.model_instance else 'N/A'}): {str(e)}"
            print(f"{error_msg}\n{traceback.format_exc()}")
            return {"error": error_msg, "status_code": "GEMINI_API_ERROR"}

class OpenAIAIService(BaseAIService):
    def __init__(self, api_key, model_name='gpt-4o'):
        super().__init__(api_key, model_name)
        self.client = None
        self._configure_service()

    def _configure_service(self):
        if not self.api_key:
            print("OpenAI: API ключ не предоставлен.")
            self.is_api_configured = False
            self.client = None
            return
        if OpenAI is None:
            print("OpenAI: Библиотека 'openai' не установлена. Выполните: pip install openai")
            self.is_api_configured = False
            self.client = None
            return
        try:
            self.client = OpenAI(api_key=self.api_key)
            self.is_api_configured = True
            print(f"OpenAIAIService: Успешно сконфигурирован. Модель по умолчанию: {self.model_name}")
        except APIError as e:
            print(f"OpenAIAIService: Ошибка API при конфигурации: {e}")
            self.is_api_configured = False
            self.client = None
        except Exception as e:
            print(f"OpenAIAIService: Непредвиденная ошибка конфигурации: {e}\n{traceback.format_exc()}")
            self.is_api_configured = False
            self.client = None

    def generate_text_content(self, prompt_text, temperature=0.7, top_p=1.0, **kwargs):
        if not self.is_configured() or not self.client:
            return {"error": "OpenAI API не сконфигурирован (проверьте API ключ).", "status_code": 503}

        model_to_use = self.model_name or "gpt-4o"
        print(f"OpenAIAIService: Промпт к модели {model_to_use} (первые 100): {prompt_text[:100]}...")
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt_text}],
                model=model_to_use,
                temperature=float(temperature),
                top_p=float(top_p) if top_p is not None else None,
            )
            response_text = chat_completion.choices[0].message.content
            return {"status": "success", "text_response": response_text.strip()}
        except APIConnectionError as e:
            return {"error": f"OpenAI ошибка соединения: {e}", "status_code": "OPENAI_CONNECTION_ERROR"}
        except RateLimitError as e:
            return {"error": f"OpenAI превышен лимит запросов: {e}", "status_code": "OPENAI_RATE_LIMIT_ERROR"}
        except APIStatusError as e:
            return {"error": f"OpenAI ошибка статуса API: status_code={e.status_code}, response={e.response}",
                    "status_code": f"OPENAI_API_STATUS_{e.status_code}"}
        except APIError as e:
            return {"error": f"OpenAI ошибка API: {e}", "status_code": "OPENAI_API_ERROR"}
        except Exception as e:
            error_msg = f"Ошибка генерации OpenAI ({model_to_use}): {str(e)}"
            print(f"{error_msg}\n{traceback.format_exc()}")
            return {"error": error_msg, "status_code": "OPENAI_UNEXPECTED_ERROR"}


class OllamaLocalService(BaseAIService):
    def __init__(self, api_key_unused=None, model_name=None, ollama_base_url="http://localhost:11434"):
        super().__init__(None, model_name)
        self.ollama_base_url = ollama_base_url.rstrip('/')
        self._configure_service()

    def _configure_service(self):
        if not self.ollama_base_url:
            self.is_api_configured = False
            print("OllamaLocalService: URL для Ollama не указан.")
            return
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                available_models = [model['name'] for model in models]
                if not available_models:
                    print("OllamaLocalService: Нет доступных моделей на сервере Ollama.")
                    self.is_api_configured = False
                    return
                if self.model_name and self.model_name not in available_models:
                    print(
                        f"OllamaLocalService: Модель '{self.model_name}' не найдена. Доступные модели: {available_models}")
                    self.is_api_configured = False
                    return
                if not self.model_name:
                    self.model_name = available_models[0]
                    print(f"OllamaLocalService: Модель не указана, выбрана по умолчанию: {self.model_name}")
                self.is_api_configured = True
                print(f"OllamaLocalService: Подключен к {self.ollama_base_url}. Выбранная модель: {self.model_name}")
            else:
                self.is_api_configured = False
                print(f"OllamaLocalService: Ollama недоступен, код ответа: {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.is_api_configured = False
            print(f"OllamaLocalService: Не удалось подключиться к Ollama: {e}")

    def generate_text_content(self, prompt_text, temperature=0.7, **kwargs):
        if not self.is_configured():
            return {"error": "Ollama Local API не сконфигурирован или недоступен.", "status_code": 503}

        model_to_use = self.model_name
        if not model_to_use:
            return {"error": "Модель для Ollama не указана.", "status_code": 400}

        api_url = f"{self.ollama_base_url}/api/generate"
        payload = {
            "model": model_to_use,
            "prompt": prompt_text,
            "stream": False,
            "options": {"temperature": float(temperature)}
        }
        print(f"OllamaLocalService: Запрос к {api_url} с моделью {model_to_use} (промпт: {prompt_text[:80]}...)")
        try:
            response = requests.post(api_url, json=payload, timeout=120)
            response.raise_for_status()

            response_data = response.json()
            if "response" in response_data:
                return {"status": "success", "text_response": response_data["response"].strip()}
            elif "error" in response_data:
                return {"error": f"Ollama API ошибка: {response_data['error']}", "status_code": "OLLAMA_API_ERROR"}
            else:
                return {"error": "Неожиданный формат ответа от Ollama.", "details": response_data,
                        "status_code": "OLLAMA_UNEXPECTED_ERROR"}
        except requests.exceptions.ConnectionError as e:
            return {"error": f"Ollama: Ошибка соединения с {self.ollama_base_url}: {e}",
                    "status_code": "OLLAMA_CONNECTION_ERROR"}
        except requests.exceptions.Timeout:
            return {"error": f"Ollama: Таймаут запроса к {api_url}", "status_code": "OLLAMA_TIMEOUT"}
        except requests.exceptions.HTTPError as e:
            return {"error": f"Ollama: HTTP ошибка - {e.response.status_code} {e.response.text}",
                    "status_code": f"OLLAMA_HTTP_{e.response.status_code}"}
        except Exception as e:
            error_msg = f"Ошибка при работе с Ollama ({model_to_use}): {str(e)}"
            print(f"{error_msg}\n{traceback.format_exc()}")
            return {"error": error_msg, "status_code": "OLLAMA_UNEXPECTED_ERROR"}


class ClaudeAIService(BaseAIService):
    def __init__(self, api_key, model_name='claude-3-5-sonnet-20241022'):
        super().__init__(api_key, model_name)
        self.client = None
        self._configure_service()

    def _configure_service(self):
        if not self.api_key:
            print("Claude: API ключ не предоставлен.")
            self.is_api_configured = False
            self.client = None
            return
        if Anthropic is None:
            print("Claude: Библиотека 'anthropic' не установлена. Выполните: pip install anthropic")
            self.is_api_configured = False
            self.client = None
            return
        try:
            self.client = Anthropic(api_key=self.api_key)
            try:
                self.client.messages.create(
                    model=self.model_name,
                    max_tokens=10,
                    messages=[{"role": "user", "content": "ping"}]
                )
                self.is_api_configured = True
                print(f"ClaudeAIService: Успешно сконфигурирован. Модель: {self.model_name}")
            except Exception as e:
                print(f"ClaudeAIService: Модель '{self.model_name}' недоступна: {e}")
                self.is_api_configured = False
                self.client = None
        except Exception as e:
            print(f"ClaudeAIService: Ошибка конфигурации: {e}\n{traceback.format_exc()}")
            self.is_api_configured = False
            self.client = None

    def generate_text_content(self, prompt_text, temperature=0.7, top_p=1.0, top_k=40, **kwargs):
        if not self.is_configured() or not self.client:
            return {"error": "Claude API не сконфигурирован (проверьте API ключ).", "status_code": 503}

        model_to_use = self.model_name or "claude-3-5-sonnet-20241022"
        print(f"ClaudeAIService: Промпт к модели {model_to_use} (первые 100): {prompt_text[:100]}...")

        try:
            message = self.client.messages.create(
                model=model_to_use,
                max_tokens=4096,
                temperature=float(temperature),
                top_p=float(top_p),
                top_k=int(top_k),
                messages=[
                    {"role": "user", "content": prompt_text}
                ]
            )
            response_text = message.content[0].text
            return {"status": "success", "text_response": response_text.strip()}
        except AnthropicConnectionError as e:
            return {"error": f"Claude ошибка соединения: {e}", "status_code": "CLAUDE_CONNECTION_ERROR"}
        except AnthropicRateLimitError as e:
            return {"error": f"Claude превышен лимит запросов: {e}", "status_code": "CLAUDE_RATE_LIMIT_ERROR"}
        except AnthropicStatusError as e:
            return {"error": f"Claude ошибка статуса API: status_code={e.status_code}",
                    "status_code": f"CLAUDE_API_STATUS_{e.status_code}"}
        except Exception as e:
            error_msg = f"Ошибка генерации Claude ({model_to_use}): {str(e)}"
            print(f"{error_msg}\n{traceback.format_exc()}")
            return {"error": error_msg, "status_code": "CLAUDE_UNEXPECTED_ERROR"}


class DeepSeekAIService(BaseAIService):
    def __init__(self, api_key, model_name='DeepSeek-V3-0324'):
        super().__init__(api_key, model_name)
        self.base_url = "https://api.deepseek.com"
        self._configure_service()

    def _configure_service(self):
        if not self.api_key:
            print("DeepSeek: API ключ не указан.")
            self.is_api_configured = False
            return
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.get(f"{self.base_url}/models", headers=headers, timeout=10)
            if response.status_code == 200:
                models = response.json().get('data', [])
                available_models = [model['id'] for model in models]
                if self.model_name not in available_models:
                    print(
                        f"DeepSeekAIService: Модель '{self.model_name}' не найдена. Доступные модели: {available_models}")
                    self.is_api_configured = False
                    return
                self.is_api_configured = True
                print(f"DeepSeekAIService: API доступен. Модель: {self.model_name}")
            else:
                self.is_api_configured = False
                print(f"DeepSeekAIService: API недоступен, код ответа: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"DeepSeekAIService: Ошибка проверки API: {e}")
            self.is_api_configured = False

    def generate_text_content(self, prompt_text, temperature=0.7, top_p=1.0, **kwargs):
        if not self.is_configured():
            return {"error": "DeepSeek API не сконфигурирован.", "status_code": 503}

        model_to_use = self.model_name or "DeepSeek-V3-0324"
        print(f"DeepSeekAIService: Генерация текста с моделью {model_to_use} (промпт: {prompt_text[:80]}...)")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model_to_use,
            "messages": [
                {"role": "user", "content": prompt_text}
            ],
            "temperature": float(temperature),
            "top_p": float(top_p),
            "max_tokens": 4096,
            "stream": False
        }

        try:
            response = requests.post(f"{self.base_url}/chat/completions",
                                     headers=headers,
                                     json=payload,
                                     timeout=60)
            response.raise_for_status()

            response_data = response.json()
            if "choices" in response_data and len(response_data["choices"]) > 0:
                content = response_data["choices"][0]["message"]["content"]
                return {"status": "success", "text_response": content.strip()}
            else:
                return {"error": "Неожиданный формат ответа от DeepSeek", "details": response_data,
                        "status_code": "DEEPSEEK_UNEXPECTED_ERROR"}

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                return {"error": "DeepSeek: Неверный API ключ", "status_code": "DEEPSEEK_AUTH_ERROR"}
            elif e.response.status_code == 429:
                return {"error": "DeepSeek: Превышен лимит запросов", "status_code": "DEEPSEEK_RATE_LIMIT_ERROR"}
            return {"error": f"DeepSeek: HTTP ошибка - {e.response.status_code} {e.response.text}",
                    "status_code": f"DEEPSEEK_HTTP_{e.response.status_code}"}
        except requests.exceptions.ConnectionError as e:
            return {"error": f"DeepSeek: Ошибка соединения: {e}", "status_code": "DEEPSEEK_CONNECTION_ERROR"}
        except requests.exceptions.Timeout:
            return {"error": "DeepSeek: Таймаут запроса", "status_code": "DEEPSEEK_TIMEOUT"}
        except Exception as e:
            error_msg = f"Ошибка генерации DeepSeek ({model_to_use}): {str(e)}"
            print(f"{error_msg}\n{traceback.format_exc()}")
            return {"error": error_msg, "status_code": "DEEPSEEK_UNEXPECTED_ERROR"}


class GrokAIService(BaseAIService):
    def __init__(self, api_key, model_name='grok-3'):
        super().__init__(api_key, model_name)
        self.base_url = "https://api.x.ai/v1"
        self._configure_service()

    def _configure_service(self):
        if not self.api_key:
            print("Grok: API ключ не указан.")
            self.is_api_configured = False
            return
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.get(f"{self.base_url}/models", headers=headers, timeout=10)
            if response.status_code == 200:
                models = response.json().get('data', [])
                available_models = [model['id'] for model in models]
                if self.model_name not in available_models:
                    print(f"GrokAIService: Модель '{self.model_name}' не найдена. Доступные модели: {available_models}")
                    self.is_api_configured = False
                    return
                self.is_api_configured = True
                print(f"GrokAIService: API доступен. Модель: {self.model_name}")
            else:
                self.is_api_configured = False
                print(f"GrokAIService: API недоступен, код ответа: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"GrokAIService: Ошибка проверки API: {e}")
            self.is_api_configured = False

    def generate_text_content(self, prompt_text, temperature=0.7, top_p=1.0, **kwargs):
        if not self.is_configured():
            return {"error": "Grok API не сконфигурирован.", "status_code": 503}

        model_to_use = self.model_name or "grok-3"
        print(f"GrokAIService: Генерация текста с моделью {model_to_use} (промпт: {prompt_text[:80]}...)")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model_to_use,
            "messages": [
                {"role": "user", "content": prompt_text}
            ],
            "temperature": float(temperature),
            "top_p": float(top_p),
            "max_tokens": 4096,
            "stream": False
        }

        try:
            response = requests.post(f"{self.base_url}/chat/completions",
                                     headers=headers,
                                     json=payload,
                                     timeout=60)
            response.raise_for_status()

            response_data = response.json()
            if "choices" in response_data and len(response_data["choices"]) > 0:
                content = response_data["choices"][0]["message"]["content"]
                return {"status": "success", "text_response": content.strip()}
            else:
                return {"error": "Неожиданный формат ответа от Grok", "details": response_data,
                        "status_code": "GROK_UNEXPECTED_ERROR"}

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                return {"error": "Grok: Неверный API ключ", "status_code": "GROK_AUTH_ERROR"}
            elif e.response.status_code == 429:
                return {"error": "Grok: Превышен лимит запросов", "status_code": "GROK_RATE_LIMIT_ERROR"}
            return {"error": f"Grok: HTTP ошибка - {e.response.status_code} {e.response.text}",
                    "status_code": f"GROK_HTTP_{e.response.status_code}"}
        except requests.exceptions.ConnectionError as e:
            return {"error": f"Grok: Ошибка соединения: {e}", "status_code": "GROK_CONNECTION_ERROR"}
        except requests.exceptions.Timeout:
            return {"error": "Grok: Таймаут запроса", "status_code": "GROK_TIMEOUT"}
        except Exception as e:
            error_msg = f"Ошибка генерации Grok ({model_to_use}): {str(e)}"
            print(f"{error_msg}\n{traceback.format_exc()}")
            return {"error": error_msg, "status_code": "GROK_UNEXPECTED_ERROR"}



if __name__ == "__main__":

    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    claude_key = os.getenv("ANTHROPIC_API_KEY")
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    grok_key = os.getenv("GROK_API_KEY")

    services = [
        OpenAIAIService(api_key=openai_key, model_name="gpt-4o"),
        GeminiAIService(api_key=gemini_key, model_name="gemini-1.5-pro-latest"),
        ClaudeAIService(api_key=claude_key, model_name="claude-3-5-sonnet-20241022"),
        DeepSeekAIService(api_key=deepseek_key, model_name="DeepSeek-V3-0324"),
        OllamaLocalService(model_name="llama3"),
        GrokAIService(api_key=grok_key, model_name="grok-3")
    ]

    test_prompt = "Привет, напиши простой пример Python кода для вывода 'Hello, World!'"

    for service in services:
        if service.is_configured():
            print(f"\nТестирование {service.__class__.__name__}:")
            result = service.generate_text_content(test_prompt)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"\n{service.__class__.__name__} не сконфигурирован.")