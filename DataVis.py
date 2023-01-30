import pandas as pd
import numpy as np

from bokeh.palettes import Category20_20
from bokeh.plotting import figure, save
from bokeh.transform import dodge
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


# Counter Function
def Cou_Nom_Data(X1, X2, X3, X4, N2):
    d = {'X1': list(X1)}
    for i in X2:
        s = []
        for j in X1:
            sum = 0
            for c in range(len(X3)):
                if N2 == "All":
                    if (j == str(X3[c])) & (i == str(X4[c])):
                        sum = sum + 1
                else:
                    if (j == str(X3[c])) & (i == str(X4[c])) & (N2 == Data['code_presentation'][c]):
                        sum = sum + 1
            s.append(sum)
        d[str(i)] = s
    d = Name_ALl(X2, d)
    return d


def Cou_Sco_data(X1, X2, X3, X4, N2):
    d = {'X1': list(X1)}
    for i in range(len(X2)):
        s = []
        for j in X1:
            sum = 0;
            for c in range(len(X3)):
                if N2 == 'All':
                    if (float(i * 10) <= X4[c]) & (X4[c] <= (float(i * 10) + 9)) & (j == X3[c]):
                        sum = sum + 1
                else:
                    if (float(i * 10) <= X4[c]) & (X4[c] <= (float(i * 10) + 9)) & (j == X3[c]) & (
                            N2 == Data_2['code_presentation'][c]):
                        sum = sum + 1
            s.append(sum)
        d[str(X2[i])] = s
    d = Name_ALl(X2, d)
    return d


def Cou_Ass_Data(X1, X2, X3, X4, N2):
    d = {'X1': list(X1)}
    for i in X2:
        s = []
        for j in X1:
            x = []
            for c in range(len(X3)):
                if N2 == 'All':
                    if (i == str(X4[c])) & (j == X3[c]):
                        x.append(Data_2['id_assessment'][c])
                else:
                    if (i == str(X4[c])) & (j == X3[c]) & (N2 == Data_2['code_presentation'][c]):
                        x.append(Data_2['id_assessment'][c])
            x = np.unique(x)
            s.append(len(x))
        d[str(i)] = s
    d = Name_ALl(X2, d)
    return d


def Color(X):
    c = []
    for i in range(len(X)):
        c.append(Category20_20[i])
    return c


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


def Name_ALl_2(X):
    if X == String(gender):
        X = ['Female', 'Male']
    elif X == String(code_presentation):
        X = ['2013 February', '2013 October', '2014 February', '2014 October']
    elif X == String(disability):
        X = ['Not Disable', 'Disable']
    elif X == String(assessment_type):
        X = ['Computer Marked Assessment', 'Final Exam', 'Tutor Marked Assessment ']
    return X


def Name_ALl(X1, X2):
    K = list(X2.keys())

    if X1 == String(gender):
        X1 = ['X1', 'Female', 'Male']
        if X1 != K:
            for i in range(len(X2)):
                X2[X1[i]] = X2.pop(K[i])

    elif X1 == String(disability):
        X1 = ['X1', 'Not Disable', 'Disable']
        if X1 != K:
            for i in range(len(X2)):
                X2[X1[i]] = X2.pop(K[i])

    elif X1 == String(code_presentation):
        X1 = ['X1', '2013 February', '2013 October', '2014 February', '2014 October']
        if X1 != K:
            for i in range(len(X2)):
                X2[X1[i]] = X2.pop(K[i])

    elif X1 == String(assessment_type):
        X1 = ['X1', 'Computer Marked Assessment', 'Final Exam', 'Tutor Marked Assessment ']
        if X1 != K:
            for i in range(len(X2)):
                X2[X1[i]] = X2.pop(K[i])
    return X2


