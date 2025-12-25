
import sys
import os

# Add parent directory to path to allow importing regex.validation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from regex.validation import validate_regex

def run_tests():
    test_cases = [
        # (Regex, IsValid, Description)
        ("ab", True, "Basic Concatenation"),
        ("a|b", True, "Basic Union"),
        ("a*", True, "Basic Star"),
        ("(a|b)*abb", True, "Complex Expression"),
        ("((a))", True, "Nested Parens"),
        
        ("", False, "Empty String"),
        ("a b", False, "Illegal Space"),
        ("a$", False, "Illegal Character"),
        
        ("(", False, "Unmatched Open"),
        (")", False, "Unmatched Close"),
        ("a)", False, "Unmatched Close Internal"),
        ("()", False, "Empty Parens"),
        ("(a|b))", False, "Unmatched Close Nested"),
        
        ("|a", False, "Union Start"),
        ("a|", False, "Union End"),
        ("(|a)", False, "Union after Open"),
        ("a|)", False, "Union before Close"),
        ("a||b", False, "Double Union"),
        ("a|*b", False, "Union then Star"),
        
        ("*a", False, "Star Start"),
        ("(*a)", False, "Star after Open"),
        ("a|*b", False, "Star after Union"), # Covered above but explicit here
        ("a**", False, "Double Star"),
    ]

    print("Running Regex Validation Tests...")
    all_passed = True
    
    for i, (regex, expected_valid, desc) in enumerate(test_cases):
        try:
            validate_regex(regex)
            is_valid = True
            error_msg = None
        except ValueError as e:
            is_valid = False
            error_msg = str(e)
            
        if is_valid == expected_valid:
            print(f"PASS: '{regex}' ({desc})")
        else:
            print(f"FAIL: '{regex}' ({desc}) - Expected {expected_valid}, Got {is_valid}")
            if error_msg:
                print(f"      Error: {error_msg}")
            all_passed = False

    if all_passed:
        print("\nAll validation tests PASSED!")
    else:
        print("\nSome tests FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
