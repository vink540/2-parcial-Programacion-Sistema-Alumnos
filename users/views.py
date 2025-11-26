from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import RegistroForm

def registro(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Enviar correo de bienvenida
            try:
                send_mail(
                    '¡Bienvenido a la Plataforma de Alumnos!',
                    f'Hola {user.username},\n\n'
                    '¡Gracias por registrarte en nuestra plataforma!\n\n'
                    'Ahora puedes iniciar sesión y comenzar a gestionar la información de tus alumnos, '
                    'generar reportes en PDF y utilizar nuestras herramientas de scraping educativo.\n\n'
                    'Saludos cordiales,\n'
                    'Equipo de la Plataforma de Alumnos',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, '¡Registro exitoso! Se ha enviado un correo de bienvenida. Ahora puedes iniciar sesión.')
            except Exception as e:
                messages.success(request, '¡Registro exitoso! Ahora puedes iniciar sesión.')
            
            # NO hacer login automático - redirigir al login
            return redirect('login')
    else:
        form = RegistroForm()
    
    return render(request, 'usuarios/registro.html', {'form': form})