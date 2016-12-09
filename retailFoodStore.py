
# coding: utf-8

import tkinter
from tkinter import *
import mysql.connector as mc

class App(Frame):

    def __init__(self,master):
        Frame.__init__(self,master)
        self.grid()
        self.create_widgets()
        zip=StringVar()
    
    def create_widgets(self):
        self.button=Button(self,text="Open Db",fg="red",command=self.ouvrir)
        self.button.grid(row=0,column=0,sticky=W)

        self.button2=Button(self,text="Close Db",command=self.fermer)
        self.button2.grid(row=0,column=3,sticky=W)
        
        self.button3=Button(self,text="Create Table",command=self.create)
        self.button3.grid(row=0,column=1,sticky=W)
        
        self.button4=Button(self,text="Import Data",command=self.importdata)
        self.button4.grid(row=0,column=2,sticky=W)
        
        self.button5=Button(self,text="1. Top ten deficiencies recorded",command=self.tendef)
        self.button5.grid(row=2,column=0,sticky=W)
        
        self.button6=Button(self,text="2. Ten entities with the most deficiencies inspected in recent year",command=self.tenenti)
        self.button6.grid(row=3,column=0,sticky=W)
        
        self.button7=Button(self,text="3. Average square feet of the entities w/ and w/o deficiency",command=self.avg)
        self.button7.grid(row=4,column=0,sticky=W)
        
        self.button8=Button(self,text="4. Cities/Counties with the most deficiencies",command=self.citycounty)
        self.button8.grid(row=5,column=0,sticky=W)
        
        self.button9=Button(self,text="5. Stores without deficiency in your area",command=self.area)
        self.button9.grid(row=6,column=0,sticky=W)
    
        self.instruction=Label(self,text="Please enter your zip code:")
        self.instruction.grid(row=7,column=0,columnspan=2,sticky=W)
        
        self.zip=Entry(self)
        self.zip.grid(row=8,column=0,sticky=W)


    def ouvrir(self):
        # Establish a MariaDB connection
        self.con=mc.connect(host='127.0.0.1',port=3306,user='root',database='retailfoodstore')
        # Get the cursor to traverse the database, line by line
        self.cur=self.con.cursor()

    def fermer(self):
        self.con.commit() 
        self.cur.close()
        self.con.close()
    
    def create(self):
        # Create table 'deficiency'
        self.cur.execute("CREATE TABLE IF NOT EXISTS deficiency (\
                         deficiencyCode CHAR(3) NOT NULL,\
                         description TEXT NOT NULL,PRIMARY KEY (deficiencyCode)) COLLATE='utf8_general_ci'ENGINE=InnoDB")
        
        # Create table 'zipcode'
        self.cur.execute("CREATE TABLE IF NOT EXISTS zipcode (\
                         zipCode CHAR(5) NOT NULL,\
                         city VARCHAR(50) NOT NULL,\
                         county VARCHAR(50) NOT NULL,PRIMARY KEY (zipCode))\
                         COLLATE='utf8_general_ci'ENGINE=InnoDB")
        
        # Create table stores
        self.cur.execute("CREATE TABLE IF NOT EXISTS stores (\
                         licenseNo VARCHAR(50) NOT NULL,\
                         establishment VARCHAR(10) NOT NULL,\
                         entityName VARCHAR(50) NOT NULL,\
                         DBAname VARCHAR(50) NOT NULL,\ 
                         squareFootage VARCHAR(50) NOT NULL,\
                         zip CHAR(5) NOT NULL,PRIMARY KEY (licenseNo),\
                         INDEX FK_stores_zipcode (zip),\
                         CONSTRAINT FK_stores_zipcode FOREIGN KEY (zip) REFERENCES zipcode (zipCode)ON DELETE NO ACTION)\
                         COLLATE='utf8_general_ci'ENGINE=InnoDB")
        
        # Create table violations
        self.cur.execute("CREATE TABLE IF NOT EXISTS violations (\
                         id INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,\ 
                         inspectionDate DATE NOT NULL, \
                         deficiencyCode CHAR(3) NOT NULL,\
                         licenseNo VARCHAR(50) NOT NULL,PRIMARY KEY (id),\
                         INDEX FK_violations_stores (licenseNo), \
                         INDEX FK_violations_deficiency (deficiencyCode),\
                         CONSTRAINT FK_violations_deficiency \
                         FOREIGN KEY (deficiencyCode) REFERENCES deficiency (deficiencyCode) ON DELETE NO ACTION, \
                         CONSTRAINT FK_violations_stores\
                         FOREIGN KEY (licenseNo) REFERENCES stores (licenseNo) ON DELETE NO ACTION)\
                         COLLATE='utf8_general_ci'ENGINE=InnoDB")
        
    def importdata(self):
        self.cur.execute("SET FOREIGN_KEY_CHECKS=0")
        
        self.cur.execute("LOAD DATA LOW_PRIORITY LOCAL INFILE 'deficiency.csv' \
                         REPLACE INTO TABLE retailfoodstore.deficiency CHARACTER SET utf8\
                         FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' ESCAPED BY '\"' LINES TERMINATED BY '\\r\\n' \
                         IGNORE 1 LINES")
        
        self.cur.execute("LOAD DATA LOW_PRIORITY LOCAL INFILE 'zip.csv'\
                         REPLACE INTO TABLE retailfoodstore.zipcode CHARACTER SET utf8\
                         FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' ESCAPED BY '\"' LINES TERMINATED BY '\\r\\n' \
                         IGNORE 1 LINES")
        
        self.cur.execute("LOAD DATA LOW_PRIORITY LOCAL INFILE 'stores.csv'\
                         REPLACE INTO TABLE retailfoodstore.stores CHARACTER SET utf8\
                         FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' ESCAPED BY '\"' LINES TERMINATED BY '\\r\\n' \
                         IGNORE 1 LINES")
        
        self.cur.execute("LOAD DATA LOW_PRIORITY LOCAL INFILE 'violations.csv'\
                         REPLACE INTO TABLE retailfoodstore.violations CHARACTER SET utf8 \
                         FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' ESCAPED BY '\"' LINES TERMINATED BY '\\r\\n' \
                         IGNORE 1 LINES")
        
        self.cur.execute("set FOREIGN_KEY_CHECKS=1")
     
    
    def tendef(self):
        self.cur.execute('SELECT count AS "Number of Violations", description AS "Deficiency" \
                         FROM deficiency d,(SELECT deficiencyCode, COUNT(deficiencyCode) AS count \
                         FROM violations GROUP BY deficiencyCode ORDER BY count DESC LIMIT 10) a \
                         WHERE d.deficiencyCode=a.deficiencyCode')
        print(self.cur.fetchall())
    
    def tenenti(self):
        self.cur.execute('SELECT DBAname AS "Store Name", county AS "County",count AS "Number of Violations" \
                         FROM stores s,zipcode z,(SELECT licenseNo, COUNT(licenseNo) AS count \
                         FROM violations WHERE inspectionDate<"2016-10-25" AND inspectionDate > "2015-10-24" \
                         GROUP BY licenseNo ORDER BY count DESC LIMIT 10) a WHERE s.licenseNo=a.licenseNo AND s.zip=z.zipCode')
        print(self.cur.fetchall())
        
    def avg(self):
        self.cur.execute('SELECT * FROM (SELECT AVG(squareFootage) AS "Average Area of Stores without Violations" \
                         FROM stores s WHERE s.licenseNo NOT IN (SELECT licenseNo FROM violations)) b,\
                         (SELECT AVG(s.squareFootage) AS "Average Area of Stores with More Than 10 Times Violations" \
                         FROM stores s,(SELECT licenseNo, COUNT(licenseNo) AS count FROM violations GROUP BY licenseNo) a \
                         WHERE count>10 AND a.licenseNo=s.licenseNo) c')
        print(self.cur.fetchall())
    
    def citycounty(self):
        self.cur.execute('SELECT z.city AS City,z.county AS County, s.zip, a.count AS "Number of Violations" \
                         FROM stores s, zipcode z,(SELECT licenseNo, COUNT(licenseNo) AS count \
                         FROM violations GROUP BY licenseNo ORDER BY count DESC) a \
                         WHERE s.licenseNo=a.licenseNo AND s.zip=z.zipCode')
        print(self.cur.fetchall())
        
    def area(self):
        self.cur.execute('SELECT entityName AS "Entity Name", DBAname AS "Store Name", city AS "City", county AS "County" \
                         FROM stores s, zipcode z WHERE s.licenseNo NOT IN (SELECT licenseNo FROM violations)\
                         AND s.zip=z.zipCode AND s.zip="%s"' % (self.zip.get()))
        print (self.cur.fetchall())

root=Tk()
root.title("Retail Stores Database Connection")
root.geometry('600x300')

app=App(root)
root.mainloop()


# In[17]:

import os
os.getcwd()


# In[ ]:



