REM delete database /q: quiet mode, do not prompt for confirmation
del /q app.db
REM remove migrations folder
rd /q /s migrations

flask2 db init && flask2 db migrate && flask2 db upgrade