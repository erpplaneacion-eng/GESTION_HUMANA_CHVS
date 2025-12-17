import io
from datetime import datetime

def generar_certificado_historico_pdf(contrato_historico):
    """
    Genera un certificado PDF para un contrato histórico usando la plantilla oficial
    """
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib.utils import simpleSplit
    from PyPDF2 import PdfReader, PdfWriter
    import os
    from django.conf import settings

    # Ruta a la plantilla
    BASE_DIR = settings.BASE_DIR.parent
    plantilla_path = os.path.join(BASE_DIR, 'archivos word', 'plantilla_certificacion.pdf')

    # Crear buffer para el contenido
    contenido_buffer = io.BytesIO()
    c = canvas.Canvas(contenido_buffer, pagesize=letter)
    width, height = letter

    # Márgenes y posiciones
    y_position = height - 2.3*inch
    margin_left = 1*inch
    margin_right = width - 1*inch
    text_width = margin_right - margin_left

    def draw_centered_text(text, y, font="Helvetica-Bold", size=11):
        c.setFont(font, size)
        text_w = c.stringWidth(text, font, size)
        c.drawString((width - text_w) / 2, y, text)

    def draw_paragraph(text, y_start, line_height=14):
        """Dibuja un párrafo con word wrap automático"""
        c.setFont("Helvetica", 10)
        lines = simpleSplit(text, "Helvetica", 10, text_width)
        y = y_start
        for line in lines:
            c.drawString(margin_left, y, line)
            y -= line_height
        return y

    # ENCABEZADO - Título dinámico desde contratante_nit
    # El contratante_nit puede ser largo, así que lo mostramos en una línea
    draw_centered_text(contrato_historico.contratante_nit, y_position, "Helvetica-Bold", 11)
    y_position -= 35

    # CERTIFICA QUE:
    draw_centered_text("CERTIFICA QUE:", y_position, "Helvetica-Bold", 11)
    y_position -= 35

    # Formatear cédula
    cedula_formateada = f"{contrato_historico.cedula:,}".replace(",", ".")

    # PÁRRAFO PRINCIPAL - construir todo el texto junto
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin_left, y_position, contrato_historico.nombre_contratista.upper())
    y_position -= 14

    # Construir el párrafo completo (sin incluir contratante_nit porque ya está en el título)
    texto_completo = (
        f"quien se identifica con la cédula de ciudadanía No. {cedula_formateada} de CALI "
        f"prestó sus servicios contractuales como PROFESIONAL para el área de {contrato_historico.area.upper()}, "
        f"para el desarrollo del proyecto denominado \"{contrato_historico.objeto_contrato}\"."
    )

    # Dibujar párrafo con wrap
    c.setFont("Helvetica", 10)
    lines = simpleSplit(texto_completo, "Helvetica", 10, text_width)
    for line in lines:
        c.drawString(margin_left, y_position, line)
        y_position -= 14

    y_position -= 10

    # ACTIVIDADES (si existen)
    if contrato_historico.actividades_especificas:
        y_position -= 5
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margin_left, y_position, "ACTIVIDADES:")
        y_position -= 16

        c.setFont("Helvetica", 10)
        actividades_lista = contrato_historico.actividades_especificas.strip().split('\n')

        for idx, actividad in enumerate(actividades_lista, start=1):
            if actividad.strip():
                # Agregar número y punto
                texto_actividad = f"{idx}. {actividad.strip()}"

                # Word wrap para actividades largas
                lineas_actividad = simpleSplit(texto_actividad, "Helvetica", 10, text_width - 0.2*inch)

                for i, linea in enumerate(lineas_actividad):
                    # Primera línea con indentación pequeña, resto con más indentación
                    indent = margin_left if i == 0 else margin_left + 0.2*inch
                    c.drawString(indent, y_position, linea)
                    y_position -= 13

                y_position -= 2  # Espacio entre actividades

        y_position -= 5

    # FECHAS DEL CONTRATO
    fecha_inicio_formateada = contrato_historico.fecha_firma.strftime('%d/%m/%Y')
    fecha_fin_formateada = contrato_historico.fecha_final.strftime('%d/%m/%Y')

    y_position -= 10
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin_left, y_position, "FECHA DE SUSCRIPCIÓN DEL CONTRATO: ")
    c.setFont("Helvetica", 10)
    c.drawString(margin_left + 260, y_position, f"{fecha_inicio_formateada},")

    y_position -= 14
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin_left, y_position, "FECHA DE TERMINACIÓN DEL CONTRATO: ")
    c.setFont("Helvetica", 10)
    c.drawString(margin_left + 260, y_position, f"{fecha_fin_formateada}.")

    # Fecha de expedición del certificado
    fecha_actual = datetime.now()
    dia = fecha_actual.day
    mes_nombres = {
        1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril', 5: 'mayo', 6: 'junio',
        7: 'julio', 8: 'agosto', 9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
    }
    mes = mes_nombres[fecha_actual.month]
    anio = fecha_actual.year

    y_position -= 25
    c.setFont("Helvetica", 10)
    texto_constancia = f"Para constancia de lo anterior se firma en Santiago de Cali, a los {dia} días del mes de {mes} de {anio}."

    # Word wrap para la constancia
    lineas_constancia = simpleSplit(texto_constancia, "Helvetica", 10, text_width)
    for linea in lineas_constancia:
        c.drawString(margin_left, y_position, linea)
        y_position -= 14

    # Firma (posición fija en parte baja)
    y_firma = 2.5*inch
    draw_centered_text("__________________________________________", y_firma)
    y_firma -= 16
    draw_centered_text("PBRO. CESAR AUGUSTO FERNANDEZ TAMAYO", y_firma, "Helvetica-Bold", 10)
    y_firma -= 14
    draw_centered_text("Gerente General del proyecto", y_firma, "Helvetica", 10)

    # Pie de página
    y_firma -= 30
    c.setFont("Helvetica", 8)
    draw_centered_text("Proyectó y elaboró: Mary Silenia Calvache Gómez – Contratista", y_firma, "Helvetica", 8)
    y_firma -= 11
    draw_centered_text("Sebastián Arias Hernández – Líder Jurídico", y_firma, "Helvetica", 8)

    # Finalizar canvas
    c.save()

    # Fusionar con la plantilla
    contenido_buffer.seek(0)
    plantilla_reader = PdfReader(plantilla_path)
    contenido_reader = PdfReader(contenido_buffer)

    writer = PdfWriter()
    plantilla_page = plantilla_reader.pages[0]
    contenido_page = contenido_reader.pages[0]
    plantilla_page.merge_page(contenido_page)
    writer.add_page(plantilla_page)

    output_buffer = io.BytesIO()
    writer.write(output_buffer)
    output_buffer.seek(0)

    return output_buffer


