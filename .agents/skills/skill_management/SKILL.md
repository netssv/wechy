---
name: refactoring_process
description: Instrucciones y técnicas que guían el proceso para identificar lógica monolítica, desacoplar dependencias y refactorizar código de flujos LLM hacia una arquitectura modular basada en agentes y skills.
---

# Skill de Personalización: Proceso de Refactorización y Modularización

Esta skill de personalización instruye al agente sobre el proceso técnico exacto y las directrices utilizadas para transformar el proyecto monolítico en una estructura desacoplada basada en agentes de IA y herramientas dinámicas.

## 1. Identificación de Lógica Monolítica
Para iniciar la refactorización, el proceso requiere:
- **Analizar dependencias acopladas**: Buscar funciones donde el análisis de red, la lógica de negocio y los elementos de visualización (Streamlit/HTML) estén entremezclados en un solo método.
- **Localizar parámetros estáticos**: Identificar listas de servidores DNS, timeouts o credenciales incrustadas de forma estática (`hardcoded`) en el código fuente.

## 2. Estrategia de Desacoplamiento (Lógica, Configuración y Agente)
El proceso de separación se ejecuta mediante las siguientes directrices:
- **Configuración Externa**: Mover constantes de tiempo, diccionarios de servidores DNS y credenciales de APIs de modelos a módulos independientes bajo `config/`.
- **Modelado de Datos Estricto**: Definir esquemas claros con Dataclasses en `models/` para evitar el paso de estructuras débiles (como diccionarios anidados arbitrarios) entre los distintos servicios.
- **Aislamiento de UI**: La interfaz de usuario no debe procesar ni calcular métricas técnicas directas; su único rol debe ser renderizar los resultados consolidados de los reportes.

## 3. Encapsulamiento de Skills Propias
Para que una funcionalidad sea considerada una skill agéntica reutilizable:
- Se implementa una clase base abstracta (`BaseSkill`) que requiere metadatos descriptivos legibles por el LLM.
- Cada skill debe ser independiente y autocontenida, validando sus parámetros de entrada antes de su ejecución para prevenir excepciones inesperadas en el ciclo del agente.

## 4. Integración y Comportamiento del Agente
- Se diseña un agente central (`AuditAgent`) dotado de un bucle de razonamiento autónomo.
- El agente lee el catálogo de skills a través de un registro dinámico (`SkillRegistry`) y decide de forma inteligente qué herramientas invocar en función de los datos de entrada, adaptando su comportamiento dinámicamente si alguna skill falla.
