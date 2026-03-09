# Accountable Justice Lab 

## Data Sources

Almost all of our datasources are available in the data folder,* all classified by: 
raw_data: data extracted from original sources
cleaned_data
viz_data 


* This is not the case of the csv files of "Sentencia.csv" and "Tesis.csv", due to their size. A link to the Drive where the information is stored is available in the README. 

### Data Source #1: Sentencias (rulings) and Tesis (precedents)
Person in charge: María Muñoz

Source URL: https://bicentenario.scjn.gob.mx/repositorio-scjn/

Source Type: Bulk + API

Description: 

1. Sentencias (rulings): information related to rulings emitted by the Supreme Court of Justice. 

Two main sources: 

- "Sentencia.csv": this is a csv file obtained directly from the Supreme Court of Justice that contains all of the rulings' historical information until August 2025.
- Engroses API: engroses is another way of saying "final draft of the rulings". The Supreme Court has an API endpoint that lists all of the ruling ids and another one that allows you to access each ruling (through its id) directly. 

For rulings, the most relevant information used is: 
File number 
Court 
Justice that was assigned to emit the decision
Date of ruling 
Justice that actually emitted the decision
Voting result (unanimous decision, majority, etc.)

Although these are not all of the fields, these are the ones used in our analysis. 

Approximate number of records: 104,901

Challenges: 

There a few challenges related to both the CSV file and the API. First, when the CSV file was read into a pandas dataframe, we notices some file numbers that usually follow the structure 'number/year" were converted to dates in the Supreme Court's excel system and thus was left that way in csv format. Additionally, some dates were incomplete or did not have the correct date structure. To clean this up, we extracted the year contained in the file number to attempt at having more information. We also noticed a big gap between information contained in older rulings than new ones.

For the API, unlike the tesis API, ruling ids are not progressive and therefore we could not be certain that a higher id meant a more recent ruling. This limited our ability to use the same structure of accessing the API and each of the records. With this, we also noticed that not all of the information provided in the CSV is contained in the fields of the json files in the API. We have already asked the Supreme Court for an update so we can have more homogeneous data. 

The most important challenge, however, is the fact that the Supreme Court has not updated its rulings API in 2026. We believe this is cause for concern and will continue monitoring to verify this information is updated soon. 

2. Tesis (judicial precedents)

Two main sources:
- "Tesis.csv": this is a csv file obtained directly from the Supreme Court of Justice that contains all of the tesis' historical information until August 2025.
- Tesis API: the Supreme Court has an API endpoint that lists all of the tesis ids and another one that allows you to access each tesis (through its id) directly. 

This datasource was more standarized. However, more data extraction was needed for this dataset. This is mainly because the column "precedents", which is unstructured text, had relevant information regarding the justice that emitted the tesis and the voting result. We therefore had to use several regex match functions to extract this information. Because the edge cases were identifiable, we decided to address them directly in our code. While we know this is not scalable, for the purposes of this project, this helped us with precision. 



### Data Source #2
Person in charge: Jimena Gómez
Source URL: https://www.plataformadetransparencia.org.mx/datos-abiertos

Source Type: Bulk data 

Summary: The Plataforma Nacional de Transparencia contains information regarding all public entities legally obligated to disclose public information regarding their operation and their staff (including the Supreme Court Justice’s). Within this platform, we can find relevant information such as asset and conflict of interest disclosures, income, curriculum and requests of information made by the public. We believe that this platform can be a valuable addition to our primary source of information, as it will help complement the justice’s profiles. Our primary focus will be the asset and conflict of interest disclosures, although we would also like to analyze requests of information and link those related to the justices so we can also identify what people are asking about them. 

Challenges:
Design of the web scraper for making periodic JSON queries.
Define up to which year we want to go. Transparency-related data started in 2015, so that could be a good starting point—assuming the platform allows it.

### Data Source #3
Person in charge: Daniela Avayú
Source URL: https://www.plataformadetransparencia.org.mx/datos-abiertos

Source Type: Bulk data 

Summary: As an additional component, we would like to extract justice’s asset and conflict of interest disclosures. This information will help us build a more robust profile of the justices. Our main aim is to extract information regarding their education, previous professional experience, as well as real estate, property, vehicles and their salaries. 

For the asset disclosure part, the most relevant information is:
Name and lastname
Level of education (all possible)
Institution of education (all possible)
Graduation date (all possible)
Employment level
Job title
Job experience (last five employments)
Salary
Was a public servant last year? (binary variable)
Other income
Vehicle: type, model, brand, cost
Number of investments (we have the investments people own but not the amount)
Liabilities (?)


Challenges:
When we download the information, we get a CSV with independent PDFs per judge. We then have to scrap each PDF.
Each PDF, although has the same overall structure, can be different in number of pages, categories and other components.
There is only information for 2024 and 2025 (up till Q3). We have Q1 2024,Q2 2024, Q3 2024, Q1 2025, Q2 2025, and Q3 2025. We have to combine them and understand if they are initial declarations, regular, or ending declarations.  
Design web scrapping code to extract information from PDF (which we have not done before). Also, not all the PDFs are the same and have similar titles for categories. Salary is in a category different from the other categories. 


## Project structure

Modules: 

1. Extraction

Sentencias: in this part of the process, ruling information from the CSV file of 

Tesis: 

Declaraciones: 

2. Cleaning and processing

join and extract data from csv files to add new fields relevant

3. Analysis

chart and table creation
ngrams

4. APP

## Team responsibilities 

María Muñoz: sentencias and tesis data sources pipeline: 
        src/extraction/tesis
        src/extraction/sentencias
        src/cleaning_and_processing/tesis
        src/cleaning_and_processing/sentencias
        src/analysis/sentencias
        src/analysis/tesis*

* the ngrams code was adapted from Jimena's code on ngram analysis for the solicitudes part. 

Jimena Gómez: solicitudes data source pipeline (for this data source there is no extraction component)
        src/cleaning_and_processing/solicitudes
        src/analysis/solicitudes

Daniela Avayú:
        src/cleaning_and_processing/declaraciones
        src/analysis/declaraciones

app.py. Joint - more intense Daniela and Jimena 

## Final thoughts 

We were aware this was going to be a challenging project. We knew the information was not readily available and that a lot of processing had to be done.
Challenging due to two reasons: 
1. structure of data 
2. type of analysis: the richness in our data lies in text extraction and analysis. We knew this would be a limitation but are proud of the analyses we were able to accomplish. We are also eager to explore what is next and to use this dataset and information to make the best of natural language processing tools and general text analysis and visualization. 

