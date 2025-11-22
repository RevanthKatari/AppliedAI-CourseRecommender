"""
Script to generate enrollments for new courses while maintaining realistic patterns.
"""
import csv
import random
from pathlib import Path

# Set random seed for reproducibility
random.seed(42)

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "synthetic"

# Read existing data
def read_csv(filename):
    with open(DATA_DIR / filename, 'r', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

def write_csv(filename, rows, fieldnames):
    with open(DATA_DIR / filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

# Read existing enrollments and students
enrollments = read_csv('enrollments.csv')
students = read_csv('students.csv')
courses = read_csv('courses.csv')

# Get new course IDs (the ones we added)
new_course_ids = [
    'MAC-COMP-8130', 'MAC-COMP-8207', 'MAC-COMP-8380', 'MAC-COMP-8390',
    'MAC-COMP-8490', 'MAC-COMP-8500', 'MAC-COMP-8540', 'MAC-COMP-8570',
    'MAC-COMP-8590', 'MAC-COMP-8610', 'MAC-COMP-8640', 'MAC-COMP-8700',
    'MAC-COMP-8740', 'MAC-COMP-8790', 'MAC-BU-8120', 'MAC-BU-8130', 'MAC-BU-8140'
]

# Get student IDs
student_ids = [s['student_id'] for s in students]

# Find max enrollment ID
max_id = max([int(e['enrollment_id'].split('-')[1]) for e in enrollments])
next_id = max_id + 1

# Terms available
terms = ['2025S', '2025F', '2026W', '2026S', '2026F']
grades = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C']
grade_points = [4.00, 3.80, 3.67, 3.33, 3.00, 2.67, 2.33, 2.00]
statuses = ['completed'] * 85 + ['withdrawn'] * 10 + ['in-progress'] * 5

new_enrollments = []

# For each new course, create enrollments
for course_id in new_course_ids:
    # Randomly select 30-60 students for each course
    num_enrollments = random.randint(30, 60)
    enrolled_students = random.sample(student_ids, num_enrollments)
    
    for student_id in enrolled_students:
        status = random.choice(statuses)
        term = random.choice(terms)
        
        # Generate enrollment
        enrollment = {
            'enrollment_id': f'ENR-{next_id:05d}',
            'student_id': student_id,
            'course_id': course_id,
            'term_code': term,
            'grade_point': '',
            'grade_letter': '',
            'completion_status': status,
            'feedback_rating': '',
            'hours_per_week': round(random.uniform(6.0, 14.0), 1),
            'engagement_score': round(random.uniform(0.4, 0.95), 2)
        }
        
        if status == 'completed':
            # Assign grade
            grade_idx = random.choices(range(len(grades)), weights=[5, 15, 20, 25, 20, 10, 3, 2])[0]
            enrollment['grade_letter'] = grades[grade_idx]
            enrollment['grade_point'] = grade_points[grade_idx]
            enrollment['feedback_rating'] = random.choice([3, 4, 5])
        
        new_enrollments.append(enrollment)
        next_id += 1

# Combine old and new enrollments
all_enrollments = enrollments + new_enrollments

# Write updated enrollments
fieldnames = enrollments[0].keys()
write_csv('enrollments.csv', all_enrollments, fieldnames)

print(f"[OK] Added {len(new_enrollments)} new enrollments")
print(f"[OK] Total enrollments: {len(all_enrollments)}")
print(f"[OK] New courses covered: {len(new_course_ids)}")
print(f"[OK] File updated: {DATA_DIR / 'enrollments.csv'}")

