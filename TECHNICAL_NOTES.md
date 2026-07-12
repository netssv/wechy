# ⚙️ Nota Técnica: Arquitectura del Sistema Agéntico — wechy

Esta nota técnica detalla la arquitectura modular y agéntica del proyecto **wechy** (Enhanced Web Audit Script), explicando el desacoplamiento de responsabilidades, la integración de IA y el diseño de la TUI.

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

[auditweb.sh (634 líneas)]
   ├── Bash scripts monolíticos con modules/ acoplados
   └── Ejecución secuencial sin agente inteligente
```

### Después (Modular y Agéntico)
```
[tui_app.py — wechy TUI]
       │ (Menú principal → selección de herramienta)
       ├── Comandos nativos Linux (dig, nslookup, openssl, curl)
       └── Skills agénticas de Python
              │
[agents/audit_agent.py — AuditAgent]
       │ (Loop: Think → Act → Observe)
       ▼
[skills/skill_registry.py — SkillRegistry]
       │ (Descubrimiento dinámico)
       ▼
[skills/*_skill.py — 6 skills agénticas]
       ▲
[config/*.py — Configuración desacoplada]
```

---

## 🧩 Skills Agénticas Implementadas

| Skill | Archivo | Categoría | Prioridad |
|-------|---------|-----------|-----------|
| `dns_analysis` | `dns_skill.py` | network | 1 (alta) |
| `ssl_analysis` | `ssl_skill.py` | security | 2 |
| `performance_analysis` | `performance_skill.py` | performance | 3 |
| `security_headers` | `security_skill.py` | security | 2 |
| `whois_lookup` | `whois_skill.py` | domain_info | 4 |
| `tech_detection` | `tech_detection_skill.py` | analysis | 4 |

---

## 🖥️ Diseño de la TUI (wechy)

### Menú Principal
```
╔══════════════════════════════════════════════╗
║  wechy — Web Check Your Site                ║
║  Powered by AI-Agentic Skills & Linux CLI   ║
╚══════════════════════════════════════════════╝

  🤖  AI Full Audit — Run all skills with AI analysis
  🌐  DNS Lookup — dig / nslookup queries
  🔒  SSL/TLS Inspector — openssl certificate details
  📡  HTTP Probe — curl response and headers
  🛡️  Security Headers Scan — check HSTS, CSP, etc.
  📧  Email Domain Validator — MX, SPF, DKIM, DMARC
  📄  WHOIS Lookup — domain registration info
  🔧  Tech Detection — server and framework fingerprint
```

### Flujo de Navegación
1. Usuario ejecuta `wechy` desde la terminal
2. Se muestra el menú principal con 8 opciones
3. Usuario selecciona una herramienta con flechas y Enter
4. Se abre la pantalla de la herramienta con campo de entrada
5. Usuario escribe el dominio/URL y presiona Run
6. Los resultados se muestran en tiempo real con formato rico
7. Escape para volver al menú, `q` para salir

### Integración de Comandos Nativos de Linux
La TUI ejecuta los comandos del sistema operativo de forma segura mediante `subprocess.run()`:
- **dig**: Consultas DNS por tipo (A, MX, NS, TXT)
- **nslookup**: Resolución de nombres alternativa
- **openssl**: Inspección de certificados SSL/TLS (cadena, fechas, SANs, cifrado)
- **curl**: Tiempos de respuesta HTTP desglosados y headers

### Stack Técnico
- **Textual**: Framework TUI moderno para Python (reemplaza ncurses)
- **Rich**: Renderizado de texto con colores, tablas y formato en terminal
- **Patrón de diseño**: Cada herramienta del menú despacha a un handler async que ejecuta el comando nativo o la skill agéntica correspondiente

---

## 🤖 Ciclo de Orquestación Agéntica

El `AuditAgent` no ejecuta un pipeline fijo. Utiliza el siguiente bucle:

```
1. Petición del usuario ("Audita google.com")
2. System prompt inyecta catálogo de Skills vía SkillRegistry
3. LLM decide llamar a "dns_analysis" (Action)
4. DNSSkill se ejecuta y devuelve resultados (Observation)
5. LLM evalúa y decide continuar con "ssl_analysis"
6. Al finalizar, genera el análisis ejecutivo con recomendaciones
```

---

## 📦 Empaquetado PyPI

El proyecto se distribuye como el paquete `wechy` con:
- **Dependencias core**: `requests`, `dnspython`, `python-whois`, `pyopenssl`, `textual`, `rich`
- **Extras opcionales**: `wechy[ai]` para soporte de LLM, `wechy[streamlit]` para la interfaz web
- **Entrypoint**: `wechy` → `tui_app_run:main`

---

## ⚙️ Skills de Personalización del Agente

Se definieron en `.agents/skills/` para guiar al agente de IA durante el desarrollo:
- **`refactoring_process`**: Directrices para identificar monolitos, desacoplar y construir skills agénticas
- **`web_auditing_techniques`**: Metodologías de auditoría DNS, SSL, rendimiento, seguridad y validación de email
