# Accountable justice lab 

## Introduction



## Data

We accessed information from two different types of data sources: 

1. Repositorio de la Suprema Corte de Justicia de la Nación (Mafer)

    ### Sentencias (court rulings)

    This is historical information of court rulings by Mexico's Supreme Court of Justice. 

    ### Tesis (judicial criteria / precedents)
    
    Both types of information had two different forms of accessing. 
    Information pre august: bulk data
    Information post august: API 

2. Plataforma Nacional de Transparencia 

    ### Solicitudes de información (Jimena)
        The solicitudes dataset contains transparency requests submitted to Mexico’s National Transparency Platform requesting information from the Supreme Court of Justice of the Nation (SCJN).
        These requests are obtained from: https://www.plataformadetransparencia.org.mx/Inicio
        The platform allows downloading yearly transparency request records. For this project, the data covers from 2017 to January 2026. Each year must be downloaded separately as a JSON export from the platform.
        

    ### Declaraciones (Dani)
       In data/declaraciones, we used the bulk download option to import CSV files for each quarter.
       Then, the script compiled_dataset.py compiles all of the CSV files into a single dataset and generates an Excel file containing the aggregated information. The script also filters the rows to keep only those corresponding to judges, and saves the filtered dataset in the same folder.
       In total, we compile 7 CSV files, which together contain approximately 9,000 rows. After applying the filter, the resulting dataset contains only 29 rows.
       Next, in the folder processing/declaraciones, we created two scripts: pdf_download_and_layout.py and json_download.py.
       The first script, pdf_download_and_layout.py, loops through the compiled dataset, retrieves the hyperlinks in each row, and generates a PDF layout for each declaration. The second script, json_download.py, loops through the compiled dataset, retrieves the JSONs in the inmbueble column and and generates a JSON for each inmueble declaration. Then with the json_inmuebles_to_excel.py we create an Excel file with all the inmuebles declarations. 
       
## Repository structure

1. data: code to access raw data from our sources. 
    for tesis and jurisprudencia: creation of individual json files for each element. 
    general json and csv to include all information. 
    eliminate empty rows for 
    manual adding of sentencias from API given incorrect structure. We recognize this is a structural problem that would need to be addressed for future updates of the platform. 


2. extraction and cleaning: code to extract relevant information from raw data, join the information and do the cleaning to generate all relevant elements for data processing and visualization. 
    set de ministros y sus nombres estandarizados por tesis y jurisprudencia.
    fuente principal para luego acceder a las solicitudes de inrormación. 
for the ngrams part - file to remove stop words from spanish but also common words in judicial context that are general and do not relate to one specific topic. 

3. processing: code and functions to help us obtain general metrics that will be ingested to the platform 
    functions to get the main visualizations. 
    General structure that can be used. 
        Línea de tiempo
        Proportions 
        Rank line para materias - unique 

ambicioso pero cool: por tema. ver cuántas han subido en proporción.
    5 elementos: género, pueblos y comunidades indígenas, niñas y niños, desca
    penitenciario y personas privadas de la libertad. gráfica para ver cómo ha crecido. 
4. front end: set up for streamlit 

## Objectives and insights 

Página general de la Corte - ver sus performance indicators and general tendencies. Una pestaña particular para la corte. 
    sentencias - tesis
    solicitudes de información (2015-2026) 

Por ministro. Hacer análisis de sus métricas. Aquí tener la posibilidad de hacer comparativo con el promedio. Para la parte de ministro mantener de 2015 a la fecha - información de sus solicitudes de información y así. Considerando que son un total de X ministros - yo creo que han de ser como 15-20 más o menos. 

## Future of the project -> next steps 

