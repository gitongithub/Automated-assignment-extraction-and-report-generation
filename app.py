import language_tool_python
import json
import re
import sys
import datetime
import matplotlib.pyplot as plt
import pandas as pd
from pip._internal.utils.misc import tabulate
from tqdm import tqdm
import numpy as np
from fpdf import FPDF, fpdf
import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import dataframe_image as dfi
noOfSub = {}
accOfSub={}
totErr=0
errorCategory = {}
student_accuracy={}
sdate="start"
edate="end"
class PDF(FPDF):
    def header(self):
        # Logo
        self.image('static\\images\\logo.png', x = 182, y = 10, w = 20, h = 10, type = '', link = '')
        self.rect(5.0, 5.0, 200.0,287.0)
        #pdf.set_fill_color(0, 0, 0)
        self.rect(8.0, 8.0, 194.0,282.0)

def Individual(author,msgList,questions,ans,accuracy,accuracy_no,errorCategory,indErr,str1):
    asgnList = []
    for i in range(len(accuracy_no)):
        asgnList.append("A"+str(accuracy_no[i]))
    plt.plot(asgnList, accuracy, marker='.',markersize=15)
    plt.title('Let us see how accurate you are', fontsize=14)
    plt.xlabel('Assignments', fontsize=14)
    plt.ylabel('Accuracy', fontsize=14)
    plt.savefig('Accuracy.png', dpi=300, bbox_inches='tight')
    plt.clf()

    y = np.array([len(accuracy_no),len(questions)-len(accuracy_no)])
    res=""
    if len(accuracy_no)>len(questions)-len(accuracy_no):
        res="You have completed a good number of assignments"
    else:
        res="You are not so regular in doing assignments"
    plt.title(res, fontsize=14)
    mylabels = ["Submitted", "Not Submitted"]
    plt.pie(y, labels=mylabels)
    plt.legend()
    plt.savefig('Attempted.png', dpi=300, bbox_inches='tight')
    plt.clf()
    mylabels = []
    lst=[]
    for i in errorCategory:
        lst.append(errorCategory[i])
        mylabels.append(i+" ("+str(errorCategory[i])+"/"+str(indErr)+")")

    y = np.array(lst)
    plt.pie(y, labels=mylabels)
    plt.title("Let us see what errors you made", fontsize=14)
    plt.savefig('errorType.png', dpi=300, bbox_inches='tight')
    plt.clf()
    pdf = PDF()
    pdf.add_page()
    pdf.set_fill_color(32.0, 47.0, 250.0)
    pdf.set_font("Arial",'B', size=30)
    pdf.set_text_color(32, 41, 140)
    pdf.cell(200, 10, txt="Student Analysis Report", ln=1, align="C")
    variable = asgnList
    variable2 = str(len(questions))
    pdf.set_font("Times",'B', size=14)
    pdf.cell(200, 10, txt="",ln=1,align="L")
    pdf.set_text_color(0,0,0)
    pdf.cell(200, 10, txt="Dear " +author+", Hope you are doing well! ",ln=1,align="L")
    pdf.cell(200, 10, txt="",ln=1,align="L")
    pdf.set_font("Times", size=12)
    pdf.cell(200, 10, txt="We have created your evaluation report. Please find it below", ln=1, align="L")
    pdf.cell(200, 10, txt="Total Number of Students in Class :-  " + variable2, ln=1, align="L")
    pdf.cell(200, 10, txt="Assignments that you submitted:-  " + str(variable) , ln=1, align="L")
    pdf.set_font("Times", 'B',size=14)
    lang="Great Going! You are using 67% English words while interacting."
    pdf.cell(200, 10, txt=lang, ln=1, align="L")
    pdf.image('Accuracy.png', x = 50, y = 100, w = 100, h = 80, type = '', link = '')
    pdf.image('Attempted.png', x=10, y=190, w=80, h=80, type='', link='')
    pdf.image('errorType.png', x=120, y=190, w=80, h=80, type='', link='')
    pdf.add_page()
    # # f = open(author+".txt", "r")
    # # for x in f:
    lang="Let us see your detailed report, "+author+"."
    pdf.cell(200, 10, txt=lang, ln=1, align="C")
    pdf.cell(200, 10, txt="", ln=1, align="C")
    pdf.set_font("Times",size=11)
    str2 = str1.encode('latin-1', 'replace').decode('latin-1')
    str2=str2.replace("?",'"')
    pdf.multi_cell(180,7,txt=str2,border=0,align='L',fill=False)
    pdf.output(author+'.pdf')

