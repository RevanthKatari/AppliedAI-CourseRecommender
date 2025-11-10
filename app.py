from __future__ import annotations

from flask import Flask, render_template, request

from app.data_loader import get_dataset
from app.recommender import recommend_for_interests, recommend_for_student


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    dataset = get_dataset()

    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip().upper()
        if not student_id:
            return render_template(
                "home.html",
                error="Please enter a student ID.",
            )

        student = dataset.students.get(student_id)
        completed_history = dataset.student_completed_courses.get(student_id, set())

        if student and completed_history:
            recommendations = recommend_for_student(student_id)
            return render_template(
                "recommendations.html",
                student=student,
                performance=dataset.performance.get(student_id),
                recommendations=recommendations,
                context="history",
            )

        preset_interests = sorted(dataset.student_interest_tags.get(student_id, set()))
        return render_template(
            "collect_interests.html",
            student=student,
            student_id=student_id,
            interest_catalog=dataset.interest_catalog,
            preset_interests=preset_interests,
            missing_student=student is None,
            missing_history=not completed_history,
        )

    return render_template("home.html")


@app.post("/interests")
def collect_interests():
    dataset = get_dataset()
    student_id = request.form.get("student_id", "").strip().upper()
    selected_interests = request.form.getlist("interests")

    recommendations = recommend_for_interests(selected_interests)
    student = dataset.students.get(student_id)

    return render_template(
        "recommendations.html",
        student=student,
        performance=dataset.performance.get(student_id),
        recommendations=recommendations,
        context="interests",
        selected_interests=selected_interests,
    )


if __name__ == "__main__":
    app.run(debug=True)



