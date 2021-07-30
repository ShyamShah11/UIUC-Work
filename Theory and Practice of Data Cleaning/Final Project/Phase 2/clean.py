# @begin AddLocationInfo @desc Use geopy package to find location information
# @in farmersmarketsor.csv @uri file:farmersmarketsor.csv
# @out farmersmarketpy.csv @uri file:farmersmarketspy.csv

import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim

def addLocations():
    
    data = pd.read_csv("Final Project/Phase 2/farmersmarketsor.csv")
    #first check for missing city and use coordinates to populate
    #lookup(data, hasCoords, "city", "municipality"), town, village, city, hamlet
    
    geocoder = Nominatim(user_agent = 'data_cleaning_project')
    zipCtr, countyCtr, cityCtr, ctr =0,0,0,0
    for index, row in data.iterrows():
        ctr+=1
        location=None
        if (pd.isnull(row["zip"]) or pd.isnull(row["County"]) or pd.isnull(row["city"])) and pd.notnull(row["x"]) and pd.notnull(row["y"]): #check if there area any missing values
            location = geocoder.reverse((data["y"][index],data["x"][index])).raw['address']
        try:    
            if location:
                if pd.isnull(row["zip"]): #check for missing zipcode
                    data.loc[index,"zip"]=str(location["postcode"]).encode("utf-8")
                    zipCtr+=1
                if pd.isnull(row["County"]): #check for missing county
                    data.loc[index, "County"]=str(location["county"]).encode("utf-8")
                    countyCtr+=1
                if pd.isnull(row["city"]): #check for missing city in order: city, muncipality, town, village, hamlet
                    if "city" in location:
                        data.loc[index, "city"]=str(location["city"]).encode("utf-8")
                    elif "municipality" in location:
                        data.loc[index, "city"]=str(location["municipality"]).encode("utf-8")
                    elif "town" in location:
                        data.loc[index, "city"]=str(location["town"]).encode("utf-8")
                    elif "village" in location:
                        data.loc[index, "city"]=str(location["village"]).encode("utf-8")
                    elif "hamlet" in location:
                        data.loc[index, "city"]=str(location["hamlet"]).encode("utf-8")
                    cityCtr+=1
        except KeyError: #either zip or county is missing so ignore
            pass
    print (zipCtr, countyCtr, cityCtr, ctr)
    data.to_csv("Final Project/Phase 2/farmersmarketspy.csv", index=False, encoding="utf-8")
#@end  AddLocationInfo
addLocations()


