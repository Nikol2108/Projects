-- ----- Insert data to tables ----- -- 

USE Nikol_Sales 

--Insert Into Table Customer--
INSERT INTO [dbo].[Customer]
(
    [CustomerID],
    [PersonID],
    [StoreID],
    [TerritoryID],
    [rowguid],
    [ModifiedDate]
)
SELECT
    [CustomerID],
    [PersonID],
    [StoreID],
    [TerritoryID],
    [rowguid],
    [ModifiedDate]
FROM [AdventureWorks2019].[Sales].[Customer]

--Insert Into Table SalesTerritory--
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

--Insert Into Table SalesPerson--
INSERT INTO [dbo].[SalesPerson]
(
    [BusinessEntityID],
    [TerritoryID],
    [SalesQuota],
    [Bonus],
    [CommissionPct],
    [SalesYTD],
    [SalesLastYear],
    [rowguid],
    [ModifiedDate]
)
SELECT
    [BusinessEntityID],
    [TerritoryID],
    [SalesQuota],
    [Bonus],
    [CommissionPct],
    [SalesYTD],
    [SalesLastYear],
    [rowguid],
    [ModifiedDate]
FROM [AdventureWorks2019].[Sales].[SalesPerson]

--Insert Into Table CreditCard (Sales)--
INSERT INTO [dbo].[CreditCard]
(
    [CreditCardID],
    [CardType],
    [CardNumber],
    [ExpMonth],
    [ExpYear],
    [ModifiedDate]
)
SELECT
    [CreditCardID],
    [CardType],
    [CardNumber],
    [ExpMonth],
    [ExpYear],
    [ModifiedDate]
FROM [AdventureWorks2019].[Sales].[CreditCard]




--Insert Into Table SalesOrderHeader (Sales)--
INSERT INTO [dbo].[SalesOrderHeader]
(
    [SalesOrderID],
    [RevisionNumber],
    [OrderDate],
    [DueDate],
    [ShipDate],
    [Status],
    [OnlineOrderFlag],
    [PurchaseOrderNumber],
    [AccountNumber],
    [CustomerID],
    [SalesPersonID],
    [TerritoryID],
    [BillToAddressID],
    [ShipToAddressID],
    [ShipMethodID],
    [CreditCardID],
    [CreditCardApprovalCode],
    [CurrencyRateID],
    [SubTotal],
    [TaxAmt],
    [Freight],
    [Comment],
    [rowguid],
    [ModifiedDate]
)
SELECT
    [SalesOrderID],
    [RevisionNumber],
    [OrderDate],
    [DueDate],
    [ShipDate],
    [Status],
    [OnlineOrderFlag],
    [PurchaseOrderNumber],
    [AccountNumber],
    [CustomerID],
    [SalesPersonID],
    [TerritoryID],
    [BillToAddressID],
    [ShipToAddressID],
    [ShipMethodID],
    [CreditCardID],
    [CreditCardApprovalCode],
    [CurrencyRateID],
    [SubTotal],
    [TaxAmt],
    [Freight],
    [Comment],
    [rowguid],
    [ModifiedDate]
FROM [AdventureWorks2019].[Sales].[SalesOrderHeader]

--Insert Into Table SalesOrderDetail (Sales)--
INSERT INTO [dbo].[SalesOrderDetail]
(
    [SalesOrderID],
    [SalesOrderDetailID],
    [CarrierTrackingNumber],
    [OrderQty],
    [ProductID],
    [SpecialOfferID],
    [UnitPrice],
    [UnitPriceDiscount],
    [rowguid],
    [ModifiedDate]
)
SELECT
    [SalesOrderID],
    [SalesOrderDetailID],
    [CarrierTrackingNumber],
    [OrderQty],
    [ProductID],
    [SpecialOfferID],
    [UnitPrice],
    [UnitPriceDiscount],
    [rowguid],
    [ModifiedDate]
FROM [AdventureWorks2019].[Sales].[SalesOrderDetail]

--Insert Into Table SpecialOfferProduct (Sales)--
INSERT INTO [dbo].[SpecialOfferProduct]
(
    [SpecialOfferID],
    [ProductID],
    [rowguid],
    [ModifiedDate]
)
SELECT
    [SpecialOfferID],
    [ProductID],
    [rowguid],
    [ModifiedDate]
FROM [AdventureWorks2019].[Sales].[SpecialOfferProduct]

--Insert Into Table Address (Person)--
INSERT INTO [dbo].[Address]
(
    [AddressID],
    [AddressLine1],
    [AddressLine2],
    [City],
    [StateProvinceID],
    [PostalCode],
    [SpatialLocation],
    [rowguid],
    [ModifiedDate]
)
SELECT
    [AddressID],
    [AddressLine1],
    [AddressLine2],
    [City],
    [StateProvinceID],
    [PostalCode],
    [SpatialLocation],
    [rowguid],
    [ModifiedDate]
FROM [AdventureWorks2019].[Person].[Address]

--Insert Into Table ShipMethod (Purchasing)--
INSERT INTO [dbo].[ShipMethod]
(
    [ShipMethodID],
    [Name],
    [ShipBase],
    [ShipRate],
    [rowguid],
    [ModifiedDate]
)
SELECT
    [ShipMethodID],
    [Name],
    [ShipBase],
    [ShipRate],
    [rowguid],
    [ModifiedDate]
FROM [AdventureWorks2019].[Purchasing].[ShipMethod]



--Insert Into Table CurrencyRate (Sales)--
INSERT INTO [dbo].[CurrencyRate]
(
    [CurrencyRateID],
    [CurrencyRateDate],
    [FromCurrencyCode],
    [ToCurrencyCode],
    [AverageRate],
    [EndOfDayRate],
    [ModifiedDate]
)
SELECT
    [CurrencyRateID],
    [CurrencyRateDate],
    [FromCurrencyCode],
    [ToCurrencyCode],
    [AverageRate],
    [EndOfDayRate],
    [ModifiedDate]
