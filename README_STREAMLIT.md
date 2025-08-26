# Enhanced Web Audit Tool - Streamlit Version 🔍

Una herramienta completa de auditoría web con interfaz Streamlit para análisis integral de sitios web.

## 🚀 Características

### 🌐 Análisis DNS Completo
- **Propagación Global**: Verificación en 16 servidores DNS mundiales
- **Registros DNS**: A, AAAA, MX, NS, TXT, CNAME, SOA
- **Análisis Geográfico**: Servidores de USA 🇺🇸, China 🇨🇳, Rusia 🇷🇺, Suiza 🇨🇭
- **Detección de Inconsistencias**: Identificación automática de problemas de propagación

### 🔒 Análisis SSL Avanzado
- **Validación de Certificados**: Estado, expiración, cadena de confianza
- **Alertas de Vencimiento**: Avisos automáticos 30/90 días antes
- **Información del Emisor**: Detalles de la autoridad certificadora
- **Subject Alternative Names**: Dominios adicionales cubiertos

### ⚡ Análisis de Rendimiento
- **Tiempo de Respuesta**: Medición precisa en milisegundos
- **Optimización**: Compresión, caché, headers de rendimiento
- **Visualización**: Gráficos interactivos con Plotly
- **Métricas del Servidor**: Identificación de tecnologías web

### 🛡️ Análisis de Seguridad
- **Headers de Seguridad**: HSTS, CSP, X-Frame-Options, etc.
- **Puntuación de Seguridad**: Calificación automática 0-100%
- **Recomendaciones**: Sugerencias para mejorar la seguridad
- **Detección de Vulnerabilidades**: Análisis de configuraciones

### 📄 Información de Dominio
- **WHOIS Lookup**: Registrador, fechas, nameservers
- **Edad del Dominio**: Cálculo automático
- **Detección de Tecnologías**: Frameworks, CMS, servidores
- **Información del Hosting**: Proveedor e infraestructura

## 🛠️ Instalación

### 1. Clona el repositorio
```bash
git clone https://github.com/netssv/enhanced-web-audit-script.git
cd enhanced-web-audit-script
```

### 2. Instala las dependencias
```bash
pip install -r requirements.txt
```

### 3. Ejecuta la aplicación
```bash
streamlit run streamlit_web_audit.py
```

### 4. Accede a la aplicación
Abre tu navegador en: `http://localhost:8501`

## 🌐 Despliegue en Streamlit Cloud

### Opción 1: Deploy Directo
1. Sube el código a tu repositorio GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu repositorio
4. Selecciona `streamlit_web_audit.py` como archivo principal

### Opción 2: Deploy con configuración
Crea un archivo `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f8f9fa"
textColor = "#262730"

[server]
maxUploadSize = 200
enableCORS = false
```

## 📋 Uso

### Modo Rápido
- Análisis esencial en segundos
- Conectividad, DNS básico, SSL, rendimiento
- Ideal para verificaciones rápidas

### Modo Completo
- Análisis exhaustivo y detallado
- Todas las características habilitadas
- Reportes profesionales completos

### Comandos Especializados
- **DNS Check**: Verificación específica de propagación
- **SSL Monitor**: Monitoreo de certificados
- **Performance Test**: Análisis de rendimiento profundo

## 🎯 Casos de Uso

### Para Desarrolladores Web
- Verificación post-deployment
- Optimización de rendimiento
- Debugging de DNS
- Monitoreo de SSL

### Para Administradores de Sistemas
- Diagnóstico de problemas
- Auditorías de seguridad
- Monitoreo de infraestructura
- Análisis de propagación DNS

### Para Soporte Técnico
- Troubleshooting de conectividad
- Verificación de configuraciones
- Análisis de rendimiento
- Reportes para clientes

### Para SEO y Marketing
- Análisis de velocidad
- Verificación de redirects
- Comprobación de certificados
- Auditorías técnicas

## 📊 Características de la Interfaz

### Dashboard Principal
- **Métricas en Tiempo Real**: Estado del dominio, conectividad, SSL, rendimiento
- **Visualizaciones Interactivas**: Gráficos con Plotly
- **Navegación por Pestañas**: Organización clara de resultados
- **Responsive Design**: Funciona en desktop y móvil

### Configuración Avanzada
- **Opciones Granulares**: Habilitar/deshabilitar análisis específicos
- **Modos de Operación**: Rápido vs Completo
- **Exportación de Datos**: JSON para integración
- **Historial de Análisis**: Comparación temporal

## 🔧 Personalización

### Servidores DNS Personalizados
Modifica la lista `global_dns_servers` en el código:
```python
self.global_dns_servers = {
    'Tu Servidor Custom 🌟': '1.2.3.4',
    # ... otros servidores
}
```

### Nuevas Métricas
Agrega análisis personalizados extendiendo la clase `WebAuditor`:
```python
def custom_analysis(self, domain):
    # Tu lógica personalizada
    return results
```

## 📈 Métricas y Benchmarks

### Tiempos de Respuesta
- **Excelente**: < 1.0s
- **Bueno**: 1.0s - 3.0s  
- **Mejorable**: > 3.0s

### Puntuación de Seguridad
- **A+**: 90-100% headers presentes
- **A**: 80-89% headers presentes
- **B**: 60-79% headers presentes
- **C**: < 60% headers presentes

### Propagación DNS
- **Consistente**: Mismo IP en todos los servidores
- **Inconsistente**: Múltiples IPs (puede ser normal para CDN)
- **Fallida**: No resuelve en algunos servidores

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Areas de mejora:

- **Nuevos Análisis**: Más tipos de verificaciones
- **Mejor UI/UX**: Mejoras en la interfaz
- **Optimización**: Rendimiento y velocidad
- **Documentación**: Más ejemplos y casos de uso

### Cómo contribuir
1. Fork el repositorio
2. Crea una rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit tus cambios: `git commit -m 'Agrega nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

### Problemas Comunes

**Error de DNS resolver**:
```bash
pip install dnspython==2.4.0
```

**Error de SSL**:
```bash
pip install pyopenssl>=23.0.0
```

**Error de importación Streamlit**:
```bash
pip install streamlit>=1.28.0
```

### Contacto
- **GitHub Issues**: Para reportar bugs
- **Discussions**: Para preguntas y sugerencias
- **Email**: Para soporte directo

## 🌟 Características Próximas

- [ ] **API REST**: Endpoints para integración
- [ ] **Alertas por Email**: Notificaciones automáticas
- [ ] **Reportes PDF**: Exportación profesional
- [ ] **Análisis Histórico**: Trending y comparaciones
- [ ] **Multi-idioma**: Soporte i18n
- [ ] **Análisis de Competencia**: Comparación entre sitios
- [ ] **Integration CI/CD**: Plugins para pipelines
- [ ] **Mobile App**: Versión nativa móvil

---

**Desarrollado con ❤️ por netss**

*Enhanced Web Audit Tool - Making web analysis simple and powerful*
