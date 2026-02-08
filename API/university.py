import requests
import json

def get_college():
 answer = requests.get("https://uomustansiriyah.edu.iq/api/dpt_list.php?dt=c&l=en")
 return json.loads(answer.text)

def get_depart(college_data, value):
 for i in college_data:
  if value == i["dept_name"]:
     res = requests.get(f"https://uomustansiriyah.edu.iq/api/dpt_list.php?dt=ds&mdid={i['id']}&l=en")
     return json.loads(res.text)
 return []
