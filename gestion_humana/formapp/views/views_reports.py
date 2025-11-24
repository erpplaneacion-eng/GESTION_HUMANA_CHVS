"""
Vistas de reportes y descargasExportación de datos a Excel, PDF y descarga masiva en ZIP.
Refactorizado desde views.py para mejor organización.
"""
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from datetime import datetime
import zipfile
import io
import os
import logging

from ..models import InformacionBasica
from ..report_generators import create_excel_for_person, generar_anexo11_pdf

logger = logging.getLogger(__name__)


@login_required
def download_individual_zip(request, pk):
    """Descarga un ZIP con todos los certificados y Excel de una persona"""
    applicant = get_object_or_404(InformacionBasica, pk=pk)

    # Crear archivo ZIP en memoria
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # 1. Agregar Excel con toda la información
        wb = create_excel_for_person(applicant)
        excel_buffer = io.BytesIO()
        wb.save(excel_buffer)
        excel_buffer.seek(0)

        filename_safe = applicant.nombre_completo.replace(' ', '_')
        zip_file.writestr(
            f"{filename_safe}_Informacion.xlsx",
            excel_buffer.getvalue()
        )

        # 2. Agregar PDF ANEXO 11
        try:
            pdf_buffer = generar_anexo11_pdf(applicant)
            zip_file.writestr(
                f"{filename_safe}_ANEXO_11.pdf",
                pdf_buffer.getvalue()
            )
        except Exception as e:
            logger.error(f"Error al generar PDF ANEXO 11: {str(e)}")

        # Función auxiliar para obtener extensión de archivo
        def get_file_extension(file_field, file_content):
            ext = os.path.splitext(file_field.name)[1]
            if not ext and hasattr(file_field, 'url'):
                url = file_field.url
                if '.' in url.split('/')[-1]:
                    ext = '.' + url.split('/')[-1].split('.')[-1].split('?')[0]
            if not ext:
                if file_content.startswith(b'%PDF'):
                    ext = '.pdf'
                elif file_content.startswith(b'\x89PNG'):
                    ext = '.png'
                elif file_content.startswith(b'\xff\xd8\xff'):
                    ext = '.jpg'
                else:
                    ext = '.pdf'
            return ext

        # 3. Agregar certificados laborales
        for idx, experiencia in enumerate(applicant.experiencias_laborales.all(), start=1):
            if experiencia.certificado_laboral:
                try:
                    certificado_file = experiencia.certificado_laboral
                    with certificado_file.open('rb') as f:
                        file_content = f.read()
                    ext = get_file_extension(certificado_file, file_content)
                    cargo_safe = experiencia.cargo.replace(' ', '_').replace('/', '-')
                    zip_file.writestr(
                        f"Certificados_Laborales/{idx}_{cargo_safe}{ext}",
                        file_content
                    )
                except Exception as e:
                    logger.error(f"Error al agregar certificado {idx} de {applicant.nombre_completo}: {e}")

        # 4. Agregar documentos de identidad
        try:
            if hasattr(applicant, 'documentos_identidad'):
                docs = applicant.documentos_identidad

                # Fotocopia cédula
                if docs.fotocopia_cedula:
                    with docs.fotocopia_cedula.open('rb') as f:
                        file_content = f.read()
                    ext = get_file_extension(docs.fotocopia_cedula, file_content)
                    zip_file.writestr(f"Documentos_Identidad/Cedula{ext}", file_content)

                # Libreta militar
                if docs.libreta_militar:
                    with docs.libreta_militar.open('rb') as f:
                        file_content = f.read()
                    ext = get_file_extension(docs.libreta_militar, file_content)
                    zip_file.writestr(f"Documentos_Identidad/Libreta_Militar{ext}", file_content)

                # Hoja de vida
                if docs.hoja_de_vida:
                    with docs.hoja_de_vida.open('rb') as f:
                        file_content = f.read()
                    ext = get_file_extension(docs.hoja_de_vida, file_content)
                    zip_file.writestr(f"Documentos_Identidad/Hoja_de_Vida{ext}", file_content)
        except Exception as e:
            logger.error(f"Error al agregar documentos de identidad de {applicant.nombre_completo}: {e}")

        # 5. Agregar antecedentes
        try:
            if hasattr(applicant, 'antecedentes'):
                ant = applicant.antecedentes
                antecedentes_files = [
                    (ant.certificado_procuraduria, "Procuraduria"),
                    (ant.certificado_contraloria, "Contraloria"),
                    (ant.certificado_policia, "Policia"),
                    (ant.certificado_medidas_correctivas, "Medidas_Correctivas"),
                    (ant.certificado_delitos_sexuales, "Delitos_Sexuales"),
                ]
                for archivo, nombre in antecedentes_files:
                    if archivo:
                        with archivo.open('rb') as f:
                            file_content = f.read()
                        ext = get_file_extension(archivo, file_content)
                        zip_file.writestr(f"Antecedentes/{nombre}{ext}", file_content)
        except Exception as e:
            logger.error(f"Error al agregar antecedentes de {applicant.nombre_completo}: {e}")

        # 6. Agregar documentos académicos
        for idx, academica in enumerate(applicant.formacion_academica.all(), start=1):
            try:
                profesion_safe = academica.profesion.replace(' ', '_').replace('/', '-')[:30]

                if academica.fotocopia_titulo:
                    with academica.fotocopia_titulo.open('rb') as f:
                        file_content = f.read()
                    ext = get_file_extension(academica.fotocopia_titulo, file_content)
                    zip_file.writestr(f"Documentos_Academicos/{idx}_{profesion_safe}_Titulo{ext}", file_content)

                if academica.fotocopia_tarjeta_profesional:
                    with academica.fotocopia_tarjeta_profesional.open('rb') as f:
                        file_content = f.read()
                    ext = get_file_extension(academica.fotocopia_tarjeta_profesional, file_content)
                    zip_file.writestr(f"Documentos_Academicos/{idx}_{profesion_safe}_Tarjeta_Profesional{ext}", file_content)

                if academica.certificado_vigencia_tarjeta:
                    with academica.certificado_vigencia_tarjeta.open('rb') as f:
                        file_content = f.read()
                    ext = get_file_extension(academica.certificado_vigencia_tarjeta, file_content)
                    zip_file.writestr(f"Documentos_Academicos/{idx}_{profesion_safe}_Certificado_Vigencia{ext}", file_content)
            except Exception as e:
                logger.error(f"Error al agregar documentos académicos {idx} de {applicant.nombre_completo}: {e}")

        # 7. Agregar anexos adicionales
        try:
            if hasattr(applicant, 'anexos_adicionales'):
                anexos = applicant.anexos_adicionales

                if anexos.anexo_03_datos_personales:
                    with anexos.anexo_03_datos_personales.open('rb') as f:
                        file_content = f.read()
                    ext = get_file_extension(anexos.anexo_03_datos_personales, file_content)
                    zip_file.writestr(f"Anexos/ANEXO_03_Datos_Personales{ext}", file_content)

                if anexos.carta_intencion:
                    with anexos.carta_intencion.open('rb') as f:
                        file_content = f.read()
                    ext = get_file_extension(anexos.carta_intencion, file_content)
                    zip_file.writestr(f"Anexos/Carta_Intencion{ext}", file_content)

                if anexos.otros_documentos:
                    with anexos.otros_documentos.open('rb') as f:
                        file_content = f.read()
                    ext = get_file_extension(anexos.otros_documentos, file_content)
                    zip_file.writestr(f"Anexos/Otros_Documentos{ext}", file_content)
        except Exception as e:
            logger.error(f"Error al agregar anexos de {applicant.nombre_completo}: {e}")

    # Preparar respuesta
    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{filename_safe}_Completo.zip"'

    return response

