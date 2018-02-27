'''This is to test modules.'''
import json
import configparser

from igclient import IGClient
from apps.market_watcher import MarketWatcher

config = configparser.ConfigParser()
config.read('config.conf')

client = IGClient()
client.session()


def main():
    epics = [i for i in json.loads(config['Epics']['EPIC_IDS'])]
    watcher = MarketWatcher(client=client, epics=epics)
    watcher.watch()


if __name__ == '__main__':
    main()
