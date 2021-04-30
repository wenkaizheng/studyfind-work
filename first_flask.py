import json
import requests
from flask import Flask, request        
app = Flask(__name__)
# this can be change depend on requirement
def search_pi_name_helper(pi_first_name,pi_middle_name,pi_last_name,offset):
    search_json = {'criteria':{
            'pi_names': [ {'first_name': pi_first_name, 'middle_name': pi_middle_name , 'last_name': pi_last_name }]
        }, 'limit' : 500, 'offset': offset
    }
    link = 'https://api.reporter.nih.gov/v1/projects/Search'

    r = requests.post(link, json=search_json)
    if not r.text:
        return 0,'' 
    rv = ''    
    data = json.loads(r.text)
    for record in data['results']:
       rv += json.dumps(record)
    return len(data['results']), rv   

'''
get the correct paramter at first
since max value for one time number of query result is 500, so we increment 500 as offset everytime
until there is no more 500 results or reply is empty string which means there is no more
'''
@app.route('/search',methods = ['GET'])
def search_pi_name():
    parameters = {'first_name': '','middle_name': '','last_name': ''}
    query_string = request.query_string.decode('utf-8')
    # standard format first_name = Matthew && middle_name = D && last_name = welch
    query_string = query_string.split('&&')
    for s in query_string:
        flag = True
        for p in parameters:
            if (s.find(p) != -1):
                pos = s.find('=')
                if pos == -1:
                    return 'Invalid URL'
                parameters[p] = s[pos+1:]
                flag = False
        if flag:
            return 'Invalid URL'

    pi_first_name = parameters['first_name']
    pi_middle_name = parameters['middle_name']
    pi_last_name = parameters['last_name']
    total = ''
    rv,content = search_pi_name_helper(pi_first_name,pi_middle_name,pi_last_name,0)
    total += content
    offset = rv
    while (rv == 500):
        rv,content = search_pi_name_helper(pi_first_name,pi_middle_name,pi_last_name,offset)
        total += content
        offset += rv
    return 'The total number of result will be ' + str(offset) + '<br/> ' + total
    
if __name__ == '__main__':
   app.run()