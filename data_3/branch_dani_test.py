#Sirve para abrir PDFs y extraer data dentro
import pdfplumber
import pandas as pd

#Sirve para expresiones regular, claves para buscar patrones de texto dentro del PDF
import re

#La función recibe la ruta del pdf. Los datos finales seran un dict que traiga como llave cada columna y value sera el valor del titulo. 
def extraer_todo_el_pdf(pdf_path):
    datos_finales = {}
    
    #Abre pdf
    with pdfplumber.open(pdf_path) as pdf:
        content = ""
        #Recorre las paginas y extrae los textos y queda todo en content
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                content += text + "\n"

    # 1. Definimos los campos que queremos buscar basados en las etiquetas del PDF
    # Lo hice solo para algunos de la primera pagina. No se que hacer con columnas que son iguales. 
    etiquetas = [
        ("nombre", r"NOMBRE\(S\)\s+(.*)"),
        ("primer_apellido", r"PRIMER APELLIDO\s+(.*)"),
        ("segundo_apellido", r"SEGUNDO APELLIDO\s+(.*)"),
        ("correo_electronico", r"CORREO ELECTRÓNICO INSTITUCIONAL\s+(.*)"),
        ("nivel_escolaridad", r"nivel\s+(.*)"),
        ("estatus_escolaridad", r"estatus\s+(.*)"),
        ("documento_obtenido", r"DOCUMENTO OBTENIDO\s+(.*)"),
        ("institucion_educativa", r"INSTITUCIÓN EDUCATIVA\s+(.*)"),
        ("carrera", r"CARRERA O ÁREA DE CONOCIMIENTO\s+(.*)"),
        ("fecha_titulo", r"FECHA DE OBTENCIÓN.*?(\d{2}/\d{2}/\d{4})"),
        ("locacion_institucion_educativa", r"LUGAR DONDE SE UBICA LA INSTITUCIÓN EDUCATIVA.*?(\d{2}/\d{2}/\d{4})"),
        
        ("nivel_gobierno", r"NIVEL / ORDEN DE GOBIERNO.*?(\d{2}/\d{2}/\d{4})"),
        ("ambito_publico", r"ÁMBITO PÚBLICO.*?(\d{2}/\d{2}/\d{4})"),
        ("fecha_de_ingreso", r"FECHA DE INGRESO.*?(\d{2}/\d{2}/\d{4})"),
        ("fecha_de_egreso", r"FECHA DE EGRESO.*?(\d{2}/\d{2}/\d{4})"),
        ("remuneración", r"I. REMUNERACIÓN NETA DEL AÑO EN CURSO A LA FECHA DE CONCLUSIÓN DEL EMPLEO, CARGO O COMISIÓN DEL DECLARANTE POR SU CARGO PÚBLICO (POR CONCEPTO DE SUELDOS, HONORARIOS, COMPENSACIONES, BONOS Y OTRAS PRESTACIONES)(CANTIDADES NETAS DESPUÉS DE IMPUESTOS).*?(\d{2}/\d{2}/\d{4})")
    ]

    # 2. Extraer campos simples usando Regex
    for columna, patron in etiquetas:
        match = re.search(patron, content, re.IGNORECASE)
        datos_finales[columna] = match.group(1).strip() if match else "N/A"

    # 3. Extraer Adeudos (Maneja múltiples deudas) - esto es para los campos que se repiten tipo titulo, marca de auto
    bloques_adeudos = re.findall(r"TIPO DE ADEUDO\s+(.*?)\n.*?TITULAR.*?OTORGANTE\n.*?NOMBRE.*?\n(.*?)\n.*?MONTO ORIGINAL.*?([\d,]+)\s+MXN", content, re.DOTALL)
    for i, adu in enumerate(bloques_adeudos, 1):
        datos_finales[f"Adeudo_{i}_Tipo"] = adu[0].strip()
        datos_finales[f"Adeudo_{i}_Institucion"] = adu[1].strip()
        datos_finales[f"Adeudo_{i}_Monto"] = adu[2].strip()

    return datos_finales

# --- EJECUCIÓN ---
try:
    print("Iniciando extracción de 1.pdf...")
    registro = extraer_todo_el_pdf("1.pdf")
    
    # Creamos el DataFrame
    df = pd.DataFrame([registro])
    
    # Guardamos en CSV
    output_name = "extraccion_completa_1.csv"
    df.to_csv(output_name, index=False, encoding='utf-8-sig')
    
    print(f"¡Éxito! Se ha creado '{output_name}' con {len(df.columns)} columnas extraídas.")
    print("\nColumnas generadas:")
    print(df.columns.tolist())

except Exception as e:
    print(f"Hubo un error: {e}")