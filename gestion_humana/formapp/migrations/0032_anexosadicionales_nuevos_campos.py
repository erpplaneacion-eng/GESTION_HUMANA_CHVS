from django.db import migrations, models
import formapp.validators


class Migration(migrations.Migration):

    dependencies = [
        ('formapp', '0031_educacionsuperior_tarjeta_archivo'),
    ]

    operations = [
        migrations.AddField(
            model_name='anexosadicionales',
            name='certificado_eps',
            field=models.FileField(
                blank=True,
                help_text='Certificado de afiliación a EPS. Formatos: PDF, JPG, PNG. Máx: 10 MB',
                max_length=200,
                null=True,
                upload_to='anexos/eps/',
                validators=[
                    formapp.validators.validate_file_size,
                    formapp.validators.validate_file_extension,
                    formapp.validators.validate_file_mime,
                ],
                verbose_name='Certificado EPS',
            ),
        ),
        migrations.AddField(
            model_name='anexosadicionales',
            name='certificado_pension',
            field=models.FileField(
                blank=True,
                help_text='Certificado de afiliación al fondo de pensiones. Formatos: PDF, JPG, PNG. Máx: 10 MB',
                max_length=200,
                null=True,
                upload_to='anexos/pension/',
                validators=[
                    formapp.validators.validate_file_size,
                    formapp.validators.validate_file_extension,
                    formapp.validators.validate_file_mime,
                ],
                verbose_name='Certificado Pensión',
            ),
        ),
        migrations.AddField(
            model_name='anexosadicionales',
            name='examen_ocupacional',
            field=models.FileField(
                blank=True,
                help_text='Resultado del examen médico ocupacional. Formatos: PDF, JPG, PNG. Máx: 10 MB',
                max_length=200,
                null=True,
                upload_to='anexos/examen_ocupacional/',
                validators=[
                    formapp.validators.validate_file_size,
                    formapp.validators.validate_file_extension,
                    formapp.validators.validate_file_mime,
                ],
                verbose_name='Examen Ocupacional',
            ),
        ),
        migrations.AddField(
            model_name='anexosadicionales',
            name='certificado_bancario',
            field=models.FileField(
                blank=True,
                help_text='Certificado de cuenta bancaria. Formatos: PDF, JPG, PNG. Máx: 10 MB',
                max_length=200,
                null=True,
                upload_to='anexos/bancario/',
                validators=[
                    formapp.validators.validate_file_size,
                    formapp.validators.validate_file_extension,
                    formapp.validators.validate_file_mime,
                ],
                verbose_name='Certificado Bancario',
            ),
        ),
        migrations.AddField(
            model_name='anexosadicionales',
            name='rut',
            field=models.FileField(
                blank=True,
                help_text='Registro Único Tributario (RUT). Formatos: PDF, JPG, PNG. Máx: 10 MB',
                max_length=200,
                null=True,
                upload_to='anexos/rut/',
                validators=[
                    formapp.validators.validate_file_size,
                    formapp.validators.validate_file_extension,
                    formapp.validators.validate_file_mime,
                ],
                verbose_name='RUT',
            ),
        ),
    ]
