#AIPtester

Welcome to the **ElitePentest AI Toolkit (Multi-AI Enhanced)**! This project is a versatile, Python-based desktop application designed to empower penetration testers and cybersecurity professionals by integrating the capabilities of multiple leading Artificial Intelligence models. Our goal is to streamline workflows, automate routine tasks, and provide intelligent assistance throughout the various phases of security testing.

The toolkit features a modular design, allowing for easy expansion and the addition of new tools and AI-driven functionalities.

##  Core Features

* **True Multi-AI Provider Support:**
    * Seamlessly switch between and utilize different AI powerhouses. Currently implemented providers:
        * **Google Gemini**
        * **OpenAI (GPT models)**
        * **Grok (xAI)**
        * **DeepSeek AI**
        * **Locally hosted models via Ollama** (e.g., Llama, Mistral, etc.)
    * User-selectable AI provider and specific model from the GUI.
    * Centralized API key management for different providers via `config.json`.
* **Comprehensive Suite of Pentesting Modules:**
    * **Pentest Plan Generator:** AI crafts detailed, structured, and professional penetration testing plans based on your input (scope, objectives, methodology).
    * **XSS Generator:** Generates diverse XSS payloads tailored for various contexts, JavaScript actions, and encoding techniques.
    * **Shellcode Generator:** AI assists in creating shellcode or `msfvenom` commands with parameters like payload type, LHOST/LPORT, architecture, format, and badchars.
    * **OSINT Assistant:** Leverages AI to gather, analyze, and structure publicly available information on specified targets.
    * **Exploit Guidance & Analysis:** AI provides insights into exploit structures, principles for various vulnerability types, and can explain provided exploit code.
    * **Network Analysis Assistant:** AI offers recommendations and next steps based on open port data from network scans.
    * **Hash Cracking Consultant:** AI provides guidance on methods, tools, and strategies for hash analysis and cracking.
    * **SQLi Testing Assistant:** AI generates testing plans and potential SQL injection vectors for given targets.
    * **API Tester GUI:** A standalone graphical tool for sending and analyzing HTTP/S requests to any API.
* **User-Friendly & Customizable GUI:**
    * Built with Python's Tkinter (`ttk`) for a clean, cross-platform interface.
    * Includes a dark theme for comfortable extended use.
    * Dynamic font size adjustment (increase/decrease) for main text areas.
    * Standard text editing features including a right-click context menu (Copy, Paste, Cut, Delete, Select All) and "Copy to Clipboard" buttons for results.
* **Configuration:** User preferences, including API keys for all supported providers, selected AI, model, and font size, are saved in a `config.json` file.

##  Screenshots

*(Placeholder: It is highly recommended to add screenshots here to showcase the toolkit's interface and capabilities.)*
* *Main window demonstrating AI provider & model selection.*
* *Pentest Plan Generator with example input and output.*
* *XSS Generator or Shellcode Generator in action.*
* *API Tester GUI.*

##  Tech Stack

* **Python 3.8+**
* **Tkinter (ttk)** for the Graphical User Interface.
* **AI Provider Libraries/APIs:**
    * `google-generativeai` for Google Gemini.
    * `openai` for OpenAI (GPT models).
    * `requests` (or specific SDKs if available and preferred) for Grok, DeepSeek, and Ollama (Ollama typically uses HTTP requests to its local server).
* `requests` library (also used by the API Tester GUI).

##  Setup and Installation

1.  **Prerequisites:**
    * Python 3.8 or newer.
    * `pip` (Python package installer).

2.  **Get the Code:**
    * Clone the repository (if applicable) or download the project files into a local directory.
    ```bash
    # Example if using Git
    # git clone https://your-repository-url/ElitePentestAIToolkit.git
    # cd ElitePentestAIToolkit
    ```

3.  **Create and Activate a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    # On Windows:
    # venv\Scripts\activate
    # On macOS/Linux:
    # source venv/bin/activate
    ```

4.  **Install Dependencies:**
    A `requirements.txt` file should be included (see generated content below). Install dependencies with:
    ```bash
    pip install -r requirements.txt
    ```
    Key libraries include `google-generativeai`, `openai`, and `requests`.

5.  **Configuration (`config.json`):**
    * The application will attempt to create a `config.json` file on first run if one doesn't exist.
    * You **must** add your API keys for the AI providers you intend to use. Edit `config.json`:
        ```json
        {
            "api_keys": {
                "Gemini": "YOUR_GEMINI_API_KEY",
                "OpenAI": "YOUR_OPENAI_API_KEY",
                "Grok": "YOUR_GROK_API_KEY", // Or relevant auth token
                "DeepSeek": "YOUR_DEEPSEEK_API_KEY",
                "Ollama-local": "" // Typically no key needed for local Ollama
            },
            "current_ai_provider": "Gemini", // e.g., Gemini, OpenAI, Grok, DeepSeek, Ollama-local
            "current_model": "gemini-1.0-pro", // A default model for the selected provider
            "font_size": 10,
            "theme": "dark"
        }
        ```
    * API keys can also be entered and saved via the GUI.

##  Usage

1.  Ensure your virtual environment is activated.
2.  Run the main application file from the project's root directory:
    ```bash
    python main.py
    ```
3.  **Using the GUI:**
    * **Select AI Provider:** Use the "AI Провайдер" dropdown to choose your desired AI service.
    * **Select Model:** The "Модель" dropdown will populate with available models for the selected provider. For Ollama, you can type the name of your locally served model.
    * **Enter API Key:** Input the API key for the selected provider in the "API Ключ (для AI)" field and click "Сохранить ключ". The API status will update.
    * **Adjust Font Size:** Use the "A+" / "A-" buttons to change the font size for readability.
    * **Navigate Tabs:** Each tab provides a different tool. Input the required information and click the action button (e.g., "Сгенерировать XSS", "Получить план пентеста").
    * **Copy Results:** Use the right-click context menu or dedicated "Копировать" buttons to copy text from output areas.

##  Modules Overview (Key Functionalities)
* **Port Scanner (AI Analysis):** AI provides insights on open ports.
* **Hash Cracker (AI Guidance):** AI suggests methods for hash cracking.
* **OSINT Reconnaissance (AI Powered):** AI gathers public information on targets.
* **Exploit Generator (AI Guidance & Explain):** AI offers conceptual exploit structures and can explain provided code.
* **API Tester GUI:** Manually test HTTP/S API endpoints.
* **SQLi Tester (AI Assistance):** AI helps generate SQLi testing plans and vectors.
* **Shellcode Generator (AI Assistance):** AI aids in crafting shellcode or `msfvenom` commands.
* **XSS Generator (AI Powered):** AI generates diverse XSS payloads.
* **Pentest Plan Generator (AI Powered):** AI creates comprehensive, detailed penetration testing plans.

---

This README provides a solid overview for users and potential contributors. Remember to replace placeholders (like repository URL or specific model IDs if they differ) and add actual screenshots to make it even more engaging!