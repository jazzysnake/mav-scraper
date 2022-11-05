import pandas as pd
import numpy as np
import re
import logger
import asyncio
import network_scrape
import time
from bs4 import BeautifulSoup

LOGGER = logger.get_logger(__name__)

style = 'background-color:red;color:white;text-align:center;white-space: normal;'

def parse_position_data(raw_json):
    df = pd.DataFrame(raw_json)
    df = pd.json_normalize(df.iloc[3],)
    df = df['Trains.Train'].values
    df = pd.json_normalize(df).T
    df = pd.DataFrame.from_records(df[0],
                                   columns=['@Delay',
                                            '@Lat',
                                            '@Relation',
                                            '@TrainNumber',
                                            '@Menetvonal',
                                            '@Lon',
                                            '@ElviraID',
                                            '@Line'])

    delayed = df.loc[df['@Delay']>5]
    delayed = delayed[['@ElviraID','@TrainNumber']]

    delayed, idk = asyncio.run(network_scrape.get_delay_multi(delayed))
    delayed = [item.result() for item in delayed]
    delayed = [parse_delay_data(elvira_id, item) for elvira_id, item in delayed]

    delayed_id = [delay_id for delay_id, delay_cause in delayed]
    delay_cause = [delay_cause for delay_id, delay_cause in delayed]

    df = df.rename(columns={'@ElviraID':'@ElviraId','@Menetvonal':'@LineKind'})
    df.columns = [_rename_col(col) for col in df.columns]
    delayed = np.array([delayed_id, delay_cause])

    df['delay_cause'] = np.nan
    df = df.apply(lambda row: _cause_to_elvira_id(row, delayed),axis=1)
        
    df['timestamp'] = int(time.time()*1000)

    LOGGER.info(f'current num of punctual trains: {len(df)-len(delayed)}')
    LOGGER.info(f'current num of delayed trains: {len(delayed[0,:])}')
    return df

def parse_delay_data(elvira_id, raw_json):
    df = pd.DataFrame(raw_json)
    df = df.T
    html = df['result'].values[0]['html']
    soup = BeautifulSoup(html,'html.parser')
    style_match = [item.text for item in soup.find_all('th',style=style)]
    cause = np.nan
    if len(style_match) > 0:
        cause = style_match[-1]
    return elvira_id, cause

def _rename_col(col):
    col = col.replace('@', '')
    return re.sub(r'(?<!^)(?=[A-Z])', '_', col).lower()

def _cause_to_elvira_id(row, delay_data):
    for i, elvira_id in enumerate(delay_data[0,:]):
        if row['elvira_id'] == delay_data[0,i]:
            row['delay_cause'] = delay_data[1,i]
    return row
