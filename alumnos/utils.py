from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from django.core.mail import EmailMessage
from django.conf import settings
import os

def generar_pdf_alumno(alumno, email_destino):
    """
    Genera un PDF con los datos del alumno y lo envía por correo
    """
    try:
        # Crear buffer para el PDF
        buffer = BytesIO()
        
        # Crear documento
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch, bottomMargin=1*inch)
        styles = getSampleStyleSheet()
        
        # Crear estilos personalizados
        titulo_style = ParagraphStyle(
            'Titulo',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER
        )
        
        subtitulo_style = ParagraphStyle(
            'Subtitulo',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=12,
            textColor=colors.HexColor('#34495e'),
            alignment=TA_LEFT
        )
        
        normal_style = styles['Normal']
        
        # Contenido del PDF
        contenido = []
        
        # Encabezado
        contenido.append(Paragraph("FICHA DEL ALUMNO", titulo_style))
        contenido.append(Spacer(1, 20))
        
        # Información personal
        contenido.append(Paragraph("INFORMACIÓN PERSONAL", subtitulo_style))
        
        # Tabla de datos personales
        datos_personales = [
            ['<b>Nombre:</b>', alumno.nombre],
            ['<b>Apellido:</b>', alumno.apellido],
            ['<b>DNI:</b>', alumno.dni],
            ['<b>Clase:</b>', alumno.clase_completa],
            ['<b>Fecha de Registro:</b>', alumno.fecha_creacion.strftime('%d/%m/%Y')],
        ]
        
        tabla_personal = Table(datos_personales, colWidths=[2*inch, 4*inch])
        tabla_personal.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
        ]))
        
        contenido.append(tabla_personal)
        contenido.append(Spacer(1, 20))
        
        # Información académica
        contenido.append(Paragraph("INFORMACIÓN ACADÉMICA", subtitulo_style))
        
        datos_academicos = [
            ['<b>Año:</b>', alumno.get_anio_display()],
            ['<b>División:</b>', alumno.get_division_display()],
            ['<b>Estado:</b>', 'Activo'],
        ]
        
        tabla_academica = Table(datos_academicos, colWidths=[2*inch, 4*inch])
        tabla_academica.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
        ]))
        
        contenido.append(tabla_academica)
        contenido.append(Spacer(1, 30))
        
        # Pie de página
        contenido.append(Paragraph(
            "<i>Este documento fue generado automáticamente por el Sistema de Gestión de Alumnos.</i>", 
            styles['Italic']
        ))
        
        # Construir PDF
        doc.build(contenido)
        
        # Obtener contenido del PDF
        pdf_content = buffer.getvalue()
        buffer.close()
        
        # Enviar por correo
        enviar_pdf_por_correo(alumno, pdf_content, email_destino)
        return True
        
    except Exception as e:
        print(f"Error generando PDF: {str(e)}")
        return False

def enviar_pdf_por_correo(alumno, pdf_content, email_destino):
    """
    Envía el PDF por correo electrónico
    """
    try:
        # Crear asunto y mensaje
        asunto = f'Ficha del Alumno - {alumno.nombre_completo}'
        mensaje = f"""
        Hola,
        
        Adjunto encontrará la ficha del alumno {alumno.nombre_completo}.
        
        Información del alumno:
        - Nombre: {alumno.nombre} {alumno.apellido}
        - DNI: {alumno.dni}
        - Clase: {alumno.clase_completa}
        - Fecha de registro: {alumno.fecha_creacion.strftime('%d/%m/%Y')}
        
        Este documento fue generado automáticamente por el Sistema de Gestión de Alumnos.
        
        Saludos cordiales,
        Sistema de Gestión de Alumnos
        """
        
        # Crear email
        email = EmailMessage(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [email_destino],
        )
        
        # Adjuntar PDF
        nombre_archivo = f"ficha_alumno_{alumno.nombre}_{alumno.apellido}.pdf".replace(" ", "_")
        email.attach(nombre_archivo, pdf_content, 'application/pdf')
        
        # Enviar email
        email.send()
        
    except Exception as e:
        print(f"Error enviando email: {str(e)}")
        raise e