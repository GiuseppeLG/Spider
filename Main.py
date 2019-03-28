import re
from urllib.parse import urlparse
from urllib.request import urlopen, Request
import requests
from hyper import HTTPConnection  # h2 lib must be v2.6.2 (not > 2.x, cause crash)
import mysql.connector

print("@author Giuseppe La Gualano - https://www.linkedin.com/in/giuseppe-la-gualano-56bb8210b")
print("@license This software is free - http://www.gnu.org/licenses/gpl.html")

# Database Handler
try:  # try to open file configDB.txt
    with open("configDB.txt", "r") as f:
        data = f.readlines()

    #  format list of config vars
    configDB = [line.rstrip('\n') for line in open('configDB.txt')]

    configDB = [w.replace('host=', '') for w in configDB]
    configDB = [w.replace('user=', '') for w in configDB]
    configDB = [w.replace('database=', '') for w in configDB]

    try:  # check if file is empty
        host = configDB[0]
        user = configDB[1]
        database = configDB[2]
    except:
        pass

    f.close()

except IOError:  # if file configDB.txt not exist, create new
    file = open("configDB.txt", 'w', newline='\n')
    print("\nDatabase connector config\n")

    #  user input for new db connector
    host = input("HostDB name: ")
    user = input("UserDB name: ")
    database = input("DB name: ")

    file.write("host=" + host + "\n")
    file.write("user=" + user + "\n")
    file.write("database=" + database)
    #  add passwd="" to insert password
    file.close()

dbConnect = True
while dbConnect:
    try:
        mydb = mysql.connector.connect(
            host=host,
            user=user,
            database=database
            #  add passwd="" to insert password
        )
        mycursor = mydb.cursor()
        dbConnect = False
    except:
        print("\nCan't connect: Error Database Config in ConfigDB.txt\n")
        file = open("configDB.txt", 'w', newline='\n')
        host = input("HostDB name: ")
        user = input("UserDB name: ")
        database = input("DB name: ")

        file.write("host=" + host + "\n")
        file.write("user=" + user + "\n")
        file.write("database=" + database)
        #  add passwd="" to insert password
        file.close()

# Initial Lists of tags and urls
start_urls = []
initial_tags = []

print("\nConnection established, make sure the Siti table is present in DB")

print("\nInit urls with only root domain (digit stopURL to complete)")
urlInput = "startURL"
while urlInput != "stopURL":
    urlInput = input("URL di partenza: ")

    if urlInput == "stopURL":
        break

    start_urls.append(urlInput)

print("\nInit TAGS or words (digit stopTAG to complete)")
tagInput = "startTAG"
while tagInput != "stopTAG":
    tagInput = input("TAG di partenza: ")

    if tagInput == "stopTAG":
        break

    initial_tags.append(tagInput)

