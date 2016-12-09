# Python-GUI-MySQL

In this project, I selected 2 datasets about retail food stores in New York State, and constructed GUI in Python to connect MariaDB, which is quite similar to MySQL, and guide users to run particular queries.

## Data Source
Two datasets were downloaded from data.ny.gov as csv files: 
#### Retail Food Stores (DS1)
- A list of all retail food stores which are licensed by the Department of Agriculture and Markets in New York State
- 15 columns: County, License Number, Operation Type, Establishment Type, Entity Name, DBA Name, Street Number, Address Line 2, Address Line 3, City, State, Zip Code, Square Footage, Location
- Source: https://data.ny.gov/Economic-Development/Retail-Food-Stores/9a8c-vfzj

#### Retail Food Store Inspections – Current Critical Violations (DS2)
- Most recent inspections of retail food store where critical deficiencies were found during the inspection
- 11 columns: County, Inspection Date, Owner Name, Trade Name, Street, City, State Code, Zip Code, Deficiency Number, Deficiency Description, Location 1
- Source: https://data.ny.gov/Economic-Development/Retail-Food-Store-Inspections-Current-Critical-Vio/d6dy-3h7r

## Build Application and Import Data
#### SQL schema normalization
-	Primary Key: “License Number” in DS1 and newly added “No.” in DS2 were the unique values to identify each retail store and each deficiency inspected. All attributes are dependent on the primary key. 
-	Columns “Location” / “Operation Type” / “Address Line 2” / “Address Line 3” in DS1 and “Location 1” in DS2 were eliminated due to meaningless values
-	Two datasets were divided into four to meet BCNF: 
  - DEFICIENCY: Deficiency Code, Deficiency Description
  - LOCATION: Zip Code, City, County
  - VIOLATIONS: Number, Inspection Date, Deficiency Number, License Number
  - STORES: License Number, Establishment Type, Entity Name, DBA Name, Sqaure Footage, Zip Code
  
#### Define relationships: 
-	A retail store has one zip code; one zip code can have many stores (one to many)
-	A violation at one inspection date must have a retail store; a retail store has N violations (N can be zero, one or many) (one to many)
-	A violation has one deficiency; a deficiency may exist in many violations (one to many)
![image](file:///C:/Users/yuanm/Desktop/1.jpg)

#### Construct GUI in Python 3.5: 
-	Import “mysql.connector” package to connect Python to MariaDB and import “tkinter” package to construct GUI
-	Define class called “App” and initialize the frame
-	Create widgets with 4 functional buttons Open database, Create table, Import data, Close database – and 5 buttons to provide users with different choices to explore the dataset
- Create database:
```
CREATE DATABASE retailFoodStore /*!40100 COLLATE 'utf8_general_ci' */
```
-	Open database: Establish a connection to the particular host, port, user, and database (In this case, host='127.0.0.1', port=3306, user='root', database=’retailfoodstore’), and instantiate the cursor object to interact with the database
-	Create table: Based on the connection, utilize “cursor.execute” to execute SQL queries
```
CREATE TABLE deficiency (
deficiencyCode CHAR(3) NOT NULL,
description TEXT NOT NULL,
PRIMARY KEY (deficiencyCode))
COLLATE='utf8_general_ci'
ENGINE=InnoDB;

CREATE TABLE zipcode (
zipCode CHAR(5) NOT NULL,
city VARCHAR(50) NOT NULL,
county VARCHAR(50) NOT NULL,
PRIMARY KEY (zipCode))
COLLATE='utf8_general_ci'
ENGINE=InnoDB;

CREATE TABLE stores (
licenseNo VARCHAR(50) NOT NULL,
establishment VARCHAR(10) NOT NULL,
entityName VARCHAR(50) NOT NULL,
DBAname VARCHAR(50) NOT NULL,
squareFootage VARCHAR(50) NOT NULL,
zip CHAR(5) NOT NULL,
PRIMARY KEY (licenseNo),
INDEX FK_stores_zipcode (zip),
CONSTRAINT FK_stores_zipcode FOREIGN KEY (zip) REFERENCES zipcode (zipCode) ON DELETE NO ACTION)
COLLATE='utf8_general_ci'
ENGINE=InnoDB;

CREATE TABLE violations (
id INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
inspectionDate DATE NOT NULL,
deficiencyCode CHAR(3) NOT NULL,
licenseNo VARCHAR(50) NOT NULL,
PRIMARY KEY (`id`),
INDEX FK_violations_stores (licenseNo),
INDEX FK_violations_deficiency (deficiencyCode),
CONSTRAINT FK_violations_deficiency FOREIGN KEY (deficiencyCode) REFERENCES deficiency (deficiencyCode) ON DELETE NO ACTION,
CONSTRAINT FK_violations_stores FOREIGN KEY (licenseNo) REFERENCES stores (licenseNo) ON DELETE NO ACTION)
COLLATE='utf8_general_ci'
ENGINE=InnoDB;
```
- Import data: Before importing, “FOREIGN_KEY_CHECKS” was set to 0 to make sure the data importing process would not be constrained by foreign keys, and reset to 1 after importing all 4 csv files. Sample codes to load ‘deficiency.csv’ are shown below:
```
LOAD DATA LOW_PRIORITY LOCAL INFILE 'deficiency.csv'
REPLACE INTO TABLE retailstore.deficiency CHARACTER SET utf8
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' ESCAPED BY '\"' LINES TERMINATED BY '\\r\\n'
IGNORE 1 LINES (deficiencyCode, description);
```
-	Close database: the connection needs to be closed before quitting the application
-	Data exploration: in a similar way, 5 SQL queries were written as a command in Python behind each button to guide users explore the dataset about retail food stores
-	Make the title of the window as "Retail Stores Database Connection" and geometry as '600x300'
-	Finally call the mainloop of the program

## Explore Data
#### Operating Requirements:
-	A database called “retailfoodstore” exists in the environment of host='127.0.0.1', port=3306, and user='root'
-	Packages “tkinter” and “mysql.connector” are successfully installed in Python 3.5
-	Data files are located in the working directory of Python 3.5

#### Step 1: Open the application called “retailStores.py” in Python 3.5, an interface would prompt out

#### Step 2: Click the red button “Open Db” on the up left corner, a connection would be made between this application and MariaDB. 

#### Step 3: If this is the first time a user running this application, clicking “Create Table” and Import Data” buttons would import the data files into the database. And this needs to be done only once. Every time a user runs the application in the following attempts, there is no need to load the data again. 

#### Step 4: There are five choices for a user to explore the dataset. 
-	Click “1. Top ten deficiencies recorded” to know the 10 most frequent deficiencies inspected in the retail food stores in New York State
-	Click “2. Ten entities with the most deficiencies inspected in recent year” to identify the 10 retail food stores that performed the worst in recent year
-	Click “3. Average square feet of the entities w/ and w/o deficiency” to compare the average square feet of retail stores with and without deficiency inspected
-	Click “4. Cities/Counties with the most deficiencies” to identify the cities and counties where retail food stores suffer from the most deficiencies 
-	As instructed, enter the zip code in the empty box at the bottom, and click “5. Stores without deficiency in your area” to explore the well-performing stores in the area of that particular zip code

#### Step 5: Remember to click “Close Db” button to disconnect the database before quitting the application. 
