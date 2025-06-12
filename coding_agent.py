# coding_agent.py (Upgraded with Interactive Apply)
import argparse
import os
from gemini_core import call_gemini

# --- System Prompt and helper functions are the same ---
SYSTEM_PROMPT = """
You are an expert pair-programming assistant.
You will be given the full content of a code file and a user request for a change.
Your task is to generate ONLY the new or modified code block that fulfills the request.
Do not output the entire file's content again.
Do not include any explanations, conversational text, or markdown formatting like ```python.
Output only the raw code. If you are modifying a function, provide the entire new function definition.
"""

def read_file_content(file_path: str) -> str | None:
    # ... (this function is unchanged)
    if not os.path.exists(file_path):
        print(f"Error: File not found at '{file_path}'")
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def construct_final_prompt(user_request: str, file_content: str) -> str:
    # ... (this function is unchanged)
    return f"""{SYSTEM_PROMPT}

--- START OF FILE CONTENT ---
{file_content}
--- END OF FILE CONTENT ---

--- USER REQUEST ---
{user_request}
--- END OF USER REQUEST ---

Based on the file content and the user request, generate the required code block now:
"""

# --- NEW HELPER FUNCTION TO APPLY CHANGES ---
def get_original_function_name(code_block: str) -> str | None:
    """A simple way to extract the function name from a 'def' line."""
    lines = code_block.strip().split('\n')
    if lines and lines[0].strip().startswith("def "):
        # e.g., from "def my_function(arg1, arg2):" get "my_function"
        return lines[0].split("def ")[1].split("(")[0].strip()
    return None

def apply_changes(file_path: str, original_content: str, new_code: str) -> bool:
    """Replaces an old function with the new code block."""
    original_func_name = get_original_function_name(new_code)
    if not original_func_name:
        print("❌ Could not determine function name from AI suggestion. Cannot apply changes automatically.")
        return False
        
    lines = original_content.split('\n')
    new_lines = []
    in_function_to_replace = False
    function_replaced = False

    for line in lines:
        # Check if we found the start of the function we want to replace
        if line.strip().startswith(f"def {original_func_name}("):
            if not function_replaced:
                new_lines.extend(new_code.split('\n')) # Add the new function
                in_function_to_replace = True
                function_replaced = True
            else: # If function with same name appears again, keep it
                new_lines.append(line)

        # Skip all other lines of the old function
        elif in_function_to_replace:
            if line.strip() == "" or line.startswith(" "):
                continue
            else:
                in_function_to_replace = False
                new_lines.append(line)
        else:
            new_lines.append(line)

    if not function_replaced:
        print("❌ Could not find the original function to replace in the file.")
        return False

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(new_lines))
        return True
    except Exception as e:
        print(f"❌ Error writing changes to file: {e}")
        return False

# --- main() is now upgraded ---
def main():
    parser = argparse.ArgumentParser(description="An interactive AI coding agent.")
    parser.add_argument("file", help="The path to the code file to modify.")
    parser.add_argument("prompt", help="Your instructions for the agent.")
    args = parser.parse_args()

    print(f"▶️  Agent starting...")
    
    # 1. Read the original file
    file_content = read_file_content(args.file)
    if file_content is None: return

    # 2. Get the AI's suggestion
    final_prompt = construct_final_prompt(args.prompt, file_content)
    print("\n[INFO] Sending request to Gemini...")
    suggested_code = call_gemini(prompt=final_prompt)
    
    print("\n✅ --- Gemini's Suggested Code ---")
    print(suggested_code)
    print("---------------------------------\n")

    # 3. Ask for confirmation
    choice = input("Apply this change to the file? (y/n): ").lower()
    if choice == 'y':
        print("[INFO] Applying changes...")
        if apply_changes(args.file, file_content, suggested_code):
            print(f"✅ Changes successfully applied to {args.file}!")
        else:
            print("Changes were not applied due to an error.")
    else:
        print("Agent finished. No changes were made to the file.")

if __name__ == '__main__':
    main()