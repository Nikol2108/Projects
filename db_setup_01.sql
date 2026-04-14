--Create DataBase--
CREATE DATABASE Nikol_Sales;
GO

USE Nikol_Sales 

--CREATE FUNCTION ufnLeadingZeros--
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

CREATE FUNCTION [dbo].[ufnLeadingZeros](
    @Value int
) 
RETURNS varchar(8) 
WITH SCHEMABINDING 
AS 
BEGIN
    DECLARE @ReturnValue varchar(8);

    SET @ReturnValue = CONVERT(varchar(8), @Value);
    SET @ReturnValue = REPLICATE('0', 8 - DATALENGTH(@ReturnValue)) + @ReturnValue;

    RETURN (@ReturnValue);
END;
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Input parameter for the scalar function ufnLeadingZeros. Enter a valid integer.' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'FUNCTION',@level1name=N'ufnLeadingZeros', @level2type=N'PARAMETER',@level2name=N'@Value'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Scalar function used by the Sales.Customer table to help set the account number.' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'FUNCTION',@level1name=N'ufnLeadingZeros'
GO

-- ----- Create Tables ----- -- 

USE Nikol_Sales 

--CREATE Table Customer--
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Customer](
    [CustomerID] [int] NOT NULL,
    [PersonID] [int] NULL,
    [StoreID] [int] NULL,
    [TerritoryID] [int] NULL,
    [AccountNumber]  AS (isnull('AW'+[dbo].[ufnLeadingZeros]([CustomerID]),'')),
    [rowguid] [uniqueidentifier] ROWGUIDCOL  NOT NULL,
    [ModifiedDate] [datetime] NOT NULL
) ON [PRIMARY]

--CREATE Table SalesTerritory--
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SalesTerritory](
    [TerritoryID] [int] NOT NULL,
    [Name] [nvarchar](50) NOT NULL,
    [CountryRegionCode] [nvarchar](3) NOT NULL,
    [Group] [nvarchar](50) NOT NULL,
    [SalesYTD] [money] NOT NULL,
    [SalesLastYear] [money] NOT NULL,
    [CostYTD] [money] NOT NULL,
    [CostLastYear] [money] NOT NULL,
    [rowguid] [uniqueidentifier] ROWGUIDCOL  NOT NULL,
    [ModifiedDate] [datetime] NOT NULL
) ON [PRIMARY]

--CREATE Table SalesPerson--
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SalesPerson](
    [BusinessEntityID] [int] NOT NULL,
    [TerritoryID] [int] NULL,
    [SalesQuota] [money] NULL,
    [Bonus] [money] NOT NULL,
    [CommissionPct] [smallmoney] NOT NULL,
    [SalesYTD] [money] NOT NULL,
    [SalesLastYear] [money] NOT NULL,
    [rowguid] [uniqueidentifier] ROWGUIDCOL  NOT NULL,
    [ModifiedDate] [datetime] NOT NULL
) ON [PRIMARY]

--CREATE Table CreditCard (Sales)--
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[CreditCard](
    [CreditCardID] [int] NOT NULL,
    [CardType] [nvarchar](50) NOT NULL,
    [CardNumber] [nvarchar](25) NOT NULL,
    [ExpMonth] [tinyint] NOT NULL,
    [ExpYear] [smallint] NOT NULL,
    [ModifiedDate] [datetime] NOT NULL
) ON [PRIMARY]

--CREATE Table SalesOrderHeader (Sales)--
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SalesOrderHeader](
    [SalesOrderID] [int] NOT NULL,
    [RevisionNumber] [tinyint] NOT NULL,
    [OrderDate] [datetime] NOT NULL,
    [DueDate] [datetime] NOT NULL,
    [ShipDate] [datetime] NULL,
    [Status] [tinyint] NOT NULL,
    [OnlineOrderFlag] [nvarchar](25) NOT NULL,
    [SalesOrderNumber]  AS (isnull(N'SO'+CONVERT([nvarchar](23),[SalesOrderID]),N'* ERROR *')),
    [PurchaseOrderNumber] [nvarchar](25) NULL,
    [AccountNumber] [nvarchar](25) NULL,
    [CustomerID] [int] NOT NULL,
    [SalesPersonID] [int] NULL,
    [TerritoryID] [int] NULL,
    [BillToAddressID] [int] NOT NULL,
    [ShipToAddressID] [int] NOT NULL,
    [ShipMethodID] [int] NOT NULL,
    [CreditCardID] [int] NULL,
    [CreditCardApprovalCode] [varchar](15) NULL,
    [CurrencyRateID] [int] NULL,
    [SubTotal] [money] NOT NULL,
    [TaxAmt] [money] NOT NULL,
    [Freight] [money] NOT NULL,
    [TotalDue]  AS (isnull(([SubTotal]+[TaxAmt])+[Freight],(0))),
    [Comment] [nvarchar](128) NULL,
    [rowguid] [uniqueidentifier] ROWGUIDCOL  NOT NULL,
    [ModifiedDate] [datetime] NOT NULL
) ON [PRIMARY]

