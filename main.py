import language_tool_python
import json
import re
import sys
import datetime
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm
import numpy as np
from fpdf import FPDF, fpdf

def Individual(author,msgList,questions,ans,accuracy,errorCategory,indErr):
    asgnList = []
    for i in range(len(ans)):
        asgnList.append("Asgn"+str(ans[i]))
    plt.plot(asgnList, accuracy, marker='.',markersize=15)
    plt.title('Assignment Evaluation', fontsize=14)
    plt.xlabel('Assignments', fontsize=14)
    plt.ylabel('Accuracy', fontsize=14)
    plt.savefig('Accuracy.png', dpi=300, bbox_inches='tight')
    plt.clf()

    y = np.array([len(ans),len(questions)-len(ans)])
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
    plt.savefig('errorType.png', dpi=300, bbox_inches='tight')
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=30)
    pdf.cell(200, 10, txt="Student Analysis Report", ln=1, align="C")
    variable = asgnList
    variable2 = str(len(questions))
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt="Name :-" + author, ln=3, align="L")
    pdf.cell(200, 10, txt="Total Number of Assignments :-  " + variable2, ln=4, align="L")
    pdf.cell(200, 10, txt="Assignments Attempted :-  " + str(variable) , ln=5, align="L")
    pdf.cell(200, 10, txt="Please find below the evaluation charts for the inputted user.", ln=6, align="L")
    pdf.image('Accuracy.png', x = 50, y = 70, w = 100, h = 80, type = '', link = '')
    pdf.image('Attempted.png', x=10, y=160, w=80, h=80, type='', link='')
    pdf.image('errorType.png', x=120, y=160, w=80, h=80, type='', link='')
    pdf.output(author+'.pdf')
def All():
    return
def findError(author, msgList,questions):
    f = open(author + ".txt", "w+")
    f.write("Submission by: " + author)
    ans=[]
    for i in msgList:
        temp1=i.split(" ",1)
        temp2=temp1[0].split("A")
        temp3=temp2[1]
        ans.append(int(temp3))
    temp="\n\nTotal Number of Assignments = " +str(len(questions)) + "\nNumber of Assignments Attempted = " + str(len(ans))
    f.write(temp)
    cnt=0
    accuracy=[]
    errorCategory={}
    indErr = 0
    for s in range(len(questions)):
        string="\n\nAssignment "+str(s+1)+":" + questions[s].split(" ",1)[1]
        f.write(string)
        if s+1 in ans:
            line = msgList[cnt].split(" ",1)[1]
            cnt+=1
            tool = language_tool_python.LanguageTool('en-US')
            i = 0
            c = 0
            errors = {}
            matches = tool.check(line)
            i = i + len(matches)
            indErr += i
            print(100-100*(len(matches)/len(line.split())))
            accuracy.append(100-100*(len(matches)/len(line.split())))
            for mistake in matches:
                c += 1
                errors[c] = {'Error': mistake.ruleId, 'Suggestion': mistake.replacements, 'Message': mistake.message,
                             'Actual': mistake.matchedText}
                if mistake.category in errorCategory.keys():
                    errorCategory[mistake.category] = errorCategory[mistake.category] + 1
                else:
                    errorCategory[mistake.category] = 1
            f.write("\n\nYour Submission: " + line)
            f.write("\n\nNo. of mistakes found in submission is " + str(i))
            for j in errors:
                temp = "\n\nError message: " + str(errors[j]['Message']) + "\nType of error: " + str(
                    errors[j]['Error']) + "\nSuggestion is: " + str(errors[j]['Suggestion']) + "\nMistake found in: " + str(
                    errors[j]['Actual'])
                f.write(temp)
        else:
            f.write("\n\nYou did not attempt this assignment.")
        f.write("\n----------x----------x---------")
    f.close()
    Individual(author, msgList, questions, ans, accuracy, errorCategory, indErr)



def split_text(filename):
    chat = open(filename, encoding="utf8")
    chatText = chat.read()
    return chatText.splitlines()


def distributeByAmPm(linesText):
    timeRegex = re.compile("\d+\/\d+\/\d+, (\d+\:\d+)")
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
        '([\w]+):',
        '([\w]+[\s]+[\w]+):',
        '([\w]+[\s]+[\w]+[\s]+[\w]+):',
        '([+]\d{2} \d{5} \d{5}):',
        '([+]\d{2} \d{3} \d{3} \d{4}):',
        '([+]\d{2} \d{4} \d{7})'
    ]
    pattern = '^' + '|'.join(patterns)
    result = re.match(pattern, s)
    if result:
        return True
    return False


def startsWithDateTime(s):
    pattern = '^([0-2][0-9]|(3)[0-1])(\/)(((0)[0-9])|((1)[0-2]))(\/)(\d{2}|\d{4}), ([0-9][0-9]):([0-9][0-9]) -'
    result = re.match(pattern, s)
    if result:
        return True
    return False


if __name__ == '__main__':
    parsedData2 = []
    questions=[]
    authorsList ={}
    conversationPath = "iSaksham Test.txt"
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
                messageBuffer.clear()
                date, time, author, message = getDataPoint(line)
                messageBuffer.append(message)
            else:
                messageBuffer.append(line)
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
    # for i in authorsList:
    #     authordf = df2.loc[df2['Author'] == i]
    #     msgList=[]
    #     for index, row in authordf.iterrows():
    #         value = str(row['Message'])
    #         msgList.append(value)
    #     findError(i, msgList,questions)
    i='Maa'
    authordf = df2.loc[df2['Author'] == i]
    msgList=[]
    for index, row in authordf.iterrows():
        value = str(row['Message'])
        msgList.append(value)
    findError(i, msgList,questions)