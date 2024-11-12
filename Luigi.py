import pandas as pd
import luigi
import os
import requests
import json

def createHouseMembersDataFrame(src_url):
    import requests
    import pandas as pd

    response = requests.get(src_url)

    response.raise_for_status()
    data = response.json().get('objects', [])

    records = []
    for item in data:
        record = {
            'sortname': item.get('person', {}).get('sortname', None),
            'name': item.get('person', {}).get('name', None),
            'firstname': item.get('person', {}).get('firstname', None),
            'middlename': item.get('person', {}).get('middlename', None),
            'lastname': item.get('person', {}).get('lastname', None),
            'namemod': item.get('person', {}).get('namemod', None),
            'nickname': item.get('person', {}).get('nickname', None),
            'description': item.get('description', None),
            'leadership_title': item.get('leadership_title', None),
            'party': item.get('party', None),
            'address': item.get('extra', {}).get('address', None),
            'phone': item.get('phone', None),
            'website': item.get('website', None)
        }
        records.append(record)

    # Converting to DataFrame
    df = pd.DataFrame(records)

    return df[['sortname', 'name', 'firstname', 'middlename', 'lastname', 'namemod', 'nickname',
               'description', 'leadership_title', 'party', 'address', 'phone', 'website']]


class FetchDataFromOrigin(luigi.Task):
    def output(self):
        # Output file path in the current directory
        return luigi.LocalTarget(os.path.join(os.path.dirname(__file__), 'step1.csv'))

    def run(self):
        # Calling createDataFrameAndFile() to fetch data and saving it to a CSV file
        createDataFrameAndFile(file_name='step1.csv', perform_check=True)


def createDataFrameAndFile(file_name, perform_check = False):

    houseMembers = createHouseMembersDataFrame(
        r"https://www.govtrack.us/api/v2/role?current=true&role_type=representative&limit=438")
    

    if perform_check:
        checkHouseMembersDataFrame(houseMembers)

    if file_name:
        houseMembers.to_csv(os.path.join(os.path.dirname(__file__),
                                         file_name), index=False)

class CheckResultOfFetch(luigi.Task):

    def requires(self):
        return FetchDataFromOrigin()

    def complete(self):
        return hasattr(self, '_task_complete') and self._task_complete

    def run(self):
        print (f'*\n* In {type(self).__name__}.run()\n*')
        print (f' > Reading file {self.input().path} into a pandas DataFrame...')
        df = pd.read_csv(self.input().path)
        cols = str(list(df.columns))
        row_count = df.shape[0]
        print (f' > Column names: {cols}')
        print (f' > Data row count: {row_count}')
        self._task_complete = True

def checkHouseMembersDataFrame(df):
    assert isinstance(df,pd.DataFrame), "Argument to df is not a pandas DataFrame"
    assert list(df.columns) == ['sortname', 'name', 'firstname', 'middlename', 'lastname', 'namemod', 'nickname', 
                                'description', 'leadership_title', 'party', 'address', 'phone', 'website'], \
        'Column names do not match specification.'
    assert df[df['phone']=='202-225-3265']['lastname'].iloc[0]=='Cohen', \
       'Data row is incorrect for sortname: "Cohen, Steve (Rep.) [D-TN9]"'
    assert df.shape[0] > 430, 'Too few data rows'
    print (f'\n***\n*** House Members DataFrame is correct!\n***')

#######################################################################################################################

if __name__ == '__main__':

    if 'createHouseMembersDataFrame' in dir():
        createDataFrameAndFile(file_name='step1.csv', perform_check = True)

    if 'FetchDataFromOrigin' in dir():
        luigi.run(main_task_cls=CheckResultOfFetch())

#######################################################################################################################

