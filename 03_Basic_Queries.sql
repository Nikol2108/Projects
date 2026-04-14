
--1
SELECT TOP 5 p.Name, SUM(sod.OrderQty) AS TotalQtySold, SUM(sod.LineTotal) AS TotalSales
FROM SalesOrderDetail sod
INNER JOIN Product p ON sod.ProductID=p.ProductID
GROUP BY p.ProductID,p.Name
ORDER BY TotalQtySold DESC

--2
SELECT PC.Name, AVG(sod.UnitPrice) AS [Average Price Per Unit]
FROM SalesOrderDetail SOD
INNER JOIN Product P ON SOD.ProductID = P.ProductID
INNER JOIN ProductSubCategory PS ON P.ProductSubcategoryID=PS.ProductSubcategoryID
INNER JOIN ProductCategory PC ON PC.ProductCategoryID=PS.ProductCategoryID
WHERE PC.Name IN('Bikes', 'Components')
GROUP BY PC.Name



--3
SELECT P.Name, SUM(sod.OrderQty) AS [Amount Per Product]
FROM SalesOrderDetail SOD
INNER JOIN Product P ON SOD.ProductID = P.ProductID
INNER JOIN ProductSubCategory PS ON P.ProductSubcategoryID=PS.ProductSubcategoryID
INNER JOIN ProductCategory PC ON PC.ProductCategoryID=PS.ProductCategoryID
WHERE P.Name not IN('Components', 'Clothing')
GROUP BY P.Name


--4
SELECT top 3 ST.Name , SUM(SOH.TotalDue) AS [Total Sales Amount]
FROM SalesTerritory ST
INNER JOIN SalesOrderHeader SOH ON st.TerritoryID = SOH.TerritoryID
GROUP BY ST.Name
ORDER BY SUM(SOH.TotalDue) DESC

--5
SELECT c.CustomerID, p.FirstName + ' ' + p.LastName AS FullName
FROM Customer c
INNER JOIN Person p ON c.PersonID = p.BusinessEntityID
LEFT JOIN SalesOrderHeader soh ON c.CustomerID = soh.CustomerID
WHERE soh.SalesOrderID IS NULL


--6
DELETE FROM SalesTerritory
WHERE TerritoryID NOT IN(SELECT TerritoryID FROM SalesPerson WHERE TerritoryID IS NOT NULL)


--7
INSERT INTO [dbo].[SalesTerritory]
(
   [TerritoryID],
   [Name],
   [CountryRegionCode],
   [Group],
   [SalesYTD],
   [SalesLastYear],
   [CostYTD],
   [CostLastYear],
   [rowguid],
   [ModifiedDate]
)
SELECT
   [TerritoryID],
   [Name],
   [CountryRegionCode],
   [Group],
   [SalesYTD],
   [SalesLastYear],
   [CostYTD],
   [CostLastYear],
   [rowguid],
   [ModifiedDate]
FROM [AdventureWorks2019].[Sales].[SalesTerritory]
WHERE TerritoryID NOT IN (
   SELECT TerritoryID
   FROM SalesTerritory
)

--8
SELECT p.FirstName + ' ' + p.LastName AS CustomerFullName, COUNT(soh.SalesOrderID) AS TotalOrders
FROM Customer c
INNER JOIN Person p ON c.PersonID = p.BusinessEntityID
INNER JOIN SalesOrderHeader soh ON c.CustomerID = soh.CustomerID
GROUP BY p.FirstName, p.LastName
HAVING COUNT(soh.SalesOrderID) > 20
ORDER BY COUNT(soh.SalesOrderID) DESC


--9
SELECT GroupName, COUNT(*) AS DepartmentsCount
FROM Department
GROUP BY GroupName
HAVING COUNT(*) > 2


--10
SELECT FirstName+' '+LastName as EmployeeName,
       d.Name as DepartmentName,
       s.Name as ShiftName
from EmployeeDepartmentHistory edh
INNER JOIN Department d ON edh.DepartmentID=d.DepartmentID
INNER JOIN Employee e on edh.BusinessEntityID=e.BusinessEntityID
INNER JOIN Person p on e.BusinessEntityID=p.BusinessEntityID
INNER JOIN Shift s on edh.ShiftID=s.ShiftID
WHERE YEAR(e.HireDate)>2010
       AND d.GroupName IN ('Manufacturing', 'Quality Assurance')



