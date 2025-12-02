import requests
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import timezone
import re

@login_required
def scraper_educativo(request):
    resultados = []
    palabra_clave = ""
    
    if request.method == 'POST':
        palabra_clave = request.POST.get('palabra_clave', '').strip()
        email_destino = request.POST.get('email_destino', request.user.email)
        accion = request.POST.get('accion', 'buscar')
        
        print(f"🔍 Búsqueda iniciada: '{palabra_clave}'")
        
        if palabra_clave:
            try:
                # Usar API oficial de Wikipedia
                resultados = buscar_wikipedia_api(palabra_clave)
                print(f"✅ Resultados encontrados: {len(resultados)}")
                
                if not resultados:
                    messages.warning(request, f'No se encontraron resultados para: "{palabra_clave}"')
                else:
                    messages.success(request, f'Se encontraron {len(resultados)} resultados para: "{palabra_clave}"')
                
                # Enviar por correo si se solicita
                if accion == 'enviar' and resultados and email_destino:
                    print(f"📧 Enviando email a: {email_destino}")
                    if enviar_resultados_email(resultados, palabra_clave, email_destino):
                        messages.success(request, f'Resultados enviados exitosamente a {email_destino}')
                    else:
                        messages.error(request, 'Error al enviar el correo')
                        
            except Exception as e:
                print(f"❌ Error en búsqueda: {str(e)}")
                messages.error(request, f'Error en la búsqueda: {str(e)}')
        else:
            messages.error(request, 'Por favor ingresa una palabra clave')
    
    return render(request, 'scraper/scraper.html', {
        'resultados': resultados,
        'palabra_clave': palabra_clave,
        'user': request.user
    })