# Plot Function
def BarGroupPlot(X1, X2, X3, X4, N1, N2, N3, N4, N5):
    X2 = String(X2)
    X1 = String(X1)
    if X2 == score:
        Data = Cou_Sco_data(X1, X2, X3, X4, N2)
    elif X2 == String(assessment_type):
        Data = Cou_Ass_Data(X1, X2, X3, X4, N2)
    else:
        Data = Cou_Nom_Data(X1, X2, X3, X4, N2)

    X2 = Name_ALl_2(X2)

    Tool = [

        (N1, '@X1'),
        (N3, "$name"),
        (N4, "@$name"),
        ('Semester', Name_Sem(N2))]

    p = figure(width=1800, height=800, x_range=X1, tools='pan, tap, wheel_zoom,zoom_in,zoom_out,reset,save,hover',
               tooltips=Tool, sizing_mode='scale_both')

    c = []
    for i in range(len(X2)):
        c.append(i / (len(X2)))

    for i in range(len(X2)):
        p.vbar(x=dodge('X1', -(c[len(X2) - 1] / 2) + c[i], range=p.x_range), top=str(X2[i]), source=Data,
               width=(1 / len(X2)) * 0.5, name=str(X2[i]), color=Category20_20[i], legend_label=str(X2[i]))

    p.title.text = N5
    p.title.text_font = "times"
    p.title.align = "center"
    p.title.text_color = "black"
    p.title.text_font_size = "20px"
    p.title.text_font_style = "bold italic"

    p.background_fill_color = "white"
    p.border_fill_color = "#FFEAA7"
    p.min_border = 10
    p.xgrid.grid_line_color = None

    p.yaxis.axis_label = N4
    p.yaxis.axis_label_text_align = "center"
    p.yaxis.axis_label_text_color = "black"
    p.yaxis.axis_label_text_font_size = '15px'
    p.yaxis.axis_label_text_font_style = 'bold'
    p.yaxis.major_label_text_font_size = "10px"
    p.yaxis.major_label_text_font_style = "bold"
    p.y_range.start = 0
    # p.xaxis.visible = False

    p.xaxis.axis_label = N1
    p.xaxis.axis_label_text_align = "center"
    p.xaxis.axis_label_text_color = "black"
    p.xaxis.axis_label_text_font_size = '15px'
    p.xaxis.axis_label_text_font_style = 'bold'
    p.xaxis.major_label_text_font_size = "10px"
    p.xaxis.major_label_text_font_style = "bold"

    # p.yaxis.visible = False

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
    p.legend.background_fill_color = 'white'
    p.legend.border_line_color = 'white'
    p.legend.orientation = 'vertical'
    p.add_layout(p.legend[0], 'right')
    p.legend.click_policy = "hide"
    # p.legend.visible = False

    p.toolbar.autohide = True

    return p


semester = ['All Semesters', '2013 February Semester', '2013 October Semester', '2014 February Semester',
            '2014 October Semester']
sem = ["All"]
for i in code_presentation:
    sem.append(i)
for i in range(len(sem)):
    p1 = BarGroupPlot(courses, gender, Data['code_module'], Data['gender'], "Courses", sem[i], 'Gender',
                      'No. of the Students',
                      'No. of Students according to their Gender in the {S}'.format(S=semester[i]))
    tab1 = TabPanel(child=p1, title="Gender")

    p2 = BarGroupPlot(courses, code_presentation, Data['code_module'], Data['code_presentation'], "Courses", sem[i],
                      'Semester', 'No. of the Students', 'No. of Students in the {S}'.format(S=semester[i]), )
    tab2 = TabPanel(child=p2, title="Semester")

    p3 = BarGroupPlot(courses, age_band, Data['code_module'], Data['age_band'], "Courses", sem[i], 'Age',
                      'No. of the Students',
                      'No. of Students according to their Age in the {S}'.format(S=semester[i]), )
    tab3 = TabPanel(child=p3, title="Age")

    p4 = BarGroupPlot(courses, region, Data['code_module'], Data['region'], "Courses", sem[i], 'Region',
                      'No. of the Students',
                      'No. of Students according to their Region in the {S}'.format(S=semester[i]), )
    tab4 = TabPanel(child=p4, title="Region")

    p5 = BarGroupPlot(courses, highest_education, Data['code_module'], Data['highest_education'], "Courses", sem[i],
                      'Highest Education', 'No. of the Students',
                      'No. of Students according to their Highest Education in the {S}'.format(S=semester[i]), )
    tab5 = TabPanel(child=p5, title="Highest Education")

    p6 = BarGroupPlot(courses, disability, Data['code_module'], Data['disability'], "Courses", sem[i], 'Disability',
                      'No. of the Students',
                      'No. of Students according to their Disability in the {S}'.format(S=semester[i]), )
    tab6 = TabPanel(child=p6, title="Disability")

    p7 = BarGroupPlot(courses, final_result, Data['code_module'], Data['final_result'], "Courses", sem[i],
                      'Final Result',
                      'No. of the Students',
                      'No. of Students according to their Final Result in the {S}'.format(S=semester[i]), )
    tab7 = TabPanel(child=p7, title="Final Result")

    p8 = BarGroupPlot(courses, num_of_prev_attempts, Data['code_module'], Data['num_of_prev_attempts'], "Courses",
                      sem[i],
                      'Previous Attempts', 'No. of the Students',
                      'No. of Students according to their Previous Attempts in the {S}'.format(S=semester[i]), )
    tab8 = TabPanel(child=p8, title="Previous Attempts")
    p9 = BarGroupPlot(courses, score, Data_2['code_module'], Data_2['score'], "Courses", sem[i], 'Scores',
                      'No. of the Students',
                      'No. of Students according to their Scores in the {S}'.format(S=semester[i]), )
    tab9 = TabPanel(child=p9, title="Scores")

    p10 = BarGroupPlot(courses, assessment_type, Data_2['code_module'], Data_2['assessment_type'], "Courses", sem[i],
                       'Exams', 'No. of the Exams',
                       'No. of Students according to Type of Assessments  in the {S}'.format(S=semester[i]), )
    tab10 = TabPanel(child=p10, title="Assessment Type")

    p = (Tabs(tabs=[tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10]))
    name = "./GroupBarVis/GroupBarVis_{S}.html".format(S=semester[i])
    save(p, name)