def generar_anexo11_pdf(applicant):
    """
    Genera un PDF en formato ANEXO 11 con la información del candidato
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

    # Función auxiliar para convertir números a texto en español
    def numero_a_texto_es(n):
        """Convierte números del 1 al 31 a texto en español"""
        numeros = {
            1: 'uno', 2: 'dos', 3: 'tres', 4: 'cuatro', 5: 'cinco',
            6: 'seis', 7: 'siete', 8: 'ocho', 9: 'nueve', 10: 'diez',
            11: 'once', 12: 'doce', 13: 'trece', 14: 'catorce', 15: 'quince',
            16: 'dieciséis', 17: 'diecisiete', 18: 'dieciocho', 19: 'diecinueve', 20: 'veinte',
            21: 'veintiuno', 22: 'veintidós', 23: 'veintitrés', 24: 'veinticuatro', 25: 'veinticinco',
            26: 'veintiséis', 27: 'veintisiete', 28: 'veintiocho', 29: 'veintinueve', 30: 'treinta',
            31: 'treinta y uno'
        }
        return numeros.get(n, str(n))

    # Diccionario de meses en español
    meses_es = {
        1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril', 5: 'mayo', 6: 'junio',
        7: 'julio', 8: 'agosto', 9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
    }

    # Crear buffer en memoria para el PDF
    pdf_buffer = io.BytesIO()

    # Crear documento
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )

    # Estilos
    styles = getSampleStyleSheet()

    # Estilo para el título
    titulo_style = ParagraphStyle(
        'TituloAnexo',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    # Estilo para subtítulos
    subtitulo_style = ParagraphStyle(
        'Subtitulo',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    # Estilo para texto normal
    normal_style = ParagraphStyle(
        'NormalText',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=12
    )

    # Estilo para texto pequeño
    small_style = ParagraphStyle(
        'SmallText',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_LEFT
    )

    # Estilo para texto en celdas de tabla (con word wrap)
    cell_style = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_LEFT,
        leading=10,  # Espaciado entre líneas
        wordWrap='CJK'  # Permite ajuste de texto
    )

    # Estilo para texto centrado en celdas de tabla
    cell_center_style = ParagraphStyle(
        'CellCenterText',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        leading=10,
        wordWrap='CJK'
    )

    # Contenido del documento
    elementos = []

    # Título principal
    elementos.append(Paragraph("ANEXO 11", titulo_style))
    elementos.append(Paragraph("CARTA DE COMPROMISO PERSONAL", subtitulo_style))
    elementos.append(Spacer(1, 0.3*inch))

    # ==================== PÁGINA 1 ====================

    # Fecha y destinatario
    fecha_obj = datetime.now()
    dia = fecha_obj.day
    mes = fecha_obj.month
    anio = fecha_obj.year

    # Nombre del día en texto y mes en español
    dia_texto = numero_a_texto_es(dia)
    mes_nombre = meses_es.get(mes, 'error')

    # Fecha en formato "04 de noviembre de 2025"
    fecha_actual = f"{dia:02d} de {mes_nombre} de {anio}"

    elementos.append(Paragraph(f"Cali, {fecha_actual}", normal_style))
    elementos.append(Spacer(1, 0.2*inch))

    elementos.append(Paragraph("Señores:", normal_style))
    elementos.append(Paragraph("<b>SECRETARÍA DE BIENESTAR SOCIAL</b>", normal_style))
    elementos.append(Paragraph("<b>DISTRITO ESPECIAL DE SANTIAGO DE CALI</b>", normal_style))
    elementos.append(Paragraph("Ciudad", normal_style))
    elementos.append(Spacer(1, 0.2*inch))

    # Referencia - usar el campo contrato
    numero_proceso = applicant.contrato or "4146.010.32.1.2366.2025"
    elementos.append(Paragraph(f"<b>REFERENCIA:</b> Proceso No. {numero_proceso}", normal_style))
    elementos.append(Spacer(1, 0.2*inch))

    # Cuerpo de la carta - usar el campo perfil
    organizacion = "UNIÓN TEMPORAL COMISIÓN ARQUIDIOCESANA VIDA JUSTICIA Y PAZ 25-2"
    cargo_propuesto = applicant.perfil or "el cargo correspondiente"

    texto_compromiso = f"""
    Yo, <b>{applicant.nombre_completo}</b>, identificado con c.c. <b>{applicant.cedula}</b>,
    acepto ser presentado por la empresa <b>{organizacion}</b>
    como <b>{cargo_propuesto}</b> en su propuesta dentro de los equipo de profesionales, y participar dentro
    de la ejecución del proceso de selección No. <b>{numero_proceso}</b>, que tiene como objeto:
    AUNAR ESFUERZOS TÉCNICOS, HUMANOS, ADMINISTRATIVOS Y FINANCIEROS PARA EL MEJORAMIENTO DE LAS
    CONDICIONES DE SEGURIDAD ALIMENTARIA DE LA POBLACIÓN VULNERABLE, GARANTIZANDO SU ACCESO A LOS
    ALIMENTOS Y BRINDANDO INTERVENCIÓN PSICOSOCIAL, EN EL DISTRITO DE SANTIAGO DE CALI, DE CONFORMIDAD
    CON EL PROYECTO DE INVERSIÓN "FORTALECIMIENTO DEL PROGRAMA DE SEGURIDAD ALIMENTARIA Y NUTRICIONAL
    EN SANTIAGO DE CALI" - BP-26005417 de acuerdo con lo establecido en la invitación, el estudio
    previo y documento denominado ANEXO TÉCNICO.
    """

    elementos.append(Paragraph(texto_compromiso, normal_style))
    elementos.append(Spacer(1, 0.15*inch))

    elementos.append(Paragraph(
        "Por lo que me comprometo a formar parte del equipo de trabajo durante el plazo que dure el convenio de asociación.",
        normal_style
    ))
    elementos.append(Spacer(1, 0.2*inch))

    # Texto de firma con fecha dinámica en español
    texto_firma = f"Para constancia se firma a los {dia_texto} ({dia}) días del mes de {mes_nombre} del {anio}."
    elementos.append(Paragraph(texto_firma, normal_style))
    elementos.append(Spacer(1, 0.5*inch))

    # Tabla de firmas
    firmas_data = [
        ['_________________________', '_________________________'],
        [f'{applicant.nombre_completo}', 'Diego Fernando Guzmán Ruiz'],
        ['Firma del Profesional', 'Firma del Representante Legal']
    ]

    tabla_firmas = Table(firmas_data, colWidths=[3.5*inch, 3.5*inch])
    tabla_firmas.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, 2), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, 0), 0),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 15),
    ]))

    elementos.append(tabla_firmas)

    # ==================== SALTO DE PÁGINA ====================
    elementos.append(PageBreak())

    # ==================== PÁGINA 2 ====================

    # 1. Tabla: RELACIÓN DE EXPERIENCIA PROFESIONALES PARA EL PERSONAL BASE
    # Construir dirección completa
    direccion_completa = f"{applicant.tipo_via} {applicant.numero_via} #{applicant.numero_casa}"
    if applicant.complemento_direccion:
        direccion_completa += f" {applicant.complemento_direccion}"
    if applicant.barrio:
        direccion_completa += f", Barrio {applicant.barrio}"

    # Datos de la tabla con título en la primera fila con fondo gris
    # Usar Paragraph para textos largos que puedan desbordarse
    tabla_experiencia_data = [
        ['RELACIÓN DE EXPERIENCIA PROFESIONALES PARA EL PERSONAL BASE', ''],  # Título con span
        ['CARGO PROPUESTO:', Paragraph(str(cargo_propuesto or ''), cell_style)],
        ['NOMBRES Y APELLIDOS:', Paragraph(str(applicant.nombre_completo or ''), cell_style)],
        ['TIPO Y Nº DOCUMENTO DE IDENTIDAD:', Paragraph(f'CC {applicant.cedula}', cell_style)],
        ['DIRECCIÓN:', Paragraph(str(direccion_completa or ''), cell_style)],
        ['TELÉFONO:', Paragraph(str(applicant.telefono or ''), cell_style)],
        ['CORREO ELECTRÓNICO:', Paragraph(str(applicant.correo or ''), cell_style)],
    ]

    tabla_experiencia = Table(tabla_experiencia_data, colWidths=[2.5*inch, 4.5*inch])
    tabla_experiencia.setStyle(TableStyle([
        # Título - Primera fila con fondo gris
        ('SPAN', (0, 0), (1, 0)),  # Combinar columnas para el título
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#D3D3D3')),  # Gris
        ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 10),
        ('TOPPADDING', (0, 0), (1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (1, 0), 8),

        # Resto de las filas
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#E8E8E8')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Cambiar a TOP para textos largos
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))

    elementos.append(tabla_experiencia)
    elementos.append(Spacer(1, 0.3*inch))

    # 2. Tabla: ESTUDIOS REALIZADOS - Formato de 4 columnas
    # Obtener todos los estudios
    formaciones_academicas = list(applicant.formacion_academica.all())
    posgrados = list(applicant.posgrados.all())
    especializaciones = list(applicant.especializaciones.all())
    educacion_basica = list(applicant.educacion_basica.all())
    educacion_superior = list(applicant.educacion_superior.all())

    # Calcular experiencia en años
    try:
        calculo_exp = applicant.calculo_experiencia
        experiencia_anos = f"{calculo_exp.total_experiencia_anos} años"
    except:
        experiencia_anos = "No calculada"

    # Construir contenido consolidado para cada columna
    # UNIVERSITARIOS - Agrupar todos los estudios universitarios
    contenido_titulos_univ = ''
    contenido_instituciones_univ = ''
    contenido_fechas_univ = ''
    tarjeta_texto = ''
    
    for formacion in formaciones_academicas:
        titulo = formacion.profesion or ''
        institucion = formacion.universidad or ''
        fecha = formacion.fecha_grado.strftime('%d/%m/%Y') if formacion.fecha_grado else ''
        
        if titulo:
            contenido_titulos_univ += f'{titulo}<br/>'
        if institucion:
            contenido_instituciones_univ += f'{institucion}<br/>'
        if fecha:
            contenido_fechas_univ += f'{fecha}<br/>'
        
        # Tarjeta profesional (solo la primera o consolidar todas)
        if not tarjeta_texto:
            if formacion.tarjeta_profesional == 'Tarjeta Profesional':
                tarjeta_texto = f"Tarjeta Profesional: {formacion.numero_tarjeta_resolucion or 'N/A'}"
            elif formacion.tarjeta_profesional == 'Resolución':
                tarjeta_texto = f"Resolución: {formacion.numero_tarjeta_resolucion or 'N/A'}"
    
    # ESPECIALIZACIÓN - Agrupar todas las especializaciones
    contenido_titulos_esp = ''
    contenido_instituciones_esp = ''
    contenido_fechas_esp = ''
    
    for especializacion in especializaciones:
        titulo = especializacion.nombre_especializacion or ''
        institucion = especializacion.universidad or ''
        fecha = especializacion.fecha_terminacion.strftime('%d/%m/%Y') if especializacion.fecha_terminacion else ''
        
        if titulo:
            contenido_titulos_esp += f'{titulo}<br/>'
        if institucion:
            contenido_instituciones_esp += f'{institucion}<br/>'
        if fecha:
            contenido_fechas_esp += f'{fecha}<br/>'
    
    # OTROS (POSGRADOS, BACHILLER, TÉCNICO/TECNÓLOGO) - Agrupar todos en OTROS
    contenido_titulos_otros = ''
    contenido_instituciones_otros = ''
    contenido_fechas_otros = ''
    
    # 1. Posgrados
    for posgrado in posgrados:
        titulo = posgrado.nombre_posgrado or ''
        institucion = posgrado.universidad or ''
        fecha = posgrado.fecha_terminacion.strftime('%d/%m/%Y') if posgrado.fecha_terminacion else ''
        
        if titulo:
            contenido_titulos_otros += f'<b>(Posgrado)</b> {titulo}<br/>'
        if institucion:
            contenido_instituciones_otros += f'{institucion}<br/>'
        if fecha:
            contenido_fechas_otros += f'{fecha}<br/>'

    # 2. Educación Superior (Técnico/Tecnólogo)
    for superior in educacion_superior:
        titulo = superior.titulo or ''
        institucion = superior.institucion or ''
        fecha = superior.fecha_grado.strftime('%d/%m/%Y') if superior.fecha_grado else ''
        nivel = superior.nivel or 'Técnico/Tecnólogo'
        
        if titulo:
            contenido_titulos_otros += f'<b>({nivel})</b> {titulo}<br/>'
        if institucion:
            contenido_instituciones_otros += f'{institucion}<br/>'
        if fecha:
            contenido_fechas_otros += f'{fecha}<br/>'

    # 3. Educación Básica (Bachiller)
    for basica in educacion_basica:
        titulo = basica.titulo or ''
        institucion = basica.institucion or ''
        anio = str(basica.anio_grado) if basica.anio_grado else ''
        
        if titulo:
            contenido_titulos_otros += f'<b>(Bachiller)</b> {titulo}<br/>'
        if institucion:
            contenido_instituciones_otros += f'{institucion}<br/>'
        if anio:
            contenido_fechas_otros += f'{anio}<br/>'
    
    # Si no hay tarjeta profesional, poner "No Aplica"
    if not tarjeta_texto:
        tarjeta_texto = "No Aplica"

    # Construir la tabla con datos consolidados
    estudios_nueva_data = [
        # Fila de título con fondo gris
        ['ESTUDIOS REALIZADOS', '', '', ''],
        # Fila de encabezados de columnas
        ['DESCRIPCIÓN', 'UNIVERSITARIOS', 'ESPECIALIZACIÓN', 'OTROS'],
        # Fila de TÍTULO OBTENIDO con todos los títulos consolidados
        ['TÍTULO OBTENIDO',
         Paragraph(contenido_titulos_univ, cell_center_style) if contenido_titulos_univ else '',
         Paragraph(contenido_titulos_esp, cell_center_style) if contenido_titulos_esp else '',
         Paragraph(contenido_titulos_otros, cell_center_style) if contenido_titulos_otros else ''],
        # Fila de INSTITUCIÓN con todas las instituciones consolidadas
        ['INSTITUCIÓN',
         Paragraph(contenido_instituciones_univ, cell_center_style) if contenido_instituciones_univ else '',
         Paragraph(contenido_instituciones_esp, cell_center_style) if contenido_instituciones_esp else '',
         Paragraph(contenido_instituciones_otros, cell_center_style) if contenido_instituciones_otros else ''],
        # Fila de FECHA DE GRADO con todas las fechas consolidadas
        ['FECHA DE GRADO',
         Paragraph(contenido_fechas_univ, cell_center_style) if contenido_fechas_univ else '',
         Paragraph(contenido_fechas_esp, cell_center_style) if contenido_fechas_esp else '',
         Paragraph(contenido_fechas_otros, cell_center_style) if contenido_fechas_otros else ''],
    ]

    # Agregar fila de tarjeta profesional (solo para universitarios)
    if formaciones_academicas:
        estudios_nueva_data.append(['TARJETA PROFESIONAL', Paragraph(str(tarjeta_texto or ''), cell_center_style), '', ''])
    
    # Agregar fila de experiencia
    estudios_nueva_data.append(['2. EXPERIENCIA:', Paragraph(str(experiencia_anos or ''), cell_center_style), '', ''])

    tabla_estudios_nueva = Table(estudios_nueva_data, colWidths=[1.75*inch, 1.75*inch, 1.75*inch, 1.75*inch])
    
    # Calcular número de filas para los estilos
    num_filas = len(estudios_nueva_data)
    
    # Construir lista de estilos base
    estilos_base = [
        # Título - Primera fila con fondo gris y span
        ('SPAN', (0, 0), (3, 0)),
        ('BACKGROUND', (0, 0), (3, 0), colors.HexColor('#D3D3D3')),
        ('TEXTCOLOR', (0, 0), (3, 0), colors.black),
        ('ALIGN', (0, 0), (3, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (3, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (3, 0), 10),

        # Encabezados de columnas - Segunda fila
        ('BACKGROUND', (0, 1), (3, 1), colors.HexColor('#366092')),
        ('TEXTCOLOR', (0, 1), (3, 1), colors.whitesmoke),
        ('ALIGN', (0, 1), (3, 1), 'CENTER'),
        ('FONTNAME', (0, 1), (3, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (3, 1), 9),

        # Primera columna (DESCRIPCIÓN) - Negrita para todas las filas de datos
        ('BACKGROUND', (0, 2), (0, num_filas - 1), colors.HexColor('#E8E8E8')),
        ('FONTNAME', (0, 2), (0, num_filas - 1), 'Helvetica-Bold'),
        ('ALIGN', (0, 2), (0, num_filas - 1), 'LEFT'),
        ('FONTSIZE', (0, 2), (0, num_filas - 1), 8),

        # Resto de datos
        ('FONTNAME', (1, 2), (3, num_filas - 1), 'Helvetica'),
        ('FONTSIZE', (1, 2), (3, num_filas - 1), 8),
        ('ALIGN', (1, 2), (3, num_filas - 1), 'CENTER'),

        # Bordes y espaciado
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # TOP para textos largos
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]
    
    # Agregar estilos para tarjeta profesional y experiencia (span solo en la primera columna)
    # Tarjeta profesional (si existe, es la penúltima fila)
    if formaciones_academicas:
        fila_tarjeta = num_filas - 2  # Penúltima fila
        estilos_base.append(('SPAN', (1, fila_tarjeta), (3, fila_tarjeta)))
    
    # Experiencia (última fila)
    fila_experiencia = num_filas - 1
    estilos_base.append(('SPAN', (1, fila_experiencia), (3, fila_experiencia)))
    
    tabla_estudios_nueva.setStyle(TableStyle(estilos_base))

    elementos.append(tabla_estudios_nueva)

    # Construir PDF
    doc.build(elementos)

    # Retornar buffer
    pdf_buffer.seek(0)
    return pdf_buffer
