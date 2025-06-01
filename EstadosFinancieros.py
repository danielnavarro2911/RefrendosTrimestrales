class EstadosFinancieros:
    def __init__(self,ruta_estados_financieros) -> None:

        '''
        Clase para cargar los datos de los estados financieros que da finanzas
        Primero se debe identificar cada hoja de los excels, para esto se usa el metodo identificar_hoja
        luego, cargamos los datos con el metodo cargar_excel

        Limpiamos los datos con limpiar_datos
        '''

        self.ruta_estados_financieros=ruta_estados_financieros
        self.excels = os.listdir(self.ruta_estados_financieros)

    def identificar_hojas(self):
        resultados = {}
        for excel in self.excels:
            resultados[excel] = {}
            if excel.endswith('.xlsx') or excel.endswith('.xlsm'):
                #identificamos las hojas visibles
                wb = load_workbook(self.ruta_estados_financieros+excel, read_only=True)
                hojas_visibles = [sheet.title for sheet in wb.worksheets if sheet.sheet_state == 'visible']
                #una vez tenemos las hojas visibles, buscamos las hojas de ESF, ER, CP
                for sheet in ["ESTADO DE SITUACION FINANCIERA","ESTADO DE RESULTADOS","CAMBIOS EN EL PATRIMONIO"]:
                    for hoja in hojas_visibles:
                        df = pd.read_excel(self.ruta_estados_financieros+excel,sheet_name=hoja).to_string().upper()
                        if sheet in df.replace('Ó','O'):
                            resultados[excel][sheet]=hoja
                            print(excel,hoja)
                            break
            else:
                #proceso manual para los archivos xls
                for sheet in ["ESTADO DE SITUACION FINANCIERA","ESTADO DE RESULTADOS","CAMBIOS EN EL PATRIMONIO"]:
                    resultados[excel][sheet]=input(f'hoja de {sheet} de {excel} ')
        return resultados
    
    def cargar_excel(self,excel,sheet):
        df = pd.read_excel(self.ruta_estados_financieros+excel,sheet_name=sheet)

        return df

    def limpiar_datos(self,df):

        '''
        Una vez cargado los datos, elimina todas las filas y columnas no importantes
        Dejando solo los datos de los estados financieros
        '''

        #Encontramos las filas de 'ACTIVO' para los estados situacion o 'INGRESOS FINANCIEROS' para los estados de resultados
        found = False
        for c in range(len(df.columns)):
            if found:
                break
            for r in df.index:
                if 'ACTIVO' == str(df.iloc[r,c]).upper().replace('S','') or 'INGRESOS FINANCIEROS' in str(df.iloc[r,c]).upper():
                    found = True
                    row = r-3
                    col = c
                    break
        #Encontramos las columnas con los datos del trimestre actual usando el anio actual
        df=df.iloc[row:,col:].reset_index(drop=True)
        found = False
        for r in df.index:
            if found:
                break
            for c in range(len(df.columns)):
            
                if str(datetime.now().year) in str(df.iloc[r,c]):
                    found = True
                    row = r
                
                    break
        #quitamos las filas sin importancia
        df=df.iloc[row:,:].reset_index(drop=True)
        #llenamos todos los valores vacios con 0
        df=df.fillna(0)
        #la primera fila la convertimos en el header
        df.columns = df.iloc[0].values
        df=df.drop(0)
        #dropeamos todas las filas que son solo de ceros
        df = df[~(df == 0).all(axis=1)].reset_index(drop=True)

        #en caso de que el estado situacion venga en dos columnas
        for num,col in enumerate(df.iloc[0].values):
            if 'PASIVO' in str(col).upper():
                df.columns.values[num]='Cuenta2'
                break
    
        df.columns.values[0]='Cuenta'
        # Encuentra las posiciones de las columnas con nomb re 0
        cols_a_eliminar  = [i for i, col in enumerate(df.columns) if col == 0]

 

        # Elimina las columnas que tienen un cero en el header
        df = df.drop(columns=df.columns[cols_a_eliminar])
        try: df = df.drop('Nota',axis = 1)
        except: pass

        columns = list(df.columns)
        #si el estado situacion estaba en 2 columnas, las convertimos a una
        if 'Cuenta2' in columns:
            temp = df.iloc[:,list(df.columns).index('Cuenta2'):]
            df = df.iloc[:,:list(df.columns).index('Cuenta2')]

            temp = temp.rename(columns={'Cuenta2':'Cuenta'})

            df = pd.concat([df,temp])
        #convertimos a numerico y damos formato al texto de cuenta
        df.iloc[:,1:]=df.iloc[:,1:].apply(pd.to_numeric, errors='coerce')

        df['Cuenta']=df['Cuenta'].str.replace(r'\b\d+\.[a-zA-Z]\b', '', regex=True).str.strip().str.lower()
        df['Cuenta'] = df['Cuenta'].str.replace(r'\b\d+\.[a-zA-Z]{2}\b', '', regex=True).str.strip()
        df['Cuenta'] = df['Cuenta'].str.replace(r'/', '').str.strip()
        df['Cuenta'] = df['Cuenta'].str.replace('(','').str.replace(')','').str.replace(',','').str.strip()
        df.columns = ['Cuenta','Monto Actual','Trimestre Anterior','Anio Pasado']
        df['Total']=df.iloc[:, 1:].sum(axis=1)

        return df

    



