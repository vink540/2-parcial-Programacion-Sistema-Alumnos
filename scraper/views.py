from django.shortcuts import render
import wikipediaapi
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import EmailMessage
import requests
import json
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import simpleSplit

def scraper(request):
    context = {
        'resultados': [],
        'query': '',
        'error': None,
        'articulo_completo': None
    }
    
    if request.GET.get('buscar'):
        query = request.GET.get('buscar', '').strip()
        context['query'] = query
        
        try:
            wiki_wiki = wikipediaapi.Wikipedia(
                language='es',
                user_agent='MiAppDjango/1.0'
            )
            
            page = wiki_wiki.page(query)
            
            if page.exists():
                context['articulo_completo'] = {
                    'titulo': page.title,
                    'extracto': page.summary[:1000],
                    'url': page.fullurl,
                    'imagen': '' 
                }
                
                context['resultados'] = [{
                    'titulo': page.title,
                    'descripcion': page.summary[:300],
                    'url': page.fullurl
                }]
            else:
                context['error'] = f'No se encontró un artículo exacto para "{query}". Intenta con otro término.'
                
        except Exception as e:
            context['error'] = f'Error al buscar en Wikipedia: {str(e)}'
            print(f"Error: {e}")
    
    return render(request, 'scraper/scraper.html', context)

@login_required
def enviar_wikipedia_email(request):
    
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Método no permitido'
        })
    
    try:
        titulo = request.POST.get('titulo', '')
        extracto = request.POST.get('extracto', '')
        url = request.POST.get('url', '')
        email_destino = request.POST.get('email', '').strip()
        
        if not email_destino:
            return JsonResponse({
                'success': False,
                'message': 'Debes proporcionar un email de destino'
            })
        
        import re
        email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_regex, email_destino):
            return JsonResponse({
                'success': False,
                'message': 'El email proporcionado no es válido'
            })
        
        if not titulo or not extracto:
            return JsonResponse({
                'success': False,
                'message': 'Faltan datos del artículo'
            })
        
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        p.setFont("Helvetica-Bold", 20)
        y_position = height - 50
        
        titulo_lines = simpleSplit(titulo, "Helvetica-Bold", 20, width - 100)
        for line in titulo_lines:
            p.drawString(50, y_position, line)
            y_position -= 25
        
        y_position -= 10
        p.line(50, y_position, width - 50, y_position)
        y_position -= 30
        
        p.setFont("Helvetica-Oblique", 10)
        p.drawString(50, y_position, f"Fuente: Wikipedia")
        y_position -= 15
        p.setFont("Helvetica", 9)
        p.drawString(50, y_position, url)
        y_position -= 30
        
        p.setFont("Helvetica", 11)

        max_width = width - 100
        lines = []

        paragraphs = extracto.split('\n')
        
        for paragraph in paragraphs:
            if paragraph.strip():
                para_lines = simpleSplit(paragraph, "Helvetica", 11, max_width)
                lines.extend(para_lines)
                lines.append('')
        
        for line in lines:
            if y_position < 50:
                p.showPage()
                p.setFont("Helvetica", 11)
                y_position = height - 50
            
            p.drawString(50, y_position, line)
            y_position -= 15
        
        p.setFont("Helvetica-Oblique", 8)
        p.drawString(50, 30, f"Documento generado desde tu aplicación - Usuario: {request.user.username}")
        
        p.showPage()
        p.save()
        
        pdf = buffer.getvalue()
        buffer.close()
        
        email = EmailMessage(
            subject=f'Artículo de Wikipedia: {titulo}',
            body=f'Hola,\n\nAdjunto encontrarás el artículo de Wikipedia sobre "{titulo}".\n\nPuedes leer el artículo completo en: {url}\n\nSaludos,\nTu aplicación',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email_destino],
        )
        
        filename = re.sub(r'[^\w\s-]', '', titulo)[:50]
        email.attach(f'wikipedia_{filename}.pdf', pdf, 'application/pdf')
        
        email.send(fail_silently=False)
        
        return JsonResponse({
            'success': True,
            'message': f'Artículo enviado correctamente a {email_destino}'
        })
        
    except Exception as e:
        print(f"Error al enviar email: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error al enviar el email: {str(e)}'
        })