#  Request and Response cycle
i = 0
while i < len(start_urls):  # hypothetical infinite list

    j = 0
    k = 0

    # Init vars of indexing
    HttpVer = None  # response header http version
    robotsFound = None  # robots.txt is accessible
    mobileFriendly = 0  # viewport found
    siteRank = 0  # ranking of website
    tagCounter = 0  # if almost one it's found, tags is present

    print("\nSite:", start_urls[i])  # Console debug

    viewportTag = "viewport"  # not viewport tag, only string
    userAgentTag = "User-agent"  # this is contained in robots.txt

    try:
        #  try to http2 protocol
        conn = HTTPConnection(start_urls[i] + ":443")  # try to upgrade HTTP2
        conn.request('GET', '/get')  # GET command
        resp = conn.get_response()

        print("HTTP/2 found")
        HttpVer = 2
        siteRank += 1

        # try to find robots.txt
        req = Request('http://' + start_urls[i], headers={'User-Agent': 'Mozilla/5.0'})
        html = str(urlopen(req).read())

        # try to find strings in all document html
        while j < len(initial_tags):
            tagValue = html.find(initial_tags[j])

            if tagValue != -1:
                tagCounter += 1

            j += 1

        if tagCounter >= 1:
            print("tag/s founded")
        else:
            print("tag/s not founded")

        vp = html.find(viewportTag)
        if vp != -1:
            print("viewport tag founded")
            siteRank += 1
            mobileFriendly = 1
        else:
            print("viewport not found")
            mobileFriendly = 0

        #  try to robots.txt
        response = requests.get("https://" + start_urls[i] + "/robots.txt")  # robots.txt finder
        test = str(response.text)

        if userAgentTag in test:  # control if current page is real crawler rules
            print("robots.txt found")
            siteRank += 1
            robotsFound = 1
        else:
            print("robots.txt not found")
            robotsFound = 0

        lines = str(resp.read().splitlines())  # split lines of response read to convert in string
        #  print(lines)

        #  Link extractor, handle try and exc
        try:
            req1 = Request('http://' + start_urls[i], headers={'User-Agent': 'Mozilla/5.0'})
            html1 = str(urlopen(req1).read())

            links = re.findall('"(http?://.*?|https?://.*?)"', html1)  # found all links in page

            # print(links)

            parser = [x for x in links if
                      start_urls[i] not in x]  # search currentDomain link founded, remove from external links

            #  search for duplicate
            while k < len(parser):
                parser[k] = urlparse(parser[k]).netloc
                if not (parser[k] in start_urls):
                    start_urls.append(parser[k])
                k += 1

        except:  # handle the 404 error page created
            pass

    except:  # if upgrade to http2 fail do this

        try:
            # try to http (1.1 or 1.0) version
            conn = HTTPConnection(start_urls[i])
            conn.request('GET', '/get')

            resp = conn.get_response()

            # try to find tag strings
            req = Request('http://' + start_urls[i], headers={'User-Agent': 'Mozilla/5.0'})
            html = str(urlopen(req).read())

            while j < len(initial_tags):
                tagValue = html.find(initial_tags[j])

                if tagValue != -1:
                    tagCounter += 1

                j += 1

            if tagCounter >= 1:
                print("tag/s founded")
            else:
                print("tag/s not founded")

            vp = html.find(viewportTag)
            if vp != -1:
                print("viewport tag founded")
                siteRank += 1
                mobileFriendly = 1
            else:
                print("viewport not found")
                mobileFriendly = 0

            #  try to find robots.txt
            response = requests.get("http://" + start_urls[i] + "/robots.txt")  # robots.txt finder
            test = str(response.text)
            #  print(test) for debug

            if userAgentTag in test:  # control if current page is real crawler rules
                print("robots.txt found")
                siteRank += 1
                robotsFound = 1
            else:
                print("robots.txt not found")
                robotsFound = 0

            #  view http/1.1 or 1.0 version
            http1Ver = "http11"
            httpString = str(resp)

            if http1Ver in httpString:  # find http version between 1.1 and 1.0
                print("HTTP/1.1 found")
                siteRank += 0.5
                HttpVer = 1.1
            else:
                print("HTTP/1.0 found ")
                HttpVer = 1.0

            lines = str(resp.read().splitlines())  # split lines of response read to convert in string

            #  Link extractor, handle try and exc
            try:
                req1 = Request('http://' + start_urls[i], headers={'User-Agent': 'Mozilla/5.0'})
                html1 = str(urlopen(req1).read())

                links = re.findall('"(http?://.*?|https?://.*?)"', html1)  # found all links in page

                # print(links)

                parser = [x for x in links if
                          start_urls[i] not in x]  # search currentDomain link founded, remove from external links

                #  search for duplicate
                while k < len(parser):
                    parser[k] = urlparse(parser[k]).netloc
                    if not (parser[k] in start_urls):
                        start_urls.append(parser[k])
                    k += 1

            except:  # handle the 404 error page created
                pass

        except:  # pass if site doesn't exits (without 404 custom page)
            pass

    try:
        if tagCounter >= 1:
            sql = "INSERT INTO Siti VALUES (%s, %s, %s, %s, %s)"  # necessary present in db table like Siti
            val = (start_urls[i], HttpVer, robotsFound, mobileFriendly, siteRank)
            mycursor.execute(sql, val)
            mydb.commit()
    except:
        pass

    i += 1  # increment for principal while cycle
