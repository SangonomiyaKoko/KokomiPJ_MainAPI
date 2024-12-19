@echo off

go build -o update.exe -ldflags="-s -w" update.go

echo Build completed: update.exe

pause