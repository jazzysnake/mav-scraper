import os
import time
import network_scrape
import response_parser
import persist_data
import logging
import pandas as pd

LOGGER = logging.getLogger(__name__)

def get_data():
    LOGGER.debug('getting data...')
    return network_scrape.get_position_data()

def parse_data(raw_data):
    LOGGER.debug('parsing data...')
    df = response_parser.parse_position_data(raw_data)
    return df

def save_data(parsed):
    LOGGER.debug('saving data...')
    persist_data.save_dataframe(parsed)

if __name__ == '__main__':

    while(True):
        try:
            response = get_data()
            parsed = parse_data(response)
            save_data(parsed)
        except Exception as e:
            LOGGER.error(f'Exception occured {e}')
        time.sleep(120)

