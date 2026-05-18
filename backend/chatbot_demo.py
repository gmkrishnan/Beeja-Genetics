import os
import sys
import json
import asyncio

# Path hack to ensure imports work
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from core.gemma import agent_chat
from core.agent import run_agent_loop
from result_manager import set_category_status, permanent_delete_category

SESSIONS_PATH = os.path.join(os.path.dirname(__file__), 'registry', 'chat_sessions.json')

def load_sessions():
    if os.path.exists(SESSIONS_PATH):
        with open(SESSIONS_PATH, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_sessions(sessions):
    os.makedirs(os.path.dirname(SESSIONS_PATH), exist_ok=True)
    with open(SESSIONS_PATH, "w") as f:
        json.dump(sessions, f, indent=4)

async def chatbot_loop():
    print("--- 🤖 BEEJA GENETIC SMART CHATBOT ---")
    print("Type 'exit' to quit, 'clear' to delete session.\n")
    
    sessions = load_sessions()
    session_id = "default_user"  # PoC uses a default session
    
    if session_id not in sessions:
        sessions[session_id] = [
            {"role": "system", "content": "You are the Beeja Genetic Assistant. You help users understand their genetics. If the user wants to research a NEW category (like 'Organ Strength' or 'Swimming'), you must ASK FOR CONFIRMATION before starting. Say: 'I can research that for you on PubMed and scan your DNA. It takes about 5 minutes. Should I proceed?' If they say yes, call the tool. Do not research on your own."}
        ]
        
    history = sessions[session_id]
    
    # Define the tools
    tools = [
        {
            "type": "function",
            "function": {
                "name": "trigger_agent",
                "description": "Triggers the Self-Evolving Agent to research a new category on PubMed and scan DNA.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category_name": {"type": "string", "description": "The name of the category to research (e.g., 'Learning Style')."},
                        "file_path": {"type": "string", "description": "The absolute path to the user's uploaded DNA file."}
                    },
                    "required": ["category_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "archive_category",
                "description": "Moves a discovered category to the archive.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category_name": {"type": "string"}
                    },
                    "required": ["category_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "trash_category",
                "description": "Moves a discovered category to the trash.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category_name": {"type": "string"}
                    },
                    "required": ["category_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_category",
                "description": "Permanently deletes a category from the trash.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category_name": {"type": "string"}
                    },
                    "required": ["category_name"]
                }
            }
        }
    ]
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            break
        elif user_input.lower() == 'clear':
            sessions[session_id] = [sessions[session_id][0]] # Keep system prompt
            save_sessions(sessions)
            print("Session cleared.")
            continue
            
        history.append({"role": "user", "content": user_input})
        
        print("Bot thinking...")
        response = await agent_chat(history, tools=tools)
        
        if "error" in response:
            print(f"Error: {response['error']}")
            continue
            
        message = response.get("message", {})
        
        # Check if the AI wants to call the tool
        if message.get("tool_calls"):
            tool_call = message["tool_calls"][0]
            function_name = tool_call["function"]["name"]
            arguments = json.loads(tool_call["function"]["arguments"])
            
            if function_name == "trigger_agent":
                category = arguments["category_name"]
                file_path = arguments.get("file_path")
                print(f"\n[SYSTEM] Triggering Agent for: {category}...")
                if file_path:
                    print(f"[SYSTEM] Using DNA file: {file_path}")
                print("[SYSTEM] This will take a few minutes. Running Agent...")
                
                goal = f"Analyze my genetic {category}. Research PubMed if needed, scan my DNA, and save the discovery."
                agent_result = await run_agent_loop(goal, dna_path=file_path)
                
                print(f"\n[SYSTEM] Agent Completed!")
                bot_reply = f"I have completed the research for '{category}'! The new category has been added to your vault. Here is the summary:\n\n{agent_result}"
                
                history.append({"role": "assistant", "content": bot_reply})
                print(f"\nBot: {bot_reply}")
                sessions[session_id] = history
                save_sessions(sessions)
                continue
                
            elif function_name == "archive_category":
                category = arguments["category_name"]
                result = set_category_status(category, "archived")
                bot_reply = result.get("success", result.get("error"))
                history.append({"role": "assistant", "content": bot_reply})
                print(f"\nBot: {bot_reply}")
                sessions[session_id] = history
                save_sessions(sessions)
                continue
                
            elif function_name == "trash_category":
                category = arguments["category_name"]
                result = set_category_status(category, "trash")
                bot_reply = result.get("success", result.get("error"))
                history.append({"role": "assistant", "content": bot_reply})
                print(f"\nBot: {bot_reply}")
                sessions[session_id] = history
                save_sessions(sessions)
                continue
                
            elif function_name == "delete_category":
                category = arguments["category_name"]
                result = permanent_delete_category(category)
                bot_reply = result.get("success", result.get("error"))
                history.append({"role": "assistant", "content": bot_reply})
                print(f"\nBot: {bot_reply}")
                sessions[session_id] = history
                save_sessions(sessions)
                continue
                
        # Normal conversation
        bot_reply = message.get("content", "I didn't understand that.")
        print(f"\nBot: {bot_reply}")
        
        # Append bot reply to history
        history.append({"role": "assistant", "content": bot_reply})
        
        # Save session
        sessions[session_id] = history
        save_sessions(sessions)

if __name__ == "__main__":
    asyncio.run(chatbot_loop())
