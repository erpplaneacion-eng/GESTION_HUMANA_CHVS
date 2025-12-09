import pandas as pd
import os

file_path = 'gestion_humana/basedatosaquicali/archivos_excel/link.xlsx'

try:
    # Leer el archivo Excel
    xls = pd.ExcelFile(file_path) 
    
    print(f"Hojas encontradas: {xls.sheet_names}")
    print("-" * 50)
    
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name, nrows=0)  # Solo leer encabezados
        print(f"\nHOJA: {sheet_name}")
        print(f"Columnas: {list(df.columns)}")

except Exception as e:
    print(f"Error leyendo el archivo: {e}")
