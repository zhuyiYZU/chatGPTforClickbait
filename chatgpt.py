import csv
import openai
import codecs
import pandas as pd
import time

list_label = list()
i = 0  # i记录list_label中的位置
TP = 0
FP = 0
FN = 0
TN = 0


#输入 api_key
chat_gpt_key1 = 'YOUR_API_KEY'

def read_csv_row_range(csv_file, start_row, end_row):
    with open(csv_file, 'r', encoding='gbk') as file:
        csv_reader = csv.reader(file)
        for index, row in enumerate(csv_reader):
            if start_row <= index + 1 <= end_row:
                yield row

#训练
def read_csv_rows(csv_file):
    with open(csv_file, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        #header = next(csv_reader)  # 跳过标题行
        for row in csv_reader:
            yield row
#
csv_file_train = '../train.csv'
str_p1 = "请帮我检测以下输入是或不是点击诱饵。\n"
for row in read_csv_rows(csv_file_train):
    if int(row[0])==1:
        str_p1 = str_p1+"输入: {"+row[1]+"}\n输出: {是，这是一个点击诱饵}\n"
    else:
        str_p1 = str_p1 + "输入: {" + row[1] + "}\n输出: {不，这不是一个点击诱饵}\n"

# str_p2 =''
# for row in read_csv_rows(csv_file_train):
#     if int(row[0])==1:
#         str_p2 = str_p2+"Sentence:{"+row[1] +"}\nQuestion: Detect the above sentence is clickbait or not.\nAnswer: {Yes, it is a clickbait}\n"
#     else:
#         str_p2 = str_p2+"Sentence:{"+row[1] +"}\nQuestion: Detect the above sentence is clickbait or not.\nAnswer: {No, it is not a clickbait}\n"

# str_p2 = 'I want you to detect whether the input sentence is clickbait or not.you should only answer yes or no\n'
# for row in read_csv_rows(csv_file_train):
#     if int(row[0])==1:
#         str_p2 = str_p2+"title:"+row[1] +'text:'+row[2][0:20]+".this is  a clickbait.your answer only should be Yes\n"
#     else:
#         str_p2 = str_p2+"title:"+row[1] +'text:'+row[2][0:20]+".this is not a clickbait.your answer only should be No\n"


csv_file = '../test.csv'
start_row = 0  # 起始行号
end_row = 100  # 结束行号
row_step = 101  # 行步长


while True:
    openai.api_key = chat_gpt_key1
    messages = []
    print("user:" + str_p1)
    content = str_p1
    messages.append({"role": "user", "content": content})

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        # model="text-davinci-003",
        messages=messages
    )
    time.sleep(20)
    chat_response = completion
    answer = chat_response.choices[0].message.content
    print(f'ChatGPT: {answer}')
    messages.append({"role": "assistant", "content": answer})
    for row in read_csv_row_range(csv_file, start_row, end_row):
        #print(row)
        #P1
        print("user:" + "输入: {"+row[1]+"}\n输出:")
        content = "输入: {"+row[1]+"}\n输出:"
        # P2
        # print("user:" + "Sentence: {" + row[1] + "}\nQuestion: Detect the above sentence is clickbait or not.\nAnswer:")
        # content = "Sentence: {" + row[1] + "}\nQuestion: Detect the above sentence is clickbait or not.\nAnswer:"
        messages.append({"role": "user", "content": content})

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            # model="text-davinci-003",
            messages=messages
        )
        time.sleep(20)
        chat_response = completion
        answer = chat_response.choices[0].message.content
        print(f'ChatGPT: {answer}')
        messages.append({"role": "assistant", "content": answer})

        if 'No' in answer:
            list_label.append([0])
        else:
            list_label.append([1])

        if int(row[0]) == 1 and list_label[i][0] == 1:
            TP = TP + 1
            i = i + 1
        elif int(row[0]) == 0 and list_label[i][0] == 1:
            FP = FP + 1
            i = i + 1
        elif int(row[0]) == 1 and list_label[i][0] == 0:
            FN = FN + 1
            i = i + 1
        elif int(row[0]) == 0 and list_label[i][0] == 0:
            TN = TN + 1
            i = i + 1
        else:
            print("出错啦")
        print(TP, FP, FN, TN)

    # 增加起始行号和结束行号
    start_row += row_step
    end_row += row_step

    # 判断是否达到文件末尾
    with open(csv_file, 'r', encoding='gbk') as file:
        csv_reader = csv.reader(file)
        line_count = sum(1 for _ in csv_reader)
        if end_row >= line_count:
            break