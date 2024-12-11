import os
from flask import Flask, render_template, session, redirect, url_for
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import RadioField, SelectMultipleField, SubmitField, TextAreaField, widgets
from wtforms.validators import InputRequired
from dependency_graph import DependencyGraph
from schedule_calculator import ScheduleCalculator

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), '../templates'),
    static_folder=os.path.join(os.path.dirname(__file__), '../static')
)

app.config['SECRET_KEY'] = 'test'

csrf = CSRFProtect(app)


class MajorForm(FlaskForm):
    name = RadioField('What is your major?', choices=[
        ('cs_bs', 'Computer Science B.S.'),
        ('cs_ba', 'Computer Science B.A.'),
        ('ce_bs', 'Computer Engineering B.S.')
    ], validators=[InputRequired(message="Please select a major.")])
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
        'Enter the courses you have taken (e.g., CS 110, CS 210, MATH 140, ENGL 101)')
    submit = SubmitField('Submit')


def get_recommended_courses(selected_major, completed_courses):
    selected_major = selected_major.replace('.', '').replace(' ', '_')
    graph = DependencyGraph(selected_major)
    calculator = ScheduleCalculator(graph, completed_courses)
    return calculator.get_semesters()[0]


@app.route('/', methods=['GET', 'POST'])
def home():
    form = MajorForm()
    if form.validate_on_submit():
        selected_major = dict(form.name.choices).get(form.name.data, "Unknown")
        session['selected_major'] = selected_major
        return redirect(url_for('geneds'))
    return render_template('index.html', form=form)


@app.route('/courses', methods=['GET', 'POST'])
def courses():
    if 'selected_major' not in session or 'gen_eds' not in session:
        return redirect(url_for('reset'))

    form = CourseForm()
    if form.validate_on_submit():
        courses_input = form.courses.data
        courses_list = [course.strip() for course in courses_input.replace(
            ',', '\n').split('\n') if course.strip()]
        session['courses'] = courses_list
        return redirect(url_for('recommendations'))
    return render_template('input_courses.html', form=form, selected_major=session['selected_major'])


@app.route('/recommendations')
def recommendations():
    if 'selected_major' not in session or 'courses' not in session or 'gen_eds' not in session:
        return redirect(url_for('reset'))

    selected_major = session.get('selected_major')
    completed_courses = session.get('courses')
    completed_geneds = session.get('gen_eds')

    # Combine courses and Gen Eds
    combined_completed = completed_courses + completed_geneds

    combined_completed = [course.strip() for course in combined_completed]

    # Determine recommended courses
    recommended_courses = get_recommended_courses(
        selected_major, combined_completed)

    return render_template('recommendations.html', selected_major=selected_major, recommended_courses=recommended_courses)


@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('home'))


@app.route('/geneds', methods=['GET', 'POST'])
def geneds():
    if 'selected_major' not in session:
        return redirect(url_for('reset'))

    form = GenEdForm()
    if form.validate_on_submit():
        selected_geneds = form.gen_eds.data
        session['gen_eds'] = selected_geneds
        return redirect(url_for('courses'))

    return render_template('select_geneds.html', form=form, selected_major=session['selected_major'])


if __name__ == '__main__':
    app.run(debug=True)
