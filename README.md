**Overview**

This project demonstrates an end-to-end database lifecycle for a retail business entity named Nikol_Sales. The project covers everything from initial data modeling and environment setup to complex ETL processes and advanced business intelligence (BI) analytics.
The system is built on SQL Server and utilizes data transformed from the industry-standard AdventureWorks2019 database.

**Tech Stack & Environment**

* Database Engine: Microsoft SQL Server
* Environment: SQL Server running on Docker (macOS)
* Language: T-SQL (Transact-SQL)

**Repository Structure**

The project is divided into four logical stages to ensure scalability and clarity:

* **db_setup_01.sql (Infrastructure):** Creation of the Nikol_Sales database, custom scalar functions with schema binding, and table architectures with defined constraints.

* **data_insertion_02.sql (ETL Process):** A robust Extract-Transform-Load process that migrates data from external sources while applying business-specific logic and formatting.

* **Basic_Queries_03.sql (Operations):** Essential business queries focusing on sales performance, inventory management, and human resources reporting.

* **Advenced_Queries_04.sql (Analytical Insights):** Advanced data analysis using CTEs, Window Functions, and PIVOT tables to derive strategic insights.

**Key Business Insights Demonstrated**

* **Customer Retention (Churn Analysis):** Developed a predictive logic to identify "Potential Churn" by comparing the average gap between customer orders against their last activity date.
Growth Metrics: Calculated Year-over-Year (YoY) growth rates using linear income projections and LAG functions.
* **Sales Intelligence:** Identified top-performing products and territories, and ranked high-value customers using DENSE_RANK.
* **Data Distribution:** Analyzed customer category distributions to understand market penetration.

**How to Run**

* Ensure you have a SQL Server instance (or Docker container) running.
* Execute the scripts in numerical order (01 through 04).
* **Note:** Script 02 requires access to the AdventureWorks2019 database as a source.
