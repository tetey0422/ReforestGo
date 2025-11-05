# Generated migration for verification and oxygen features
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        # Agregar campos al modelo Perfil
        migrations.AddField(
            model_name='perfil',
            name='rol',
            field=models.CharField(
                choices=[('usuario', 'Usuario'), ('verificador', 'Verificador'), ('admin', 'Administrador')],
                default='usuario',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='perfil',
            name='verificaciones_realizadas',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='perfil',
            name='verificaciones_aprobadas',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='perfil',
            name='puntos_verificacion',
            field=models.IntegerField(default=0),
        ),
        
        # Actualizar estado de Siembra
        migrations.AlterField(
            model_name='siembra',
            name='estado',
            field=models.CharField(
                choices=[
                    ('pendiente', 'Pendiente'),
                    ('en_verificacion', 'En Verificación'),
                    ('validada', 'Validada'),
                    ('rechazada', 'Rechazada')
                ],
                default='pendiente',
                max_length=20
            ),
        ),
        
        # Agregar campos de oxígeno a Siembra
        migrations.AddField(
            model_name='siembra',
            name='oxigeno_generado',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text='kg O2/año',
                max_digits=10
            ),
        ),
        migrations.AddField(
            model_name='siembra',
            name='co2_absorbido',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text='kg CO2/año',
                max_digits=10
            ),
        ),
        migrations.AddField(
            model_name='siembra',
            name='ultima_actualizacion_oxigeno',
            field=models.DateTimeField(auto_now_add=True),
            preserve_default=False,
        ),
        
        # Crear modelo Verificacion
        migrations.CreateModel(
            name='Verificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('foto_verificacion', models.ImageField(upload_to='verificaciones/%Y/%m/')),
                ('foto_ubicacion', models.ImageField(blank=True, null=True, upload_to='verificaciones/%Y/%m/')),
                ('latitud_verificacion', models.DecimalField(decimal_places=6, max_digits=9)),
                ('longitud_verificacion', models.DecimalField(decimal_places=6, max_digits=9)),
                ('notas_verificador', models.TextField(blank=True, max_length=500)),
                ('fecha_verificacion', models.DateTimeField(auto_now_add=True)),
                ('estado', models.CharField(
                    choices=[('pendiente', 'Pendiente'), ('aprobada', 'Aprobada'), ('rechazada', 'Rechazada')],
                    default='pendiente',
                    max_length=20
                )),
                ('fecha_revision', models.DateTimeField(blank=True, null=True)),
                ('notas_admin', models.TextField(blank=True)),
                ('puntos_otorgados', models.IntegerField(default=0)),
                ('revisada_por', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='verificaciones_revisadas',
                    to=settings.AUTH_USER_MODEL
                )),
                ('siembra', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='verificaciones',
                    to='core.siembra'
                )),
                ('verificador', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='verificaciones_realizadas',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Verificación',
                'verbose_name_plural': 'Verificaciones',
                'ordering': ['-fecha_verificacion'],
            },
        ),
    ]