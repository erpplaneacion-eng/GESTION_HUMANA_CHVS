from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.db.models import Q, Count
from django.http import HttpResponse
from django.utils.html import strip_tags
from django.conf import settings
from django.template.loader import render_to_string
from .models import InformacionBasica, CalculoExperiencia, ExperienciaLaboral, InformacionAcademica, Posgrado
from .forms import (
    InformacionBasicaPublicForm,
    InformacionBasicaForm,
    ExperienciaLaboralFormSet,
    InformacionAcademicaFormSet,
    PosgradoFormSet,
)
import zipfile
import io
import os
import json
import base64
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import threading

logger = logging.getLogger(__name__)

# Gmail API scope
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def calcular_experiencia_total(informacion_basica):
    """Calcula automáticamente la experiencia total de una persona"""
    experiencias = informacion_basica.experiencias_laborales.all()

    total_meses = sum(exp.meses_experiencia for exp in experiencias)
    total_dias = sum(exp.dias_experiencia for exp in experiencias)

    # Convertir a años (considerando 12 meses por año)
    total_anos = round(total_meses / 12, 2)

    # Calcular años y meses para formato legible
    anos = total_meses // 12
    meses_restantes = total_meses % 12
    anos_y_meses = f"{anos} años y {meses_restantes} meses"

    # Crear o actualizar el registro de cálculo
    calculo, created = CalculoExperiencia.objects.update_or_create(
        informacion_basica=informacion_basica,
        defaults={
            'total_meses_experiencia': total_meses,
            'total_dias_experiencia': total_dias,
            'total_experiencia_anos': total_anos,
            'anos_y_meses_experiencia': anos_y_meses,
        }
    )
    return calculo

def enviar_correo_confirmacion(informacion_basica):
    """Envía correo de confirmación al usuario que completó el formulario usando Gmail API"""
    try:
        # Obtener la ruta del token.json (en la raíz del proyecto)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        token_path = os.path.join(BASE_DIR, 'token.json')
        
        # Cargar credenciales desde token.json
        if not os.path.exists(token_path):
            logger.error(f'No se encontró token.json en {token_path}')
            return False
            
        with open(token_path, 'r') as token_file:
            token_data = json.load(token_file)
        
        # Crear credenciales desde el token
        creds = Credentials(
            token=token_data.get('token'),
            refresh_token=token_data.get('refresh_token'),
            token_uri=token_data.get('token_uri'),
            client_id=token_data.get('client_id'),
            client_secret=token_data.get('client_secret'),
            scopes=token_data.get('scopes', SCOPES)
        )
        
        # Refrescar el token si es necesario
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            
        # Construir el servicio de Gmail
        service = build('gmail', 'v1', credentials=creds)
        
        # Preparar contexto para el template
        context = {
            'nombre_completo': informacion_basica.nombre_completo,
            'cedula': informacion_basica.cedula,
            'correo': informacion_basica.correo,
            'telefono': informacion_basica.telefono,
            'fecha_registro': datetime.now().strftime('%d/%m/%Y %H:%M'),
        }
        
        # Renderizar template HTML
        html_message = render_to_string('formapp/email_confirmacion.html', context)
        
        # Crear mensaje de correo
        message = MIMEMultipart('alternative')
        message['To'] = informacion_basica.correo
        message['From'] = settings.DEFAULT_FROM_EMAIL
        message['Subject'] = 'Confirmación de Registro - Gestión Humana CHVS'
        
        # Adjuntar contenido HTML
        html_part = MIMEText(html_message, 'html', 'utf-8')
        message.attach(html_part)
        
        # Codificar el mensaje en base64
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        send_message = {'raw': raw_message}
        
        # Enviar correo
        service.users().messages().send(userId='me', body=send_message).execute()
        
        logger.info(f'Correo enviado exitosamente a {informacion_basica.correo} vía Gmail API')
        return True
        
    except Exception as e:
        logger.error(f'Error al enviar correo a {informacion_basica.correo}: {str(e)}')
        return False

