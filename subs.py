import re
import csv

def loadAllianceCorrections(filename):
    corrections = []
    with open(filename, 'r') as f:
        csv_reader = csv.reader(f, delimiter=',')
        for row in csv_reader:
            corrections.append([row[0], row[1]])

    return corrections

def translateTFEW(search, corrections):
    for key, val in corrections:
        search = re.sub(r'^' + key + '$', val, search)

    return search

def extractNoteName(name, p1, start):
    note = name[p1:]
    # Remove the trailing parenths wherever its at (might be in the middle)
    note = re.sub('\)', '', note)
    # If there's a double parenths...remove that too
    note = re.sub('\(', '', note)

    # Remove the entire note from the name, including the space before, if its there
    if name[p1 - 2 + start] == ' ':
        name = name[:p1 - 2 + start]
    else:
        name = name[:p1 - 1 + start]

    return name, note

def extractRegex(regex, name, note):
    # Go back one spot if the regex already includes the leading space
    remove = 1
    if regex[1] == ' ':
        remove = 0
    test = re.search(regex, name)
    if test:
        name, nnote = extractNoteName(name, test.span()[0], remove)
        if note:
            note += ' ' + nnote
        else:
            note = nnote

    return name, note

def removeExtra(name):
    note = ''

    # First find paranthesis start so we can extract the note
    # Assuming that everything after a parenths start is the note!
    p1 = name.find('(') + 1
    if p1:
        name, note = extractNoteName(name, p1, 0)

    # If we didn't find one, check for a date-type note...then another, and another
    # Dates like 11/12/2022, 11.12.2022 or Nov.12.2022
    name, note = extractRegex('\w+[\/\.-]', name, note)
    # Dates like Nov 12, 2022 or Nov 12th, 2022
    name, note = extractRegex('\w+ \w+, \d+', name, note)
    # Alliance identifiers like SP, SE, sx
    name, note = extractRegex(' [Ss][A-Za-z]', name, note)
    # EX DZ is also a problem for some reason
    name, note = extractRegex(' [Ee][Xx]', name, note)
    name, note = extractRegex(' [Dd][Zz]', name, note)

    return name, note
