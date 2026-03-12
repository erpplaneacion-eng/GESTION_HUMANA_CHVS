from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formapp', '0032_anexosadicionales_nuevos_campos'),
    ]

    operations = [
        migrations.AddField(
            model_name='educacionsuperior',
            name='tiene_tarjeta_profesional',
            field=models.CharField(
                choices=[('No Aplica', 'No Aplica'), ('Si', 'Sí tiene Tarjeta Profesional')],
                default='No Aplica',
                max_length=20,
                verbose_name='¿Tiene Tarjeta Profesional?',
            ),
        ),
    ]