def public_form_view(request):
    if request.method == 'POST':
        form = InformacionBasicaPublicForm(request.POST, request.FILES)
        experiencia_formset = ExperienciaLaboralFormSet(request.POST, request.FILES)
        academica_formset = InformacionAcademicaFormSet(request.POST, request.FILES)
        posgrado_formset = PosgradoFormSet(request.POST, request.FILES)

        if form.is_valid():
            try:
                with transaction.atomic():
                    informacion_basica = form.save()

                    experiencia_formset = ExperienciaLaboralFormSet(request.POST, request.FILES, instance=informacion_basica)
                    if experiencia_formset.is_valid():
                        experiencia_formset.save()
                        # Calcular experiencia automáticamente
                        calcular_experiencia_total(informacion_basica)

                    academica_formset = InformacionAcademicaFormSet(request.POST, request.FILES, instance=informacion_basica)
                    if academica_formset.is_valid():
                        academica_formset.save()

                    posgrado_formset = PosgradoFormSet(request.POST, request.FILES, instance=informacion_basica)
                    if posgrado_formset.is_valid():
                        posgrado_formset.save()

                    # Enviar correo de confirmación al usuario en un thread separado
                    # para no bloquear la respuesta del formulario
                    def enviar_correo_async():
                        try:
                            enviar_correo_confirmacion(informacion_basica)
                        except Exception as e:
                            logger.error(f'Error en thread de correo: {str(e)}')

                    thread = threading.Thread(target=enviar_correo_async)
                    thread.daemon = True
                    thread.start()

                    messages.success(request, '¡Formulario enviado con éxito! Recibirás un correo de confirmación en los próximos minutos.')
                    return redirect('formapp:public_form')
            except Exception as e:
                messages.error(request, f'Error al guardar el formulario: {str(e)}')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = InformacionBasicaPublicForm()
        experiencia_formset = ExperienciaLaboralFormSet()
        academica_formset = InformacionAcademicaFormSet()
        posgrado_formset = PosgradoFormSet()

    context = {
        'form': form,
        'experiencia_formset': experiencia_formset,
        'academica_formset': academica_formset,
        'posgrado_formset': posgrado_formset,
    }
    return render(request, 'formapp/public_form.html', context)

