import pandas as pd
import numpy as np
from math import pi

from bokeh.palettes import Category20_20
from bokeh.plotting import figure, save
from bokeh.transform import cumsum
from bokeh.models import TabPanel, Tabs

Data = pd.read_csv('./ProcessedData/mergedDate.csv')
Data_2 = pd.read_csv('./ProcessedData/assResults.csv')

courses = np.unique(Data['code_module'])
num_of_prev_attempts = np.unique(Data['num_of_prev_attempts'])
code_presentation = np.unique(Data['code_presentation'])

assessment_type = np.unique(Data_2['assessment_type'])
gender = np.unique(Data['gender'])
age_band = np.unique(Data['age_band'])
region = np.unique(Data['region'])
highest_education = np.unique(Data['highest_education'])
disability = np.unique(Data['disability'])
final_result = np.unique(Data['final_result'])
score = ['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90-100']


# Data Preparations Functions

# Specific Course Data
def Cou_Nom_Data(X1, X2, X3, N1, N2):
    d = {}
    for i in X1:
        sum = 0
        for j in range(len(X2)):
            if N2 == 'All':
                if (i == str(X2[j])) & (N1 == X3[j]):
                    sum = sum + 1
            else:
                if (i == str(X2[j])) & (N1 == X3[j]) & (N2 == Data['code_presentation'][j]):
                    sum = sum + 1
        d[str(i)] = sum
        d = Name_ALl(X1, d)
    return d


# Specific Course + Score Data
def Cou_Sco_data(X1, X2, X3, N1, N2):
    d = {}
    for i in range(len(X1)):
        sum = 0;
        for j in range(len(X3)):
            if N2 == 'All':
                if (float(i * 10) <= X2[j]) & (X2[j] <= (float(i * 10) + 9)) & (N1 == X3[j]):
                    sum = sum + 1
            else:
                if (float(i * 10) <= X2[j]) & (X2[j] <= (float(i * 10) + 9)) & (N1 == X3[j]) & (
                        N2 == Data_2['code_presentation'][j]):
                    sum = sum + 1
        d[str(X1[i])] = sum
        d = Name_ALl(X1, d)
    return d


# Specific Course + Assessments Data
def Cou_Ass_Data(X1, X2, X3, N1, N2):
    d = {}
    for i in X1:
        s = []
        for j in range(len(X2)):
            if N2 == 'All':
                if (i == str(X2[j])) & (N1 == X3[j]):
                    s.append(Data_2['id_assessment'][j])
            else:
                if (i == str(X2[j])) & (N1 == X3[j]) & (N2 == Data_2['code_presentation'][j]):
                    s.append(Data_2['id_assessment'][j])
        s = np.unique(s)
        d[str(i)] = len(s)
        d = Name_ALl(X1, d)
    return d


# Color Assignment Function
def Color(N1):
    c = []
    for i in range(len(N1)):
        c.append(Category20_20[i])
    return c


# String Function
def String(X):
    s = []
    for i in X:
        s.append(str(i))
    return s


def Name_Sem(X):
    if X == '2013B':
        X = '2013 February'
    elif X == '2013J':
        X = '2013 October'
    elif X == '2014B':
        X = '2014 February'
    elif X == '2014J':
        X = '2014 October'
    return X


def Name_ALl(X1, X2):
    K = list(X2.keys())

    if X1 == String(gender):
        X1 = ['Female', 'Male']

    elif X1 == String(disability):
        X1 = ['Not Disable', 'Disable']

    elif X1 == String(code_presentation):
        X1 = ['2013 February', '2013 October', '2014 February', '2014 October']

    elif X1 == String(assessment_type):
        X1 = ['Computer Marked Assessment', 'Final Exam', 'Tutor Marked Assessment ']

    if X1 != K:
        for i in range(len(X2)):
            X2[X1[i]] = X2.pop(K[i])

    return X2


