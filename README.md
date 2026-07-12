# wechy - Web Check Your Site

Una herramienta de terminal (TUI) interactiva para auditar sitios web, revisar seguridad y analizar infraestructura. Todo apoyado por un agente de IA y skills autonomas.

## Que incluye

- AI Full Audit: Un agente que evalua y ejecuta herramientas por su cuenta.
- DNS Lookup: Consultas rapidas de red sin salir de la TUI usando dig y nslookup.
- SSL/TLS Inspector: Revisa los certificados y cadenas completas con openssl.
- HTTP Probe: Checa la velocidad de respuesta y los headers.
- Security Headers Scan: Verifica si un sitio tiene buenas practicas de seguridad (HSTS, CSP, etc).
- Email Domain Validator: Valida registros importantes de correo como MX, SPF, DKIM y DMARC.
- WHOIS Lookup: Informacion de registro del dominio.
- Tech Detection: Identifica el stack de servidor y los frameworks web.

## Como instalarlo

Si quieres correrlo directamente desde el repositorio:

```bash
git clone https://github.com/netssv/wechy.git
cd wechy
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Pronto estara en PyPI y podras instalarlo solo con `pip install wechy`.

## Como usarlo

La manera mas facil y recomendada de usarlo es iniciar la TUI interactiva. Solo tienes que correr esto en tu terminal:

```bash
.venv/bin/python tui_app_run.py
```

Vas a ver un menu principal en tu pantalla. Usa las flechas de tu teclado para moverte entre las opciones, escribe el dominio o URL que quieras revisar y presiona Run. Para regresar al menu, solo presiona la tecla Escape.

Si prefieres usarlo en modo comando directo sin la interfaz interactiva, puedes correr:
```bash
.venv/bin/python demo_audit.py google.com
```

## Configurar el agente de IA (Opcional)

Si quieres habilitar el analisis inteligente que te da recomendaciones y puntajes, solo necesitas configurar tus credenciales en la terminal:

```bash
export LLM_PROVIDER="google"
export LLM_MODEL="gemini-2.0-flash"
export LLM_API_KEY="tu-api-key"
```

## Sobre la arquitectura

Si te interesa como esta construido el codigo, puedes echarle un ojo al archivo TECHNICAL_NOTES.md. Ahi detallamos como pasamos de un monolito a una arquitectura basada en agentes y skills dinamicas.

## Licencia

Este proyecto usa la licencia MIT. Puedes revisar el archivo LICENSE para mas detalles.
