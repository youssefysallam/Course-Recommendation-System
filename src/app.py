import os
import json
from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import RadioField, SelectMultipleField, SubmitField, TextAreaField, widgets
from wtforms.validators import InputRequired
from dependency_graph import DependencyGraph
from schedule_calculator import ScheduleCalculator, CREDIT_LOADS
from availability import get_offered_courses, available_semesters

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), '../templates'),
    static_folder=os.path.join(os.path.dirname(__file__), '../static')
)

app.config['SECRET_KEY'] = 'test'
csrf = CSRFProtect(app)

MAJOR_CHOICES = [
    ('cs_bs', 'Computer Science B.S.'),
    ('cs_ba', 'Computer Science B.A.'),
    ('ce_bs', 'Computer Engineering B.S.')
]

MAJOR_FILE_MAP = {
    'Computer Science B.S.': 'Computer_Science_BS',
    'Computer Science B.A.': 'Computer_Science_BA',
    'Computer Engineering B.S.': 'Computer_Engineering_BS',
}


def _graph_for(major_display: str) -> DependencyGraph:
    major_file = MAJOR_FILE_MAP.get(major_display, major_display.replace('.', '').replace(' ', '_'))
    return DependencyGraph(major_file)


def _all_course_codes(major_display: str) -> list:
    graph = _graph_for(major_display)
    return sorted(graph.courses_map.keys())


class MajorForm(FlaskForm):
    name = RadioField(
        'What is your major?',
        choices=MAJOR_CHOICES,
        validators=[InputRequired(message="Please select a major.")]
    )
    submit = SubmitField('Submit')


class GenEdForm(FlaskForm):
    gen_eds = SelectMultipleField(
        'Select the categories you have completed:',
        choices=[
            ('United States Diversity', 'United States Diversity'),
            ('International Diversity', 'International Diversity'),
            ('Social & Behavioral Sciences', 'Social & Behavioral Sciences'),
            ('Humanities', 'Humanities'),
            ('The Arts', 'The Arts'),
            ('World Culture / World Language', 'World Culture / World Language'),
            ('First Year Seminar', 'First Year Seminar'),
            ('Intermediate Seminar', 'Intermediate Seminar'),
        ],
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False)
    )
    submit = SubmitField('Submit')


class CourseForm(FlaskForm):
    courses = TextAreaField(
        'Enter the courses you have taken (e.g., CS 110, CS 210, MATH 140, ENGL 101)'
    )
    credit_load = RadioField(
        'Credit load per semester',
        choices=[
            ('light',  'Light — 12 cr'),
            ('normal', 'Normal — 15 cr'),
            ('heavy',  'Heavy — 18 cr'),
        ],
        default='normal'
    )
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def home():
    form = MajorForm()
    if form.validate_on_submit():
        selected_major = dict(form.name.choices).get(form.name.data, "Unknown")
        session['selected_major'] = selected_major
        return redirect(url_for('geneds'))
    return render_template('index.html', form=form)


@app.route('/geneds', methods=['GET', 'POST'])
def geneds():
    if 'selected_major' not in session:
        return redirect(url_for('reset'))

    form = GenEdForm()
    if form.validate_on_submit():
        session['gen_eds'] = form.gen_eds.data
        return redirect(url_for('courses'))

    return render_template('select_geneds.html', form=form, selected_major=session['selected_major'])


@app.route('/courses', methods=['GET', 'POST'])
def courses():
    if 'selected_major' not in session or 'gen_eds' not in session:
        return redirect(url_for('reset'))

    selected_major = session['selected_major']
    known_codes = set(_all_course_codes(selected_major))
    form = CourseForm()

    if form.validate_on_submit():
        raw = form.courses.data or ''
        entered = [c.strip().upper() for c in raw.replace(',', '\n').split('\n') if c.strip()]
        unknown = [c for c in entered if c not in known_codes]
        # Store everything (unknown codes are silently ignored by the graph)
        session['courses'] = entered
        session['credit_load'] = form.credit_load.data
        session['unknown_courses'] = unknown
        return redirect(url_for('recommendations'))

    return render_template(
        'input_courses.html',
        form=form,
        selected_major=selected_major,
        known_codes=sorted(known_codes),
    )


@app.route('/recommendations')
def recommendations():
    if 'selected_major' not in session or 'courses' not in session or 'gen_eds' not in session:
        return redirect(url_for('reset'))

    selected_major   = session['selected_major']
    completed_courses = session['courses']
    completed_geneds  = session['gen_eds']
    credit_load      = session.get('credit_load', 'normal')
    unknown_courses  = session.get('unknown_courses', [])

    combined = [c.strip() for c in completed_courses + completed_geneds]

    graph      = _graph_for(selected_major)
    calculator = ScheduleCalculator(graph, combined, credit_load=credit_load)
    all_sems   = calculator.get_semesters()
    skipped    = calculator.get_skipped_courses()

    # Availability filtering: annotate semester-1 courses with offering info
    offered_fall   = get_offered_courses('fall_2024')
    offered_spring = get_offered_courses('spring_2025')

    def annotate(course_code: str) -> dict:
        in_fall   = course_code in offered_fall
        in_spring = course_code in offered_spring
        if in_fall and in_spring:
            badge = 'Fall & Spring'
        elif in_fall:
            badge = 'Fall only'
        elif in_spring:
            badge = 'Spring only'
        else:
            badge = None
        return {'code': course_code, 'availability': badge}

    annotated_sems = [[annotate(c) for c in sem] for sem in all_sems]
    next_sem = annotated_sems[0] if annotated_sems else []

    return render_template(
        'recommendations.html',
        selected_major=selected_major,
        next_semester=next_sem,
        all_semesters=annotated_sems,
        skipped=skipped,
        unknown_courses=unknown_courses,
        credit_load=credit_load,
        credit_cap=CREDIT_LOADS.get(credit_load, 15),
    )


@app.route('/api/courses')
def api_courses():
    major = session.get('selected_major')
    if not major:
        return jsonify([])
    return jsonify(_all_course_codes(major))


@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
