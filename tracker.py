import requests
from bs4 import BeautifulSoup
import tempfile
import os
from dateutil import parser
import datetime
import json

#HOME_URL="http://www.indiapost.gov.in/speednettracking.aspx"
HOME_URL="http://www.indiapost.gov.in/ParcelNetTracking.aspx"
CAPTCHA_URL="http://www.indiapost.gov.in/captcha.aspx"
ROOT_URL = "http://www.indiapost.gov.in/"

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            encoded_object = list(obj.timetuple())[0:6]
        else:
            encoded_object =json.JSONEncoder.default(self, obj)
        return encoded_object

class Tracker:
  def __init__(self):
    self.POST_DATA = {}

    self.session = requests.Session()
    home_response = self.session.get(HOME_URL)

    dom = BeautifulSoup(home_response.content, "lxml")

    inputs = dom.find_all('input')

    for input in inputs:
      if 'value' in input.attrs:
        self.POST_DATA[input.attrs['name']] = input.attrs['value']
      else:
        self.POST_DATA[input.attrs['name']] = None

    self.captcha_url = dom.find(id="imgcap").attrs['src']

    captcha_response = self.session.get(ROOT_URL + self.captcha_url)
    captcha_file = tempfile.NamedTemporaryFile(delete=False)

    captcha_file.write(captcha_response.content)

    captcha_file.close()
    self.POST_DATA['txtCaptcha'] = os.popen("python captcha.py "+captcha_file.name).read().strip()
#print self.POST_DATA['txtCaptcha']
    os.remove(captcha_file.name)

  def track(self, id):
    details = {}
    self.POST_DATA['Txt_ArticleTrack'] = id
    response = self.session.post(HOME_URL, data=self.POST_DATA)
#   print response
    dom = BeautifulSoup(response.content, "lxml")
#print dom

    general_details = dom.find(id="GridView1").findAll('td')

    if len(general_details) < 7:
      return None

    details['id'] = dom.find(id='Lbl_Track1').text.strip()
#print details['id']
    details['Booked at'] = general_details[0].text.strip()
#print details['Booked at'] 
    details['Booked on'] = parser.parse(general_details[1].text.strip())
    details['Destination'] = general_details[2].text.strip()
    details['Tariff'] = general_details[3].text.strip()
    details['Article Type'] = general_details[4].text.strip()
    details['Delivered at'] = general_details[5].text.strip()
    details['Paid on'] = general_details[6].text.strip()
    details['delivered'] = (details['Delivered at'] != 'Not Available')

    details['events'] = []

    events = dom.find(id='GridView2').findAll('tr')[1:]
    for tr in events:
      event = {}
      data = tr.findAll('td')
#event['date'] = parser.parse(data[0].text.strip() + ' ' + data[1].text.strip() + ' IST')
      event['date'] = data[0].text.strip()
      event['office'] = data[2].text.strip()
      event['description'] = data[3].text.strip()

      details['events'].append(event)

# print details
    return details

if __name__ == '__main__':
  orderList = []
  orderList.append("CG003693164IN")
  orderList.append("CG002825473IN")
  for orderID in orderList:
    tracker = Tracker()
    print json.dumps(tracker.track(orderID), cls=DateTimeEncoder, sort_keys=True, indent=4, separators=(',', ': '))
