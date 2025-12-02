import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

@login_required
def scraping_educativo(request):
    resultados = []
    
    if request.method == 'POST':
        palabra_clave = request.POST.get('palabra_clave')
        enviar_email = request.POST.get('enviar_email')
        
        if palabra_clave:
            try:
                # Scraping de ejemplo (Wikipedia educativa)
                resultados = scrape_wikipedia(palabra_clave)
                
                if enviar_email and resultados:
                    enviar_resultados_email(request.user.email, palabra_clave, resultados)
                    messages.success(request, 'Resultados enviados por email!')
                    
            except Exception as e:
                messages.error(request, f'Error en el scraping: {str(e)}')
    
    return render(request, 'scraper/scraping.html', {'resultados': resultados})

def scrape_wikipedia(palabra_clave):
    """Scraping básico de Wikipedia para contenido educativo"""
    url = f"https://es.wikipedia.org/wiki/{palabra_clave.replace(' ', '_')}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    resultados = []
    
    # Extraer título
    titulo = soup.find('h1')
    if titulo:
        resultados.append(('Título', titulo.get_text().strip()))
    
    # Extraer primer párrafo
    primer_parrafo = soup.find('div', class_='mw-parser-output').find('p')
    if primer_parrafo:
        texto = primer_parrafo.get_text().strip()[:500] + '...'
        resultados.append(('Resumen', texto))
    
    # Extraer tabla de contenido básica
    tablas = soup.find_all('table', class_='infobox')
    for tabla in tablas[:2]:  # Máximo 2 tablas
        filas = tabla.find_all('tr')
        for fila in filas[:5]:  # Máximo 5 filas por tabla
            celdas = fila.find_all(['th', 'td'])
            if len(celdas) >= 2:
                clave = celdas[0].get_text().strip()
                valor = celdas[1].get_text().strip()
                if clave and valor:
                    resultados.append((clave, valor))
    
    return resultados[:10]  # Máximo 10 resultados

def enviar_resultados_email(destinatario, palabra_clave, resultados):
    """Envía los resultados del scraping por email"""
    subject = f'Resultados Scraping - {palabra_clave}'
    
    # Formatear resultados para email
    mensaje_resultados = "\n".join([f"{clave}: {valor}" for clave, valor in resultados])
    
    message = f'''
    Resultados del scraping para: {palabra_clave}
    
    {mensaje_resultados}
    
    ---
    Este email fue generado automáticamente por el sistema de scraping educativo.
    '''
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [destinatario],
        fail_silently=False,
    )