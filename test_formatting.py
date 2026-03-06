#!/usr/bin/env python3
"""Quick test for report formatting"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import json
import re
import os

# Get API key from environment
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ GOOGLE_API_KEY not set")
    exit(1)

# Test task
test_task = "checked ia 1 papers"

# Create prompt (same as in routes.py)
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a professional report formatter. Convert brief task notes into properly formatted report entries.

CRITICAL RULES:
1. Format ONLY the tasks provided - DO NOT invent additional tasks
2. The number of output tasks must EXACTLY match the number of input tasks
3. DO NOT add, invent, or generate tasks based on abbreviations or context

FORMAT REQUIREMENTS:
- Title: Professional description of what was done (capitalize properly)
- Description: 1-2 sentences in first person explaining the task in detail

ABBREVIATION RULES:
- Keep abbreviations EXACTLY as written (IA, BE, GITS, etc.)
- DO NOT expand unless universally known (PhD, Dr., etc.)

EXAMPLES:

Input: "checked ia 1 papers"
Output:
{
  "title": "Task 01: Checked IA 1 Papers",
  "description": "I reviewed and evaluated the IA 1 examination papers. This involved checking student responses and preparing for grading."
}

Input: "done with lectures"
Output:
{
  "title": "Task 01: Completed Lectures",
  "description": "I finished conducting my scheduled lecture sessions for the day."
}

Input: "GITS meeting attended"
Output:
{
  "title": "Task 01: Attended GITS Meeting",
  "description": "I participated in the GITS committee meeting and contributed to the discussions."
}

Return ONLY a JSON array. Number tasks as Task 01, Task 02, etc."""),
    ("user", "Format these {task_count} task(s):\n\n{tasks}\n\nReturn JSON array with exactly {task_count} formatted task(s).")
])

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    temperature=0.1,
    google_api_key=api_key,
)

# Format input
tasks_text = f"1. {test_task}"
task_count = 1

print(f"Input: '{test_task}'")
print("=" * 60)

try:
    chain = prompt | llm
    result = chain.invoke({"tasks": tasks_text, "task_count": task_count})

    print("AI Response:")
    print(result.content)
    print("=" * 60)

    # Parse JSON
    json_match = re.search(r'\[.*\]', result.content, re.DOTALL)
    if json_match:
        formatted_data = json.loads(json_match.group())

        print("\nParsed Output:")
        for item in formatted_data:
            print(f"Title: {item['title']}")
            print(f"Description: {item['description']}")
            print()

        if len(formatted_data) == 1:
            print("✅ SUCCESS: Got exactly 1 task with proper formatting")
        else:
            print(f"❌ FAILED: Got {len(formatted_data)} tasks instead of 1")
    else:
        print("❌ FAILED: Could not find JSON in response")

except Exception as e:
    print(f"❌ ERROR: {e}")
