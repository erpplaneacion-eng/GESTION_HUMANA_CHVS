"""
Generadores de reportes (Excel y PDF) para formapp.
Wrapper para mantener compatibilidad.
"""
from .report_generators_excel import create_excel_for_person
from .report_generators_pdf import generar_anexo11_pdf

__all__ = ['create_excel_for_person', 'generar_anexo11_pdf']