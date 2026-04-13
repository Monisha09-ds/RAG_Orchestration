import logging
import sys

# Configure logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
from graph_rag.controller import handle_question

print("--- Starting Strict Grounding Verification ---")
try:
    # 1. Test Known Fact (Should return concise answer)
    q1 = "What skills does she have?"
    print(f"\nQ: {q1}")
    ans1 = handle_question(q1)
    print(f"A: {ans1}")
    
    # 2. Test Missing Fact (Should return strict refusal)
    # Asking something random that shouldn't be in the portfolio
    q2 = "What is her favorite color?"
    print(f"\nQ: {q2}")
    ans2 = handle_question(q2)
    print(f"A: {ans2}")

    # 3. Test Intent Scoping (Check logs for 'Intent: PROJECTS')
    q3 = "Tell me about her projects."
    print(f"\nQ: {q3}")
    ans3 = handle_question(q3)
    print(f"A: {ans3}")

except Exception as e:
    print(f"❌ Verification failed: {e}")
