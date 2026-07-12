---
name: refactoring_process
description: Instrucciones y técnicas que guían el proceso para identificar lógica monolítica, desacoplar dependencias y refactorizar código de flujos LLM hacia una arquitectura modular basada en agentes y skills.
---

# Skill: Proceso de Refactorización y Modularización

Esta skill instruye al agente sobre el proceso técnico y las directrices utilizadas para transformar el proyecto monolítico en una estructura desacoplada basada en agentes de IA, herramientas dinámicas y una TUI interactiva.

## 1. Identificación de Lógica Monolítica
Para iniciar la refactorización, el proceso requiere:
- **Analizar dependencias acopladas**: Buscar funciones donde el análisis de red, la lógica de negocio y los elementos de visualización (Streamlit/HTML) estén entremezclados en un solo método.
- **Localizar parámetros estáticos**: Identificar listas de servidores DNS, timeouts o credenciales incrustadas de forma estática (`hardcoded`) en el código fuente.
- **Detectar scripts legacy**: Reconocer scripts bash antiguos monolitico (`auditweb.sh`) cuya funcionalidad puede ser portada a Python para unificar la base de código bajo un solo paquete.

## 2. Estrategia de Desacoplamiento (Lógica, Configuración y Agente)
El proceso de separación se ejecuta mediante las siguientes directrices:
- **Configuración Externa**: Mover constantes de tiempo, diccionarios de servidores DNS y credenciales de APIs de modelos a módulos independientes bajo `config/`.
- **Modelado de Datos Estricto**: Definir esquemas claros con Dataclasses en `models/` para evitar el paso de estructuras débiles (como diccionarios anidados arbitrarios) entre los distintos servicios.
- **Aislamiento de UI**: La interfaz de usuario no debe procesar ni calcular métricas técnicas directas; su único rol debe ser renderizar los resultados consolidados de los reportes.

## 3. Encapsulamiento de Skills Propias
Para que una funcionalidad sea considerada una skill agéntica reutilizable:
- Se implementa una clase base abstracta (`BaseSkill`) que requiere metadatos descriptivos legibles por el LLM.
- Cada skill debe ser independiente y autocontenida, validando sus parámetros de entrada antes de su ejecución para prevenir excepciones inesperadas en el ciclo del agente.
- Las skills se auto-registran en el `SkillRegistry` vía decorador `@SkillRegistry.register` al ser importadas.

## 4. Integración y Comportamiento del Agente
- Se diseña un agente central (`AuditAgent`) dotado de un bucle de razonamiento autónomo (Think → Act → Observe).
- El agente lee el catálogo de skills a través del registro dinámico (`SkillRegistry`) y decide de forma inteligente qué herramientas invocar en función de los datos de entrada, adaptando su comportamiento dinámicamente si alguna skill falla.

## 5. Diseño de la TUI Interactiva (wechy)
- Se construye una interfaz de terminal (TUI) usando la librería Textual que presenta un menú principal intuitivo.
- La TUI integra tanto las skills agénticas de Python como comandos nativos de Linux (`dig`, `nslookup`, `openssl`, `curl`) para ofrecer diagnósticos directos sin dependencias externas innecesarias.
- La herramienta se empaqueta para PyPI bajo el nombre `wechy` con un único comando de invocación (`wechy`) sin requerir argumentos complejos.
- Se incluyen herramientas de validación de correo electrónico (MX, SPF, DKIM, DMARC) como capacidad adicional integrada en el menú.
