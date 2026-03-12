from django.db import migrations, models
import formapp.validators


class Migration(migrations.Migration):

    dependencies = [
        ('formapp', '0030_antecedentes_certificado_redam_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='educacionsuperior',
            name='tarjeta_profesional_archivo',
            field=models.FileField(
                blank=True,
                help_text='Si aplica: PDF, JPG, PNG. Máx: 10 MB',
                max_length=200,
                null=True,
                upload_to='educacion_superior/tarjetas/',
                validators=[
                    formapp.validators.validate_file_size,
                    formapp.validators.validate_file_extension,
                    formapp.validators.validate_file_mime,
                ],
                verbose_name='Tarjeta Profesional (Archivo)',
            ),
        ),
    ]
