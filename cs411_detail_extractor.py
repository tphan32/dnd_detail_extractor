# -*- coding: utf-8 -*-
"""
https://konklone.io/json/
https://python-markdown.github.io/reference/
https://www.convertjson.com/json-to-sql.htm
"""

import os
import re
import markdown
from bs4 import BeautifulSoup
import json
from pathlib import Path

all_classes = ["barbarian", "bard", "cleric", "druid", "fighter", "monk", "paladin", "ranger", "rogue", "sorcerer", "warlock", "wizard"]
abilities = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
num_pattern = r'[0-9]+'
rm_tags_pattern = r'<.*?>'

def stringCleaner(str):
    str = str.strip(' *\n')
    return str

def mrkd2json(inp,tableName):
    lines = inp.split('\n')
    ret={tableName:[]}
    keys=[]
    for i,l in enumerate(lines):
        if i==0:
            keys=[_i.strip() for _i in l.split('|')]
        elif i==1: continue
        else:
            ret[tableName].append({keys[_i]:v.strip() for _i,v in enumerate(l.split('|')) if  _i>0 and _i<len(keys)-1})         
    return json.dumps(ret, indent = 4) 

def cleanTxt(pattern, newStr, txt):
    clean = re.compile(pattern)
    return re.sub(clean, newStr , txt)

def findMatchingStr(pattern, txt):
    rex = re.compile(pattern)
    return rex.findall(txt)

def extractMagic():
    magic_list = []
    magic_table = {"Magic":[]}
    def extractMagicHelper(file_path):
        fromAtt2Idx = { 'Level' : 0, 'Proficiency Bonus': 1, 'Cantrips Known': 2, 'Spells Known' : 3, 
                       '1st': 4,  '2nd' : 5, '3rd':6, '4th':7, '5th':8, '6th':9, '7th':10, '8th':11,
                       '9th':12, 'Features':13}
        heads = ['level','profBonus', 'cantrips', 'spellKnown', 'slotsLvl1', 'slotsLvl2', 'slotsLvl3', 'slotsLvl4', 'slotsLvl5' , 'slotsLvl6' , 'slotsLvl7', 'slotsLvl8','slotsLvl9', 'Features', 'className']
        
        with open(file_path, 'r',  encoding="utf-8") as f:
            html = markdown.markdown(f.read())
            f.close()
        
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text().split('\n')
            className = text[0]
        
        
            row = ["NULL"]*len(heads)
            row[-1] = className
            
            idxs = []
            attributes = text[2].split('|')[1:-1]
            for att in attributes:
                key = stringCleaner(att)
                idxs.append(fromAtt2Idx[key])
        
            table = text[4:24]
            for r in table:
                r = r.split('|')[1:-1]
                for i,entry in enumerate(r):
                    value = stringCleaner(entry)
                    if value != '-':
                        if i == 0:
                            if 'st' in value:
                                row[idxs[i]] = value.replace("st", '')
                            elif 'nd' in value:
                                row[idxs[i]] = value.replace("nd", '')
                            elif 'rd' in value:
                                row[idxs[i]] = value.replace("rd", '')
                            else:
                                row[idxs[i]] = value.replace("th", '')
                        elif i == 1:
                            row[idxs[i]]  = value.replace('+', '')
                        else:
                            row[idxs[i]] = value
                magic_list.append([row[-2], row[-1],row[0]])
                new_row = row[:-2]
                new_row.append(row[-1])
                new_heads = heads[:-2]
                new_heads.append(heads[-1])
                magic_table["Magic"].append({ new_heads[i]:value for i,value in enumerate(new_row)}) 
    path = 'Enter your dir here /5thSRD-master/docs/character/classes/'
    os.chdir(path)
    for file in os.listdir():
        if file.endswith(".md"):
            file_path = f"{path}/{file}"
            extractMagicHelper(file_path)  
    return json.dumps(magic_table, indent = 4), magic_list



