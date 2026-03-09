# Accountable Justice Lab 

## Members

- {Jimena Gómez <jimenagomez@uchicago.edu>} 
- {Daniela Avayu <davayu@uchicago.edu>}
- {Maria Fernanda Muñoz <mfmunoz@uchicago.edu>}

## Abstract

Our project focuses on metrics related to Mexico’s Supreme Court, with special emphasis on its justices. We have approached these metrics from two perspectives: transparency and access to public information and “judicial content production”. The first perspective (transparency and access to public information) will examine two elements. The first, corresponds to requests of information addressed to the Supreme Court, which we have linked to specific topics of interest, but particularly, when directly referencing justices. We analyze requests of public information, with an emphasis on mentions to justices, and a salient word analysis of the requests that mention each justice. Additionally, we added an index of no response to the requests; the no response is understood as no informatión delivered from the institution to the citizen making the request. The second element related to transparency and access to justice will link justice’s annual income and asset disclosures, which we will process to identify each of the justice’s education, previous work experience and assets (personal property, real estate, vehicles, etc.). 

For the second perspective (judicial content production), we generated a set of charts that identify trends and patterns for both court rulings (sentencias) and judicial precedents (tesis). In the case of rulings, one particular element of interest was the integrity of the data: we noticed there was a big difference between historical information and recent dates, which we believe is a valuable insight in itself, as it allows researchers and people to understand how reliable and complete the data is depending on the year of analysis. In addition to this, we have added charts related to total rulings and tesis emitted through the years, classifying by type, voting result. To complement the quantitative metrics, we have added a topic analysis component, that identifies the most mentioned words or set of words in the title of tesis (which we know have relevant legal content).

Although the official name of our project is "Accountable Justice Lab", the name of our platform is "Ojo Piojo". This is a popular Chilean phrase that hints at being alert. We wanted a playful name because we believe the intersection of data analysis and social change needs an element of fun, creativity and playfulness - we believe this is how we find things out of the ordinary. 

## Data

This project combines data from two primary sources.

1. Repositorio de la Suprema Corte de Justicia de la Nación

    ### Sentencias (court rulings)

    This is historical information of court rulings by Mexico's Supreme Court of Justice. 

    ### Tesis (judicial criteria / precedents)
    
    Both types of information had two different forms of accessing. 
    Information pre august: bulk data
    Information post august: API 

2. Plataforma Nacional de Transparencia: https://www.plataformadetransparencia

    ### Solicitudes de información (Jimena)
        The solicitudes dataset contains transparency requests submitted to Mexico’s National Transparency Platform requesting information from the Supreme Court of Justice of the Nation (SCJN). The platform allows downloading yearly transparency request records. For this project, the data covers from 2017 to January 2026. Each year must be downloaded separately as a JSON export from the platform.
        
        The main issue with this dataset is that the raw requests files (solicitudes) cannot be parsed because some records contained malformed or broken JSON, especially quotes and commas. 

    ### Declaraciones (Dani)
       The declaraciones(disclosures) are retrieved by bulk downloading CSV files for each quarter. Then, the script compiled_dataset.py compiles all of the CSV files into a single dataset and generates an Excel file containing the aggregated information. The script also filters the rows to keep only those corresponding to judges, and saves the filtered dataset. In total, we compile 7 CSV files, which together contain approximately 9,000 rows. After applying the filter, the resulting dataset contains only 29 rows, that represent information of 13 judges.

    This data source presents several limitations:
    1) Incompleteness: Most PDFs are not completed full. We do not have information about asset declaration of all judges, for examples.  
    2) There is no historical information, we ust have information of 2025 and 2026.
    3) The PDFs are similar but no identical in content/structure. 
    
       
## Repository structure

1. Data: Divided into raw/ clean /visualization. 

raw_data: Original files downloaded from external sources
clean_data: Processed datasets used for analysis
viz_dev: Intermediate files used for visualization development

2. SRC
Contains the actual source code of  project and contains 4 four sub folders. 
a) Analysis: Data processed used to the visualizations. 
b) Cleaning_and_processing: Data is processed.
c) App: The Streamlit application that powers the interactive dashboard.
d) Extraction: Data is extracted from multiple sources. 

3. Tests: Contains simple validation tests for the three main datasets.

## Objectives and insights 

The application aims to provide insights into the performance and activity of the Supreme Court through two main perspectives.

First, it presents a general overview of the Court, highlighting key performance indicators and long-term trends. These include the volume and evolution of court rulings (sentencias), judicial precedents (tesis), and information requests between 2015 and 2026. This perspective focuses on identifying institutional patterns and changes over time.

Second, the application provides a justice-level analysis, allowing users to explore metrics associated with individual justices. For each justice, users can examine indicators such as transparency requests referencing them, asset declarations, and other available information. The analysis spans 2015 to the present, enabling comparisons across the approximately 15–20 justices that compose the Court.

## How to run code

Requirements:
* Python 3.13.7
* uv
* Streamlit

Installation:
Clone the repository: 
git clone https://github.com/your-repository/project-accountable-justice-lab.git
cd project-accountable-justice-lab
Create the environment and install dependencies: uv sync
Run the application: streamlit run src/app/app.py

## Future of the project -> next steps 
Potential extensions of this project include:
* Expanding the historical coverage of asset declarations
* Improving automatic PDF parsing and extraction accuracy
* Developing additional transparency metrics, such as response time to information requests
* Conducting topic analysis by policy areas, such as gender, childhood, equality and        non-discrimination, economic, social and environmental rights, and Indigenous rights, in order to identify how specific subtopics within these areas have evolved over time.

## Link to project video


