import language_tool_python
import json
import re
import sys
import datetime
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm
import numpy as np
# Mention the language keyword
def func(author,s):
    line=s
    tool = language_tool_python.LanguageTool('en-US')
    i = 0
    c=0
    errors={}
    matches = tool.check(line)
    print(matches)
    i = i + len(matches)
    for mistake in matches:
        c += 1
        errors[c] = {'Error': mistake.ruleId, 'Suggestion': mistake.replacements,'Message':mistake.message, 'Actual': mistake.matchedText}
    print("No. of mistakes found in document is ", i)
    print()
    y = json.dumps(errors)
    print(y)
    f = open(author+".txt", "w+")
    f.write("Submission by: "+author)
    f.write("\n\nYour Submission: "+line)
    f.write("\n\nNo. of mistakes found in submission is "+str(i))
    for j in errors:
        temp="\n\nError message: "+str(errors[j]['Message'])+"\nType of error: "+str(errors[j]['Error']) +"\nSuggestion is: "+str(errors[j]['Suggestion'])+"\nMistake found in: "+str(errors[j]['Actual'])
        f.write(temp)
    f.close()
def split_text(filename):
    """
    Split file contents by newline.
    """
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
        print("True")
        return 0
    elif re.match(aPattern, message):
        print("False")
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
    parsedData = []
    parsedData2 = []
    conversationPath = "WhatsApp Chat with Induction 20' Volunteers.txt"
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
                    value=typeOfMessage(' '.join(messageBuffer))
                    if value==0:
                        parsedData.append([date, time, author, ' '.join(messageBuffer)])
                    elif value==1:
                        parsedData2.append([date, time, author, ' '.join(messageBuffer)])
                messageBuffer.clear()
                date, time, author, message = getDataPoint(line)
                messageBuffer.append(message)
            else:
                messageBuffer.append(line)
    df = pd.DataFrame(parsedData, columns=['Date', 'Time', 'Author', 'Message'])
    df.head()
    print(df)
    df2 = pd.DataFrame(parsedData2, columns=['Date', 'Time', 'Author', 'Message'])
    df2.head()
    print(df2)
    desired_width = 320
    pd.set_option('display.width', desired_width)
    np.set_printoptions(linewidth=desired_width)
    pd.set_option('display.max_columns', 10)
    pd.set_option('display.max_rows', None)
    df = df.sort_values(by='Author')
    df = df[df.Author.notnull()]
    media_messages_df = df[df['Message'] == '<Media omitted>']
    df = df.drop(media_messages_df.index)
    author="Aniansh"
    authordf = df.loc[df['Author'] == author]
    value = str(authordf.iloc[-1].Message)
    print(value)
    #func(author,value)


