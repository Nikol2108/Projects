-- 1 
WITH cte_base as (
SELECT YEAR(a.OrderDate) as YEAR,
        SUM(ExtendedPrice-TaxAmount) as IncomePerYear,
        COUNT(distinct month(a.OrderDate)) as Months,
        CAST(SUM(ExtendedPrice-TaxAmount)/COUNT(distinct month(a.OrderDate)) * 12 as DECIMAL(12,2)) as YearlyLinearIncome
FROM [sales].[Orders] a 
LEFT outer JOIN sales.invoices b ON a.OrderID=b.OrderID
LEFT outer JOIN sales.invoiceLines c ON b.invoiceid=c.invoiceid
GROUP BY year(a.OrderDate))

, cte_Final as (
select year, incomeperyear, Months, YearlyLinearIncome,
        lag(YearlyLinearIncome) over (order by year) as Prev_YearlyLinearIncome
FROM cte_base )

SELECT year, incomeperyear, Months, YearlyLinearIncome, 
    CAST(((YearlyLinearIncome/Prev_YearlyLinearIncome)-1) *100 as DECIMAL(10,2)) as GrowthRate
FROM cte_Final

-- 2
WITH cte_income as (
SELECT YEAR(a.OrderDate) as TheYear, DATEPART(QUARTER, a.OrderDate) AS TheQuarter, c.CustomerName, 
        SUM(b.Quantity * b.UnitPrice) as IncomePerYear
FROM [sales].[Orders] a
INNER JOIN [Sales].[OrderLines] b on a.orderid=b.orderid
INNER JOIN [Sales].[Customers] c on a.CustomerID=c.CustomerID
GROUP BY YEAR(a.OrderDate), DATEPART(QUARTER, a.OrderDate), c.CustomerName
) 
, cte_ranked as (
SELECT TheYear, TheQuarter, CustomerName, IncomePerYear, 
    DENSE_RANK() OVER (PARTITION BY TheYear, TheQuarter ORDER BY IncomePerYear DESC) AS DNR 
FROM cte_income )

SELECT TheYear, TheQuarter, CustomerName, IncomePerYear, DNR
FROM cte_ranked
WHERE DNR <=5
ORDER BY TheYear, TheQuarter, IncomePerYear DESC

-- 3

SELECT top 10 a.StockItemID, b.StockItemName,
    SUM(a.ExtendedPrice - a.TaxAmount) AS TotalProfit 
FROM sales.InvoiceLines a
INNER JOIN Warehouse.StockItems b on a.StockItemID=b.StockItemID
GROUP BY a.StockItemID, b.StockItemName
ORDER BY TotalProfit DESC

-- 4
SELECT ROW_NUMBER() OVER (ORDER BY (RecommendedRetailPrice - UnitPrice) DESC) AS Rn,
    StockItemID, StockItemName, UnitPrice, RecommendedRetailPrice, 
    (RecommendedRetailPrice - UnitPrice) as NominalProductProfit,
    DENSE_RANK() OVER (ORDER BY (RecommendedRetailPrice - UnitPrice) DESC) as DNR
FROM Warehouse.StockItems
WHERE ValidTo>GETDATE()

-- 5
SELECT CAST(a.SupplierID AS varchar(25)) + ' - ' + a.SupplierName AS SupplierDetails,
    STRING_AGG(CAST(b.StockItemID AS varchar(25)) + ' ' + b.StockItemName, ' , / ') AS ProductDetails
FROM Purchasing.Suppliers a
INNER JOIN Warehouse.StockItems b ON a.SupplierID = b.SupplierID

GROUP BY a.SupplierID, a.SupplierName
ORDER BY a.SupplierID

-- 6
SELECT TOP 5 c.CustomerId, d.CityName, f.CountryName, f.Continent, f.Region, 
    SUM(a.ExtendedPrice) as TotalExtendedPrice
FROM Sales.InvoiceLines a
INNER JOIN Sales.Invoices b ON a.InvoiceId=b.InvoiceId
INNER JOIN Sales.Customers c ON b.CustomerId=c.CustomerId
INNER JOIN Application.Cities d ON c.DeliveryCityId=d.cityId
INNER JOIN Application.StateProvinces e ON d.StateProvinceID=e.StateProvinceID
INNER JOIN Application.Countries f ON e.CountryID=f.CountryID
GROUP BY c.CustomerId, d.CityName, f.CountryName, f.Continent, f.Region
ORDER BY SUM(a.ExtendedPrice) DESC

