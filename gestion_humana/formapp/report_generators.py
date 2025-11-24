"""
Generadores de reportes (Excel y PDF) para formapp.
Funciones auxiliares que se mantendrán en views.py hasta completar la migración.
"""

# Importación lazy para evitar circular imports
# Las funciones están definidas en el views.py original
def create_excel_for_person(applicant):
    """Importación lazy de create_excel_for_person"""
    from formapp import views as views_module
    return views_module.create_excel_for_person(applicant)


def generar_anexo11_pdf(applicant):
    """Importación lazy de generar_anexo11_pdf"""
    from formapp import views as views_module
    return views_module.generar_anexo11_pdf(applicant)


__all__ = ['create_excel_for_person', 'generar_anexo11_pdf']
