@echo off
rem Launcher to run the NotesOrg API from any location
set "BASE=%~dp0"
set "SRC=%BASE%src"
set "PYTHONPATH=%SRC%"
python -m notesorg.api
