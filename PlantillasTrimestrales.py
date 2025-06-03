import os
import pandas as pd

class PlantillasTrimestrales:
    '''
    Clase para cargar datos de plantillas de victor
    '''
    def __init__(self,ruta_plantillas):
        self.ruta_plantillas = ruta_plantillas 
        self.excels =os.listdir(ruta_plantillas)
    def cargar_datos_plantilla(self,subsidiaria,sheet):
        plantilla = [i for i in self.excels if subsidiaria in i][0]
        plantilla_path=self.ruta_plantillas+plantilla

        usecols = 'R:X' if sheet == 'SF' else 'T:AB'
        skiprows = 38 if sheet == 'SF' else 39

        df_vic=pd.read_excel(plantilla_path,sheet_name=sheet,skiprows=skiprows,usecols=usecols)
        df_vic=self.__limpiar_datos_plantilla(df_vic,sheet)

        return df_vic

    def __limpiar_datos_plantilla(self, df_vic,sheet):
        df_vic.iloc[:,0]=df_vic.iloc[:,0].str.replace(r'\(\d+\)','',regex=True).str.strip()
        df_vic.iloc[:,0]=df_vic.iloc[:,0].str.lower().str.replace('.m','').str.replace('.','')
        df_vic.iloc[:,0] = df_vic.iloc[:,0].str.replace('(','').str.replace(')','').str.replace(',','').str.strip()
        df_vic.iloc[:,0] = df_vic.iloc[:,0].str.replace(r'\d+(\.\d+)?', '', regex=True).str.replace('+','-').str.replace('-','').str.strip()
        if sheet == 'SF':
            '''
            df_vic['ACTIVO']=df_vic['ACTIVO'].str.replace(r'\(\d+\)','',regex=True).str.strip()
            df_vic['ACTIVO']=df_vic['ACTIVO'].str.lower()
            df_vic['ACTIVO'] = df_vic['ACTIVO'].str.replace('(','').str.replace(')','').str.replace(',','').str.strip()
            df_vic['ACTIVO'] = df_vic['ACTIVO'].str.replace(r'\d+(\.\d+)?', '', regex=True).str.replace('+','-').str.replace('-','').str.strip()
            '''
            df_vic=df_vic.drop(['Unnamed: 18','Unnamed: 19','Unnamed: 20'],axis=1)
            df_vic.iloc[:,[1,2,3]] = df_vic.iloc[:,[1,2,3]].apply(pd.to_numeric, errors='coerce')

            #df_vic[['Unnamed: 21','Unnamed: 22','Unnamed: 23']] = df_vic[['Unnamed: 21','Unnamed: 22','Unnamed: 23']].apply(pd.to_numeric, errors='coerce')
            
        if sheet == 'ER':
            #df_vic=df_vic.drop(['Unnamed: 20','Unnamed: 21','Unnamed: 22','Unnamed: 24'],axis=1)
            df_vic = df_vic[['Unnamed: 19','Unnamed: 23','Unnamed: 25']]
            df_vic.iloc[:,[1,2]] = df_vic.iloc[:,[1,2]].apply(pd.to_numeric, errors='coerce')
        
        
        df_vic['Total']=df_vic.iloc[:, 1:].sum(axis=1)

        return df_vic
