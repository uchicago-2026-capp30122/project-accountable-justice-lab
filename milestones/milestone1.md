# Accountable Justice Lab 

## Members

- {Jimena Gómez <jimenagomez@uchicago.edu>} 
- {Daniela Avayu <davayu@uchicago.edu>}
- {Maria Fernanda Muñoz <mfmunoz@uchicago.edu>}

## Abstract

Our project focuses on an analysis of Mexico’s Supreme Court Justices from two main perspectives. The first will focus on their judicial activity and performance through productivity metrics, such as number of rulings produced per year, number of rulings passed by unanimity, number of precedents they have created, and the most recurring topics they have ruled. For this component, we will use the Supreme Court of Justice’s API, which provides access to two sources of information: tesis/jurisprudencia (similar to judicial precedents) and court rulings.

The second perspective examines each justice’s academic background, professional trajectory, and personal profile. This will include their academic and professional backgrounds, as well as data regarding their income and asset disclosures, which they are legally required to report as public servants. Our primary source will be the Plataforma Nacional de Transparencia, a portal that consolidates information published by federal and local public entities regarding their transparency duties. Through this platform, we can incorporate two types of information: 1) the justice’s annual assets and conflicts of interest disclosures or 2) citizen requests of information addressed to the Supreme Court, which can be linked to specific justices and examined for their content. 

Our objective with this project is to develop a platform that incorporates relevant information regarding the justices’ profiles, combining background characteristics with indicators of performance while in office. We believe this initiative can help establish an important precedent for the systematic monitoring of judges. This is particularly relevant in Mexico’s current institutional context: in 2025, the judicial selection mechanism shifted from a career-based public service system to an electoral model in which all judges are elected by popular vote. Eligibility requirements were lowered, removing mandatory prior judicial experience. We intend for this platform to serve as a foundation for future statistical analyses of the reform’s effect on judicial indicators, such as productivity, independence and quality, and to eventually expand this analysis beyond the Supreme Court to include judges at the federal and local level who have been recently elected. 

*These details can & will change as much as needed over the next few weeks.*

## Preliminary Data Sources

### Data Source #1

Source URL: https://bicentenario.scjn.gob.mx/repositorio-scjn/

Source Type: API
Summary: Last year, the Mexican Supreme Court of Justice released an API for developers to access information regarding tesis and jurisprudencia (legal precedents) and court rulings.

For the tesis/jurisprudencia part, the most relevant information is: 
- Unique registry number 
- Year
- Month
- Type of the court that emitted the precedent 
- Name of the court that emitted the precedent
- Subject 
- Type of tesis (tesis or jurisprudencia)
- Title
- Text 

For the court ruling part, the most relevant information is:
- File number 
- Court 
- Justice that was assigned to emit the decision
- Topic
- Court case of origin (the Supreme Court usually reviews lower courts’ decisions)
- Court of origin (the Supreme Court usually reviews lower courts’ decisions)
- Date of ruling 
- Resolutive points 
- Justice that actually emitted the decision
- Ruling document 
- Voting result (unanimous decision, majority, etc.). 


Challenges:
We are not entirely sure if we will be able to directly access the court ruling documents or whether the API is simply limited to getting the hyperlink of the ruling.
According to the website, the last update for the court rulings was December 2025. Although we would have sufficient historical information up until that point, there is a possibility and concern that the Supreme Court’s new presidency will not seek to continue updating the information available within the API (tesis/jurisprudencia was last updated in January 2026 - so we are confident this data source will continue to be updated). However, it might also be the case that there is a lag after Winter vacation break. 


### Data Source #2

Source URL: https://www.plataformadetransparencia.org.mx/Inicio

Source Type: Bulk data or web scrapping

Summary: The Plataforma Nacional de Transparencia contains information regarding all public entities legally obligated to disclose public information regarding their operation and their staff (including the Supreme Court Justice’s). Within this platform, we can find relevant information such as asset and conflict of interest disclosures, income, curriculum and requests of information made by the public. We believe that this platform can be a valuable addition to our primary source of information, as it will help complement the justice’s profiles. Our primary focus will be the asset and conflict of interest disclosures, although we would also like to analyze requests of information and link those related to the justices so we can also identify what people are asking about them. 


Challenges:
This is a platform that usually takes a lot of time to load and sometimes when updated loses the location where you originally were and have to start over (that is why we think web-scrapping might not be the best choice). We are considering doing bulk downloads, but we are aware this might have some limitations in terms of automatization. 
Although this platform contains historical data, the time required for public entities to keep that information varies from one type of information to another (which usually has a maximum of 3 years), so it might not be possible to go that back. However, this is something we need to explore further.  

## Questions

1) The first data source (API) uses pagination to access the ids of tesis and jurisprudencia (which should later be used to access the json of each), but we’re not sure how to apply that pagination and not get the same result every time (GET  /api/v1/tesis/ids). We would like to check with you how to apply this pagination. We have an alternative solution if this is a design problem of the API. 
2) We are not sure what the best strategy for the second data source is. We believe the best path would be to do bulk download of json files and rather do the linking between data sources through those json files and not through a web-scrapping technique. 
3) What is the minimum number of variables that the justice’s profile should have? Should we run some sort of statistical test to check for the independence of these variables? 

