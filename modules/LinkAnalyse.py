import re

def getLinks(body):
    links = []

    regex = re.compile(r"https?://[^\s^\"^\'^<]+")
    for match in re.findall(regex, body):
        if links.count(match) == -0:
            links.append(match)
    
    return links