def All(questions,ans,accuracy,no_of_students,student_asgn_count):
    global totErr
    global errorCategory
    global noOfSub
    global accOfSub
    global sdate
    global edate
    asgn = []
    subs = []
    accs = []
    list_of_students=""
    print("length",len(questions))
    for i in student_asgn_count:
        print(i,student_asgn_count[i])
    for i in student_asgn_count:
        if(student_asgn_count[i]==len(questions)):
            list_of_students=list_of_students+i+" "
    if(list_of_students==""):
        list_of_students="None"
    print(list_of_students)
    for i in noOfSub:
        asgn.append('A' + str(i))
        subs.append(noOfSub[i])
        if(noOfSub[i]==0):
            accs.append(0);
        else:
            accs.append(accOfSub[i]/noOfSub[i])

    plt.bar(asgn, subs)
    plt.title('Summary Evaluation', fontsize=14)
    plt.xlabel('Assignments', fontsize=14)
    plt.ylabel('No of Submissions', fontsize=14)
    plt.savefig('Submissions.png', dpi=300, bbox_inches='tight')
    plt.clf()


    plt.plot(asgn, accs, marker='.', markersize=15)
    plt.title('Accuracy Summary', fontsize=14)
    plt.xlabel('Assignment', fontsize=14)
    plt.ylabel('Average Accuracy', fontsize=14)
    plt.savefig('Avg_Accuracy.png', dpi=300, bbox_inches='tight')
    plt.clf()

    lst=[]
    mylabels=[]
    for i in errorCategory:
        lst.append(errorCategory[i])
        mylabels.append(i+" ("+str(errorCategory[i])+"/"+str(totErr)+")")
    y = np.array(lst)
    plt.pie(y, labels=mylabels)
    plt.savefig('errorType.png', dpi=300, bbox_inches='tight')
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=30)
    pdf.cell(200, 10, txt="Student Analysis Report", ln=1, align="C")
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt="Please find below the evaluation results", ln=4, align="L")
    pdf.cell(200, 10, txt="Duration between :-" + sdate+" to "+edate, ln=5, align="L")
    pdf.cell(200, 10, txt="Total Number of Students in Class :-  " +str(no_of_students)+ "", ln=6 ,align="L")
    pdf.cell(200, 10, txt="Students who submitted all assignments: "+list_of_students, ln=8, align="L")
    pdf.image('Avg_Accuracy.png', x = 50, y = 70, w = 100, h = 80, type = '', link = '')
    pdf.image('Submissions.png', x=10, y=160, w=80, h=80, type='', link='')
    pdf.image('errorType.png', x=95, y=160, w=95, h=80, type='', link='')
    pdf.image('dataframe.png', x=75, y=250, w=60, h=40, type='', link='')
    pdf.output('Summary.pdf')
    return


def findError3(author, msgList, questions):
    ans = []
    global totErr
    global errorCategory
    global noOfSub
    global accOfSub
    global student_accuracy
    for i in msgList:
        temp1 = i.split(" ", 1)
        temp2 = temp1[0].split("A")
        temp3 = temp2[1]
        ans.append(int(temp3))
    cnt = 0
    for i in ans:
        noOfSub[i]+=1
    accuracy = []
    acc=0;
    for s in range(len(questions)):
        if s + 1 in ans:
            line = msgList[cnt].split(" ", 1)[1]
            cnt += 1
            tool = language_tool_python.LanguageTool('en-US')
            i = 0
            c = 0
            matches = tool.check(line)
            i = i + len(matches)
            totErr += i
            print("finderror"+str(totErr))
            val = 100 - 100 * (len(matches) / len(line.split()))
            acc+=val
            accuracy.append(val)
            accOfSub[s+1] += val
            for mistake in matches:
                c += 1
                if mistake.category in errorCategory.keys():
                    errorCategory[mistake.category] = errorCategory[mistake.category] + 1
                else:
                    errorCategory[mistake.category] = 1
        else:
            pass
    student_accuracy[author]=(acc)/len(ans)