def buscar_wikipedia_api(palabra_clave):
    """
    Busca en Wikipedia usando la API oficial de Wikipedia
    """
    resultados = []
    
    try:
        print("🌐 Conectando a Wikipedia API...")
        
        # 1. Primero buscar páginas relacionadas
        search_url = "https://es.wikipedia.org/w/api.php"
        search_params = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srsearch': palabra_clave,
            'srlimit': 5,
            'utf8': 1,
            'srprop': 'snippet'
        }
        
        print(f"📡 Buscando: {palabra_clave}")
        response = requests.get(search_url, params=search_params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            search_results = data.get('query', {}).get('search', [])
            print(f"🔎 Resultados de búsqueda: {len(search_results)}")
            
            for item in search_results:
                page_id = item.get('pageid')
                title = item.get('title')
                snippet = item.get('snippet', '')
                
                if page_id and title:
                    try:
                        # 2. Obtener información detallada de cada página
                        detail_url = "https://es.wikipedia.org/api/rest_v1/page/summary/"
                        page_title = title.replace(' ', '_')
                        
                        print(f"📖 Obteniendo detalles de: {title}")
                        detail_response = requests.get(
                            f"{detail_url}{page_title}",
                            headers={'User-Agent': 'SistemaAlumnos/1.0'},
                            timeout=10
                        )
                        
                        if detail_response.status_code == 200:
                            page_data = detail_response.json()
                            
                            # Extraer información
                            extract = page_data.get('extract', '')
                            if not extract and snippet:
                                extract = snippet
                            
                            # Limpiar HTML del extracto
                            extract = re.sub(r'<[^>]+>', '', extract)
                            if len(extract) > 300:
                                extract = extract[:300] + '...'
                            
                            resultado = {
                                'titulo': page_data.get('title', title),
                                'extracto': extract or 'Descripción no disponible',
                                'url': page_data.get('content_urls', {}).get('desktop', {}).get('page', 
                                      f'https://es.wikipedia.org/wiki/{page_title}'),
                                'tipo': 'Wikipedia',
                                'imagen': page_data.get('thumbnail', {}).get('source', '') if page_data.get('thumbnail') else ''
                            }
                            
                            resultados.append(resultado)
                            print(f"✅ Añadido: {resultado['titulo']}")
                            
                    except Exception as e:
                        print(f"⚠️ Error procesando {title}: {str(e)}")
                        # Si falla, usar solo el snippet
                        resultado = {
                            'titulo': title,
                            'extracto': re.sub(r'<[^>]+>', '', snippet)[:200] + '...' if snippet else 'Descripción no disponible',
                            'url': f'https://es.wikipedia.org/wiki/{title.replace(" ", "_")}',
                            'tipo': 'Wikipedia',
                            'imagen': ''
                        }
                        resultados.append(resultado)
                        continue
        
        # Si no hay resultados de búsqueda, intentar página directa
        if not resultados:
            print("🔄 Intentando obtener página directa...")
            try:
                direct_url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{palabra_clave.replace(' ', '_')}"
                direct_response = requests.get(direct_url, timeout=10)
                
                if direct_response.status_code == 200:
                    direct_data = direct_response.json()
                    
                    extract = direct_data.get('extract', '')
                    extract = re.sub(r'<[^>]+>', '', extract)
                    if len(extract) > 300:
                        extract = extract[:300] + '...'
                    
                    resultado = {
                        'titulo': direct_data.get('title', palabra_clave),
                        'extracto': extract or 'Descripción no disponible',
                        'url': direct_data.get('content_urls', {}).get('desktop', {}).get('page', 
                              f'https://es.wikipedia.org/wiki/{palabra_clave.replace(" ", "_")}'),
                        'tipo': 'Wikipedia',
                        'imagen': direct_data.get('thumbnail', {}).get('source', '') if direct_data.get('thumbnail') else ''
                    }
                    
                    resultados.append(resultado)
                    print(f"✅ Página directa añadida: {resultado['titulo']}")
                    
            except Exception as e:
                print(f"⚠️ Error página directa: {str(e)}")
                
    except requests.exceptions.Timeout:
        print("❌ Timeout en la búsqueda")
        raise Exception("La búsqueda tardó demasiado tiempo. Intenta nuevamente.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {str(e)}")
        raise Exception(f"Error de conexión con Wikipedia: {str(e)}")
    except Exception as e:
        print(f"❌ Error general: {str(e)}")
        raise Exception(f"Error procesando los resultados: {str(e)}")
    
    print(f"🎯 Total resultados: {len(resultados)}")
    return resultados

def enviar_resultados_email(resultados, palabra_clave, email_destino):
    """
    Envía los resultados de búsqueda por correo electrónico
    """
    try:
        print(f"📧 Preparando email para: {email_destino}")
        
        # Crear contenido del correo
        asunto = f'Resultados de Búsqueda Educativa - {palabra_clave}'
        
        # Crear contenido HTML para el email
        contenido_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 20px; }}
                .header {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 25px; border-left: 5px solid #007bff; }}
                .resultado {{ margin: 20px 0; padding: 18px; border: 1px solid #dee2e6; border-radius: 6px; background: #fff; }}
                .titulo {{ color: #007bff; font-weight: bold; font-size: 1.2em; margin-bottom: 10px; }}
                .extracto {{ color: #495057; margin: 10px 0; }}
                .url {{ color: #6c757d; font-size: 0.9em; margin-top: 10px; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 2px solid #e9ecef; color: #6c757d; text-align: center; }}
                .badge {{ background: #28a745; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.8em; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🔍 Resultados de Búsqueda Educativa</h2>
                <p><strong>Término buscado:</strong> <span style="color: #dc3545;">{palabra_clave}</span></p>
                <p><strong>Total de resultados:</strong> <span class="badge">{len(resultados)}</span></p>
                <p><strong>Fuente:</strong> Wikipedia - La enciclopedia libre</p>
                <p><small>Información bajo licencia Creative Commons</small></p>
            </div>
            
            <div class="resultados">
        """
        
        for i, resultado in enumerate(resultados, 1):
            imagen_html = ""
            if resultado.get('imagen'):
                imagen_html = f'<p><img src="{resultado["imagen"]}" alt="Imagen" style="max-width: 200px; border-radius: 5px; margin: 10px 0;"></p>'
            
            contenido_html += f"""
                <div class="resultado">
                    <div class="titulo">{i}. {resultado['titulo']}</div>
                    {imagen_html}
                    <p class="extracto">{resultado['extracto']}</p>
                    <p class="url"><strong>🔗 Enlace:</strong> <a href="{resultado['url']}">{resultado['url']}</a></p>
                    <p><em>Tipo: {resultado['tipo']}</em></p>
                </div>
            """
        
        contenido_html += f"""
            </div>
            
            <div class="footer">
                <p>📅 <strong>Fecha de generación:</strong> {timezone.now().strftime('%d/%m/%Y a las %H:%M')}</p>
                <p>🚀 <strong>Sistema:</strong> Búsqueda Educativa - Sistema de Gestión de Alumnos</p>
                <p>📚 <strong>Fuente de datos:</strong> API oficial de Wikipedia</p>
                <hr style="border: none; border-top: 1px dashed #ccc; margin: 20px 0;">
                <p style="font-size: 0.9em; color: #868e96;">
                    Este correo fue generado automáticamente. Los datos son proporcionados por Wikipedia bajo licencia Creative Commons.
                </p>
            </div>
        </body>
        </html>
        """
        
        # Crear versión texto plano
        contenido_texto = f"═" * 60 + "\n"
        contenido_texto += "RESULTADOS DE BÚSQUEDA EDUCATIVA\n"
        contenido_texto += f"Término buscado: {palabra_clave}\n"
        contenido_texto += f"Total resultados: {len(resultados)}\n"
        contenido_texto += f"Fuente: Wikipedia\n"
        contenido_texto += "═" * 60 + "\n\n"
        
        for i, resultado in enumerate(resultados, 1):
            contenido_texto += f"┌─[{i}] {resultado['titulo']}\n"
            contenido_texto += f"│ {resultado['extracto']}\n"
            contenido_texto += f"│ 🔗 URL: {resultado['url']}\n"
            contenido_texto += f"│ 📄 Tipo: {resultado['tipo']}\n"
            contenido_texto += "└" + "─" * 50 + "\n\n"
        
        contenido_texto += "═" * 60 + "\n"
        contenido_texto += f"Fecha de generación: {timezone.now().strftime('%d/%m/%Y %H:%M')}\n"
        contenido_texto += "Sistema de Búsqueda Educativa\n"
        contenido_texto += "Datos proporcionados por Wikipedia API\n"
        contenido_texto += "═" * 60
        
        # Enviar email
        email = EmailMessage(
            asunto,
            contenido_texto,
            settings.DEFAULT_FROM_EMAIL,
            [email_destino],
        )
        
        # Agregar versión HTML
        email.content_subtype = "html"
        email.body = contenido_html
        
        email.send()
        print("✅ Email enviado exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error enviando email: {str(e)}")
        return False