-- 7
WITH cte_MonthlySales AS (
SELECT YEAR(a.OrderDate) AS OrderYear, MONTH(a.OrderDate) AS OrderMonth,
        SUM(c.ExtendedPrice-c.TaxAmount) AS MonthlyTotal
FROM Sales.Orders a
JOIN Sales.Invoices b ON a.OrderID = b.OrderID
JOIN Sales.InvoiceLines c ON b.InvoiceID = c.InvoiceID
GROUP BY YEAR(a.OrderDate), MONTH(a.OrderDate) )

,cte_total AS (
SELECT OrderYear, OrderMonth, MonthlyTotal,
    SUM(MonthlyTotal) over (partition by orderyear order by ordermonth) as MonthTotalCumulative
FROM cte_MonthlySales )

,cte_YearlySales AS (
SELECT OrderYear, SUM(MonthlyTotal) as YearlyTotal
FROM cte_MonthlySales 
GROUP BY OrderYear )

,cte_final AS (
SELECT OrderYear, OrderMonth, CAST(OrderMonth as varchar(10)) as MonthName, MonthlyTotal, MonthTotalCumulative FROM cte_total 
    UNION ALL
    SELECT OrderYear,13,'Grand Total', yearlyTotal, yearlyTotal
    FROM cte_YearlySales )

    SELECT OrderYear, MonthName, MonthlyTotal, MonthTotalCumulative 
    FROM cte_final
    ORDER BY OrderYear, OrderMonth

-- 8 
SELECT
    OrderMonth, [2013], [2014], [2015], [2016]
FROM (SELECT MONTH(OrderDate) AS OrderMonth, YEAR(OrderDate)  AS OrderYear, OrderID
        FROM Sales.Orders ) as a
PIVOT ( COUNT(OrderID) FOR OrderYear IN ([2013], [2014], [2015], [2016])) as PivotTable

ORDER BY OrderMonth

-- 9
WITH cte_Base AS (
SELECT a.CustomerId, b.CustomerName, a.OrderDate,
    LAG(a.OrderDate) OVER (PARTITION BY a.CustomerID ORDER BY a.OrderDate) as PrevOrderDate,
    MAX(a.OrderDate) OVER (PARTITION BY a.CustomerID) as LastOrderDatePerCust,
    MAX(a.OrderDate) OVER () as LastOrderAll
FROM Sales.Orders a
INNER JOIN Sales.Customers b ON a.CustomerID= b.CustomerID )

,cte_CustOrdersAvgDiff AS (
SELECT CustomerId,
        AVG(DATEDIFF(day,PrevOrderDate,OrderDate)) as DiffOrderDate
        
FROM cte_Base
GROUP BY CustomerId )

SELECT a.CustomerId, CustomerName, OrderDate, PrevOrderDate, b.DiffOrderDate,
        DATEDIFF(day,LastOrderDatePerCust, LastOrderAll) as DiffLastOrderDate,
        CASE 
            WHEN  b.DiffOrderDate * 2 < DATEDIFF(day,LastOrderDatePerCust, LastOrderAll) 
            THEN 'Potential Churn' 
            ELSE 'Active' 
        END
FROM cte_Base a
INNER JOIN cte_CustOrdersAvgDiff b ON a.CustomerId=b.CustomerId

-- 10
WITH cte_Customers AS (
SELECT CustomerCategoryName,
        COUNT (distinct CASE
                            WHEN CustomerName LIKE 'Wingtip%' THEN 'Wingtip Toys'
                            WHEN CustomerName LIKE 'Tailspin%' THEN 'Tailspin Toys'
                            ELSE CustomerName
                        END) as CustomerCount
FROM Sales.Customers a
INNER JOIN Sales.CustomerCategories b ON a.CustomerCategoryID=b.CustomerCategoryID
GROUP BY CustomerCategoryName )

SELECT CustomerCategoryName, CustomerCount, 
        SUM(CustomerCount) OVER() as TotalCustCount,
        FORMAT(CAST(CustomerCount AS FLOAT)/CAST(SUM(CustomerCount) OVER()AS FLOAT), '#,#.00%') as DistributionFactor
FROM cte_Customers
ORDER BY CustomerCount DESC



