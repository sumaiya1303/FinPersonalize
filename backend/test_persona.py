from app.services import calculate_persona

def test_persona_logic():
    print("--- Testing Persona Calculation Logic ---")

    # Test Case 1: Low Score (< 40)
    # Answers: 10 + 10 + 5 = 25
    answers_low = {'q1': 10, 'q2': 10, 'q3': 5}
    score_low, persona_low = calculate_persona(answers_low)
    print(f"Test 1 (Low): Score={score_low}, Persona={persona_low}")
    assert score_low == 25
    assert persona_low == 'Conservative Protector'

    # Test Case 2: Medium Score (40-70)
    # Answers: 20 + 20 + 10 = 50
    answers_med = {'q1': 20, 'q2': 20, 'q3': 10}
    score_med, persona_med = calculate_persona(answers_med)
    print(f"Test 2 (Medium): Score={score_med}, Persona={persona_med}")
    assert score_med == 50
    assert persona_med == 'Balanced Strategist'

    # Test Case 3: High Score (> 70)
    # Answers: 30 + 30 + 20 = 80
    answers_high = {'q1': 30, 'q2': 30, 'q3': 20}
    score_high, persona_high = calculate_persona(answers_high)
    print(f"Test 3 (High): Score={score_high}, Persona={persona_high}")
    assert score_high == 80
    assert persona_high == 'Growth Seeker'

    print("\nAll tests passed successfully!")

if __name__ == "__main__":
    test_persona_logic()
