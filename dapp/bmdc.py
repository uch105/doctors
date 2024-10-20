import requests
from bs4 import BeautifulSoup

def fetch_doctor_data(s):

    response = requests.get(s)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        bmdc = soup.find("h3",{'class': 'mt-1'}).text
        name = soup.find("h3",{'class': 'mb-4'}).text
        h5s = soup.find_all('h5')
        regyear = h5s[0].text
        regvalidyear = h5s[1].text
        h6s = soup.find_all('h6')
        dob = h6s[0].text
        bg = h6s[1].text
        fname = h6s[2].text
        mname = h6s[3].text
        status = h6s[4].text
        context = {
            'Validation': True,
            'bmdc': bmdc,
            'name': name,
            'regyear': regyear,
            'regvalidyear': regvalidyear,
            'dob': dob,
            'bg': bg,
            'fname': fname,
            'mname': mname,
            'status': status,
        }
        return context
    else:
        context={'Validation': False,}
        return context