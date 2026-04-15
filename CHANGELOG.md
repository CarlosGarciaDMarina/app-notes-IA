# Changelog

## Unreleased
- Refactor en capas (Opción A): Presentación (API), Lógica de negocio y Repositorio con SQLite. Endpoints conservados.
- Añadido soporte de DI en la API para usar el NoteService sin cambios en los endpoints.
- Pruebas: tests para repositorio/servicio, API con DI y UI (Playwright) con fallback si no está disponible.
- Mejora de infraestructura: launcher para facilitar el arranque desde cualquier carpeta.
- Ajustes de estabilidad: manejo de conexiones SQLite por operación para evitar threading issues.

## v0.2.0 (en desarrollo)
- Preparación para release candidate: documentación de arquitectura, tests ampliados y plan de release.