def extractClassDetails(magic2lvl):
    class_table = {"Class": []}
    feature_table = {"ClassFeature": []}
    def classDetailsHelper(file_path,file_path2):
        with open(file_path, 'r', encoding="utf-8") as f:
            dndClass = ["className ", "subClass", "hitPoints", "description", "gold", "spellCastAbility"]
            classFeatures = ['featureName','description','className','classLevel']
            
            html = markdown.markdown(f.read())
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text()
        
            className = cleanTxt(rm_tags_pattern,'',soup.find_all("h1")[0].text)
            subClass = "NULL"
            with open(file_path2, 'r',  encoding="utf-8") as f2:
                description = BeautifulSoup(markdown.markdown(f2.read()), "html.parser").get_text()
                f2.close()
            gold = 0
            
            body_pattern = r'</strong>.*'
            body = findMatchingStr(body_pattern, html)
            hitPoint = body[1][10:12]
            
            spell_ab_idx = text.find("Spellcasting Ability")+len("Spellcasting Ability")
            spellCastAbility = text[spell_ab_idx:spell_ab_idx+20].split(' ')[0]
            if len(spellCastAbility) <= 2:
                spellCastAbility = "NULL"
        
            dndClassValues = [className, subClass, hitPoint, description, gold, spellCastAbility ]
            
            class_table["Class"].append({dndClass[i]:v for i,v in enumerate(dndClassValues)})
        
            features_heads = [cleanTxt(rm_tags_pattern,'',s.text) for s in soup.find_all('h3')]
            feature_pattern = r'<hr />'
            list_idx = list(re.finditer(feature_pattern, html))
            features_body = []
            for i in range(len(list_idx)-1):
                body = html[list_idx[i].end():list_idx[i+1].start()]
                h3_idx = body.find("<h3>")
                body = cleanTxt(rm_tags_pattern, '', body[:h3_idx]).strip("\n")
                features_body.append(body)
            features_body.append(cleanTxt(rm_tags_pattern, '', html[list_idx[i+1].end():]).strip("\n"))
            
            for i,feature in enumerate(features_heads):
                lvl = 'NULL'
                for magic in magic2lvl:
                    if feature in magic[0] and className == magic[1]:
                        lvl = magic[2]
                        featureValues = [feature, features_body[i], className, lvl]
                        feature_table["ClassFeature"].append({classFeatures[j]:v for j,v in enumerate(featureValues)})
                if lvl == 'NULL':
                    featureValues = [feature, features_body[i], className, lvl]
                    feature_table["ClassFeature"].append({classFeatures[j]:v for j,v in enumerate(featureValues)})
                    

    path = 'Enter your dir here /5thSRD-master/docs/character/classes/'
    os.chdir(path)
    for file in os.listdir():
        if file.endswith(".md"):
            file_path = f"{path}/{file}"
            file_path2 = file_path[:-3] + ".des"
            classDetailsHelper(file_path, file_path2)    
    return json.dumps(class_table, indent = 4), json.dumps(feature_table, indent = 4)

def extractRaceAndFeatures():
    features_table = {"RaceFeature":[]}
    races_table = {"Race":[]}
    def extractHelper(file_path):        
        with open(file_path, 'r', encoding="utf-8") as f:
            html = markdown.markdown(f.read())
            soup = BeautifulSoup(html, "html.parser")
            raceName = cleanTxt(rm_tags_pattern,'',soup.find_all("h1")[0].text)
            subRace = '-'
            if len(soup.find_all("h2")) > 1: 
                subRace = cleanTxt(rm_tags_pattern,'',soup.find_all("h2")[1].text)
                
            head =[ cleanTxt(rm_tags_pattern,'',s.text).replace('.', '') for s in soup.find_all("strong") ]
            body_pattern = r'</strong>.*</p>?'
            rex = re.compile(body_pattern, re.IGNORECASE)
            targets = rex.findall(html)
            body = [cleanTxt(rm_tags_pattern, '', s) for s in targets]
            result =list(zip(head,body)) 
            keys = ['raceName','subRace','abilityScoreIncrease1','abilityScoreIncrease2','ability1','ability2', 'ageRange', 'description', 'size', 'speed' ]
            values = [raceName,subRace]
            container = features_table["RaceFeature"]
            for r in result:
                if r[0] == 'Ability Score Increase' and raceName != "Human":
                    for a in abilities:
                        if a in r[1]:
                            values.append(a)
                    if len(values) == 3:
                        values.append(('NULL'))
                    values = values + findMatchingStr(num_pattern, r[1])
                    if len(values) == 5:
                        values.append('NULL')
                elif r[0] == 'Ability Score Increase' and raceName == "Human":
                    n = ['NULL']*4 
                    values = values + n 
                elif r[0] == 'Alignment' or r[0] == 'Age':
                    values.append(r[1].strip(' '))
                elif r[0] == 'Size':
                    values = values + findMatchingStr(r'Large|Medium|Small', r[1])
                elif r[0] == 'Speed':
                    values = values + findMatchingStr(num_pattern, r[1])
                else:
                    if raceName != "Human":
                        container.append({})
                        container[-1].update({"featureName":r[0]})
                        container[-1].update({"description":r[1].strip(' ')})
                        container[-1].update({"raceName":raceName})
            races_table["Race"].append({keys[i]:value for i,value in enumerate(values)}) 

    path = 'Enter your dir here /5thSRD-master/docs/character/races/'
    os.chdir(path)
    for file in os.listdir():
        if file.endswith(".md"):
            file_path = f"{path}/{file}"
            extractHelper(file_path)
    return json.dumps(races_table, indent=4), json.dumps(features_table, indent=4)



