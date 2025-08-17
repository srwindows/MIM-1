#!/bin/bash
echo "Creando carpetas..."
mkdir -p recursos/imagenes
mkdir -p recursos/soundfonts
mkdir -p recursos/escenas
mkdir -p recursos/vsts

echo "Instalando dependencias Python..."
pip install PyQt5 sf2utils

echo "Coloca tus archivos .sf2 en recursos/soundfonts y tus imágenes en recursos/imagenes"
echo "¡Listo!"
