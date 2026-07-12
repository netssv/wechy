---
name: web_auditing_techniques
description: Técnicas y metodologías utilizadas para realizar auditorías sobre DNS, certificados SSL, rendimiento de carga de red y headers de seguridad.
---

# Skill: Técnicas de Auditoría Web

Esta skill instruye sobre los criterios y flujos de análisis que se utilizan para evaluar la infraestructura de un sitio web de manera robusta, tanto a través de las skills agénticas de Python como de los comandos nativos de Linux integrados en la TUI `wechy`.

## 1. Validación de DNS y Red
- **Propagación Regional**: Consultar múltiples resolvedores de DNS geográficamente distribuidos de forma concurrente usando hilos para medir la consistencia del direccionamiento.
- **Tipos de Registros**: Extraer de forma estructurada los registros A, AAAA, MX, CNAME, TXT y NS para validar la configuración del dominio.
- **Herramientas nativas**: Invocar `dig +short` y `nslookup` para obtener resultados directos del sistema operativo sin dependencias de terceros.

## 2. Inspección del Certificado de Seguridad (SSL/TLS)
- **Cálculo de Expiración**: Conectarse al puerto 443 del dominio objetivo y analizar las fechas `notBefore` y `notAfter` en el certificado para calcular los días de validez restantes.
- **Validación del Emisor y SANs**: Extraer el emisor del certificado y los Subject Alternative Names (SANs) para asegurar que el certificado cubre el dominio auditado.
- **Herramientas nativas**: Usar `openssl s_client` y `openssl x509` para obtener la cadena de certificados, protocolo TLS, cifrado y fingerprint directamente desde la terminal.

## 3. Análisis de Rendimiento y Optimización
- **Tiempos de Respuesta**: Evaluar el tiempo total transcurrido desde el inicio de la petición HTTP hasta la recepción completa del contenido.
- **Validación de Caching y Compresión**: Comprobar la existencia del encabezado `Content-Encoding: gzip/br` para validar la transferencia comprimida, y verificar directivas de `Cache-Control` y `ETag`.
- **Herramientas nativas**: Invocar `curl -w` con formato personalizado para medir tiempos granulares de DNS, conexión, TLS, y transferencia total.

## 4. Auditoría de Headers de Seguridad
- **Verificación de Seguridad en Transporte**: Comprobar si `Strict-Transport-Security` (HSTS) está forzando conexiones seguras.
- **Políticas de Origen e Inyección**: Evaluar la presencia y robustez de los headers `Content-Security-Policy` (CSP), `X-Frame-Options` y `X-Content-Type-Options` para mitigar ataques XSS y Clickjacking.

## 5. Validación de Dominio de Correo Electrónico
- **Registros MX**: Verificar que el dominio tiene servidores de correo configurados correctamente.
- **SPF (Sender Policy Framework)**: Buscar en los registros TXT la cadena `v=spf1` que autoriza servidores de envío.
- **DKIM (DomainKeys Identified Mail)**: Consultar selectores comunes (`default`, `google`, `selector1`, `selector2`, `k1`) en `_domainkey.{domain}`.
- **DMARC**: Verificar la existencia del registro TXT en `_dmarc.{domain}` para la política de autenticación de correo.
