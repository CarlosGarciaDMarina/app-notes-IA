# NotesOrg

Notas y organizador ligero en Python.

Características principales
- Crear notas con título, contenido, cuaderno (notebook) y etiquetas (tags)
- Listar notas filtrando por cuaderno o etiqueta
- Buscar texto en título o contenido
- Listar cuadernos existentes
- Ver y editar notas individuales
- Persistencia en un archivo JSON local (~/.notesorg/notes.json)

Arquitectura básica
- Core: src/notesorg/core.py; maneja almacenamiento, modelos y operaciones CRUD
- CLI: src/notesorg/cli.py; interfaz de línea de comandos basada en argparse
- Paquete Python: src/notesorg/

Ejecución rápida (Ejemplos)
- Crear una nota:
  python -m notesorg.cli add --title "Compras" --content "Comprar leche y pan" --notebook Personal --tags compras,hogar
- Listar todas las notas:
  python -m notesorg.cli list
- Buscar notas con la palabra 'pan':
  python -m notesorg.cli search --query pan
- Ver cuadernos disponibles:
  python -m notesorg.cli notebooks

Notas
- Este proyecto es un prototipo. Para producción, considerar mejoras como CLI más rica, validación de entradas, migraciones de storage, y tests.
- Ejecución rápida (Ejemplos)
  python -m notesorg.cli add --title "Compras" --content "Comprar leche y pan" --notebook Personal --tags compras,hogar
- Listar todas las notas:
  python -m notesorg.cli list
- Buscar notas con la palabra 'pan':
  python -m notesorg.cli search --query pan
- Ver cuadernos disponibles:
  python -m notesorg.cli notebooks

