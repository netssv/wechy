# 🔍 wechy — Web Check Your Site

Una herramienta interactiva de terminal (TUI) para diagnóstico web, auditoría de seguridad y análisis de infraestructura, potenciada por un agente de IA autónomo con skills agénticas.

---

## ✨ Características

- **🤖 AI Full Audit**: Agente orquestador que razona y ejecuta skills de forma autónoma vía LLM
- **🌐 DNS Lookup**: Consultas `dig` y `nslookup` directas desde la TUI
- **🔒 SSL/TLS Inspector**: Análisis de certificados con `openssl`
- **📡 HTTP Probe**: Tiempos de respuesta y headers con `curl`
- **🛡️ Security Headers Scan**: Evaluación de HSTS, CSP, X-Frame-Options y más
- **📧 Email Domain Validator**: Verificación de MX, SPF, DKIM y DMARC
- **📄 WHOIS Lookup**: Información de registro del dominio
- **🔧 Tech Detection**: Fingerprinting de servidor, CMS y frameworks

---

## 🚀 Instalación

### Desde PyPI (cuando esté publicado)
```bash
pip install wechy
```

### Desde el repositorio
```bash
git clone https://github.com/netssv/enhanced-web-audit-script.git
cd enhanced-web-audit-script
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 💻 Uso

### TUI Interactiva (recomendada)
```bash
wechy
```

O si estás ejecutando desde el repositorio:
```bash
.venv/bin/python tui_app.py
```

Se abrirá un menú principal con todas las herramientas disponibles. Selecciona una con las flechas del teclado, ingresa el dominio/URL y presiona **Run**.

### CLI Rápida (sin interfaz)
```bash
.venv/bin/python demo_audit.py google.com
```

### Interfaz Web (Streamlit)
```bash
pip install wechy[streamlit]
.venv/bin/streamlit run streamlit_web_audit.py
```

---

## ⚙️ Configuración del Agente de IA (Opcional)

Para habilitar el análisis inteligente con LLM:
```bash
export LLM_PROVIDER="google"     # google | openai | ollama
export LLM_MODEL="gemini-2.0-flash"
export LLM_API_KEY="tu-api-key"
```

---

## 🏗️ Arquitectura

Consulta [TECHNICAL_NOTES.md](TECHNICAL_NOTES.md) para la documentación completa de la arquitectura agéntica, el sistema de skills y las decisiones de diseño.

---

## 📝 Licencia

MIT License — ver [LICENSE](LICENSE).