FROM [AdventureWorks2019].[Sales].[CurrencyRate]

--Insert Into Product--
INSERT INTO [dbo].[Product]
(  [ProductID],
    [Name],
    [ProductNumber],
    [MakeFlag],
    [FinishedGoodsFlag],
    [Color],
    [SafetyStockLevel],
    [ReorderPoint],
    [StandardCost],
    [ListPrice],
    [Size],
    [SizeUnitMeasureCode],
    [WeightUnitMeasureCode],
    [Weight],
    [DaysToManufacture],
    [ProductLine],
    [Class],
    [Style],
    [ProductSubcategoryID],
    [ProductModelID],
    [SellStartDate],
    [SellEndDate],
    [DiscontinuedDate],
    [rowguid],
    [ModifiedDate]
)
SELECT
 [ProductID],
    [Name],
    [ProductNumber],
    [MakeFlag],
    [FinishedGoodsFlag],
    [Color],
    [SafetyStockLevel],
    [ReorderPoint],
    [StandardCost],
    [ListPrice],
    [Size],
    [SizeUnitMeasureCode],
    [WeightUnitMeasureCode],
    [Weight],
    [DaysToManufacture],
    [ProductLine],
    [Class],
    [Style],
    [ProductSubcategoryID],
    [ProductModelID],
    [SellStartDate],
    [SellEndDate],
    [DiscontinuedDate],
    [rowguid],
    [ModifiedDate]
FROM [AdventureWorks2019].[Production].[Product]

--Insert Into ProductCategory --
INSERT INTO [ProductCategory](
    [ProductCategoryID]
      ,[Name]
      ,[rowguid]
      ,[ModifiedDate] ) 
SELECT [ProductCategoryID]
      ,[Name]
      ,[rowguid]
      ,[ModifiedDate]
FROM [AdventureWorks2019].[Production].[ProductCategory]








--Insert Into ProductSubcategory--
INSERT INTO [ProductSubcategory](
    [ProductSubcategoryID]
      ,[ProductCategoryID]
      ,[Name]
      ,[rowguid]
      ,[ModifiedDate] ) 
SELECT [ProductSubcategoryID]
      ,[ProductCategoryID]
      ,[Name]
      ,[rowguid]
      ,[ModifiedDate]
FROM [AdventureWorks2019].[Production].[ProductSubcategory]



--Insert Into person--
INSERT INTO [dbo].[Person](
    [BusinessEntityID]
      ,[PersonType]
      ,[NameStyle]
      ,[Title]
      ,[FirstName]
      ,[MiddleName]
      ,[LastName]
      ,[Suffix]
      ,[EmailPromotion]
      ,[AdditionalContactInfo]
      ,[Demographics]
      ,[rowguid]
      ,[ModifiedDate] ) 
SELECT [BusinessEntityID]
      ,[PersonType]
      ,[NameStyle]
      ,[Title]
      ,[FirstName]
      ,[MiddleName]
      ,[LastName]
      ,[Suffix]
      ,[EmailPromotion]
      ,[AdditionalContactInfo]
      ,[Demographics]
      ,[rowguid]
      ,[ModifiedDate]
FROM [AdventureWorks2019].[Person].[Person]


--Insert Into Department—
INSERT INTO [dbo].[Department](
    [DepartmentID]
      ,[Name]
      ,[GroupName]
      ,[ModifiedDate] ) 
SELECT [DepartmentID]
      ,[Name]
      ,[GroupName]
      ,[ModifiedDate]
FROM [AdventureWorks2019].[HumanResources].[Department]

--Insert Into Employee —
INSERT INTO [dbo].[Employee](
    [BusinessEntityID]
      ,[NationalIDNumber]
      ,[LoginID]
      ,[OrganizationNode]
      ,[JobTitle]
      ,[BirthDate]
      ,[MaritalStatus]
      ,[Gender]
      ,[HireDate]
      ,[SalariedFlag]
      ,[VacationHours]
      ,[SickLeaveHours]
      ,[CurrentFlag]
      ,[rowguid]
      ,[ModifiedDate] ) 
SELECT [BusinessEntityID]
      ,[NationalIDNumber]
      ,[LoginID]
      ,[OrganizationNode]
      ,[JobTitle]
      ,[BirthDate]
      ,[MaritalStatus]
      ,[Gender]
      ,[HireDate]
      ,[SalariedFlag]
      ,[VacationHours]
      ,[SickLeaveHours]
      ,[CurrentFlag]
      ,[rowguid]
      ,[ModifiedDate]
FROM [AdventureWorks2019].[HumanResources].[Employee]



--Insert Into EmployeeDepartmentHistory —
INSERT INTO [dbo].[EmployeeDepartmentHistory](
    [BusinessEntityID]
      ,[DepartmentID]
      ,[ShiftID]
      ,[StartDate]
      ,[EndDate]
      ,[ModifiedDate] ) 
SELECT [BusinessEntityID]
      ,[DepartmentID]
      ,[ShiftID]
      ,[StartDate]
      ,[EndDate]
      ,[ModifiedDate]
FROM [AdventureWorks2019].[HumanResources].[EmployeeDepartmentHistory]


--Insert Into Shift—
INSERT INTO [dbo].[Shift](
    [ShiftID]
      ,[Name]
      ,[StartTime]
      ,[EndTime]
      ,[ModifiedDate] ) 
SELECT [ShiftID]
      ,[Name]
      ,[StartTime]
      ,[EndTime]
      ,[ModifiedDate]
FROM [AdventureWorks2019].[HumanResources].[Shift]
