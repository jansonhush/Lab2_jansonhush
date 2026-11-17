import csv
import sys
import os

PASS_MARK = 50
TOTAL_WEIGHT = 100
FORMATIVE_WEIGHT = 60
SUMMATIVE_WEIGHT = 40
MAX_GPA = 5.0


def load_csv_data():
    """
    Prompts the user for a filename, checks if it exists, 
    and extracts all fields into a list of dictionaries.
    """
    filename = input("Enter the name of the CSV file to process (e.g., grades.csv): ").strip()

    if not os.path.exists(filename):
        print(f"Error: The file '{filename}' was not found.")
        sys.exit(1)

    assignments = []

    try:
        with open(filename, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            line_number = 1
            for row in reader:
                line_number = line_number + 1
                try:
                    assignments.append({
                        'assignment': row['assignment'].strip(),
                        'group': row['group'].strip(),
                        'score': float(row['score']),
                        'weight': float(row['weight'])
                    })
                except ValueError:
                    print(f"Error on line {line_number}: 'score' and 'weight' must be numbers "
                          f"(e.g., 85 or 72.5), but got score='{row['score']}', weight='{row['weight']}'.")
                    sys.exit(1)
                except Exception:
                    print(f"Error on line {line_number}: the row is incomplete. "
                          "Expected columns: assignment,group,score,weight")
                    sys.exit(1)
        return assignments
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        sys.exit(1)


def evaluate_grades(data):
    """
    'data' is a list of dictionaries containing the assignment records.
    """
    print("\n--- Processing Grades ---")

    if len(data) == 0:
        print("Error: No assignment records found. The file is empty "
              "(did organizer.sh just reset grades.csv?).")
        return

    # a) Check that all scores are percentages (0-100)
    invalid_scores = []
    for item in data:
        valid = item['score'] >= 0 and item['score'] <= 100
        if not valid:
            invalid_scores.append(item)

    if len(invalid_scores) > 0:
        print("Error: Every score must be between 0 and 100. Invalid scores found:")
        for item in invalid_scores:
            print(f"  - {item['assignment']}: {item['score']}")
        return

    # b) Validate weights (Total = 100, Formative = 60, Summative = 40)
    total_weight = 0
    formative_weight = 0
    summative_weight = 0
    unknown_groups = []

    for item in data:
        group = item['group'].lower()
        if item['weight'] < 0:
            print(f"Error: '{item['assignment']}' has a negative weight ({item['weight']}).")
            return
        total_weight = total_weight + item['weight']
        if group == 'formative':
            formative_weight = formative_weight + item['weight']
        elif group == 'summative':
            summative_weight = summative_weight + item['weight']
        else:
            unknown_groups.append(item)

    if len(unknown_groups) > 0:
        print("Error: The 'group' column must be either 'Formative' or 'Summative'. Found:")
        for item in unknown_groups:
            print(f"  - {item['assignment']}: '{item['group']}'")
        return

    weight_errors = []
    if round(total_weight, 2) != TOTAL_WEIGHT:
        weight_errors.append(f"Total weight is {total_weight}, expected {TOTAL_WEIGHT}.")
    if round(formative_weight, 2) != FORMATIVE_WEIGHT:
        weight_errors.append(f"Formative weight is {formative_weight}, expected {FORMATIVE_WEIGHT}.")
    if round(summative_weight, 2) != SUMMATIVE_WEIGHT:
        weight_errors.append(f"Summative weight is {summative_weight}, expected {SUMMATIVE_WEIGHT}.")

    if len(weight_errors) > 0:
        print("Error: Invalid weights.")
        for message in weight_errors:
            print(f"  - {message}")
        return

    # c) Calculate the final grade and GPA
    formative_earned = 0
    summative_earned = 0

    for item in data:
        weighted_score = item['score'] * item['weight'] / 100
        if item['group'].lower() == 'formative':
            formative_earned = formative_earned + weighted_score
        else:
            summative_earned = summative_earned + weighted_score

    total_grade = formative_earned + summative_earned
    gpa = (total_grade / 100) * MAX_GPA

    formative_percent = formative_earned / FORMATIVE_WEIGHT * 100
    summative_percent = summative_earned / SUMMATIVE_WEIGHT * 100

    # d) Pass/Fail: at least 50% in BOTH categories
    if formative_percent >= PASS_MARK and summative_percent >= PASS_MARK:
        status = "PASSED"
    else:
        status = "FAILED"

    # e) Failed formative assignments (below 50%) with the highest weight
    failed_formative = []
    for item in data:
        if item['group'].lower() == 'formative' and item['score'] < PASS_MARK:
            failed_formative.append(item)

    resubmit = []
    if len(failed_formative) > 0:
        highest_weight = failed_formative[0]['weight']
        for item in failed_formative:
            if item['weight'] > highest_weight:
                highest_weight = item['weight']
        for item in failed_formative:
            if item['weight'] == highest_weight:
                resubmit.append(item)

    # f) Print the final decision and resubmission options
    print(f"Formative: {round(formative_earned, 2)} / {FORMATIVE_WEIGHT} ({round(formative_percent, 2)}%)")
    print(f"Summative: {round(summative_earned, 2)} / {SUMMATIVE_WEIGHT} ({round(summative_percent, 2)}%)")
    print(f"Total Grade: {round(total_grade, 2)} / 100")
    print(f"GPA: {round(gpa, 4)} / {MAX_GPA}")
    print(f"Final Status: {status}")

    if len(resubmit) > 0:
        print("\nEligible for resubmission (failed formative with the highest weight):")
        for item in resubmit:
            print(f"  - {item['assignment']} (score: {item['score']}%, weight: {item['weight']})")
    else:
        print("\nNo failed formative assignments. No resubmission needed.")


if __name__ == "__main__":
    course_data = load_csv_data()
    evaluate_grades(course_data)