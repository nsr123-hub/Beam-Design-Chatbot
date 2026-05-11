from dotenv import load_dotenv
import google.generativeai as genai
import json
import os
import re
from calculator_2 import design_rc_beam_chatbot_entry

# =========================================================
# CONFIGURATION
# =========================================================

# ✅ Use environment variable
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
load_dotenv()
key = os.getenv("GEMINI_API_KEY")

# check api 

if key:
    print("API key found")
    print(key[:10] + "...")
else:
    print("API key not found")

genai.configure(api_key=key)


model = genai.GenerativeModel("gemini-2.5-flash")

# =========================================================
# VALIDATION
# =========================================================

REQUIRED_KEYS = ["L", "w", "fck", "fy", "b", "d"]

DEFAULTS = {
    "fy": 415,
    "b": 300,
    "d": 500
}

LIMITS = {
    "L": (1, 20),
    "w": (1, 500),
    "fck": (15, 80),
    "fy": (250, 600),
    "b": (150, 1500),
    "d": (150, 3000)
}


def validate_inputs(data):
    """
    Validate engineering ranges.
    """
    for key in REQUIRED_KEYS:
        if key not in data:
            return False

        value = data[key]

        if not isinstance(value, (int, float)):
            return False

        min_val, max_val = LIMITS[key]

        if not (min_val <= value <= max_val):
            return False

    return True


# =========================================================
# STEP 1: INPUT EXTRACTION
# =========================================================

def extract_json(text):
    """
    Extract JSON safely from LLM response.
    """
    match = re.search(r'\{.*\}', text, re.DOTALL)

    if not match:
        return None

    try:
        return json.loads(match.group())
    except:
        return None


def extract_inputs(user_prompt):
    """
    Convert natural language into structured beam input.
    """

    extraction_prompt = f"""
    You are an expert civil structural engineer.

    Extract these RCC beam design parameters:

    - L  = span in meters
    - w  = load in kN/m
    - fck = concrete grade in MPa
    - fy  = steel grade in MPa
    - b   = beam width in mm
    - d   = effective depth in mm

    Return ONLY valid JSON.

    Example:
    {{
        "L": 6,
        "w": 25,
        "fck": 25,
        "fy": 415,
        "b": 300,
        "d": 500
    }}

    User Input:
    {user_prompt}
    """

    try:
        response = model.generate_content(extraction_prompt)

        data = extract_json(response.text)

        if not data:
            return None

        # Apply defaults
        for key, value in DEFAULTS.items():
            data.setdefault(key, value)

        # Convert values to float
        for key in REQUIRED_KEYS:
            data[key] = float(data[key])

        # Validate
        if not validate_inputs(data):
            return None

        return data

    except Exception as e:
        print("Extraction Error:", e)
        return None


# =========================================================
# STEP 2: EXPLAIN RESULTS
# =========================================================

def explain_results(user_prompt, data, result):
    """
    Generate conversational engineering explanation.
    """

    if "error" in result:
        return f"Design calculation failed: {result['error']}"

    explanation_prompt = f"""
    You are a professional Structural Engineer AI assistant.

    USER REQUEST:
    {user_prompt}

    INPUT DATA:
    {json.dumps(data, indent=2)}

    CALCULATION RESULT:
    {json.dumps(result, indent=2)}

    Generate a concise conversational explanation.

    Rules:
    - Maximum 6 sentences.
    - Mention:
        1. Beam safety
        2. Ultimate moment
        3. Reinforcement provided
        4. Shear condition
        5. Important warnings if unsafe
    - If unsafe, clearly explain WHY.
    - Mention practical engineering suggestions.
    - Sound professional but friendly.
    - Avoid repeating raw JSON.
    """

    try:
        response = model.generate_content(explanation_prompt)
        return response.text.strip()

    except Exception as e:
        print("Explanation Error:", e)

        return (
            f"Beam Design Status: {result['design_status']}\n"
            f"Ultimate Moment: {result['ultimate_moment_kNm']} kN·m\n"
            f"Reinforcement: {result['reinforcement']}\n"
            f"Shear: {result['shear_status']}"
        )


# =========================================================
# STEP 3: PRETTY PRINT TECHNICAL OUTPUT
# =========================================================

def display_result(result):
    """
    Clean engineering output formatting.
    """

    print("\n================ RCC BEAM DESIGN ================\n")

    print(f"Ultimate Moment      : {result['ultimate_moment_kNm']} kN·m")
    print(f"Limiting Moment      : {result['limiting_moment_kNm']} kN·m")
    print(f"Reinforcement        : {result['reinforcement']}")
    print(f"Shear Status         : {result['shear_status']}")
    print(f"Design Status        : {result['design_status']}")

    print("\n--- Explanation ---")

    for key, value in result["explanation"].items():
        print(f"{key.capitalize():<12}: {value}")

    if result["suggestions"]:
        print("\n--- Suggestions ---")

        for i, suggestion in enumerate(result["suggestions"], start=1):
            print(f"{i}. {suggestion}")

    print("\n=================================================\n")


# =========================================================
# MAIN CHATBOT LOOP
# =========================================================

# def beam_chatbot():

    print("\n========================================")
    print("      RCC Beam Design AI Assistant")
    print("========================================")
    print("Type 'exit' to quit.\n")

    while True:

        user_input = input("You: ").strip()

        if user_input.lower() in ["exit", "quit"]:
            print("\nGoodbye Engineer 👷\n")
            break

        # -------------------------------------
        # Extract Inputs
        # -------------------------------------

        data = extract_inputs(user_input)

        if not data:
            print(
                "\nBot: I couldn't extract complete beam parameters.\n"
                "Please specify:\n"
                "- Span (L)\n"
                "- Load (w)\n"
                "- Concrete grade (fck)\n"
                "- Steel grade (fy)\n"
                "- Beam width (b)\n"
                "- Effective depth (d)\n"
            )
            continue

        # -------------------------------------
        # Perform Design
        # -------------------------------------

        result = design_rc_beam_chatbot_entry(data)

        # -------------------------------------
        # Show Technical Output
        # -------------------------------------

        display_result(result)

        # -------------------------------------
        # Conversational AI Response
        # -------------------------------------

        explanation = explain_results(user_input, data, result)

        print("AI Engineer:\n")
        print(explanation)
        print()


# =========================================================
# ENTRY POINT
# =========================================================

# flask

def process_user_message(user_input):

    # Extract Inputs
    data = extract_inputs(user_input)

    if not data:
        return {
            "success": False,
            "response": (
                "I couldn't extract complete beam parameters.\n"
                "Please specify:\n"
                "- Span (L)\n"
                "- Load (w)\n"
                "- Concrete grade (fck)\n"
                "- Steel grade (fy)\n"
                "- Beam width (b)\n"
                "- Effective depth (d)"
            )
        }

    # Perform Design
    result = design_rc_beam_chatbot_entry(data)

    # AI Explanation
    explanation = explain_results(user_input, data, result)

    return {
        "success": True,
        "input_data": data,
        "technical_result": result,
        "ai_response": explanation
    }