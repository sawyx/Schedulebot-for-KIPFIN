import requests as r
import re
import json

url = 'http://www.fa.ru/org/spo/kip/Pages/class_h.aspx'
headers = {
  'User-Agent':
  'Mozilla/5.0 (X11; Windows; Windows x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36'
}


# update once a year :D
def parsing_group():
  res = r.get(url, headers=headers)
  list_of_group = re.findall(r'\d[а-яА-Я]{4,6}-\d{3,4}',
                             res.text.replace('\u200b', ''))

  return list_of_group


def list_to_dict():
  list_of_group = parsing_group()
  dictionary = {}
  for i in list_of_group:
    key = i[0]
    if key not in dictionary:
      dictionary[key] = []
    dictionary[key].append(i)

  return dictionary


def save_json():
  list_of_group = list_to_dict()
  with open('group.json', 'w') as f:
    json.dump(list_of_group, f)

  return list_of_group
