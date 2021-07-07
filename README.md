# dnd_detail_extractor
Get clean data from .md files for CS411 project

1. You should change 'Enter your dir here /5thSRD-master/docs/adventuring/equipment/only_armor.md' so that the app can work. 
'Enter your dir here ' should be replaced by your home directory (e.g. C:\User\...)

2. All data are in .json format. You can use https://konklone.io/json/ to check the data. 
Just enter values returned by armors, weapons, items, languages, races, raceFeatures,classes, classFeatures.

3. Data are stored in those variables so you can choose to write some code to write data to files or just use print() (e.g. print(armors))
or use an IDE that allows you to view the data directly. (i use spyder from anaconda)

So the data in armors will look like this :
{
    "Armor": [
        {
            "armorName": "Padded",
            "cost": "5 ",
            "armorClass": "11 + Dex modifier",
            "strNeeded": "-",
            "stealthDisadv": "True",
            "weight": "8 ",
            "category": "Light Armor"
        },
        {
            "armorName": "Leather",
            "cost": "10 ",
            "armorClass": "11 + Dex modifier",
            "strNeeded": "-",
            "stealthDisadv": "False",
            "weight": "10 ",
            "category": "Light Armor"
        }]}

You can use https://konklone.io/json/ or https://www.convertjson.com/json-to-sql.htm to convert data into a nice looking table.

4. There are some tables left : Proficiences, Background, Background Info. I don't where to get Background's data, so I didn't do it. For Proficiences, I might need to do some
web scraping.

5. For relationship tables CanCast, ClassEquipment ,TrainedProf,Understand I believe you can write some simple code to generate these tables given current data.

6. If you can, please write a data auto-generator to generate more rows for tables.
