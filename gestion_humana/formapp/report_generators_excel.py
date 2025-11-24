def create_excel_for_person(applicant):
    """Crea un archivo Excel con toda la información de una persona"""
    wb = Workbook()

    # Estilos
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    title_font = Font(bold=True, size=14, color="2C3E50")
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # Hoja 1: Información Básica
    ws1 = wb.active
    ws1.title = "Información Básica"

    # Título
    ws1['A1'] = f"INFORMACIÓN PERSONAL - {applicant.nombre_completo}"
    ws1['A1'].font = title_font
    ws1.merge_cells('A1:B1')

    # Datos personales
    row = 3
    personal_data = [
        ("Cédula", applicant.cedula),
        ("Nombre Completo", applicant.nombre_completo),
        ("Género", applicant.genero),
        ("Dirección", f"{applicant.tipo_via} {applicant.numero_via} #{applicant.numero_casa}"),
        ("Complemento Dirección", applicant.complemento_direccion or "N/A"),
        ("Barrio", applicant.barrio or "N/A"),
        ("Teléfono", applicant.telefono),
        ("Correo", applicant.correo),
    ]

    for label, value in personal_data:
        ws1[f'A{row}'] = label
        ws1[f'A{row}'].font = Font(bold=True)
        ws1[f'A{row}'].fill = PatternFill(start_color="E8E8E8", end_color="E8E8E8", fill_type="solid")
        ws1[f'B{row}'] = value
        ws1[f'A{row}'].border = border
        ws1[f'B{row}'].border = border
        row += 1

    # Información profesional
    row += 2
    ws1[f'A{row}'] = "INFORMACIÓN PROFESIONAL"
    ws1[f'A{row}'].font = title_font
    ws1.merge_cells(f'A{row}:B{row}')
    row += 2

    professional_data = [
        ("Perfil", applicant.perfil or "N/A"),
        ("Área del Conocimiento", applicant.area_del_conocimiento or "N/A"),
        ("Profesión", applicant.profesion or "N/A"),
        ("Contrato", applicant.contrato or "N/A"),
        ("Observaciones", applicant.observacion or "N/A"),
    ]

    for label, value in professional_data:
        ws1[f'A{row}'] = label
        ws1[f'A{row}'].font = Font(bold=True)
        ws1[f'A{row}'].fill = PatternFill(start_color="E8E8E8", end_color="E8E8E8", fill_type="solid")
        ws1[f'B{row}'] = value
        ws1[f'A{row}'].border = border
        ws1[f'B{row}'].border = border
        row += 1

    ws1.column_dimensions['A'].width = 30
    ws1.column_dimensions['B'].width = 50

    # Hoja 2: Experiencia Laboral
    ws2 = wb.create_sheet("Experiencia Laboral")
    ws2['A1'] = f"EXPERIENCIA LABORAL - {applicant.nombre_completo}"
    ws2['A1'].font = title_font
    ws2.merge_cells('A1:H1')

    # Encabezados
    headers = ["Cargo", "Cargo Anexo 11", "Fecha Inicial", "Fecha Terminación",
               "Meses", "Días", "Objeto Contractual", "Funciones"]
    for col, header in enumerate(headers, start=1):
        cell = ws2.cell(row=3, column=col)
        cell.value = header
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = border

    # Datos
    row = 4
    for exp in applicant.experiencias_laborales.all():
        ws2.cell(row=row, column=1, value=exp.cargo).border = border
        ws2.cell(row=row, column=2, value=exp.cargo_anexo_11).border = border
        ws2.cell(row=row, column=3, value=exp.fecha_inicial.strftime('%Y-%m-%d')).border = border
        ws2.cell(row=row, column=4, value=exp.fecha_terminacion.strftime('%Y-%m-%d')).border = border
        ws2.cell(row=row, column=5, value=exp.meses_experiencia).border = border
        ws2.cell(row=row, column=6, value=exp.dias_experiencia).border = border
        ws2.cell(row=row, column=7, value=exp.objeto_contractual).border = border
        ws2.cell(row=row, column=8, value=exp.funciones).border = border
        row += 1

    for col in range(1, 9):
        ws2.column_dimensions[chr(64 + col)].width = 20

    # Hoja 3: Información Académica
    ws3 = wb.create_sheet("Información Académica")
    ws3['A1'] = f"INFORMACIÓN ACADÉMICA - {applicant.nombre_completo}"
    ws3['A1'].font = title_font
    ws3.merge_cells('A1:F1')

    # Encabezados
    headers = ["Profesión", "Universidad", "Tarjeta Profesional",
               "N° Tarjeta/Resolución", "Fecha Expedición", "Fecha Grado"]
    for col, header in enumerate(headers, start=1):
        cell = ws3.cell(row=3, column=col)
        cell.value = header
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = border

    # Datos
    row = 4
    for academica in applicant.formacion_academica.all():
        ws3.cell(row=row, column=1, value=academica.profesion).border = border
        ws3.cell(row=row, column=2, value=academica.universidad).border = border
        ws3.cell(row=row, column=3, value=academica.tarjeta_profesional).border = border
        ws3.cell(row=row, column=4, value=academica.numero_tarjeta_resolucion or "N/A").border = border
        ws3.cell(row=row, column=5, value=academica.fecha_expedicion.strftime('%Y-%m-%d') if academica.fecha_expedicion else "N/A").border = border
        ws3.cell(row=row, column=6, value=academica.fecha_grado.strftime('%Y-%m-%d')).border = border
        row += 1

    for col in range(1, 7):
        ws3.column_dimensions[chr(64 + col)].width = 20

    # Hoja 4: Posgrados
    ws4 = wb.create_sheet("Posgrados")
    ws4['A1'] = f"POSGRADOS - {applicant.nombre_completo}"
    ws4['A1'].font = title_font
    ws4.merge_cells('A1:C1')

    # Encabezados
    headers = ["Nombre Posgrado", "Universidad", "Fecha Terminación"]
    for col, header in enumerate(headers, start=1):
        cell = ws4.cell(row=3, column=col)
        cell.value = header
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = border

    # Datos
    row = 4
    for posgrado in applicant.posgrados.all():
        ws4.cell(row=row, column=1, value=posgrado.nombre_posgrado).border = border
        ws4.cell(row=row, column=2, value=posgrado.universidad).border = border
        ws4.cell(row=row, column=3, value=posgrado.fecha_terminacion.strftime('%Y-%m-%d')).border = border
        row += 1

    for col in range(1, 4):
        ws4.column_dimensions[chr(64 + col)].width = 25

    # Hoja 5: Especializaciones
    ws5 = wb.create_sheet("Especializaciones")
    ws5['A1'] = f"ESPECIALIZACIONES - {applicant.nombre_completo}"
    ws5['A1'].font = title_font
    ws5.merge_cells('A1:C1')

    # Encabezados
    headers = ["Nombre Especialización", "Universidad", "Fecha Terminación"]
    for col, header in enumerate(headers, start=1):
        cell = ws5.cell(row=3, column=col)
        cell.value = header
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = border

    # Datos
    row = 4
    for especializacion in applicant.especializaciones.all():
        ws5.cell(row=row, column=1, value=especializacion.nombre_especializacion).border = border
        ws5.cell(row=row, column=2, value=especializacion.universidad).border = border
        ws5.cell(row=row, column=3, value=especializacion.fecha_terminacion.strftime('%Y-%m-%d')).border = border
        row += 1

    for col in range(1, 4):
        ws5.column_dimensions[chr(64 + col)].width = 25

    # Hoja 6: Cálculo de Experiencia
    ws6 = wb.create_sheet("Cálculo Experiencia")
    ws6['A1'] = f"CÁLCULO DE EXPERIENCIA - {applicant.nombre_completo}"
    ws6['A1'].font = title_font
    ws6.merge_cells('A1:B1')

    row = 3
    try:
        calculo = applicant.calculo_experiencia
        calculo_data = [
            ("Total Meses Experiencia", calculo.total_meses_experiencia),
            ("Total Días Experiencia", calculo.total_dias_experiencia),
            ("Total Experiencia (Años)", calculo.total_experiencia_anos),
            ("Años y Meses", calculo.anos_y_meses_experiencia),
        ]
    except:
        calculo_data = [
            ("Total Meses Experiencia", "No calculado"),
            ("Total Días Experiencia", "No calculado"),
            ("Total Experiencia (Años)", "No calculado"),
            ("Años y Meses", "No calculado"),
        ]

    for label, value in calculo_data:
        ws6[f'A{row}'] = label
        ws6[f'A{row}'].font = Font(bold=True)
        ws6[f'A{row}'].fill = PatternFill(start_color="E8E8E8", end_color="E8E8E8", fill_type="solid")
        ws6[f'B{row}'] = value
        ws6[f'A{row}'].border = border
        ws6[f'B{row}'].border = border
        row += 1

    ws6.column_dimensions['A'].width = 30
    ws6.column_dimensions['B'].width = 30

    return wb

