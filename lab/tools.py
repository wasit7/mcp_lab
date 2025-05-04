import os
import sqlite3
import pandas as pd
import logging

logger = logging.getLogger(__name__)

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'northwind.db'))

class ToolRegistry:
    def __init__(self):
        self.tools = []
        self.tool_functions = {}

    def register_tool(self, name, description, parameters, func):
        tool_schema = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters
            }
        }
        self.tools.append(tool_schema)
        self.tool_functions[name] = func

    def get_tools(self):
        return self.tools

    def get_tool_functions(self):
        return self.tool_functions

# Database connection function
def get_db_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        logger.error(f"Failed to connect to database: {e}")
        return None

# Tool functions
def get_customers_by_country(country):
    conn = get_db_connection()
    if conn is None:
        return {"error": "Database connection failed"}
    try:
        query = "SELECT CompanyName FROM Customers WHERE Country = ? LIMIT 10"
        df = pd.read_sql_query(query, conn, params=(country,))
        conn.close()
        if df.empty:
            return ["No customers found"]
        return df.to_markdown(index=False)
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        conn.close()
        return {"error": f"Database error: {e}"}

def get_orders_by_customer(customer_id):
    conn = get_db_connection()
    if conn is None:
        return {"error": "Database connection failed"}
    try:
        query = "SELECT OrderID, OrderDate, ShipCountry FROM Orders WHERE CustomerID = ? LIMIT 5"
        df = pd.read_sql_query(query, conn, params=(customer_id,))
        conn.close()
        if df.empty:
            return ["No orders found"]
        return df.to_markdown(index=False)
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        conn.close()
        return {"error": f"Database error: {e}"}

def get_products_by_category(category_name):
    conn = get_db_connection()
    if conn is None:
        return {"error": "Database connection failed"}
    try:
        query = """
        SELECT p.ProductName, p.UnitPrice, c.CategoryName
        FROM Products p
        JOIN Categories c ON p.CategoryID = c.CategoryID
        WHERE c.CategoryName = ?
        LIMIT 10
        """
        df = pd.read_sql_query(query, conn, params=(category_name,))
        conn.close()
        if df.empty:
            return ["No products found"]
        return df.to_markdown(index=False)
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        conn.close()
        return {"error": f"Database error: {e}"}

def get_employees_by_region(region):
    conn = get_db_connection()
    if conn is None:
        return {"error": "Database connection failed"}
    try:
        query = """
        SELECT e.FirstName, e.LastName, r.RegionDescription
        FROM Employees e
        JOIN EmployeeTerritories et ON e.EmployeeID = et.EmployeeID
        JOIN Territories t ON et.TerritoryID = t.TerritoryID
        JOIN Regions r ON t.RegionID = r.RegionID
        WHERE r.RegionDescription = ?
        LIMIT 10
        """
        df = pd.read_sql_query(query, conn, params=(region,))
        conn.close()
        if df.empty:
            return ["No employees found"]
        return df.to_markdown(index=False)
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        conn.close()
        return {"error": f"Database error: {e}"}

def get_suppliers_by_country(country):
    conn = get_db_connection()
    if conn is None:
        return {"error": "Database connection failed"}
    try:
        query = "SELECT CompanyName, ContactName, Country FROM Suppliers WHERE Country = ? LIMIT 10"
        df = pd.read_sql_query(query, conn, params=(country,))
        conn.close()
        if df.empty:
            return ["No suppliers found"]
        return df.to_markdown(index=False)
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        conn.close()
        return {"error": f"Database error: {e}"}

# Initialize the ToolRegistry
registry = ToolRegistry()

# Register tools
registry.register_tool(
    name="get_customers_by_country",
    description="Retrieve a list of customers from a specified country",
    parameters={
        "type": "object",
        "properties": {
            "country": {"type": "string", "description": "The country to filter customers by"}
        },
        "required": ["country"]
    },
    func=get_customers_by_country
)

registry.register_tool(
    name="get_orders_by_customer",
    description="Retrieve all orders placed by a specific customer",
    parameters={
        "type": "object",
        "properties": {
            "customer_id": {"type": "string", "description": "The ID of the customer"}
        },
        "required": ["customer_id"]
    },
    func=get_orders_by_customer
)

registry.register_tool(
    name="get_products_by_category",
    description="Retrieve all products in a specific category",
    parameters={
        "type": "object",
        "properties": {
            "category_name": {"type": "string", "description": "The name of the category"}
        },
        "required": ["category_name"]
    },
    func=get_products_by_category
)

registry.register_tool(
    name="get_employees_by_region",
    description="Retrieve all employees working in a specific region",
    parameters={
        "type": "object",
        "properties": {
            "region": {"type": "string", "description": "The region to filter employees by"}
        },
        "required": ["region"]
    },
    func=get_employees_by_region
)

registry.register_tool(
    name="get_suppliers_by_country",
    description="Retrieve all suppliers from a specified country",
    parameters={
        "type": "object",
        "properties": {
            "country": {"type": "string", "description": "The country to filter suppliers by"}
        },
        "required": ["country"]
    },
    func=get_suppliers_by_country
)

# Function to get the registry for dependency injection
def get_tool_registry():
    return registry