import requests
import pdfplumber
import json
import re

headers = {'User-Agent': 'Mozilla/5.0 (X11; Windows; Windows x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36'}
url_schedule = 'http://www.fa.ru/org/spo/kip/Documents/raspisanie/2022-2023/аудитории.pdf'


def download_pdf():
    response = requests.get(url_schedule, headers=headers)
    with open('аудитории.pdf', 'wb') as f:
        f.write(response.content)

    convert2json()

def convert2json():
    pdf = pdfplumber.open("аудитории.pdf")

    table = []
    for i in pdf.pages:
        table += i.extract_table()

    date_pdf = pdf.pages[0].within_bbox((0, 0, pdf.pages[0].width, pdf.pages[0].height/2 )).extract_text()[:40]
    if 'Аудитории' in date_pdf:
      try:
        date = 'Расписание на ' + re.search(r"\d\d.\d\d.\d\d\d\d \(\w+\)", date_pdf).group()
      except:
        date = 'Расписание на ' + re.search(r"\d\d.\d\d.\d\d\d\d\(\w+\)", date_pdf).group()
    else:
      date = 'Расписание'
      
    with open('schedule.json', 'w') as f:
        json.dump(table + [date], f)

def get_schedule(group="1ОИБАС-1022"):
 
    with open('schedule.json') as f:
        table = json.load(f)
    temp1 = ''.join(table[0]).replace(' ', '').replace('\n', '')
    try:
      if group.startswith("1"):
          time = re.findall(r"\d\d:\d\d-\d\d:\d\d", temp1.replace(re.search("\d\d:\d\d-\d\d:\d\d2-4курс", temp1).group(), '')) 
      else:
         time = re.findall(r"\d\d:\d\d-\d\d:\d\d", temp1.replace(re.search("\d\d:\d\d-\d\d:\d\d1курс", temp1).group(), ''))
    except:
      time = re.findall(r"\d\d:\d\d-\d\d:\d\d", temp1)
      
    text = f"`{table[-1]}`\n"

    temp = []

    for key, value in enumerate(table):
        for k, v in enumerate(value):
            if v is not None and group in v:
                if any(x == k for x, *_ in temp):
                    for x, y in enumerate(temp):
                        if k == y[0]:
                            temp[x] += [[table[key+1][k], value[0]]]
                    continue        
                temp += [[k, [table[key+1][k], value[0]]]]

    temp = sorted(temp)
    if temp:
      for i in temp:
        if len(i) < 3:
            text += f'\n{str(i[0]) + " пара"} ({time[i[0]-1]})\n\t\t*{i[1][0]}* _{i[1][1]}_'
        else:
            text += f'\n{str(i[0]) + " пара"} ({time[i[0]-1]})\n\t\t*{i[1][0]}* _{i[1][1]}_\n\t\t*{i[2][0]}* _{i[2][1]}_'

    else:
      text += '\n*Занятий нет*'
            
    return text

def get_list_of_teacher():
    with open('schedule.json') as f:
        table = json.load(f)
      
    _list = [(table[i][0], str(i)) for i in range(1, len(table)-1, 2)]
  
    return _list

def get_teacher(id):
    with open('schedule.json') as f:
        table = json.load(f)

    return table[int(id)][0]

def get_schedule_for_teacher(name):
    with open('schedule.json') as f:
        table = json.load(f)
      
    for i, k in enumerate(table):
      if k[0] == name:
        auds = table[i+1]
        teacher = k
        break
    else:
     return None
    
    zipped = zip(teacher, auds)
    temp = []
    for i, (group, aud) in enumerate(zipped):
      if i == 0:
        temp += [group]
        continue
      temp += [[group, aud]]

    temp1 = ''.join(table[0]).replace(' ', '').replace('\n', '')
    try:
        time1 = re.findall(r"\d\d:\d\d-\d\d:\d\d", temp1.replace(re.search("\d\d:\d\d-\d\d:\d\d2-4курс", temp1).group(), '')) 
        time2 = re.findall(r"\d\d:\d\d-\d\d:\d\d", temp1.replace(re.search("\d\d:\d\d-\d\d:\d\d1курс", temp1).group(), ''))
    except:
      time1 = time2 = re.findall(r"\d\d:\d\d-\d\d:\d\d", temp1)

    text = f"`{table[-1]}`\nПреподаватель: {temp[0]}\n"
  
    for i, k in enumerate(temp):
      if isinstance(k, list) and k[0]:
        if k[0].startswith('1'):
          time = time2
        else:
          time = time2
          
        text += f'\n{str(i) + " пара"} ({time[i-1]})\n\t\t*{k[1]}* _{k[0]}_'


    return text

if __name__ == "__main__":
    #print(get_schedule())
    print(get_teacher(11))