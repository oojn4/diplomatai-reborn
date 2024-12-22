import json
from app.func_call.Functions import FunctionsTools

market_intelligence_func = json.loads(open("app/func_call/market_intelligence_function_middleware.json", "r").read())
chatbot_func = json.loads(open("app/func_call/chatbot_function_middleware.json", "r").read())