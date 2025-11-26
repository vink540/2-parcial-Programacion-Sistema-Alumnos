from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Alumno(models.Model):
    ANIOS = [
        ('primero', '1ro'),
        ('segundo', '2do'), 
        ('tercero', '3ro'),
        ('cuarto', '4to'),
        ('quinto', '5to'),
        ('sexto', '6to'),
    ]
    
    DIVISIONES = [
        ('a', 'A'),
        ('b', 'B'),
        ('c', 'C'),
        ('d', 'D'),
        ('e', 'E'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, unique=True)
    anio = models.CharField(max_length=10, choices=ANIOS)
    division = models.CharField(max_length=1, choices=DIVISIONES)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['anio', 'division', 'apellido', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"
    
    @property
    def clase_completa(self):
        try:
            año_display = self.get_anio_display()
            division_display = self.get_division_display()
            return f"{año_display} {division_display}"
        except:
            return "Error"
    
    def get_absolute_url(self):
        return reverse('alumnos:dashboard')
    
    def get_delete_url(self):
        return reverse('alumnos:eliminar_alumno', kwargs={'pk': self.pk})