# ⚙️ Especificación Técnica y Arquitectura del Sistema Agéntico

Esta nota técnica detalla la arquitectura modular y agéntica del proyecto **Enhanced Web Audit Script**, explicando el desacoplamiento de responsabilidades y la integración de IA.

---

## 🏗️ Comparativa de Arquitectura: Antes vs. Después

### Antes (Monolito)
```
[streamlit_web_audit.py (824 líneas)]
   ├── Lógica de Red y DNS (resolución, propagación)
   ├── Lógica de Seguridad (SSL, headers)
   ├── Lógica de Rendimiento (cálculo de tiempos, compresión)
   ├── Servidores DNS y Timeouts hardcodeados
   └── Interfaz Gráfica (Streamlit, Plotly, HTML/CSS)
```

### Después (Modular y Agéntico)
```
[ui/app.py (Streamlit UI)]
       │ (Lee y visualiza)
       ▼
[models/audit_result.py (Modelos tipados / Dataclasses)]
       ▲
       │ (Genera / Modifica)
[agents/audit_agent.py (AuditAgent: Cerebro LLM)]
       │ (Razona y decide qué usar)
       ▼
[skills/skill_registry.py (Catálogo de herramientas)]
       │ (Descubre y crea)
       ▼
[skills/*_skill.py (Skills agénticas aisladas)]
       ▲
       │ (Parámetros desde configuración externa)
[config/*.py (Ajustes de red, DNS y LLM)]
```

---

## 🧩 Detalle de las Skills Agénticas Implementadas

Cada skill es ahora una entidad autónoma autodescriptiva que el agente LLM puede invocar:

1. **`dns_analysis`** (`dns_skill.py`):
   - **Objetivo**: Resolución del dominio y chequeo de propagación en 16 servidores globales concurrentes.
2. **`ssl_analysis`** (`ssl_skill.py`):
   - **Objetivo**: Extracción detallada del certificado TLS, SANs y cálculo de días hasta la expiración con alertas dinámicas.
3. **`performance_analysis`** (`performance_skill.py`):
   - **Objetivo**: Métricas HTTP de velocidad, tamaño y validación de caché.
4. **`security_headers`** (`security_skill.py`):
   - **Objetivo**: Escaneo y puntuación porcentual de los headers de endurecimiento HTTP (CSP, HSTS, X-Frame-Options).
5. **`whois_lookup`** (`whois_skill.py`):
   - **Objetivo**: Información del registrador del dominio.
6. **`tech_detection`** (`tech_detection_skill.py`):
   - **Objetivo**: Fingerprinting de tecnologías web (CMS, librerías, servidores).

---

## 🤖 El Ciclo de Orquestación Agéntica

El `AuditAgent` no ejecuta un pipeline fijo. Utiliza el siguiente bucle para orquestar la auditoría:

```
1. Petición del usuario ("Audita google.com")
2. Prompt de Sistema inyecta catálogo de Skills
3. LLM decide llamar a "dns_analysis" (Action)
4. DNSSkill se ejecuta y devuelve resultados (Observation)
5. LLM evalúa el resultado de DNS y decide continuar con "ssl_analysis"
6. Al finalizar los checks, el ReportAgent genera el informe en Markdown
```

---

## ⚙️ Mecanismo de Personalización del Agente (Agent Customizations)

Se crearon las siguientes definiciones de personalización bajo `.agents/skills/` para que los agentes de IA (como Gemini/Antigravity) entiendan el contexto del proyecto de forma nativa:
- **`web_auditing`** (`.agents/skills/web_auditing/SKILL.md`): Instruye al agente sobre cómo evaluar la salud general de una web y el significado de los niveles de alerta.
- **`skill_management`** (`.agents/skills/skill_management/SKILL.md`): Guía técnica para que el agente aprenda a crear y registrar nuevas skills agénticas respetando la arquitectura actual.
