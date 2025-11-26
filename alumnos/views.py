from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Alumno
from .forms import AlumnoForm

@login_required
def dashboard(request):
    alumnos = Alumno.objects.filter(usuario=request.user)
    context = {
        'alumnos': alumnos,
        'user': request.user
    }
    return render(request, 'alumnos/dashboard.html', context)

@login_required
def crear_alumno(request):
    if request.method == 'POST':
        form = AlumnoForm(request.POST)
        if form.is_valid():
            alumno = form.save(commit=False)
            alumno.usuario = request.user
            alumno.save()
            messages.success(request, f'Alumno {alumno.nombre_completo} creado exitosamente.')
            return redirect('alumnos:dashboard')
    else:
        form = AlumnoForm()
    
    return render(request, 'alumnos/crear_alumno.html', {'form': form})

@login_required
def editar_alumno(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        form = AlumnoForm(request.POST, instance=alumno)
        if form.is_valid():
            alumno_actualizado = form.save()
            messages.success(request, f'Alumno {alumno_actualizado.nombre_completo} actualizado exitosamente.')
            return redirect('alumnos:dashboard')
    else:
        form = AlumnoForm(instance=alumno)
    
    return render(request, 'alumnos/editar_alumno.html', {
        'form': form,
        'alumno': alumno
    })

@login_required
def eliminar_alumno(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        nombre_completo = alumno.nombre_completo
        alumno.delete()
        messages.success(request, f'Alumno {nombre_completo} eliminado exitosamente.')
        return redirect('alumnos:dashboard')
    
    return render(request, 'alumnos/eliminar_alumno.html', {'alumno': alumno})

@login_required
def enviar_pdf(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id, usuario=request.user)
    
    try:
        # Importar la utilidad de PDF
        from .utils import generar_pdf_alumno
        
        # Generar y enviar PDF al email del usuario
        if generar_pdf_alumno(alumno, request.user.email):
            messages.success(request, f'PDF enviado exitosamente a {request.user.email}')
        else:
            messages.error(request, 'Error al generar el PDF')
            
    except Exception as e:
        messages.error(request, f'Error al enviar el PDF: {str(e)}')
    
    return redirect('alumnos:dashboard')