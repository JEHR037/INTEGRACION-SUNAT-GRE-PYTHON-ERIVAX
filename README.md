#####################
# Sistema de Integración con SUNAT
#####################

Este proyecto es un sistema de integración con la API de SUNAT para la generación y envío de archivos XML relacionados con guías de remisión electrónicas. El sistema permite la autenticación de usuarios, la generación de archivos XML conforme a los estándares de SUNAT, el envío de estos archivos y la gestión de respuestas, incluyendo la recepción y manejo de archivos CDR.

#####################
# Características
#####################

- Generación de archivos XML de acuerdo a los estándares de SUNAT.
- Envío de archivos XML a SUNAT y manejo de respuestas (incluyendo CDR).
- Autenticación y manejo de sesiones de usuario.
- Interfaz de usuario basada en tecnologías web para facilitar la generación y envío de archivos.
- Actualización automática de tokens de autenticación para mantener la sesión activa con SUNAT.
- Registros de actividad y bitácora de envíos para seguimiento de operaciones.

#####################
# Tecnologías Utilizadas
#####################

- Flask (Framework de Python para desarrollo web).
- Python para lógica de backend y scripts de automatización.
- HTML/CSS/JavaScript para el frontend.
- Requests para solicitudes HTTP a la API de SUNAT.
- LXML y ElementTree para la manipulación de archivos XML.
- Base64 y Hashlib para codificación y seguridad.
- JSON para el manejo de datos y configuraciones.
- Waitress y pyInstaller para el despliegue y distribución.

#####################
# Instalación y Configuración
#####################

Instrucciones para la instalación:
1. Clona el repositorio del proyecto.
2. Instala las dependencias con `pip install -r requirements.txt`.
3. Configura las variables de entorno necesarias (por ejemplo, credenciales de acceso a la API de SUNAT).
4. Ejecuta `python app.py` para iniciar el servidor Flask.
5. Ejecuta `python pyinstaller` para buildear.

#####################
# Uso
#####################

Para utilizar el sistema:
1. Inicia sesión con tus credenciales de usuario.
2. Navega a la sección de generación de XML y completa los campos requeridos para crear un archivo XML.
3. Envía el archivo XML a SUNAT a través de la interfaz del sistema.
4. Verifica el estado de tu envío y revisa el archivo CDR recibido en respuesta en los zip.

#####################
# Estructura de Archivos
#####################

- `app.py`: Punto de entrada del servidor Flask y rutas del sistema.
- `acceso.py`: Script para la gestión y actualización de tokens de autenticación.
- `templates/`: Directorio que contiene archivos HTML para la interfaz de usuario.
- `static/`: Archivos estáticos como CSS, JavaScript e imágenes.

#####################
# Contribuir
#####################

Si estás interesado en contribuir al proyecto, por favor envía un pull request o abre un issue en el repositorio para discutir los cambios o mejoras que propones.

#####################
# Licencia
#####################

Este proyecto está licenciado bajo la Licencia MIT.

#####################
# Contacto/Autor
#####################

- Autor: Erivax 
- Contacto: [LinkedIn de Erivax](https://es.linkedin.com/in/javier-hernandezjh)
