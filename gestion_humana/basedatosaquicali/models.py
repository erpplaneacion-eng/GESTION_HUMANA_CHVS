from django.db import models

class PersonalUrl(models.Model):
    carpeta_general = models.CharField(max_length=50, verbose_name="Carpeta General", default="CONTRATOS PERSONAL 2025-2017")
    area = models.CharField(max_length=100, verbose_name="Área (Nivel 1)")
    contratista = models.CharField(max_length=200, verbose_name="Contratista (Nivel 2)")
    enlace_carpeta = models.URLField(max_length=500, verbose_name="Enlace Carpeta Contratista")
    cedula = models.BigIntegerField(verbose_name="Cédula", db_index=True)

    class Meta:
        verbose_name = "URL Carpeta Personal"
        verbose_name_plural = "URLs Carpetas Personales"

    def __str__(self):
        return f"{self.contratista} - {self.cedula}"


class ExperienciaTotal(models.Model):
    cedula = models.BigIntegerField(verbose_name="Cédula del Contratista", db_index=True)
    nombre_contratista = models.CharField(max_length=200, verbose_name="Nombre del Contratista")
    experiencia_bruta_dias = models.IntegerField(verbose_name="Experiencia Bruta (Días - Con Traslape)")
    experiencia_neta_dias = models.IntegerField(verbose_name="Experiencia Neta (Días - Sin Superposición)")
    experiencia_neta_texto = models.CharField(max_length=100, verbose_name="Experiencia Neta (Años, Meses, Días)")

    class Meta:
        verbose_name = "Experiencia Total Acumulada"
        verbose_name_plural = "Experiencias Totales Acumuladas"

    def __str__(self):
        return f"{self.nombre_contratista} - {self.experiencia_neta_texto}"


class ContratoHistorico(models.Model):
    cedula = models.BigIntegerField(verbose_name="Cédula", db_index=True)
    nombre_contratista = models.CharField(max_length=200, verbose_name="Nombre Contratista")
    numero_registro = models.IntegerField(verbose_name="N°")
    contrato = models.CharField(max_length=100, verbose_name="Contrato")
    fecha_inicio = models.DateField(verbose_name="Fecha Inicio")
    fecha_fin = models.DateField(verbose_name="Fecha Fin")
    dias_brutos = models.IntegerField(verbose_name="Días Brutos")
    traslape = models.CharField(max_length=10, verbose_name="¿Traslape/Unión?") # Usamos Char por si viene 'SI'/'NO'
    explicacion_detallada = models.TextField(verbose_name="Explicación Detallada", blank=True, null=True)
    dias_reales_contribuidos = models.IntegerField(verbose_name="Días Reales Contribuidos")

    class Meta:
        verbose_name = "Contrato Histórico"
        verbose_name_plural = "Historial de Contratos (Detalle)"
        ordering = ['cedula', 'fecha_inicio']

    def __str__(self):
        return f"{self.contrato} - {self.nombre_contratista}"


class ConsolidadoBaseDatos(models.Model):
    area = models.CharField(max_length=100, verbose_name="Área")
    tipo_documento = models.CharField(max_length=100, verbose_name="Tipo de Documento")
    numero_contrato_otrosi = models.CharField(max_length=100, verbose_name="No. de Contrato / Otrosí")
    nombre_contratista = models.CharField(max_length=200, verbose_name="Nombre del Contratista")
    cedula = models.BigIntegerField(verbose_name="Cédula del Contratista", db_index=True)
    contratante_nit = models.CharField(max_length=300, verbose_name="Contratante (NIT)")
    objeto_contrato = models.TextField(verbose_name="Objeto del Contrato")
    fecha_firma = models.DateField(verbose_name="Fecha de Firma")
    fecha_final = models.DateField(verbose_name="Plazo de Duración (Fecha Final)")
    actividades_especificas = models.TextField(verbose_name="Actividades Específicas / Modificación", blank=True, null=True)
    estado = models.CharField(max_length=50, verbose_name="ESTADO")

    class Meta:
        verbose_name = "Consolidado Base de Datos"
        verbose_name_plural = "Consolidados Base de Datos"

    def __str__(self):
        return f"{self.numero_contrato_otrosi} - {self.nombre_contratista}"