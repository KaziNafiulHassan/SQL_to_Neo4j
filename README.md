# Neo4j_NoSQL
This repository contains tools and scripts to facilitate the migration of a PostgreSQL database to Neo4j. It includes data extraction, transformation, and loading processes, along with schema mapping and validation to ensure a smooth and accurate transition from a relational to a graph database.

## Clone the project using following command

```bash
git clone **https://github.com/Albinaqifi/Neo4j_NoSQL.git**
```

## PgAdmin4 and Neo4j Desktop

Links to download required software
```bash
PGAdmin:  https://www.pgadmin.org/download/

Neo4jDesktop: https://neo4j.com/download/
```

## Creating SQL Database using PgAdmin4

Open PgAdmin, create a database and run the following DDL

```bash
-- Now we are able to delete database, if exists
DROP DATABASE IF EXISTS "PharmaTrack";

-- Recreate the database
CREATE DATABASE "PharmaTrack";

-- Table creation
CREATE TABLE "Medications" (
    medication_id SERIAL PRIMARY KEY,
    med_name VARCHAR(30) NOT NULL,
    med_description TEXT,
    med_strength VARCHAR(20),
    med_dosageForm VARCHAR(20)
);

CREATE TABLE "Supplier" (
    supplier_id SERIAL PRIMARY KEY,
    supplier_name VARCHAR(50) NOT NULL,
    supplier_contact VARCHAR(30),
    supplier_address VARCHAR(30)
);

CREATE TABLE "Employee" (
    employee_id SERIAL PRIMARY KEY,
    employee_name VARCHAR(50) NOT NULL,
    employee_address VARCHAR(30),
    employee_contact VARCHAR(30)
);

CREATE TABLE "Inventory" (
    inventory_id SERIAL PRIMARY KEY,
    medication_id INT NOT NULL,
    supplier_id INT NOT NULL,
    arrival_date DATE NOT NULL,
    amount INT NOT NULL,
    FOREIGN KEY (medication_id) REFERENCES "Medications"(medication_id),
    FOREIGN KEY (supplier_id) REFERENCES "Supplier"(supplier_id)
);

CREATE TABLE "Customer" (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(50),
    customer_contact VARCHAR(30)
);

CREATE TABLE "Sales" (
    sales_id SERIAL PRIMARY KEY,
    sale_date DATE,
    sale_value DECIMAL(10,2) NOT NULL,
    amount_sold INT,
    medication_id INT,
    customer_id INT,
    employee_id INT,
    FOREIGN KEY (medication_id) REFERENCES "Medications"(medication_id),
    FOREIGN KEY (customer_id) REFERENCES "Customer"(customer_id),
    FOREIGN KEY (employee_id) REFERENCES "Employee"(employee_id)
);

CREATE TABLE "Sales_description" (
    sales_description_id SERIAL PRIMARY KEY,
    sales_id INT NOT NULL,
    medication_id INT NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (sales_id) REFERENCES "Sales"(sales_id),
    FOREIGN KEY (medication_id) REFERENCES "Medications"(medication_id)
);

CREATE TABLE "Expired_medications" (
    expired_id SERIAL PRIMARY KEY,
    medication_id INT NOT NULL,
    expiration_date DATE NOT NULL,
    FOREIGN KEY (medication_id) REFERENCES "Medications"(medication_id)
);

-- Create trigger function for checking medication expiry
CREATE OR REPLACE FUNCTION check_medication_expiry() 
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.arrival_date + INTERVAL '1 year' < CURRENT_DATE THEN
        INSERT INTO "Expired_medications"(medication_id, expiration_date) 
        VALUES (NEW.medication_id, NEW.arrival_date + INTERVAL '1 year');
        -- Generate alarm or notification here
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to call the function after insert on Inventory
CREATE TRIGGER check_medication_expiry 
AFTER INSERT ON "Inventory"
FOR EACH ROW EXECUTE FUNCTION check_medication_expiry();

```

## Neo4j Desktop

  -Open Neo4j desktop, and create a new project.  
  -Add a username and password, remember those and remember port the project is ran on, usually is 7789


## Python Script

Use following commands to install required libraries

```bash
python install pip (if not already installed)

pip install psycopg2-binary

pip install neo4j 
```

After installing the libraries use the following command to execute the script

```bash
python mmigrate_2.py
```

