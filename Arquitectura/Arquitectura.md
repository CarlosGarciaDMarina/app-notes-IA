# Arquitectura del Back-End (Opción A: Capas Clásicas)

Este documento describe una propuesta de refactor hacia una arquitectura en capas (presentación, negocio y repositorio) con DTOs para un backend de notas, notas.autos.

Visión general
- Objetivo: facilitar el mantenimiento, las pruebas y el reemplazo de componentes sin afectar las demás capas.
- Capas básicas:
  - Presentación: interacción con el cliente (API REST) y, si aplica, interfaz frontend. Responsable de validación inicial y mapeo de entradas/salidas a DTOs. 
  - Capa de Interfaz (Lógica de Aplicación/Negocio): orquesta la lógica del negocio para CRUD de notas, notebooks y tags; aplica reglas de negocio y transformaciones entre DTOs y entidades.
  - Capa de Repositorio: abstrae el acceso a la persistencia (BD) y operaciones de CRUD, encapsulando consultas SQL o acceso a ORM.
  - DTOs: objetos de transferencia de datos que exponen solo la información necesaria entre capas, promoviendo desacoplamiento.

Estado actual y plan de refactor
- Estado actual: la implementación existente en el repositorio combina lógica de negocio y acceso a datos en un único conjunto de archivos (core.py, api.py). No hay una separación formal de capas. La UI/CLI siguen funcionando como capas de presentación, pero el núcleo está acoplado a la persistencia.
- Propuesta de migración progresiva (EJECUCIÓN en fases):
  1) DTOs: crear definiciones simples para Nota, Notebook y Etiqueta, diferenciando lo que se expone en la API de lo que se persiste.
  2) Repositorio: introducir interfaces y una implementación SQLite (si se mantiene, o adaptable) con métodos: get_note, add_note, update_note, delete_note, list_notes, search_notes, list_notebooks.
  3) Capa de negocio: implementar un servicio de notas que use el repositorio para realizar operaciones, aplicar reglas de negocio y orquestar validaciones. Aislar la lógica de negocio de la capa de persistencia.
  4) Presentación: adaptar la API (interfaces HTTP) para usar DTOs y el servicio de negocio, manteniendo las rutas existentes y agregando pruebas unitarias/fundamentales.
  5) Pruebas y despliegue: pruebas unitarias en cada capa, mocks para el repositorio, pruebas de integración para la API, y pipelines de CI/CD.

Decisiones de diseño
- Desacoplamiento: cada capa tendrá dependencias unidireccionales (presentación -> negocio -> repositorio).
- Interfaces claras: definimos interfaces para el repositorio y para el servicio de negocio para facilitar sustitución (p.ej. cambiar DB a PostgreSQL sin tocar la lógica de negocio).
- DTOs: minimizan el acoplamiento entre capas y evitan exponer estructuras internas.
- Mantenibilidad: las rutas de la API deben depender del servicio de negocio y no de la capa de repositorio.

Extensión futura
- Sustitución de almacenamiento: el repositorio podría cambiar a otro backend (p.ej. PostgreSQL) sin tocar el negocio o la presentación.
- Escalabilidad: podemos añadir patrones como Unit of Work, repositorios especializados, o incluso una arquitectura hexagonal si las necesidades crecen.

Pruebas y despliegue
- Pruebas unitarias por capa: tests de DTOs, tests de repositorio (con DB en memoria o SQLite), tests de negocio con mocks, tests de API.
- Pruebas de integración: pruebas end-to-end para la API y flujo de negocio completo.
- Despliegue: mantener una configuración clara de dependencias (poetry/venv), y pruebas en CI para validar cambios.

Notas finales
- Este documento propone una ruta de refactorización gradual para evitar grandes rupturas y facilitar pruebas y mantenimiento.
