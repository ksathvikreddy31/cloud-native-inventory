from services import sql_service, mongo_service

def execute(module, action, data):
    db_type = data.get("db", "sql")
    
    # Auth and Godown are ALWAYS SQL
    if module in ["godown", "auth"]:
        return sql_service.execute_action(module, action, data)
        
    if db_type == "mongo":
        return mongo_service.execute_action(module, action, data)
    else:
        return sql_service.execute_action(module, action, data)