#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para generar carnets estudiantiles
Lee datos de base.txt y genera un PDF con 8 carnets por hoja
"""

from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import os
import sys

# Configuración
CARNET_WIDTH_MM = 85.6
CARNET_HEIGHT_MM = 54.0
CARNETS_PER_PAGE = 8

# Convertir mm a puntos (1 mm = 2.83465 puntos)
CARNET_WIDTH_PT = CARNET_WIDTH_MM * mm
CARNET_HEIGHT_PT = CARNET_HEIGHT_MM * mm

# Convertir mm a píxeles para imagen (300 DPI)
DPI = 300
CARNET_WIDTH_PX = int(CARNET_WIDTH_MM / 25.4 * DPI)
CARNET_HEIGHT_PX = int(CARNET_HEIGHT_MM / 25.4 * DPI)


def leer_datos_estudiantes(archivo='base.txt'):
    """Lee el archivo de texto con los datos de los estudiantes"""
    estudiantes = []

    if not os.path.exists(archivo):
        print(f"Error: No se encuentra el archivo {archivo}")
        return estudiantes

    with open(archivo, 'r', encoding='utf-8') as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue

            # Formato: Apellidos y Nombres, Curso, Cedula, Nivel Educativo, ruta foto
            partes = [p.strip() for p in linea.split(',')]

            if len(partes) >= 5:
                estudiante = {
                    'nombres': partes[0],
                    'curso': partes[1],
                    'cedula': partes[2],
                    'nivel': partes[3],
                    'foto': partes[4]
                }
                estudiantes.append(estudiante)

    return estudiantes


def crear_carnet(estudiante, imagen_fondo='Captura.PNG', directorio_base='.'):
    """Crea la imagen de un carnet individual"""

    # Cargar imagen de fondo
    try:
        fondo = Image.open(imagen_fondo)
        # Redimensionar al tamaño del carnet
        fondo = fondo.resize((CARNET_WIDTH_PX, CARNET_HEIGHT_PX), Image.Resampling.LANCZOS)
    except Exception as e:
        print(f"Error al cargar imagen de fondo: {e}")
        # Crear imagen en blanco si no existe el fondo
        fondo = Image.new('RGB', (CARNET_WIDTH_PX, CARNET_HEIGHT_PX), 'white')

    # Crear copia para trabajar
    carnet = fondo.copy()
    draw = ImageDraw.Draw(carnet)

    # Intentar cargar fuentes
    try:
        font_titulo = ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf", 40)
        font_etiqueta = ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf", 28)
        font_dato = ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSans.ttf", 32)
    except:
        # Usar fuente por defecto si no se encuentran las fuentes
        font_titulo = ImageFont.load_default()
        font_etiqueta = ImageFont.load_default()
        font_dato = ImageFont.load_default()

    # Cargar foto del estudiante
    foto_path = os.path.join(directorio_base, estudiante['foto'].lstrip('/'))
    foto_agregada = False

    if os.path.exists(foto_path):
        try:
            foto = Image.open(foto_path)
            # Dimensiones para la foto (ajustar según diseño)
            foto_width = int(CARNET_WIDTH_PX * 0.35)  # 35% del ancho
            foto_height = int(CARNET_HEIGHT_PX * 0.55)  # 55% del alto

            # Redimensionar manteniendo aspecto
            foto.thumbnail((foto_width, foto_height), Image.Resampling.LANCZOS)

            # Posición: alineada a la izquierda, margen superior
            margen = int(CARNET_WIDTH_PX * 0.05)
            foto_x = margen
            foto_y = int(CARNET_HEIGHT_PX * 0.25)

            # Pegar foto
            if foto.mode == 'RGBA':
                carnet.paste(foto, (foto_x, foto_y), foto)
            else:
                carnet.paste(foto, (foto_x, foto_y))

            foto_agregada = True
        except Exception as e:
            print(f"Error al cargar foto {foto_path}: {e}")
    else:
        print(f"Advertencia: No se encuentra la foto {foto_path}")

    # Título: "Identificación estudiantil" (movido 10% a la derecha)
    titulo = "Identificación estudiantil"
    bbox = draw.textbbox((0, 0), titulo, font=font_titulo)
    titulo_width = bbox[2] - bbox[0]
    titulo_x = (CARNET_WIDTH_PX - titulo_width) // 2 + int(CARNET_WIDTH_PX * 0.10)
    titulo_y = int(CARNET_HEIGHT_PX * 0.20)
    draw.text((titulo_x, titulo_y), titulo, fill='black', font=font_titulo)

    # Datos en la parte inferior derecha
    datos_x = int(CARNET_WIDTH_PX * 0.42)  # Dejar espacio para la foto
    inicio_y = int(CARNET_HEIGHT_PX * 0.34)
    espacio_linea = int(CARNET_HEIGHT_PX * 0.09)

    # Apellidos y Nombres
    draw.text((datos_x, inicio_y), "Apellidos y Nombres:", fill='navy', font=font_etiqueta)
    draw.text((datos_x, inicio_y + 30), estudiante['nombres'], fill='black', font=font_dato)

    # Curso
    y_curso = inicio_y + espacio_linea + 30
    draw.text((datos_x, y_curso), "Curso:", fill='navy', font=font_etiqueta)
    draw.text((datos_x, y_curso + 30), estudiante['curso'], fill='black', font=font_dato)

    # Cédula
    y_ci = y_curso + espacio_linea + 30
    draw.text((datos_x, y_ci), "C.I.:", fill='navy', font=font_etiqueta)
    draw.text((datos_x, y_ci + 30), estudiante['cedula'], fill='black', font=font_dato)

    # Nivel Educativo
    y_nivel = y_ci + espacio_linea + 30
    draw.text((datos_x, y_nivel), "Nivel:", fill='navy', font=font_etiqueta)
    draw.text((datos_x, y_nivel + 30), estudiante['nivel'], fill='black', font=font_dato)

    return carnet


def generar_pdf(estudiantes, archivo_salida='carnets.pdf', imagen_fondo='Captura.PNG'):
    """Genera un PDF con 8 carnets por hoja A4"""

    # Crear canvas PDF
    c = canvas.Canvas(archivo_salida, pagesize=A4)
    ancho_pagina, alto_pagina = A4

    # Configuración de disposición (2 columnas x 4 filas = 8 carnets)
    columnas = 2
    filas = 4
    margen = 10 * mm
    espacio_horizontal = (ancho_pagina - 2 * margen - columnas * CARNET_WIDTH_PT) / (columnas - 1)
    espacio_vertical = (alto_pagina - 2 * margen - filas * CARNET_HEIGHT_PT) / (filas - 1)

    carnets_en_pagina = 0
    directorio_base = os.path.dirname(os.path.abspath(imagen_fondo))

    # Crear directorio temporal para carnets
    temp_dir = 'carnets_temp'
    os.makedirs(temp_dir, exist_ok=True)

    for idx, estudiante in enumerate(estudiantes):
        print(f"Generando carnet {idx + 1}/{len(estudiantes)}: {estudiante['nombres']}")

        # Crear imagen del carnet
        carnet_img = crear_carnet(estudiante, imagen_fondo, directorio_base)

        # Guardar temporalmente
        temp_path = os.path.join(temp_dir, f'carnet_{idx}.png')
        carnet_img.save(temp_path, 'PNG', dpi=(DPI, DPI))

        # Calcular posición en la hoja
        fila = carnets_en_pagina // columnas
        columna = carnets_en_pagina % columnas

        x = margen + columna * (CARNET_WIDTH_PT + espacio_horizontal)
        # Invertir Y porque PDF cuenta desde abajo
        y = alto_pagina - margen - (fila + 1) * CARNET_HEIGHT_PT - fila * espacio_vertical

        # Dibujar carnet en PDF
        c.drawImage(temp_path, x, y, width=CARNET_WIDTH_PT, height=CARNET_HEIGHT_PT)

        carnets_en_pagina += 1

        # Nueva página cada 8 carnets
        if carnets_en_pagina >= CARNETS_PER_PAGE:
            c.showPage()
            carnets_en_pagina = 0

    # Guardar PDF
    if carnets_en_pagina > 0:  # Si hay carnets en la última página
        c.showPage()

    c.save()

    # Limpiar archivos temporales
    for archivo in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, archivo))
    os.rmdir(temp_dir)

    print(f"\n✓ PDF generado exitosamente: {archivo_salida}")
    print(f"✓ Total de carnets: {len(estudiantes)}")


def main():
    """Función principal"""
    print("=" * 60)
    print("Generador de Carnets Estudiantiles")
    print("=" * 60)

    # Leer datos
    print("\nLeyendo datos de estudiantes...")
    estudiantes = leer_datos_estudiantes('base.txt')

    if not estudiantes:
        print("Error: No se encontraron estudiantes en base.txt")
        sys.exit(1)

    print(f"✓ Se encontraron {len(estudiantes)} estudiantes")

    # Verificar imagen de fondo
    if not os.path.exists('Captura.PNG'):
        print("Advertencia: No se encuentra Captura.PNG, se usará fondo blanco")

    # Generar PDF
    print("\nGenerando carnets...")
    generar_pdf(estudiantes, 'carnets.pdf', 'Captura.PNG')


if __name__ == '__main__':
    main()
