import pandas as pd

def limpiar_datos_plantilla(df_vic):
    df_vic['ACTIVO']=df_vic['ACTIVO'].str.replace(r'\(\d+\)','',regex=True).str.strip()
    df_vic['ACTIVO']=df_vic['ACTIVO'].str.lower()
    df_vic['ACTIVO'] = df_vic['ACTIVO'].str.replace('(','').str.replace(')','').str.replace(',','').str.strip()
    df_vic['ACTIVO'] = df_vic['ACTIVO'].str.replace(r'\d+(\.\d+)?', '', regex=True).str.replace('+','-').str.replace('-','').str.strip()
    df_vic=df_vic.drop(['Unnamed: 18','Unnamed: 19','Unnamed: 20'],axis=1)

    df_vic[['Unnamed: 21','Unnamed: 22','Unnamed: 23']] = df_vic[['Unnamed: 21','Unnamed: 22','Unnamed: 23']].apply(pd.to_numeric, errors='coerce')
    df_vic['Total']=df_vic.iloc[:, 1:].sum(axis=1)
    return df_vic
