#!/bin/bash
powershell.exe -NoProfile -Command "Stop-Process -Name X2 -Force -ErrorAction SilentlyContinue" 
sleep 8
powershell.exe -NoProfile -Command "Start-Process 'C:\Program Files\Altium\AD26\X2.EXE'"
echo started