# Pie Plot Function
def PiePlot(X1, X2, X3, N1, N2, N3, N4, N5):
    X1 = String(X1)
    if X1 == score:
        x = Cou_Sco_data(X1, X2, X3, N1, N2)
    elif X1 == String(assessment_type):
        x = Cou_Ass_Data(X1, X2, X3, N1, N2)
    else:
        x = Cou_Nom_Data(X1, X2, X3, N1, N2)
    z = []
    for i in x.items():
        z.append(i[1])
    if sum(z) != 0:
        Data = pd.Series(x).reset_index(name='value').rename(columns={'index': 'X'})
        Data['angle'] = Data['value'] / Data['value'].sum() * 2 * pi
        Data['color'] = Color(X1)
        Tool = [
            ('Course', N1),
            (N3, '@X'),
            (N4, "@value"),
            ('Semester', Name_Sem(N2))]

        p = figure(height=500, toolbar_location='right', tools='pan, tap, wheel_zoom,zoom_in,zoom_out,reset,save,hover' ,tooltips=Tool, x_range=(-0.5, 0.75), sizing_mode='scale_both')
        p.wedge(x=0, y=1, radius=0.4,
                start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                line_color="white", fill_color='color', legend_field='X', source=Data)

        p.axis.axis_label = None
        p.axis.visible = False
        p.grid.grid_line_color = None

        p.title.text = N5
        p.title.text_font = "times"
        p.title.align = "center"
        p.title.text_color = "black"
        p.title.text_font_size = "20px"
        p.title.text_font_style = "bold"

        p.border_fill_color = "#FFEAA7"
        p.min_border = 5

        p.legend.label_text_font = "times"
        p.legend.location = "top_right"

        p.legend.title = N3
        p.legend.title_text_color = "Black"
        p.legend.title_text_font = "times"
        p.legend.title_text_font_style = "bold"
        p.legend.title_text_align = "left"
        p.legend.title_text_font_size = "20px"

        p.legend.label_text_font = "times"
        p.legend.label_text_font_size = "15px"
        p.legend.label_text_align = "left"
        p.legend.label_text_font_style = "bold"
        p.legend.background_fill_color = '#FFEAA7'
        p.legend.border_line_color = 'white'
        p.legend.border_line_width = 2

        p.toolbar.autohide = True

    else:
        p = figure(width=1800, height=800, tools='pan, tap, wheel_zoom,zoom_in,zoom_out,reset,save,hover',sizing_mode='scale_both')
        p.image_url(url=['./NoCourse.JPG'], x=0, y=1, w=0.8, h=0.6)


        p.title.text = N5
        p.title.text_font = "times"
        p.title.align = "center"
        p.title.text_color = "black"
        p.title.text_font_size = "20px"
        p.title.text_font_style = "bold italic"
        p.min_border = 40
        p.background_fill_color = "white"
        p.border_fill_color = "#FFEAA7"

        p.xaxis.visible = False
        p.yaxis.visible = False
        p.axis.axis_label = None
        p.axis.visible = False
        p.grid.grid_line_color = None

        p.toolbar.autohide = True

    return p


semester = ['All Semesters', '2013 February', '2013 October', '2014 February', '2014 October']
sem = ["All"]
for i in code_presentation:
    sem.append(i)
for i in range(len(sem)):
    for j in courses:
        p1 = PiePlot(gender, Data['gender'], Data['code_module'], j, sem[i], 'Gender', 'No. of the Students',
                     'No. of Students in Course {C} according to their Gender in the {S}'.format(C=j, S=semester[i]))
        tab1 = TabPanel(child=p1, title="Gender")

        p2 = PiePlot(code_presentation, Data['code_presentation'], Data['code_module'], j, sem[i], 'Semester',
                     'No. of the Students', 'No. of Students in Course {C} in the {S}'.format(C=j, S=semester[i]) )
        tab2 = TabPanel(child=p2, title="Semester")

        p3 = PiePlot(age_band, Data['age_band'], Data['code_module'], j, sem[i], 'Age', 'No. of the Students',
                     'No. of Students in Course {C} according to their Age in the {S}'.format(C=j, S=semester[i]), )
        tab3 = TabPanel(child=p3, title="Age")

        p4 = PiePlot(region, Data['region'], Data['code_module'], j, sem[i], 'Region', 'No. of the Students',
                     'No. of Students in Course {C} according to their Region in the {S}'.format(C=j, S=semester[i]), )
        tab4 = TabPanel(child=p4, title="Region")

        p5 = PiePlot(highest_education, Data['highest_education'], Data['code_module'], j,sem[i],
                     'Highest Education',
                     'No. of the Students',
                     'No. of Students in Course {C} according to their Highest Education in the {S}'.format(C=j, S=semester[i]), )
        tab5 = TabPanel(child=p5, title="Highest Education")

        p6 = PiePlot(disability, Data['disability'], Data['code_module'], j,sem[i], 'Disability',
                     'No. of the Students',
                     'No. of Students in Course {C} according to their Disability in the {S}'.format(C=j, S=semester[i]), )
        tab6 = TabPanel(child=p6, title="Disability")

        p7 = PiePlot(final_result, Data['final_result'], Data['code_module'], j,sem[i], 'Final Result',
                     'No. of the Students', 'No. of Students in Course {C} according to their Final Result'.format(C=j, S=semester[i]), )
        tab7 = TabPanel(child=p7, title="Final Result")

        p8 = PiePlot(num_of_prev_attempts, Data['num_of_prev_attempts'], Data['code_module'], j,sem[i],
                     'Previous Attempts',
                     'No. of the Students', 'No. of Students in Course {C} according to their Previous Attempts in the {S}'.format(C=j, S=semester[i]), )
        tab8 = TabPanel(child=p8, title="Previous Attempts")

        p9 = PiePlot(score, Data_2['score'], Data_2['code_module'], j,sem[i], 'Scores', 'No. of the Students',
                     'No. of Students in Course {C} according to their Scores in the {S}'.format(C=j, S=semester[i]), )
        tab9 = TabPanel(child=p9, title="Scores")

        p10 = PiePlot(assessment_type, Data_2['assessment_type'], Data_2['code_module'], j,sem[i], 'Exams',
                      'No. of the Exams', 'No. of Students in Course {C} according to Assessment Type in the {S}'.format(C=j, S=semester[i]) )
        tab10 = TabPanel(child=p10, title="Assessment Type")
        p = (Tabs(tabs=[tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10]))
        name = "./PieVis/BarVis_{C}_{S}.html".format(C=j, S=semester[i])
        save(p,name)