class ApplicantListView(LoginRequiredMixin, ListView):
    model = InformacionBasica
    template_name = 'formapp/applicant_list.html'
    context_object_name = 'applicants'
    ordering = ['-id']
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        # Búsqueda por cédula o nombre
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(cedula__icontains=search_query) |
                Q(nombre_completo__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Estadísticas correctamente calculadas
        context['total_personal'] = InformacionBasica.objects.count()
        context['con_experiencia'] = InformacionBasica.objects.filter(
            experiencias_laborales__isnull=False
        ).distinct().count()
        context['profesionales'] = InformacionBasica.objects.filter(
            formacion_academica__isnull=False
        ).distinct().count()
        context['con_posgrado'] = InformacionBasica.objects.filter(
            posgrados__isnull=False
        ).distinct().count()
        # Mantener el valor de búsqueda en el contexto
        context['search_query'] = self.request.GET.get('search', '')
        return context

class ApplicantDetailView(LoginRequiredMixin, DetailView):
    model = InformacionBasica
    template_name = 'formapp/applicant_detail.html'
    context_object_name = 'applicant'

@login_required
def applicant_edit_view(request, pk):
    """Vista para editar un registro existente"""
    applicant = get_object_or_404(InformacionBasica, pk=pk)

    if request.method == 'POST':
        form = InformacionBasicaForm(request.POST, request.FILES, instance=applicant)
        experiencia_formset = ExperienciaLaboralFormSet(request.POST, request.FILES, instance=applicant)
        academica_formset = InformacionAcademicaFormSet(request.POST, request.FILES, instance=applicant)
        posgrado_formset = PosgradoFormSet(request.POST, request.FILES, instance=applicant)

        if form.is_valid():
            try:
                with transaction.atomic():
                    informacion_basica = form.save()

                    if experiencia_formset.is_valid():
                        experiencia_formset.save()
                        # Calcular experiencia automáticamente
                        calcular_experiencia_total(informacion_basica)

                    if academica_formset.is_valid():
                        academica_formset.save()

                    if posgrado_formset.is_valid():
                        posgrado_formset.save()

                    messages.success(request, f'Registro de {informacion_basica.nombre_completo} actualizado con éxito!')
                    return redirect('formapp:applicant_detail', pk=informacion_basica.pk)
            except Exception as e:
                messages.error(request, f'Error al actualizar el registro: {str(e)}')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = InformacionBasicaForm(instance=applicant)
        experiencia_formset = ExperienciaLaboralFormSet(instance=applicant)
        academica_formset = InformacionAcademicaFormSet(instance=applicant)
        posgrado_formset = PosgradoFormSet(instance=applicant)

    context = {
        'form': form,
        'experiencia_formset': experiencia_formset,
        'academica_formset': academica_formset,
        'posgrado_formset': posgrado_formset,
        'applicant': applicant,
    }
    return render(request, 'formapp/applicant_edit.html', context)

@login_required
def applicant_delete_view(request, pk):
    """Vista para eliminar un registro"""
    applicant = get_object_or_404(InformacionBasica, pk=pk)

    if request.method == 'POST':
        nombre = applicant.nombre_completo
        try:
            applicant.delete()
            messages.success(request, f'Registro de {nombre} eliminado exitosamente.')
        except Exception as e:
            messages.error(request, f'Error al eliminar el registro: {str(e)}')
        return redirect('formapp:applicant_list')

    # Si no es POST, redirigir a la lista
    return redirect('formapp:applicant_list')

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
        ("Área de Conocimiento", applicant.area_conocimiento or "N/A"),
        ("Área del Conocimiento", applicant.area_del_conocimiento or "N/A"),
        ("Tipo de Perfil", applicant.tipo_perfil or "N/A"),
        ("Profesión", applicant.profesion or "N/A"),
        ("Experiencia", applicant.experiencia or "N/A"),
        ("Tiempo de Experiencia", applicant.tiempo_experiencia or "N/A"),
        ("Cantidad", applicant.cantidad or "N/A"),
        ("Descripción", applicant.descripcion or "N/A"),
        ("Base Anexo 11", applicant.base_anexo_11 or "N/A"),
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
    ws3.merge_cells('A1:G1')

    # Encabezados
    headers = ["Profesión", "Universidad", "Tarjeta Profesional",
               "N° Tarjeta/Resolución", "Fecha Expedición", "Fecha Grado", "Meses Experiencia"]
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
        ws3.cell(row=row, column=7, value=academica.meses_experiencia_profesion).border = border
        row += 1

    for col in range(1, 8):
        ws3.column_dimensions[chr(64 + col)].width = 20

    # Hoja 4: Posgrados
    ws4 = wb.create_sheet("Posgrados")
    ws4['A1'] = f"POSGRADOS - {applicant.nombre_completo}"
    ws4['A1'].font = title_font
    ws4.merge_cells('A1:D1')

    # Encabezados
    headers = ["Nombre Posgrado", "Universidad", "Fecha Terminación", "Meses Experiencia"]
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
        ws4.cell(row=row, column=4, value=posgrado.meses_de_experiencia).border = border
        row += 1

    for col in range(1, 5):
        ws4.column_dimensions[chr(64 + col)].width = 25

    # Hoja 5: Cálculo de Experiencia
    ws5 = wb.create_sheet("Cálculo Experiencia")
    ws5['A1'] = f"CÁLCULO DE EXPERIENCIA - {applicant.nombre_completo}"
    ws5['A1'].font = title_font
    ws5.merge_cells('A1:B1')

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
        ws5[f'A{row}'] = label
        ws5[f'A{row}'].font = Font(bold=True)
        ws5[f'A{row}'].fill = PatternFill(start_color="E8E8E8", end_color="E8E8E8", fill_type="solid")
        ws5[f'B{row}'] = value
        ws5[f'A{row}'].border = border
        ws5[f'B{row}'].border = border
        row += 1

    ws5.column_dimensions['A'].width = 30
    ws5.column_dimensions['B'].width = 30

    return wb

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

        # 2. Agregar certificados laborales
        for idx, experiencia in enumerate(applicant.experiencias_laborales.all(), start=1):
            if experiencia.certificado_laboral:
                try:
                    # Leer el archivo del certificado
                    certificado_file = experiencia.certificado_laboral
                    certificado_file.open('rb')
                    file_content = certificado_file.read()
                    certificado_file.close()

                    # Obtener la extensión del archivo
                    # Cloudinary puede no incluir extensión en el nombre, así que intentamos obtenerla de la URL
                    ext = os.path.splitext(certificado_file.name)[1]
                    if not ext and hasattr(certificado_file, 'url'):
                        # Intentar obtener extensión de la URL de Cloudinary
                        url = certificado_file.url
                        # La URL de Cloudinary tiene formato: .../upload/v123456/archivo.ext
                        if '.' in url.split('/')[-1]:
                            ext = '.' + url.split('/')[-1].split('.')[-1].split('?')[0]

                    # Si aún no hay extensión, detectar por contenido
                    if not ext:
                        # Detectar tipo por magic bytes
                        if file_content.startswith(b'%PDF'):
                            ext = '.pdf'
                        elif file_content.startswith(b'\x89PNG'):
                            ext = '.png'
                        elif file_content.startswith(b'\xff\xd8\xff'):
                            ext = '.jpg'
                        else:
                            ext = '.pdf'  # Default a PDF si no se puede detectar

                    cargo_safe = experiencia.cargo.replace(' ', '_').replace('/', '-')

                    # Agregar al ZIP
                    zip_file.writestr(
                        f"Certificados/{idx}_{cargo_safe}{ext}",
                        file_content
                    )
                except Exception as e:
                    print(f"Error al agregar certificado: {e}")

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
        ws.merge_cells('A1:L1')

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
                   "Profesión", "Área Conocimiento", "Tipo Perfil", "Experiencia",
                   "Tiempo Experiencia", "Cantidad", "Observaciones"]

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
            ws.cell(row=row, column=6, value=applicant.profesion or "N/A").border = border
            ws.cell(row=row, column=7, value=applicant.area_conocimiento or "N/A").border = border
            ws.cell(row=row, column=8, value=applicant.tipo_perfil or "N/A").border = border
            ws.cell(row=row, column=9, value=applicant.experiencia or "N/A").border = border
            ws.cell(row=row, column=10, value=applicant.tiempo_experiencia or "N/A").border = border
            ws.cell(row=row, column=11, value=applicant.cantidad or "N/A").border = border
            ws.cell(row=row, column=12, value=applicant.observacion or "N/A").border = border
            row += 1

        # Ajustar anchos de columna
        for col in range(1, 13):
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

            # 3. Agregar certificados de cada persona
            for idx, experiencia in enumerate(applicant.experiencias_laborales.all(), start=1):
                if experiencia.certificado_laboral:
                    try:
                        certificado_file = experiencia.certificado_laboral
                        certificado_file.open('rb')
                        file_content = certificado_file.read()
                        certificado_file.close()

                        # Obtener la extensión del archivo
                        # Cloudinary puede no incluir extensión en el nombre, así que intentamos obtenerla de la URL
                        ext = os.path.splitext(certificado_file.name)[1]
                        if not ext and hasattr(certificado_file, 'url'):
                            # Intentar obtener extensión de la URL de Cloudinary
                            url = certificado_file.url
                            # La URL de Cloudinary tiene formato: .../upload/v123456/archivo.ext
                            if '.' in url.split('/')[-1]:
                                ext = '.' + url.split('/')[-1].split('.')[-1].split('?')[0]

                        # Si aún no hay extensión, detectar por contenido
                        if not ext:
                            # Detectar tipo por magic bytes
                            if file_content.startswith(b'%PDF'):
                                ext = '.pdf'
                            elif file_content.startswith(b'\x89PNG'):
                                ext = '.png'
                            elif file_content.startswith(b'\xff\xd8\xff'):
                                ext = '.jpg'
                            else:
                                ext = '.pdf'  # Default a PDF si no se puede detectar

                        cargo_safe = experiencia.cargo.replace(' ', '_').replace('/', '-')

                        zip_file.writestr(
                            f"Personal/{filename_safe}/Certificados/{idx}_{cargo_safe}{ext}",
                            file_content
                        )
                    except Exception as e:
                        print(f"Error al agregar certificado: {e}")

    # Preparar respuesta
    zip_buffer.seek(0)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="Personal_Completo_{timestamp}.zip"'

    return response