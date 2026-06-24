from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from django.shortcuts import redirect
from django.db.models import Count, Q
from django.utils import timezone

from .models import Espacio, Reserva, Horario, Usuario
from .forms import (
    EspacioForm, ReservaForm, HorarioForm,
    ReservaAdminForm, UsuarioRegistroForm, LoginForm
)


class RegistroView(CreateView):
    template_name = 'core/registro.html'
    form_class = UsuarioRegistroForm
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        from .models import Usuario
        if not Usuario.objects.exists():
            form.instance.rol = 'admin'
        else:
            form.instance.rol = 'regular'
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class LoginPersonalizadoView(LoginView):
    template_name = 'core/login.html'
    form_class = LoginForm


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user

        if usuario.es_admin():
            reservas = Reserva.objects.all()
            espacios = Espacio.objects.all()
        else:
            reservas = Reserva.objects.filter(usuario=usuario)
            espacios = Espacio.objects.all()

        hoy = timezone.now()
        context['total_reservas'] = reservas.count()
        context['pendientes'] = reservas.filter(estado='pendiente').count()
        context['confirmadas'] = reservas.filter(estado='confirmada').count()
        context['completadas'] = reservas.filter(estado='completada').count()
        context['canceladas'] = reservas.filter(estado='cancelada').count()
        context['espacios'] = espacios
        context['total_espacios'] = espacios.count()
        context['proximas_reservas'] = reservas.filter(
            fecha_inicio__gte=hoy, estado__in=['pendiente', 'confirmada']
        ).order_by('fecha_inicio')[:5]
        return context


class EspacioListView(LoginRequiredMixin, ListView):
    model = Espacio
    template_name = 'core/espacio_list.html'

    def get_queryset(self):
        qs = Espacio.objects.all()
        tipo = self.request.GET.get('tipo')
        if tipo:
            qs = qs.filter(tipo=tipo)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipos'] = Espacio.TIPOS
        return context


class EspacioCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Espacio
    form_class = EspacioForm
    template_name = 'core/espacio_form.html'
    success_message = 'Espacio creado exitosamente.'
    success_url = reverse_lazy('espacio_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.es_admin():
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)


class EspacioUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Espacio
    form_class = EspacioForm
    template_name = 'core/espacio_form.html'
    success_message = 'Espacio actualizado exitosamente.'
    success_url = reverse_lazy('espacio_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.es_admin():
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)


class EspacioDeleteView(LoginRequiredMixin, DeleteView):
    model = Espacio
    template_name = 'core/espacio_confirm_delete.html'
    success_url = reverse_lazy('espacio_list')
    success_message = 'Espacio eliminado exitosamente.'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.es_admin():
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)


class ReservaListView(LoginRequiredMixin, ListView):
    model = Reserva
    template_name = 'core/reserva_list.html'

    def get_queryset(self):
        qs = Reserva.objects.select_related('espacio', 'usuario')
        if not self.request.user.es_admin():
            qs = qs.filter(usuario=self.request.user)

        estado = self.request.GET.get('estado')
        espacio = self.request.GET.get('espacio')
        if estado:
            qs = qs.filter(estado=estado)
        if espacio:
            qs = qs.filter(espacio_id=espacio)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['espacios_filtro'] = Espacio.objects.all()
        return context


class ReservaCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Reserva
    template_name = 'core/reserva_form.html'
    success_message = 'Reserva creada exitosamente.'
    success_url = reverse_lazy('reserva_list')

    def get_form_class(self):
        if self.request.user.es_admin():
            return ReservaAdminForm
        return ReservaForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user
        return kwargs

    def form_valid(self, form):
        if not self.request.user.es_admin():
            form.instance.usuario = self.request.user
            form.instance.estado = 'pendiente'
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        espacio_id = self.request.GET.get('espacio')
        if espacio_id:
            initial['espacio'] = espacio_id
        return initial


class ReservaUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Reserva
    template_name = 'core/reserva_form.html'
    success_message = 'Reserva actualizada exitosamente.'
    success_url = reverse_lazy('reserva_list')

    def get_form_class(self):
        if self.request.user.es_admin():
            return ReservaAdminForm
        return ReservaForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        obj = self.get_object()
        if not request.user.es_admin() and obj.usuario != request.user:
            return HttpResponseForbidden()
        if not request.user.es_admin() and obj.estado == 'cancelada':
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)


class ReservaDeleteView(LoginRequiredMixin, DeleteView):
    model = Reserva
    template_name = 'core/reserva_confirm_delete.html'
    success_url = reverse_lazy('reserva_list')
    success_message = 'Reserva eliminada exitosamente.'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        obj = self.get_object()
        if not request.user.es_admin() and obj.usuario != request.user:
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)


class ReservaCancelView(LoginRequiredMixin, UpdateView):
    model = Reserva
    fields = []
    template_name = 'core/reserva_confirm_cancel.html'
    success_url = reverse_lazy('reserva_list')
    success_message = 'Reserva cancelada exitosamente.'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        obj = self.get_object()
        if not request.user.es_admin() and obj.usuario != request.user:
            return HttpResponseForbidden()
        if obj.estado == 'cancelada':
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.estado = 'cancelada'
        return super().form_valid(form)


class HorarioListView(LoginRequiredMixin, ListView):
    model = Horario
    template_name = 'core/horario_list.html'

    def get_queryset(self):
        qs = Horario.objects.select_related('espacio')
        espacio_id = self.request.GET.get('espacio')
        if espacio_id:
            qs = qs.filter(espacio_id=espacio_id)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['espacios_filtro'] = Espacio.objects.all()
        return context


class HorarioCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Horario
    form_class = HorarioForm
    template_name = 'core/horario_form.html'
    success_message = 'Horario creado exitosamente.'
    success_url = reverse_lazy('horario_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.es_admin():
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)


class HorarioUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Horario
    form_class = HorarioForm
    template_name = 'core/horario_form.html'
    success_message = 'Horario actualizado exitosamente.'
    success_url = reverse_lazy('horario_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.es_admin():
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)


class HorarioDeleteView(LoginRequiredMixin, DeleteView):
    model = Horario
    template_name = 'core/horario_confirm_delete.html'
    success_url = reverse_lazy('horario_list')
    success_message = 'Horario eliminado exitosamente.'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.es_admin():
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)
