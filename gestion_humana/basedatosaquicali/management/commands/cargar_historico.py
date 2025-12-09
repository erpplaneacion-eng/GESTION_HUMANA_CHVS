import os
import pandas as pd
from datetime import datetime
from dateutil import parser
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from basedatosaquicali.models import (
    PersonalUrl, ExperienciaTotal, ContratoHistorico, ConsolidadoBaseDatos
)

class Command(BaseCommand):
    help = 'Carga datos históricos desde el archivo Excel "link.xlsx" a las tablas de la aplicación basedatosaquicali.'

    def parse_fecha_flexible(self, fecha_value):
        """
        Parsea fechas de forma flexible, manejando formatos mixtos y fechas inválidas.
        Si el día es inválido para el mes, ajusta al último día válido del mes.
        """
        # Si ya es un datetime de pandas, convertir a date
        if isinstance(fecha_value, pd.Timestamp):
            return fecha_value.date()

        # Si es string, intentar parsear
        if isinstance(fecha_value, str):
            try:
                # Intentar parsear con dayfirst=True
                return parser.parse(fecha_value, dayfirst=True).date()
            except ValueError as e:
                # Si falla, intentar ajustar fechas inválidas (ej: 31/09/2017)
                import re
                match = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', fecha_value)
                if match:
                    dia, mes, anio = int(match.group(1)), int(match.group(2)), int(match.group(3))

                    # Ajustar día al último día válido del mes
                    import calendar
                    max_dia = calendar.monthrange(anio, mes)[1]
                    if dia > max_dia:
                        dia = max_dia
                        self.stdout.write(self.style.WARNING(
                            f'   📅 Fecha ajustada: {fecha_value} → {dia:02d}/{mes:02d}/{anio} (último día válido del mes)'
                        ))

                    return datetime(anio, mes, dia).date()
                raise

        # Si es datetime, convertir a date
        if isinstance(fecha_value, datetime):
            return fecha_value.date()

        raise ValueError(f"No se pudo parsear la fecha: {fecha_value}")

    def handle(self, *args, **options):
        excel_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            '..', '..', 'archivos_excel', 'link.xlsx'
        )

        if not os.path.exists(excel_file_path):
            raise CommandError(f'El archivo Excel no se encontró en: {excel_file_path}')

        self.stdout.write(self.style.SUCCESS(f"Iniciando carga desde {excel_file_path}..."))

        try:
            xls = pd.ExcelFile(excel_file_path)

            with transaction.atomic():
                # --- Cargar PersonalUrl ---
                self.stdout.write(self.style.HTTP_INFO('Cargando PersonalUrl...'))
                PersonalUrl.objects.all().delete() # Limpiar tabla existente
                df_personal_url = pd.read_excel(xls, sheet_name='personal_url')
                for index, row in df_personal_url.iterrows():
                    PersonalUrl.objects.create(
                        carpeta_general=row['Carpeta General'],
                        area=row['Área (Nivel 1)'],
                        contratista=row['Contratista (Nivel 2)'],
                        enlace_carpeta=row['Enlace Carpeta Contratista'],
                        cedula=row['CEDULA']
                    )
                self.stdout.write(self.style.SUCCESS(f'Cargados {len(df_personal_url)} registros en PersonalUrl.'))

                # --- Cargar ExperienciaTotal ---
                self.stdout.write(self.style.HTTP_INFO('Cargando ExperienciaTotal...'))
                ExperienciaTotal.objects.all().delete()
                df_experiencia_total = pd.read_excel(xls, sheet_name='experiencia_total')
                for index, row in df_experiencia_total.iterrows():
                    ExperienciaTotal.objects.create(
                        cedula=row['Cédula del Contratista'],
                        nombre_contratista=row['Nombre del Contratista'],
                        experiencia_bruta_dias=row['Experiencia Bruta (Días - Con Traslape)'],
                        experiencia_neta_dias=row['Experiencia Neta (Días - Sin Superposición)'],
                        experiencia_neta_texto=row['Experiencia Neta (Años, Meses, Días)']
                    )
                self.stdout.write(self.style.SUCCESS(f'Cargados {len(df_experiencia_total)} registros en ExperienciaTotal.'))

                # --- Cargar ContratoHistorico ---
                self.stdout.write(self.style.HTTP_INFO('Cargando ContratoHistorico...'))
                ContratoHistorico.objects.all().delete()
                df_experiencia = pd.read_excel(xls, sheet_name='eXperiencia')
                for index, row in df_experiencia.iterrows():
                    # Convertir fechas con formato más flexible
                    fecha_inicio = self.parse_fecha_flexible(row['Fecha Inicio'])
                    fecha_fin = self.parse_fecha_flexible(row['Fecha Fin'])

                    ContratoHistorico.objects.create(
                        cedula=row['Cédula'],
                        nombre_contratista=row['Nombre Contratista'],
                        numero_registro=row['N°'],
                        contrato=row['Contrato'],
                        fecha_inicio=fecha_inicio,
                        fecha_fin=fecha_fin,
                        dias_brutos=row['Días Brutos'],
                        traslape=row['¿Traslape/Unión?'],
                        explicacion_detallada=row['Explicación Detallada'] if pd.notna(row['Explicación Detallada']) else '',
                        dias_reales_contribuidos=row['Días Reales Contribuidos']
                    )
                self.stdout.write(self.style.SUCCESS(f'Cargados {len(df_experiencia)} registros en ContratoHistorico.'))

                # --- Cargar ConsolidadoBaseDatos ---
                self.stdout.write(self.style.HTTP_INFO('Cargando ConsolidadoBaseDatos...'))
                ConsolidadoBaseDatos.objects.all().delete()
                df_consolidado = pd.read_excel(xls, sheet_name='consolidado_basedatos')

                registros_cargados = 0
                registros_con_error = 0

                for index, row in df_consolidado.iterrows():
                    try:
                        # Convertir fechas con formato más flexible
                        fecha_firma = self.parse_fecha_flexible(row['Fecha de Firma'])
                        fecha_final = self.parse_fecha_flexible(row['Plazo de Duración (Fecha Final) (DD/MM/AAAA)'])

                        ConsolidadoBaseDatos.objects.create(
                            area=row['area'],
                            tipo_documento=row['Tipo de Documento'],
                            numero_contrato_otrosi=row['No. de Contrato / Otrosí'],
                            nombre_contratista=row['Nombre del Contratista'],
                            cedula=row['Cédula del Contratista'],
                            contratante_nit=row['Contratante (NIT)'],
                            objeto_contrato=row['Objeto del Contrato'],
                            fecha_firma=fecha_firma,
                            fecha_final=fecha_final,
                            actividades_especificas=row['Actividades Específicas del Contratista / Modificación'] if pd.notna(row['Actividades Específicas del Contratista / Modificación']) else '',
                            estado=row['ESTADO']
                        )
                        registros_cargados += 1
                    except Exception as e:
                        registros_con_error += 1
                        self.stdout.write(self.style.WARNING(
                            f'⚠️ Error en fila {index + 1} (Contrato: {row.get("No. de Contrato / Otrosí", "N/A")}): {str(e)}'
                        ))
                        self.stdout.write(self.style.WARNING(
                            f'   Fecha de Firma: {row["Fecha de Firma"]}, Fecha Final: {row["Plazo de Duración (Fecha Final) (DD/MM/AAAA)"]}'
                        ))

                self.stdout.write(self.style.SUCCESS(
                    f'Cargados {registros_cargados} registros en ConsolidadoBaseDatos.'
                ))
                if registros_con_error > 0:
                    self.stdout.write(self.style.WARNING(
                        f'⚠️ {registros_con_error} registros con errores fueron omitidos.'
                    ))

            self.stdout.write(self.style.SUCCESS('¡Carga de datos históricos completada exitosamente!'))

        except Exception as e:
            raise CommandError(f'Ocurrió un error durante la carga de datos: {e}')