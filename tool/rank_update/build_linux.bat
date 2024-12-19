@echo off

set GOOS=linux
set GOARCH=amd64

go build -o update_linux -ldflags="-s -w" update.go

echo Build completed: update_linux