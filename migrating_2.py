import psycopg
from neo4j import GraphDatabase
import pandas as pd

pg_conn_params = {
    'dbname': 'PharmaTrack',
    'user': 'postgres',
    'password': 'Admin',
    'host': 'localhost',
    'port': '5432'
}

neo4j_uri = "bolt://localhost:7687"
neo4j_user = "neo4j"
neo4j_password = "Sonicaqq11!?"

pg_conn = psycopg.connect(**pg_conn_params)

def extract_data(query):
    return pd.read_sql_query(query, pg_conn)

medications_df = extract_data("SELECT * FROM \"Medications\"")
supplier_df = extract_data("SELECT * FROM \"Supplier\"")
employee_df = extract_data("SELECT * FROM \"Employee\"")
inventory_df = extract_data("SELECT * FROM \"Inventory\"")
customer_df = extract_data("SELECT * FROM \"Customer\"")
sales_df = extract_data("SELECT * FROM \"Sales\"")
sales_description_df = extract_data("SELECT * FROM \"Sales_description\"")
expired_medications_df = extract_data("SELECT * FROM \"Expired_medications\"")

driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

def create_node(tx, label, properties):
    query = f"CREATE (n:{label} {{"
    query += ", ".join([f"{key}: ${key}" for key in properties.keys()])
    query += "})"
    print(f"Executing query: {query} with properties: {properties}")
    tx.run(query, **properties)

def create_relationship(tx, from_label, from_id, rel_type, to_label, to_id):
    query = (f"MATCH (a:{from_label} {{id: $from_id}}), (b:{to_label} {{id: $to_id}}) "
             f"CREATE (a)-[r:{rel_type}]->(b)")
    print(f"Executing query: {query} with from_id: {from_id}, to_id: {to_id}")
    tx.run(query, from_id=from_id, to_id=to_id)

with driver.session() as session:
    for _, row in medications_df.iterrows():
        session.write_transaction(create_node, "Medication", row.to_dict())

    for _, row in supplier_df.iterrows():
        session.write_transaction(create_node, "Supplier", row.to_dict())

    for _, row in employee_df.iterrows():
        session.write_transaction(create_node, "Employee", row.to_dict())

    for _, row in customer_df.iterrows():
        session.write_transaction(create_node, "Customer", row.to_dict())

    for _, row in inventory_df.iterrows():
        session.write_transaction(create_relationship, "Supplier", row["supplier_id"], "SUPPLIES", "Medication", row["medication_id"])

    for _, row in sales_df.iterrows():
        session.write_transaction(create_node, "Sale", row.to_dict())
        session.write_transaction(create_relationship, "Sale", row["sales_id"], "INCLUDES", "Customer", row["customer_id"])
        session.write_transaction(create_relationship, "Sale", row["sales_id"], "HANDLED_BY", "Employee", row["employee_id"])

    for _, row in sales_description_df.iterrows():
        session.write_transaction(create_relationship, "Sale", row["sales_id"], "INCLUDES", "Medication", row["medication_id"])

    for _, row in expired_medications_df.iterrows():
        session.write_transaction(create_relationship, "Medication", row["medication_id"], "EXPIRED_ON", "Date", row["expiration_date"])

pg_conn.close()
driver.close()