--CREATE Table SalesOrderDetail (Sales)--
CREATE TABLE [SalesOrderDetail](
    [SalesOrderID] [int] NOT NULL,
    [SalesOrderDetailID] [int]  NOT NULL,
    [CarrierTrackingNumber] [nvarchar](25) NULL,
    [OrderQty] [smallint] NOT NULL,
    [ProductID] [int] NOT NULL,
    [SpecialOfferID] [int] NOT NULL,
    [UnitPrice] [money] NOT NULL,
    [UnitPriceDiscount] [money] NOT NULL,
    [LineTotal]  AS (isnull(([UnitPrice]*((1.0)-[UnitPriceDiscount]))*[OrderQty],(0.0))),
    [rowguid] [uniqueidentifier] ROWGUIDCOL  NOT NULL,
    [ModifiedDate] [datetime] NOT NULL
) ON [PRIMARY]

--CREATE Table SpecialOfferProduct (Sales)--
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SpecialOfferProduct](
    [SpecialOfferID] [int] NOT NULL,
    [ProductID] [int] NOT NULL,
    [rowguid] [uniqueidentifier] ROWGUIDCOL  NOT NULL,
    [ModifiedDate] [datetime] NOT NULL
) ON [PRIMARY]

--CREATE Table Address (Person)--
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Address](
    [AddressID] [int] NOT NULL,
    [AddressLine1] [nvarchar](60) NOT NULL,
    [AddressLine2] [nvarchar](60) NULL,
    [City] [nvarchar](30) NOT NULL,
    [StateProvinceID] [int] NOT NULL,
    [PostalCode] [nvarchar](15) NOT NULL,
    [SpatialLocation] [geography] NULL,
    [rowguid] [uniqueidentifier] ROWGUIDCOL  NOT NULL,
    [ModifiedDate] [datetime] NOT NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]

--CREATE Table ShipMethod (Purchasing)--
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ShipMethod](
    [ShipMethodID] [int] NOT NULL,
    [Name] [nvarchar](25) NOT NULL,
    [ShipBase] [money] NOT NULL,
    [ShipRate] [money] NOT NULL,
    [rowguid] [uniqueidentifier] ROWGUIDCOL  NOT NULL,
    [ModifiedDate] [datetime] NOT NULL
) ON [PRIMARY]

--CREATE Table CurrencyRate (Sales)--
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[CurrencyRate](
    [CurrencyRateID] [int] NOT NULL,
    [CurrencyRateDate] [datetime] NOT NULL,
    [FromCurrencyCode] [nchar](3) NOT NULL,
    [ToCurrencyCode] [nchar](3) NOT NULL,
    [AverageRate] [money] NOT NULL,
    [EndOfDayRate] [money] NOT NULL,
    [ModifiedDate] [datetime] NOT NULL
) ON [PRIMARY]

--CREATE Table Product (Production)--
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [Product](
    [ProductID] [int] NOT NULL,
    [Name] [nvarchar](50) NOT NULL,
    [ProductNumber] [nvarchar](25) NOT NULL,
    [MakeFlag] [nvarchar](25) NOT NULL,
    [FinishedGoodsFlag] [nvarchar](25) NOT NULL,
    [Color] [nvarchar](15) NULL,
    [SafetyStockLevel] [smallint] NOT NULL,
    [ReorderPoint] [smallint] NOT NULL,
    [StandardCost] [money] NOT NULL,
    [ListPrice] [money] NOT NULL,
    [Size] [nvarchar](5) NULL,
    [SizeUnitMeasureCode] [nchar](3) NULL,
    [WeightUnitMeasureCode] [nchar](3) NULL,
    [Weight] [decimal](8, 2) NULL,
    [DaysToManufacture] [int] NOT NULL,
    [ProductLine] [nchar](2) NULL,
    [Class] [nchar](2) NULL,
    [Style] [nchar](2) NULL,
    [ProductSubcategoryID] [int] NULL,
    [ProductModelID] [int] NULL,
    [SellStartDate] [datetime] NOT NULL,
    [SellEndDate] [datetime] NULL,
    [DiscontinuedDate] [datetime] NULL,
    [rowguid] [uniqueidentifier] ROWGUIDCOL  NOT NULL,
    [ModifiedDate] [datetime] NOT NULL
) ON [PRIMARY]