def findError(author, msgList, questions):
    str1=  ""
    f = open(author + ".txt", "w+")
    f.write("Submission by: " + author)
    str1 = str1 + "Submission by: " + author
    ans = []
    for i in msgList:
        temp1 = i.split(" ", 1)
        temp2 = temp1[0].split("A")
        temp3 = temp2[1]
        ans.append(int(temp3))
    temp = "\n\nTotal Number of Assignments = " + str(len(questions)) + "\nNumber of Assignments Attempted = " + str(
        len(ans))
    f.write(temp)
    str1 = str1 + temp
    cnt = 0
    accuracy = []
    accuracy_no = []
    errorCategory = {}
    indErr = 0
    for s in range(len(questions)):
        string = "\n\nAssignment " + str(s + 1) + ":" + questions[s].split(" ", 1)[1]
        str1 = str1 + string
        f.write(string)
        if s + 1 in ans:
            line = msgList[cnt].split(" ", 1)[1]
            cnt += 1
            tool = language_tool_python.LanguageTool('en-US')
            i = 0
            c = 0
            errors = {}
            matches = tool.check(line)
            count_simple=0
            i=0
            for mistake in matches:
                if(mistake.category=="GRAMMAR" or mistake.category=="TYPOS"or mistake.category=="CASING"):
                    c += 1
                    count_simple+=1
                    errors[c] = {'Error': mistake.ruleId, 'Suggestion': mistake.replacements, 'Message': mistake.message,
                                 'Actual': mistake.matchedText}
                    if mistake.category in errorCategory.keys():
                        errorCategory[mistake.category] = errorCategory[mistake.category] + 1
                    else:
                        errorCategory[mistake.category] = 1
            i = i + count_simple
            indErr += i
            print(100 - 100 * (len(matches) / len(line.split())))
            accuracy.append(100 - 100 * (len(matches) / len(line.split())))
            accuracy_no.append(s + 1)
            f.write("\n\nYour Submission: " + line)
            str1 = str1 + "\n\nYour Submission: " + line
            f.write("\n\nNo. of mistakes found in submission is " + str(i))
            str1 = str1 + "\n\nNo. of mistakes found in submission is " + str(i)
            for j in errors:
                temp = "\n\nError message: " + str(errors[j]['Message']) + "\nSuggestion is: " + str(
                    errors[j]['Suggestion']) + "\nMistake found in: " + str(
                    errors[j]['Actual'])
                f.write(temp)
                str1 = str1 + temp

        else:
            f.write("\n\nYou did not attempt this assignment.")
            str1 = str1 + "\n\nYou did not attempt this assignment."
        f.write("\n----------x----------x---------")
        str1 = str1 + "\n----------x----------x---------"
    f.close()
    Individual(author, msgList, questions, ans, accuracy, accuracy_no, errorCategory, indErr, str1)


def split_text(filename):
    chat = open(filename, encoding="utf8")
    chatText = chat.read()
    return chatText.splitlines()


def distributeByAmPm(linesText):
    timeRegex = re.compile("\\d+\\/\\d+\\/\\d+, (\\d+\\:\\d+)")
    AM, PM = [], []
    for index, line in tqdm(enumerate(linesText)):
        matches = re.findall(timeRegex, line)
        if (len(matches) > 0):
            match = datetime.datetime.strptime(
                matches[0], "%H:%M").strftime('%p')
            if match == "AM":
                AM.append(matches[0])
            else:
                PM.append(matches[0])
    return AM, PM


def getDataPoint(line):
    splitLine = line.split(' - ')
    dateTime = splitLine[0]
    date, time = dateTime.split(', ')
    message = ' '.join(splitLine[1:])
    if startsWithAuthor(message):
        splitMessage = message.split(': ')
        author = splitMessage[0]
        message = ' '.join(splitMessage[1:])
    else:
        author = None
    return date, time, author, message


def typeOfMessage(message):
    qPattern = 'Q[0-9]{1,2}'
    aPattern = 'A[0-9]{1,2}'
    if re.match(qPattern, message):
        return 0
    elif re.match(aPattern, message):
        return 1
    else:
        return -1


def startsWithAuthor(s):
    patterns = [
        '([\\w]+):',
        '([\\w]+[\\s]+[\\w]+):',
        '([\\w]+[\\s]+[\\w]+[\\s]+[\\w]+):',
        '([+]\\d{2} \\d{5} \\d{5}):',
        '([+]\\d{2} \\d{3} \\d{3} \\d{4}):',
        '([+]\\d{2} \\d{4} \\d{7})'
    ]
    pattern = '^' + '|'.join(patterns)
    result = re.match(pattern, s)
    if result:
        return True
    return False


def startsWithDateTime(s):
    pattern = '^([0-2][0-9]|(3)[0-1])(\\/)(((0)[0-9])|((1)[0-2]))(\\/)(\\d{2}|\\d{4}), ([0-9][0-9]):([0-9][0-9]) -'
    result = re.match(pattern, s)
    if result:
        return True
    return False

app = Flask(__name__,template_folder='templates')


@app.route('/')
def upload_file():
    return render_template('index.html')

