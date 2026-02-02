# Accountable Justice Lab 

## Members

- {Jimena Gómez <jimenagomez@uchicago.edu>} 
- {Daniela Avayu <davayu@uchicago.edu>}
- {Maria Fernanda Muñoz <mfmunoz@uchicago.edu>}

## Abstract

Our project focuses on metrics related to Mexico’s Supreme Court, with special emphasis on its justices. We will approach these metrics from two perspectives: transparency and access to public information and “judicial content production”. The second perspective (transparency and access to public information) will examine two elements. The first, corresponds to requests of information addressed to the Supreme Court, which we will link to specific topics of interest, but particularly, when directly referencing justices. We will link all requests of public information linked to each of the Supreme Court justices and analyze what kind of information people are most interested in. Additionally, we will also add metrics related to the proportion of responses that fully addressed the requests or those that were discarded (and thus there was not a satisfactory answer). Once again, we will do this both for the Supreme Court as a whole and also for each justice (we will try to do this with as many justices as possible even if they are no longer in office). 

The second element related to transparency and access to justice will link justice’s annual income and asset disclosures, which we will process to identify each of the justice’s education, previous work experience and assets (personal property, real estate, vehicles, etc.). 

For the second perspective (judicial content production), we will build a set of performance and effectiveness indicators, applicable to the Supreme Court as a whole and to each of the justices: number of court cases processed per year, number of rulings passed by unanimity, number of precedents created, and most recurring topics ruled. For this component, we will use the Supreme Court of Justice’s API, which provides access to two sources of information: tesis/jurisprudencia (similar to judicial precedents) and court rulings.

Our objective with this project is to develop a platform that incorporates relevant information regarding performance metrics of the Supreme Court and its justices. We will create a dashboard template applicable to the institution and each judge, which will incorporate both perspectives previously mentioned. 

This is particularly relevant in Mexico’s current institutional context: in 2025, the judicial selection mechanism shifted from a career-based public service system to an electoral model in which all judges are elected by popular vote. Eligibility requirements were lowered, removing mandatory prior judicial experience. We intend for this platform to serve as a foundation for future statistical analyses of the reform’s effect on judicial indicators, such as productivity, independence and quality, and to eventually expand this analysis beyond the Supreme Court to include judges at the federal and local level who have been recently elected. 

*These details can & will change as much as needed over the next few weeks.*

## Preliminary Data Sources

### Data Source #1
Person in charge: María Muñoz

Source URL: https://bicentenario.scjn.gob.mx/repositorio-scjn/

Source Type: Bulk + API
Summary: Last year, the Mexican Supreme Court of Justice released an API for developers to access information regarding tesis and jurisprudencia (legal precedents) and court rulings (i.e. two APIs with different data but same query structure).

For the tesis/jurisprudencia part, the most relevant information is: 
Unique registry number 
Year
Month
Type of the court that emitted the precedent 
Name of the court that emitted the precedent
Subject 
Type of tesis (tesis or jurisprudencia)
Title
Text 

Approximate number of records: 311,033
When filtering for the Supreme Court and 2015-2016 we get around 600 records (this is historical data that includes tesis since the 1930s). Given the reduction of information, we are considering keeping all records for the general trend analysis and keep information from 2015 on regarding topic analysis (we could expand this time frame such that we get robust results and enough variability across justices). 
Approximate number of attributes: 17

For the court ruling part, the most relevant information is:
File number 
Court 
Justice that was assigned to emit the decision
Topic
Court case of origin (the Supreme Court usually reviews lower courts’ decisions)
Court of origin (the Supreme Court usually reviews lower courts’ decisions)
Date of ruling 
Resolutive points 
Justice that actually emitted the decision
Ruling document 
Voting result (unanimous decision, majority, etc.). 

Approximate number of records: 104,901
Approximate number of attributes: 11

Current status: 
We had access to bulk historical data (up until August 2025). We have already processed and integrated this data in one json file as well as individual json files corresponding to each tesis and ruling. We will use this information as the starting point where we will add our API requests for information from August 2025 on. There is one small detail regarding one field’s text that we would like to check with James and see whether it will present issues. 
Both APIs’ structures have been analyzed and preliminary code has been written. We will need to access around 2,000 extra records for this period. We expect the API to be done by Week 5 and completely integrated with historical data (into a unique json per type of information and individual jsons to keep records of the information accessed).

Challenges:
One of our objectives is to reconcile the data contained in the tesis API with court rulings (a tesis consists of a judicial criterion that is produced and extracted from a court ruling). Therefore, we can see which tesis were produced per ruling - although not all rulings have tesis. However, when analyzing the data, we noticed there is one key component in the ruling data structure that would have allowed us to do a clean and complete match between those two sources (tipo de asunto). Because of this, we will try to match them using: file number, justice, date as the primary matching components and identify the percentage of cases we were able to match. 

We have also asked around if it is possible for them to change the API such that we can access this element. 

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

## Data reconciliation plan

Tesis and court rulings: we will match them using file number, justice name and date of ruling. A second layer of matching will aim at finding key unique words in the tesis/ruling summary to verify they refer to the same topic. 
Tesis/court rulings with information requests and asset disclosures: we will extract all information requests that mention justices. For this, we will first extract a list of justices from the tesis and rulings data and then perform a fuzzy match on our json files of requests of information. 

## Project plan 


Weekly Tasks
**Week 5**
- Data source 1: Maria Muñoz
 1) Transform historical data into a unique json file and individual json files (done)
 2) Filter all information to keep only the Supreme Court of Justice’s tesis and rulings from 2015 to August 2025 (done)
 3) Design and execute API requests for remaining information between August 2025 and January 2026 (in process). 
 4) Start exploring and testing matches between tesis and rulings. 

Data source 2: Jimena Gómez
 1) Begin writing code and run n-gram analysis to identify most frequent terms and validate categories to do the following:
 2) Filter requests mentioning Supreme Court justices or the SCJN (names, “Minister”, “Justice”, “SCJN”).
 3) Extract request outcome/status to classify
 4) Compute access-to-information indicators by justice and aggregated
 5) Classify request content using keyword rules
 6) Build yearly counts of requests to identify peaks and time trends

Data source 3: Daniela Avayu 
 1) Analyze multiple PDFs to understand most important data assets and understand differences in information
 2) Do the skeleton code to scrap one PDF
 3) Understand scope: how can this code replicate the process for all PDFs
**Week 6**
Data Analysis and conciliation:
1) Definition of general metrics per data source: each person will be responsible for their data sources. 
2) Data conciliation execution:
  - Connection between tesis and rulings (María Muñoz)
  - Conciliation between justices and requests for public information (María Muñoz and Jimena Gómez)
  - Conciliation between justices and asset disclosures (María Muñoz and Daniela Avayú). 
**Week 7**
- Final definition visualizations and principal insights we would like to show at a general level (Supreme Court of Justice) and individual (justices). 
- Final design of the page’s template. 
**Week 8**
Page design, implementation and execution. 
**Week 9**
Final update of available information. 