def cleanSpellsFiles():
    spells = {"spells":[]}
    def extractSpellsDetails(file_path):
        with open(file_path,'r', encoding="utf-8") as f:
            if 'spells' in file_path:
                container = spells["spells"]
                container.append({})
                key = ''
                value = ''
                des = ''
                for line in f:
    
                    if len(container[-1].keys()) > 7 and line != '\n':
                        des = des + line
                        continue
                        
                    cclass = stringCleaner(line)
                    if cclass in all_classes:
                        container[-1][key] = cclass+"," +value
                        continue
                    
                    if line == '\n' or line[0] == '#' or line[0] == '_':
                        continue
                    key = stringCleaner(line[:line.find(':')])
                    value = stringCleaner(line[line.find(':')+1:])
                    container[-1].update({key:value}) 
    
            container[-1].update({"description":des}) 
            f.close()
            classes = (container[-1]["classes"])
            if ',' in classes:
                classes = classes.split(",")
                new_entry = container.pop()
                for c in classes:
                    cp_entry = new_entry.copy()
                    cp_entry["classes"] = c 
                    container.append(cp_entry)
    path = 'Enter your dir here /5thSRD-master/docs/spellcasting/spells'
    os.chdir(path)
    for file in os.listdir():
        if file.endswith(".md"):
            file_path = f"{path}/{file}"
            extractSpellsDetails(file_path)
    return spells

def extractDetails(path, tableName,oldnewStr =()):
    with open (path, "r", encoding="utf-8") as f: 
        details = mrkd2json(f.read(), tableName)
        for p in oldnewStr:
            details = cleanTxt(p[0], p[1], details)
        f.close()
    return details

if __name__ == "__main__":
    spells = cleanSpellsFiles()
    
    replace_str_iw = [(r"gp|lb.|Str|cp|sp|",''), (r'"-"', '"NULL"')]
    replace_str_armor = [(r'Disadvantage','True'),(r"gp|lb.|Str|", '')]

    path = 'Enter your dir here /5thSRD-master/docs/adventuring/equipment/only_armor.md'
    armors = extractDetails(path,"Armor",replace_str_armor)
    
    path = 'Enter your dir here /5thSRD-master/docs/adventuring/equipment/only_weapons.md'
    weapons = extractDetails(path,"Weapon", replace_str_iw)
    
    path = 'Enter your dir here /5thSRD-master/docs/adventuring/equipment/only_items.md'
    items = extractDetails(path,"GeneralItem", replace_str_iw)
    
    path = 'Enter your dir here /5thSRD-master/docs/character/only_languages.md'
    languages = extractDetails(path,"Language")
    
    races, raceFeatures =extractRaceAndFeatures()
    
    magic, magic2lvl = extractMagic()
    
    classes, classFeatures = extractClassDetails(magic2lvl)