app.config['UPLOAD_FOLDER'] = 'C:\\Users\\Gitansh\\Documents\\flask_app\\templates'
@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    global totErr
    global errorCategory
    global noOfSub
    global accOfSub
    global student_accuracy
    global edate
    global sdate
    student_asgn_count={}

    if request.method=='POST':
        f = request.files['file1']
        sdate = request.form['startdate']
        edate = request.form['enddate']
        print(request.form.get('userss'))
        inputss = request.form['textt']
        print(inputss)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
        parsedData = []
        parsedData2 = []
        questions=[]
        authorsList ={}
        conversationPath = "C:\\Users\\Gitansh\\Documents\\flask_app\\templates\\dataset.txt"
        with open(conversationPath, encoding="utf-8") as fp:
            fp.readline()
            messageBuffer = []
            date, time, author = None, None, None
            while True:
                line = fp.readline()
                if not line:
                    break
                line = line.strip()
                if startsWithDateTime(line):
                    if len(messageBuffer) > 0:
                        value = typeOfMessage(' '.join(messageBuffer))
                        if value == 0:
                            questions.append(' '.join(messageBuffer))
                        elif value == 1:
                            parsedData2.append([date, time, author, ' '.join(messageBuffer)])
                            if author in authorsList.keys():
                                authorsList[author] = authorsList[author] + 1
                            else:
                                authorsList[author] = 1
                        parsedData.append([date, time, author, ' '.join(messageBuffer)])
                    messageBuffer.clear()
                    date, time, author, message = getDataPoint(line)
                    date_time_obj = datetime.datetime.strptime(date, '%d/%m/%y')
                    date_time_start = datetime.datetime.strptime(sdate, '%Y-%m-%d')
                    date_time_end = datetime.datetime.strptime(edate, '%Y-%m-%d')
                    if(date_time_obj>=date_time_start and date_time_obj<=date_time_end):
                        messageBuffer.append(message)
                else:
                    messageBuffer.append(line)

        for i in range(len(questions)):
            noOfSub[i+1] = 0
        print(len(questions),"mujhe dekho")
        for i in range(len(questions)):
            accOfSub[i+1] = 0
        df = pd.DataFrame(parsedData, columns=['Date', 'Time', 'Author', 'Message'])
        df.head()
        author_value_counts = df['Author'].value_counts()  # Number of messages per author
        dff=pd.DataFrame(author_value_counts, columns=['Author'])
        dff.head()
        autha=[]
        written=[]
        dff.sort_values('Author',ascending=False)
        print(dff)
        for index, row in dff.iterrows():
            autha.append(index)
            written.append(row['Author'])
        temp_df = pd.DataFrame({'Student': autha, 'No_of_Messages': written})
        temp_df = temp_df.sort_values('No_of_Messages',ascending=True)
        temp_df.index.name=None
        temp_df=temp_df.sort_index()
        temp_df=temp_df.head(5)
        dfi.export(temp_df, 'dataframe.png')
        df2 = pd.DataFrame(parsedData2, columns=['Date', 'Time', 'Author', 'Message'])
        df2.head()
        desired_width = 320
        pd.set_option('display.width', desired_width)
        np.set_printoptions(linewidth=desired_width)
        pd.set_option('display.max_columns', 10)
        pd.set_option('display.max_rows', None)
        df2 = df2.sort_values(by='Author')
        df2 = df2[df2.Author.notnull()]
        media_messages_df = df2[df2['Message'] == '<Media omitted>']
        df2 = df2.drop(media_messages_df.index)
        no_of_students = len(authorsList)
        #print("heeloeoeoezeko",no_of_students)
        for i in authorsList:
            authordf = df2.loc[df2['Author'] == i]
            msgList=[]
            for index, row in authordf.iterrows():
                value = str(row['Message'])
                msgList.append(value)
            findError(i, msgList,questions)
        # for i in authorsList:
        #     authordf = df2.loc[df2['Author'] == i]
        #     msgList=[]
        #     for index, row in authordf.iterrows():
        #         if not i in student_asgn_count.keys():
        #             student_asgn_count[i]=0
        #         student_asgn_count[i]+=1
        #         value = str(row['Message'])
        #         msgList.append(value)
        #     findError3(i, msgList,questions)
        ans =[]
        accuracy =0
        # All(questions,ans,accuracy,no_of_students,student_asgn_count)
        
        # i='Maa'
        # authordf = df2.loc[df2['Author'] == i]
        # msgList=[]
        # for index, row in authordf.iterrows():
        #     value = str(row['Message'])
        #     msgList.append(value)
        # findError(i, msgList,questions)
        return "Uploaded successfully!"

if __name__ == '__main__':

    app.run(debug=true)
    