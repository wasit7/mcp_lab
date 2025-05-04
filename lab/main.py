import json
import requests
import logging
from tools import ToolRegistry

# Set DEBUG_MODE to True for debug mode, False for production mode
DEBUG_MODE = False  # Toggle this to False for production mode

# Configure logging based on mode
if DEBUG_MODE:
    logging_level = logging.DEBUG
else:
    logging_level = logging.INFO

logging.basicConfig(level=logging_level)
logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434"

# MODEL = "qwen2.5"
MODEL = "llama3.2"

def check_ollama():
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        response.raise_for_status()
        models = [model["name"] for model in response.json().get("models", [])]
        if f"{MODEL}:latest" not in models:
            logger.error(f"Model {MODEL} not found in Ollama")
            return False
        return True
    except requests.RequestException as e:
        logger.error(f"Ollama API not available: {e}")
        return False

def get_tool_call(query, tool_registry):
    if not check_ollama():
        return None, {"error": f"Ollama API or model {MODEL} unavailable"}
    try:
        print(f" Processing query: {query}")
        
        # Get tools from registry
        tools = tool_registry.get_tools()
        
        # Send query to Ollama API for tool selection
        response = requests.post(f"{OLLAMA_URL}/api/chat", json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "Please get query from user response in English"},
                {"role": "user", "content": query+"\n\n Please query in English"}
            ],
            "tools": tools,
            "stream": False
        }, timeout=30)
        response.raise_for_status()
        result = response.json()
        if DEBUG_MODE:
            logger.debug(f"Ollama response: {json.dumps(result, indent=2)}")
        
        message = result.get("message", {})
        tool_calls = message.get("tool_calls", [])
        
        if not tool_calls:
            print(" ❌ No tool calls identified")
            return None, {"message": "No specific tool required for this query. Please refine your query or check tool availability."}
        
        tool_call = tool_calls[0]
        function = tool_call.get("function", {})
        tool_name = function.get("name")
        arguments = function.get("arguments", {})
        
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse arguments: {e}")
                raise ValueError(f"Failed to parse arguments: {e}")
        elif not isinstance(arguments, dict):
            logger.error(f"Invalid arguments type: {type(arguments)}")
            return None, {"error": f"Invalid arguments type: {type(arguments)}"}
        
        print(f" ✅ Selected tool: {tool_name}, Arguments: {arguments}")
        return tool_name, arguments
    except requests.RequestException as e:
        logger.error(f"Ollama API error: {e}")
        return None, {"error": str(e)}

def call_mcp_tool(tool_name, params, tool_registry):
    tool_functions = tool_registry.get_tool_functions()
    if tool_name in tool_functions:
        try:
            return tool_functions[tool_name](**params)
        except Exception as e:
            logger.error(f"Tool execution failed for {tool_name}: {e}")
            return {"error": f"Tool execution failed: {e}"}
    logger.warning(f"Unknown tool: {tool_name}")
    return {"error": f"Unknown tool: {tool_name}"}

def get_final_response(tool_response, original_query):
    if isinstance(tool_response, dict) and "error" in tool_response:
        return tool_response["error"]
    try:
        messages = [
            {"role": "user", "content": original_query},
            {"role": "assistant", "content": "Here is the result from the tool:"},
            {"role": "user", "content": f"Tool output:\n\n{tool_response}\n\nPresent this in the original format."}
        ]
        response = requests.post(f"{OLLAMA_URL}/api/chat", json={
            "model": MODEL,
            "messages": messages,
            "stream": False
        }, timeout=60)
        response.raise_for_status()
        result = response.json()
        if DEBUG_MODE:
            logger.debug(f"Ollama final response: {json.dumps(result, indent=2)}")
        return result.get("message", {}).get("content", "No content returned")
    except requests.RequestException as e:
        logger.error(f"Error generating final response: {e}")
        return f"Error generating final response: {e}"

def process_query(query, tool_registry):
    try:
        tool_name, params = get_tool_call(query, tool_registry)
        if tool_name:
            tool_response = call_mcp_tool(tool_name, params, tool_registry)
            final_response = get_final_response(tool_response, query)
        else:
            final_response = params.get("message", "Unable to process query")
    except Exception as e:
        logger.error(f"Error processing query '{query}': {e}")
        final_response = f"Error processing query: {e}"
        print(final_response)
    return final_response

if __name__ == "__main__":
    from tools import get_tool_registry
    tool_registry = get_tool_registry()
    
    logger.info("Starting MCP Server...")
    # print("Starting MCP Server...")
    queries = [
        # "List all customers from France", # def get_customers_by_country(country):
        # "List all orders for customer id VINET", # def get_orders_by_customer(customer_id):
        # "Retrieve orders for customer id TOMSP", # def get_orders_by_customer(customer_id):
        # "List products in the Condiments category", # def get_products_by_category(category_name):
        # "Show products in the Beverages category", # def get_products_by_category(category_name):
        # "List employees in the Eastern region", # def get_employees_by_region(region):
        # "Get suppliers from Germany", # def get_suppliers_by_country(country):
        # "Find suppliers in the UK", # def get_suppliers_by_country(country):
        "แสดงรายชื่อลูกค้าทั้งหมดจากฝรั่งเศส", # def get_customers_by_country(country):
        "แสดงรายชื่อคำสั่งซื้อทั้งหมดสำหรับรหัสลูกค้า VINET", # def get_orders_by_customer(customer_id):
        "เรียกค้นคำสั่งซื้อสำหรับรหัสลูกค้า TOMSP", # def get_orders_by_customer(customer_id):
        "แสดงรายชื่อผลิตภัณฑ์ในหมวดหมู่เครื่องปรุงรส", # def get_products_by_category(category_name):
        "แสดงรายชื่อผลิตภัณฑ์ในหมวดหมู่เครื่องดื่ม", # def get_products_by_category(category_name):
        "แสดงรายชื่อพนักงานในภูมิภาคตะวันออก", # def get_employees_by_region(region):
        "รับซัพพลายเออร์จากเยอรมนี", # def get_suppliers_by_country(country):
        "ค้นหาซัพพลายเออร์ในสหราชอาณาจักร"
    ]
    # query=queries[8]
    for i,query in enumerate(queries):
        print(f'\n🎯*** Query {i:02} ***')
        result = process_query(query, tool_registry)
        # print(f"Query: {query}")
        print(f"Result: {result}")