from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class Usuario(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('regular', 'Usuario Regular'),
    )
    rol = models.CharField(max_length=10, choices=ROLES, default='regular')
    telefono = models.CharField(max_length=20, blank=True)

    def es_admin(self):
        return self.rol == 'admin' or self.is_staff


class Espacio(models.Model):
    TIPOS = (
        ('laboratorio', 'Laboratorio'),
        ('sala_estudio', 'Sala de Estudio'),
        ('equipo', 'Equipo'),
        ('aula', 'Aula'),
        ('taller', 'Taller'),
    )
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(max_length=20, choices=TIPOS, default='laboratorio')
    capacidad = models.PositiveIntegerField(default=1)
    ubicacion = models.CharField(max_length=200, blank=True)
    disponible = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Espacio'
        verbose_name_plural = 'Espacios'

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"


class Horario(models.Model):
    DIAS_SEMANA = (
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
    )
    espacio = models.ForeignKey(Espacio, on_delete=models.CASCADE, related_name='horarios')
    dia_semana = models.IntegerField(choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['dia_semana', 'hora_inicio']
        verbose_name = 'Horario'
        verbose_name_plural = 'Horarios'

    def __str__(self):
        return f"{self.espacio.nombre} - {self.get_dia_semana_display()} {self.hora_inicio}-{self.hora_fin}"


class Reserva(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('completada', 'Completada'),
    )
    espacio = models.ForeignKey(Espacio, on_delete=models.CASCADE, related_name='reservas')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reservas')
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    estado = models.CharField(max_length=15, choices=ESTADOS, default='pendiente')
    proposito = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_inicio']
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'

    def __str__(self):
        return f"{self.espacio.nombre} - {self.usuario.username} ({self.fecha_inicio.strftime('%d/%m/%Y %H:%M')})"

    def clean(self):
        if self.fecha_inicio and self.fecha_fin and self.fecha_inicio >= self.fecha_fin:
            raise ValidationError('La fecha de inicio debe ser anterior a la fecha de fin.')

        if self.espacio_id:
            conflictos = Reserva.objects.filter(
                espacio_id=self.espacio_id,
                estado__in=['pendiente', 'confirmada'],
                fecha_inicio__lt=self.fecha_fin,
                fecha_fin__gt=self.fecha_inicio,
            )
            if self.pk:
                conflictos = conflictos.exclude(pk=self.pk)

            if conflictos.exists():
                raise ValidationError('El espacio ya está reservado en ese horario.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
