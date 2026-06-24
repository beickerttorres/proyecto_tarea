from django.contrib import admin
from .models import Usuario, Espacio, Reserva, Horario

admin.site.register(Usuario)
admin.site.register(Espacio)
admin.site.register(Reserva)
admin.site.register(Horario)
