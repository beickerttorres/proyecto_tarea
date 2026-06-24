from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.LoginPersonalizadoView.as_view(), name='login'),
    path('registro/', views.RegistroView.as_view(), name='registro'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    path('espacios/', views.EspacioListView.as_view(), name='espacio_list'),
    path('espacios/nuevo/', views.EspacioCreateView.as_view(), name='espacio_create'),
    path('espacios/<int:pk>/editar/', views.EspacioUpdateView.as_view(), name='espacio_update'),
    path('espacios/<int:pk>/eliminar/', views.EspacioDeleteView.as_view(), name='espacio_delete'),

    path('reservas/', views.ReservaListView.as_view(), name='reserva_list'),
    path('reservas/nueva/', views.ReservaCreateView.as_view(), name='reserva_create'),
    path('reservas/<int:pk>/editar/', views.ReservaUpdateView.as_view(), name='reserva_update'),
    path('reservas/<int:pk>/eliminar/', views.ReservaDeleteView.as_view(), name='reserva_delete'),
    path('reservas/<int:pk>/cancelar/', views.ReservaCancelView.as_view(), name='reserva_cancel'),

    path('horarios/', views.HorarioListView.as_view(), name='horario_list'),
    path('horarios/nuevo/', views.HorarioCreateView.as_view(), name='horario_create'),
    path('horarios/<int:pk>/editar/', views.HorarioUpdateView.as_view(), name='horario_update'),
    path('horarios/<int:pk>/eliminar/', views.HorarioDeleteView.as_view(), name='horario_delete'),
]
