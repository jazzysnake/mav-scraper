import requests
import asyncio
import pandas as pd
import numpy as np
import logger

LOGGER = logger.get_logger(__name__)

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json; charset=UTF-8',
    'Origin': 'http://vonatinfo.mav-start.hu',
    'Referer': 'http://vonatinfo.mav-start.hu/',
    'Sec-GPC': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}

json_data_pos = {
    'a': 'TRAINS',
    'jo': {
        'history': True,
        'id': True,
    },
}

json_data_delay_cause = {
    'a': 'TRAIN',
    'jo': {
        'v': '6227914_221029',
        'vsz': '559555',
        'zoom': False,
        'csakkozlekedovonat': False,
    },
}

url = 'http://vonatinfo.mav-start.hu/map.aspx/getData'

def get_position_data():
    response = requests.post(url, headers=headers, json=json_data_pos, verify=False)
    return response.json()

async def get_delay_multi(delayed):
    groups = [get_delay(
        train['@ElviraID'],train['@TrainNumber']) for index, train in delayed.iterrows()]
    delayed = await asyncio.wait(groups)
    return delayed

async def get_delay(elvira_id, train_id):
    json_data_delay_cause['jo']['v'] = elvira_id
    json_data_delay_cause['jo']['vsz'] = train_id
    try:
        response = requests.post(url, headers=headers, json=json_data_delay_cause, verify=False)
    except Exception as e:
        LOGGER.error(f'Exception occured when getting delay for {elvira_id}, {train_id}')
        LOGGER.error(e)
        return elvira_id, np.nan

    return elvira_id, response.json()
