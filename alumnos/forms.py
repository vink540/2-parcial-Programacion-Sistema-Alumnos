from django import forms
from .models import Alumno

class AlumnoForm(forms.ModelForm):
    class Meta:
        model = Alumno
        fields = ['nombre', 'apellido', 'dni', 'anio', 'division']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del alumno'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido del alumno'
            }),
            'dni': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de DNI'
            }),
            'anio': forms.Select(attrs={
                'class': 'form-control'
            }),
            'division': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'nombre': 'Nombre',
            'apellido': 'Apellido', 
            'dni': 'DNI',
            'anio': 'Año',
            'division': 'División',
        }