-- CREATE Table ProductCategory (Production) --
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [ProductCategory](
    [ProductCategoryID] [int] NOT NULL,
    [Name] NVARCHAR(25) NOT NULL,
    [rowguid] [uniqueidentifier] ROWGUIDCOL  NOT NULL,
    [ModifiedDate] [datetime] NOT NULL
) ON [PRIMARY]


-- CREATE Table ProductSubcategory (Production) --
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [ProductSubcategory](
    [ProductSubcategoryID] [int] NOT NULL,
    [ProductCategoryID] [int] NOT NULL,
    [Name] NVARCHAR(25) NOT NULL,
    [rowguid] [uniqueidentifier] ROWGUIDCOL  NOT NULL,
    [ModifiedDate] [datetime] NOT NULL
) ON [PRIMARY]


--CREATE Table Person (person)--
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [Person](
      [BusinessEntityID] [int] NOT NULL,
      [PersonType] [nchar](2) NOT NULL,
      [NameStyle] [nvarchar](25) NOT NULL,
      [Title] [nvarchar](8) NULL,
      [FirstName] [nvarchar](25) NOT NULL,
      [MiddleName] [nvarchar](25) NULL,
      [LastName] [nvarchar](25) NOT NULL,
      [Suffix] [nvarchar](25) NULL,
      [EmailPromotion] [int] NOT NULL,
      [AdditionalContactInfo] [xml] NULL,
      [Demographics] [xml] NULL,
      [rowguid] [uniqueidentifier] ROWGUIDCOL  NOT NULL,
      [ModifiedDate] [datetime] NOT NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]


--CREATE Table Department (HumanResources)--
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [Department](
      [DepartmentID] [smallint] NOT NULL,
      [Name] [nvarchar](50) NOT NULL,
      [GroupName] [nvarchar](50) NOT NULL,
      [ModifiedDate] [datetime] NOT NULL
) ON [PRIMARY]

--CREATE Table Employee (HumanResources)--
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [Employee](
      [BusinessEntityID] [int] NOT NULL,
      [NationalIDNumber] [nvarchar](15) NOT NULL,
      [LoginID] [nvarchar](256) NOT NULL,
      [OrganizationNode] [hierarchyid] NULL,
      [JobTitle] [nvarchar](50) NOT NULL,
      [BirthDate] [date] NOT NULL,
      [MaritalStatus] [nchar](1) NOT NULL,
      [Gender] [nchar](1) NOT NULL,
      [HireDate] [date] NOT NULL,
      [SalariedFlag] [nvarchar](50) NOT NULL,
      [VacationHours] [smallint] NOT NULL,
      [SickLeaveHours] [smallint] NOT NULL,
      [CurrentFlag] [nvarchar](50) NOT NULL,
      [rowguid] [uniqueidentifier] ROWGUIDCOL  NOT NULL,
      [ModifiedDate] [datetime] NOT NULL
) ON [PRIMARY]


--CREATE Table EmployeeDepartmentHistory (HumanResources)--
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [EmployeeDepartmentHistory](
      [BusinessEntityID] [int] NOT NULL,
      [DepartmentID] [smallint] NOT NULL,
      [ShiftID] [tinyint] NOT NULL,
      [StartDate] [date] NOT NULL,
      [EndDate] [date] NULL,
      [ModifiedDate] [datetime] NOT NULL
) ON [PRIMARY]


--CREATE Table Shift (HumanResources)--
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [Shift](
      [ShiftID] [tinyint] NOT NULL,
      [Name] [nvarchar](50) NOT NULL,
      [StartTime] [time](7) NOT NULL,
      [EndTime] [time](7) NOT NULL,
      [ModifiedDate] [datetime] NOT NULL
) ON [PRIMARY]

