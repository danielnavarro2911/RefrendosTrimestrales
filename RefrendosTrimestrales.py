import PyPDF2
import pandas as pd
import re

class RefrendosTrimestrales:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.reader = PyPDF2.PdfReader(pdf_path)
        self.pdf = {n: page.extract_text() for n, page in enumerate(self.reader.pages, 1)}

    def __extraer_monto_esf(self,pagina):
        '''
        Metodo para extraer todos los montos de ESTADO DE SITUACIÓN FINANCIERA
        '''
        texto=self.pdf[pagina]
        lineas = texto.strip().split('\n')
        lineas = [line.strip() for line in lineas if line.strip() and not re.match(r'^\-?\d+\-?$', line.strip()) and 'Nota' not in line and 'auditado' not in line]

        # Expresión regular para capturar descripción + 3 montos al final
        patron = re.compile(
            r'^(.*?)\s+([\(\)\d\.\-]+)\s+([\(\)\d\.\-]+)\s+([\(\)\d\.\-]+)$'
        )

        # Extraer coincidencias válidas
        datos = []
        for linea in lineas:
            match = patron.search(linea)
            if match:
                descripcion = match.group(1).strip()
                valores = match.group(2), match.group(3), match.group(4)
                datos.append([descripcion] + list(valores))

        # Crear DataFrame
        df = pd.DataFrame(datos, columns=['ACTIVO', 'Monto Actual', 'Trimestre Anterior', 'Anio Pasado'])

        # Limpiar valores numéricos
        def limpiar_valor(v):
            v = v.replace('.', '').replace('(', '-').replace(')', '')
            return float(v) if v != '-' else None

        for col in ['Monto Actual', 'Trimestre Anterior', 'Anio Pasado']:
            df[col] = df[col].apply(limpiar_valor)

        return df
    def extraer_esf(self,paginas=[3,4]):
        df = pd.DataFrame()
        for pagina in paginas:
            df = pd.concat([df, self.__extraer_monto_esf(pagina)])
        df=df.reset_index(drop=True)
        #limpiamos el df
        df['ACTIVO']=df['ACTIVO'].str.replace(r'\b\d+\.[a-zA-Z]\b', '', regex=True).str.strip().str.lower()
        df['ACTIVO'] = df['ACTIVO'].str.replace(r'\b\d+\.[a-zA-Z]{2}\b', '', regex=True).str.strip()
        df['ACTIVO'] = df['ACTIVO'].str.replace(r'/', '').str.strip()
        df['ACTIVO'] = df['ACTIVO'].str.replace('(','').str.replace(')','').str.replace(',','').str.strip()
        df['Total']=df.iloc[:, 1:].sum(axis=1)
        return df

    def __limpiar_notas(self,n):
        #l guarda la pagina y la convertimos en listas separando por \n. asi cada linea es una lista
        l=self.pdf[n].split('\n')
        #eliminamos espacios sobrantes en cada linea
        l=list(map(lambda x: x.strip(), l))
        #traemos solo las filas que coinciden con \d\.[a-zA-Z], es decir, solo las filas que tienen notas 3.a
        l=[row for row in l if re.search(r'\d\.[a-zA-Z]',row)]
        #limpiamos los datos
        l = list(map(lambda x : x.replace(' -',' 0.0').replace(' /','/').replace('/ ','/').strip(),l))
        l = list(map(lambda x : re.sub(r'(\d+\.a)(\d+)', r'\1 \2', x),l))

        return l

    def __extraer_nota_x_pagina(self,n):
        #limpiamos las notas
        l=self.__limpiar_notas(n)

        #convertimos a dataframe
        rows = []
        for item in l:
            #buscamos casos donde la nota aparezca pegada al monto, e introducimos un espacio
            item = re.sub(r'([a-zA-Z]\.[a-zA-Z])(\d)', r'\1 \2', item)
            # Extrae la actividad, la nota, y los montos
            match_ = re.match(r'^(.*?)\s+([0-9.a-zA-Z/]+)\s+([\(\)\d\.\-]+)\s+([\(\)\d\.\-]+)\s+([\(\)\d\.\-]+)$', item.strip())
            if match_:
                #si hay coincidendia guarda los valores
                nombre, notas, valor1, valor2, valor3 = match_.groups()
                rows.append([nombre.strip(), notas.strip(), valor1, valor2, valor3,n])
            else:
                #si no hay coincidendia, intenta para los casos donde solo viene el año actual y el pasado
                match_ = re.match(r'^(.*?)\s+([0-9.a-zA-Z/]+)\s+([\(\)\d\.\-]+)\s+([\(\)\d\.\-]+)$', item.strip())
                if match_:
                    nombre, notas, valor1, valor2 = match_.groups()
                    rows.append([nombre.strip(), notas.strip(), valor1, valor2, 0,n])
                #else:
                    #print(f"No se pudo procesar: {item}")

        # Crear el DataFrame
        return pd.DataFrame(rows, columns=["Actividad", "Notas", "Valor_1", "Valor_2", "Valor_3","Pagina"])

