from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario, Espacio, Reserva, Horario


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class UsuarioRegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'telefono', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 3:
            raise forms.ValidationError('El usuario debe tener al menos 3 caracteres.')
        return username


class EspacioForm(forms.ModelForm):
    class Meta:
        model = Espacio
        fields = ['nombre', 'descripcion', 'tipo', 'capacidad', 'ubicacion', 'disponible']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
        return nombre


class ReservaForm(forms.ModelForm):
    fecha_inicio = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S'],
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
    )
    fecha_fin = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S'],
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
    )

    class Meta:
        model = Reserva
        fields = ['espacio', 'fecha_inicio', 'fecha_fin', 'proposito']
        widgets = {
            'espacio': forms.Select(attrs={'class': 'form-select'}),
            'proposito': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        self.fields['espacio'].queryset = Espacio.objects.filter(disponible=True)
        if self.usuario and not self.usuario.es_admin():
            self.fields['espacio'].queryset = Espacio.objects.filter(disponible=True)

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        if fecha_inicio and fecha_fin and fecha_inicio >= fecha_fin:
            raise forms.ValidationError('La fecha de inicio debe ser anterior a la fecha de fin.')
        return cleaned_data


class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = ['espacio', 'dia_semana', 'hora_inicio', 'hora_fin', 'activo']
        widgets = {
            'espacio': forms.Select(attrs={'class': 'form-select'}),
            'dia_semana': forms.Select(attrs={'class': 'form-select'}),
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ReservaAdminForm(forms.ModelForm):
    fecha_inicio = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S'],
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
    )
    fecha_fin = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S'],
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
    )

    class Meta:
        model = Reserva
        fields = ['espacio', 'usuario', 'fecha_inicio', 'fecha_fin', 'estado', 'proposito']
        widgets = {
            'espacio': forms.Select(attrs={'class': 'form-select'}),
            'usuario': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'proposito': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
