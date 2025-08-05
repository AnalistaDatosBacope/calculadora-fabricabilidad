#!/usr/bin/env python3
"""
Script de verificación de visibilidad de títulos
Verifica que los estilos se estén aplicando correctamente
"""

import requests
from bs4 import BeautifulSoup
import re

def test_visibility_fix():
    """Prueba la aplicación de los estilos de visibilidad"""
    
    print("🔍 Verificando aplicación de estilos de visibilidad...")
    
    # URL de la aplicación
    url = "https://calculadora-fabricabilidad.onrender.com/"
    
    try:
        # Hacer request a la página
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Parsear el HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Verificar elementos específicos
        issues_found = []
        
        # 1. Verificar título principal
        main_title = soup.find('h1', class_='h5')
        if main_title:
            print(f"✅ Título principal encontrado: {main_title.get_text().strip()}")
            if 'style=' in str(main_title):
                print("✅ Estilos inline aplicados al título principal")
            else:
                issues_found.append("❌ Título principal sin estilos inline")
        else:
            issues_found.append("❌ Título principal no encontrado")
        
        # 2. Verificar CSS cargado
        css_links = soup.find_all('link', rel='stylesheet')
        css_loaded = False
        for link in css_links:
            if 'style.css' in link.get('href', ''):
                css_loaded = True
                print(f"✅ CSS cargado: {link.get('href')}")
                break
        
        if not css_loaded:
            issues_found.append("❌ CSS no encontrado")
        
        # 3. Verificar estilos en head
        head_styles = soup.find('style')
        if head_styles:
            print("✅ Estilos en head encontrados")
            style_content = str(head_styles)
            if 'animated-text' in style_content and '!important' in style_content:
                print("✅ Estilos específicos para animated-text encontrados")
            else:
                issues_found.append("❌ Estilos específicos no encontrados en head")
        else:
            issues_found.append("❌ No hay estilos en head")
        
        # 4. Verificar elementos del sidebar
        sidebar_elements = soup.find_all(class_=re.compile(r'text-uppercase|animated-text'))
        if sidebar_elements:
            print(f"✅ {len(sidebar_elements)} elementos del sidebar encontrados")
            for elem in sidebar_elements:
                if 'style=' in str(elem):
                    print(f"✅ Elemento con estilos inline: {elem.get_text().strip()}")
                else:
                    issues_found.append(f"❌ Elemento sin estilos: {elem.get_text().strip()}")
        else:
            issues_found.append("❌ No se encontraron elementos del sidebar")
        
        # 5. Verificar versión del CSS
        if 'v=4.1' in response.text:
            print("✅ Versión CSS 4.1 detectada")
        else:
            issues_found.append("❌ Versión CSS 4.1 no detectada")
        
        # Resumen
        print("\n📊 RESUMEN DE VERIFICACIÓN:")
        if issues_found:
            print("❌ PROBLEMAS ENCONTRADOS:")
            for issue in issues_found:
                print(f"  {issue}")
        else:
            print("✅ TODOS LOS ELEMENTOS VERIFICADOS CORRECTAMENTE")
        
        print(f"\n🌐 URL verificada: {url}")
        print("💡 Si los problemas persisten, intenta:")
        print("   1. Limpiar caché del navegador (Ctrl+F5)")
        print("   2. Abrir en modo incógnito")
        print("   3. Esperar 2-3 minutos para que Render.com actualice")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al conectar con la aplicación: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_visibility_fix() 