import os
import urllib.request
import json
import pandas as pd

os.environ['CENSUS_KEY'] = ""


class census(object):
    def __init__(self, estimates, year: int = 2017, dataset: int = 1, geography: str = "state", geoids: str = "*", statefips = None, countyfips = None, key: str = os.getenv('CENSUS_KEY')):
        self.estimates = estimates
        self.year = year
        self.dataset = dataset
        self.geography = geography
        self.geoids = geoids
        self.statefips = statefips
        self.countyfips = countyfips
        self.key = key

    def get_product(self, estimates):
        """
        Figures out the product table associated with passed estimate.
        """
        for estimate in estimates[0]:
            if estimate[0] == "S":
                product = "/subject"
            elif estimate[0:1] == "DP":
                product = "/profile"
            elif estimate[0:1] == "CP":
                product = "/cprofile"
            else:
                product = ""
        return product
    
    def build_url(self, key, estimates, year, dataset, geography,  geoids, statefips, countyfips):
        """
        Creates url to pass to Census' API
        """
        
        endpoint = "https://api.census.gov/data/{}/acs".format(year)
        
        # handle 2009
        if year > 2009:
            endpoint += "/acs"
        
        # get product based on estimates
        product = self.get_product(estimates)  
        
        # create estimates
        if type(estimates) == list:
            estimates = ",".join(estimates)
            estimates+=","
        else:
            estimates = "group({})".format(estimates)
        
        # handle geoids, statefips, and countyfips
        geoids = ",".join(geoids)
        
        if statefips is not None:
            statefips = ",".join(statefips)
        
        if countyfips is not None:
            countyfips = ",".join(countyfips)
        
        
        # construct url
        # distinctions for: all states, subset of states, subset of states and subset of counties, and metro areas
        url = endpoint + str(dataset) + product + "?get={}NAME&for=".format(estimates)
        
        if geography != "metro": ## pseudo
            url = url + geography + ":" + geoids
            
            if geography != "state" and statefips is not None:
                url = url + "&in=state:" + statefips
                
                if countyfips is not None:
                    url = url + " county:" + countyfips
        else:
            url = url + "for=state%20(or%20part):{}&in={}:{}".format(statefips, geography, geoids)
        
        url += "&key=" + key
        url = url.replace(" ", "%20")
        
        return url
    
    def retrieve_census(self, url):
        """
        Takes url and reads JSON into memory
        """
        response = urllib.request.urlopen(url)
        data = json.loads(response.read())
        return data
    
    def census_to_df(self, data):
        """
        Stores retrieved Census data as pandas dataframe
        """
        columns = data[0]
        rows = data[1:]
        df = pd.DataFrame(columns=columns, data=rows)
        return df

    def get_table(self):
        self.url = self.build_url(self.key, self.estimates, self.year, self.dataset, self.geography, self.geoids, self.statefips, self.countyfips)
        self.data = self.retrieve_census(self.url)
        self.table = self.census_to_df(self.data)
        return self.table

### Tests

census(['B01001_001E'], geography = "state").get_table()

# County table
acs = census(["B01001_001E"], geography = "county")
county = acs.get_table()

# Update query and get state tables instead
acs.geography = "state"
state = acs.get_table()

dicts = {}
i = 0
for geo in ['state', 'county', 'cd']:
    df = get_table(x, y, z, geo = geo)
i = 