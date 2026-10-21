"""Student Marks Management System - command-line edition.

Stores one record per student ID and subject in students.csv.
Run: python student_manager.py
"""

import csv
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "students.csv"
FIELDS = ["student_id", "name", "subject", "marks"]


def load_records():
    """Load saved records. Return an empty list if the file does not exist."""
    if not DATA_FILE.exists():
        return []
    with DATA_FILE.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames or not set(FIELDS).issubset(reader.fieldnames):
            raise ValueError("CSV file is missing required columns.")
        records = []
        for row in reader:
            records.append({key: row[key] for key in FIELDS})
        return records


def save_records(records):
    """Write every record to the CSV file."""
    with DATA_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)


def calculate_grade(marks):
    """Example grading thresholds; adjust to your institution's policy."""
    marks = float(marks)
    if marks >= 75:
        return "A"
    if marks >= 65:
        return "B"
    if marks >= 50:
        return "C"
    if marks >= 35:
        return "S"
    return "F"


def valid_marks(value):
    try:
        marks = float(value)
    except (ValueError, TypeError):
        raise ValueError("Marks must be a number.") from None
    if not 0 <= marks <= 100:
        raise ValueError("Marks must be between 0 and 100.")
    return marks


def find_index(records, student_id, subject):
    for i, record in enumerate(records):
        if (record["student_id"].casefold() == student_id.casefold()
                and record["subject"].casefold() == subject.casefold()):
            return i
    return None


def add_record(records, student_id, name, subject, marks):
    student_id, name, subject = student_id.strip(), name.strip(), subject.strip()
    if not all((student_id, name, subject)):
        raise ValueError("ID, name, and subject are required.")
    score = valid_marks(marks)
    if find_index(records, student_id, subject) is not None:
        raise ValueError("A record with that student ID and subject already exists.")
    records.append({"student_id": student_id, "name": name,
                    "subject": subject, "marks": f"{score:g}"})
    save_records(records)


def update_record(records, student_id, subject, name, marks):
    index = find_index(records, student_id.strip(), subject.strip())
    if index is None:
        raise ValueError("Record not found.")
    if not name.strip():
        raise ValueError("Name is required.")
    score = valid_marks(marks)
    records[index]["name"] = name.strip()
    records[index]["marks"] = f"{score:g}"
    save_records(records)


def delete_record(records, student_id, subject):
    index = find_index(records, student_id.strip(), subject.strip())
    if index is None:
        raise ValueError("Record not found.")
    del records[index]
    save_records(records)


def print_records(records):
    if not records:
        print("No matching records.")
        return
    print(f"{'Student ID':<15} {'Name':<24} {'Subject':<20} {'Marks':>7}  Grade")
    print("-" * 78)
    for r in records:
        print(f"{r['student_id']:<15.15} {r['name']:<24.24} "
              f"{r['subject']:<20.20} {float(r['marks']):>7g}  "
              f"{calculate_grade(r['marks'])}")


def show_statistics(records):
    if not records:
        print("No records to analyze.")
        return
    scores = [float(r["marks"]) for r in records]
    print(f"Records: {len(records)}")
    print(f"Average mark: {sum(scores) / len(scores):.2f}")
    print(f"Highest mark: {max(scores):g}")
    print(f"Lowest mark: {min(scores):g}")


def main():
    try:
        records = load_records()
    except (OSError, ValueError, KeyError) as error:
        print(f"Cannot load records: {error}")
        return
    while True:
        print("\n=== STUDENT MARKS MANAGEMENT ===")
        print("1. Add record\n2. View all\n3. Search by ID\n4. Update record")
        print("5. Delete record\n6. Statistics\n7. Exit")
        choice = input("Select 1-7: ").strip()
        try:
            if choice == "1":
                add_record(records, input("Student ID: "), input("Name: "),
                           input("Subject: "), input("Marks (0-100): "))
                print("Record saved.")
            elif choice == "2":
                print_records(records)
            elif choice == "3":
                student_id = input("Student ID to find: ").strip()
                print_records([r for r in records if r["student_id"].casefold() == student_id.casefold()])
            elif choice == "4":
                student_id = input("Student ID: ")
                subject = input("Subject: ")
                name = input("New name: ")
                marks = input("New marks (0-100): ")
                update_record(records, student_id, subject, name, marks)
                print("Record updated.")
            elif choice == "5":
                student_id = input("Student ID: ")
                subject = input("Subject: ")
                if input("Delete this record? (y/N): ").strip().lower() == "y":
                    delete_record(records, student_id, subject)
                    print("Record deleted.")
                else:
                    print("Deletion cancelled.")
            elif choice == "6":
                show_statistics(records)
            elif choice == "7":
                print("Goodbye!")
                break
            else:
                print("Please choose a number from 1 to 7.")
        except (ValueError, OSError) as error:
            print(f"Error: {error}")
            # Reload after a failed file write so memory and disk agree.
            try:
                records = load_records()
            except (OSError, ValueError, KeyError):
                print("Please check the CSV file before continuing.")
                break


if __name__ == "__main__":
    main()