@login_required
def download_all_zip(request):
    """Descarga un ZIP con toda la información de TODO el personal"""
    applicants = InformacionBasica.objects.all()

    # Crear archivo ZIP en memoria
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # 1. Crear Excel consolidado con TODO el personal
        wb = Workbook()
        ws = wb.active
        ws.title = "Personal Completo"

        # Título
        ws['A1'] = "REGISTRO COMPLETO DE PERSONAL"
        ws['A1'].font = Font(bold=True, size=14, color="2C3E50")
        ws.merge_cells('A1:J1')

        # Encabezados
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        headers = ["Cédula", "Nombre Completo", "Género", "Teléfono", "Correo",
                   "Perfil", "Área del Conocimiento", "Profesión", "Contrato", "Observaciones"]

        for col, header in enumerate(headers, start=1):
            cell = ws.cell(row=3, column=col)
            cell.value = header
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = border

        # Datos
        row = 4
        for applicant in applicants:
            ws.cell(row=row, column=1, value=applicant.cedula).border = border
            ws.cell(row=row, column=2, value=applicant.nombre_completo).border = border
            ws.cell(row=row, column=3, value=applicant.genero).border = border
            ws.cell(row=row, column=4, value=applicant.telefono).border = border
            ws.cell(row=row, column=5, value=applicant.correo).border = border
            ws.cell(row=row, column=6, value=applicant.perfil or "N/A").border = border
            ws.cell(row=row, column=7, value=applicant.area_del_conocimiento or "N/A").border = border
            ws.cell(row=row, column=8, value=applicant.profesion or "N/A").border = border
            ws.cell(row=row, column=9, value=applicant.contrato or "N/A").border = border
            ws.cell(row=row, column=10, value=applicant.observacion or "N/A").border = border
            row += 1

        # Ajustar anchos de columna
        for col in range(1, 11):
            ws.column_dimensions[chr(64 + col)].width = 20

        # Guardar Excel consolidado
        excel_buffer = io.BytesIO()
        wb.save(excel_buffer)
        excel_buffer.seek(0)
        zip_file.writestr("Personal_Completo.xlsx", excel_buffer.getvalue())

        # 2. Agregar Excel individual de cada persona
        for applicant in applicants:
            wb_individual = create_excel_for_person(applicant)
            excel_individual_buffer = io.BytesIO()
            wb_individual.save(excel_individual_buffer)
            excel_individual_buffer.seek(0)

            filename_safe = applicant.nombre_completo.replace(' ', '_')
            zip_file.writestr(
                f"Personal/{filename_safe}/{filename_safe}_Informacion.xlsx",
                excel_individual_buffer.getvalue()
            )

            # 2.1. Agregar PDF ANEXO 11 de cada persona
            try:
                pdf_buffer_individual = generar_anexo11_pdf(applicant)
                zip_file.writestr(
                    f"Personal/{filename_safe}/{filename_safe}_ANEXO_11.pdf",
                    pdf_buffer_individual.getvalue()
                )
            except Exception as e:
                logger.error(f"Error al generar PDF ANEXO 11 para {applicant.nombre_completo}: {str(e)}")

            # Función auxiliar para obtener extensión de archivo
            def get_file_extension(file_field):
                if not file_field:
                    return '.pdf'
                ext = os.path.splitext(file_field.name)[1]
                if not ext and hasattr(file_field, 'url'):
                    url = file_field.url
                    if '.' in url.split('/')[-1]:
                        ext = '.' + url.split('/')[-1].split('.')[-1].split('?')[0]
                if not ext:
                    try:
                        with file_field.open('rb') as f:
                            content = f.read(10)
                            file_field.seek(0)
                        if content.startswith(b'%PDF'):
                            ext = '.pdf'
                        elif content.startswith(b'\x89PNG'):
                            ext = '.png'
                        elif content.startswith(b'\xff\xd8\xff'):
                            ext = '.jpg'
                        else:
                            ext = '.pdf'
                    except:
                        ext = '.pdf'
                return ext

            # Función auxiliar para agregar archivo al ZIP
            def add_file_to_zip(file_field, zip_path):
                if file_field:
                    try:
                        with file_field.open('rb') as f:
                            file_content = f.read()
                        ext = get_file_extension(file_field)
                        zip_file.writestr(f"{zip_path}{ext}", file_content)
                    except Exception as e:
                        logger.error(f"Error al agregar archivo {zip_path}: {e}")

            # 3. Agregar documentos de identidad
            if hasattr(applicant, 'documentos_identidad') and applicant.documentos_identidad:
                docs_id = applicant.documentos_identidad
                add_file_to_zip(docs_id.fotocopia_cedula, f"Personal/{filename_safe}/Documentos_Identidad/Cedula")
                add_file_to_zip(docs_id.hoja_de_vida, f"Personal/{filename_safe}/Documentos_Identidad/Hoja_de_Vida")
                add_file_to_zip(docs_id.libreta_militar, f"Personal/{filename_safe}/Documentos_Identidad/Libreta_Militar")

            # 4. Agregar antecedentes
            if hasattr(applicant, 'antecedentes') and applicant.antecedentes:
                antec = applicant.antecedentes
                add_file_to_zip(antec.certificado_procuraduria, f"Personal/{filename_safe}/Antecedentes/Procuraduria")
                add_file_to_zip(antec.certificado_contraloria, f"Personal/{filename_safe}/Antecedentes/Contraloria")
                add_file_to_zip(antec.certificado_policia, f"Personal/{filename_safe}/Antecedentes/Policia")
                add_file_to_zip(antec.certificado_medidas_correctivas, f"Personal/{filename_safe}/Antecedentes/Medidas_Correctivas")
                add_file_to_zip(antec.certificado_delitos_sexuales, f"Personal/{filename_safe}/Antecedentes/Delitos_Sexuales")

            # 5. Agregar documentos académicos
            for idx, academica in enumerate(applicant.formacion_academica.all(), start=1):
                profesion_safe = academica.profesion.replace(' ', '_').replace('/', '-')[:30]
                add_file_to_zip(academica.fotocopia_titulo, f"Personal/{filename_safe}/Documentos_Academicos/{idx}_{profesion_safe}_Titulo")
                add_file_to_zip(academica.fotocopia_tarjeta_profesional, f"Personal/{filename_safe}/Documentos_Academicos/{idx}_{profesion_safe}_Tarjeta_Profesional")
                add_file_to_zip(academica.certificado_vigencia_tarjeta, f"Personal/{filename_safe}/Documentos_Academicos/{idx}_{profesion_safe}_Vigencia_Tarjeta")

            # 6. Agregar anexos adicionales
            if hasattr(applicant, 'anexos_adicionales') and applicant.anexos_adicionales:
                anexos = applicant.anexos_adicionales
                add_file_to_zip(anexos.anexo_03_datos_personales, f"Personal/{filename_safe}/Anexos/Anexo_03_Datos_Personales")
                add_file_to_zip(anexos.carta_intencion, f"Personal/{filename_safe}/Anexos/Carta_Intencion")
                add_file_to_zip(anexos.otros_documentos, f"Personal/{filename_safe}/Anexos/Otros_Documentos")

            # 7. Agregar certificados laborales
            for idx, experiencia in enumerate(applicant.experiencias_laborales.all(), start=1):
                if experiencia.certificado_laboral:
                    cargo_safe = experiencia.cargo.replace(' ', '_').replace('/', '-')[:30]
                    add_file_to_zip(experiencia.certificado_laboral, f"Personal/{filename_safe}/Certificados_Laborales/{idx}_{cargo_safe}")

    # Preparar respuesta
    zip_buffer.seek(0)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="Personal_Completo_{timestamp}.zip"'

    return response