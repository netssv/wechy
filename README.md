# 🔍 AI-Agentic Web Audit Tool

Un auditor de sitios web inteligente, modular y extensible con soporte para agentes de IA autónomos y herramientas estructuradas (skills agénticas).

---

## ✨ Características

- **🤖 Agente Orquestador Central (`AuditAgent`)**: Razona autónomamente qué herramientas invocar según el dominio y modo de auditoría.
- **🧩 Arquitectura de Skills Agénticas**: Sistema modular donde cada herramienta (DNS, SSL, Performance, Security Headers, WHOIS, Tech Detection) se autodescribe para ser consumida mediante *Function Calling* por el LLM.
- **🎨 Interfaz Streamlit Renovada**: Panel de control limpio y interactivo que muestra las visualizaciones y el análisis generado por la IA en tiempo real.
- **⚙️ Configuración Desacoplada**: Centralización de umbrales, timeouts y claves en variables de entorno.
- **🧠 Personalización de Agentes**: Incluye especificaciones en `.agents/` para guiar a asistentes de desarrollo de IA.

---

## 🚀 Inicio Rápido

### 1. Clonar e Instalar Dependencias

```bash
git clone https://github.com/netssv/enhanced-web-audit-script.git
cd enhanced-web-audit-script
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurar el LLM (Opcional)

Establece tu proveedor y clave API para el agente de IA:

```bash
export LLM_PROVIDER="google"
export LLM_MODEL="gemini-2.0-flash"
export LLM_API_KEY="tu-api-key"
```

### 3. Ejecutar la Aplicación

Puedes lanzar la interfaz gráfica:

```bash
streamlit run streamlit_web_audit.py
```

O realizar una auditoría desde la terminal:

```bash
python demo_audit.py google.com
```

---

## 🏗️ Guía Técnica

Consulta las [TECHNICAL_NOTES.md](file:///home/netss/Projects/enhanced-web-audit-script/TECHNICAL_NOTES.md) para comprender a fondo la arquitectura, el flujo agéntico y cómo extender el sistema con nuevas skills agénticas.
