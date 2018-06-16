#!/usr/bin/python

import os
import sys
import glob
import time
import asyncio
import logging
from thrift.Thrift import TException
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.transport import TZlibTransport
from thrift.protocol import TBinaryProtocol
from thrift.protocol import TCompactProtocol
from thrift.protocol import TJSONProtocol
from thrift.server import TServer, TNonblockingServer, THttpServer
dir_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(dir_root)
sys.path.append(dir_root + '/protocol/gen-py/')
#sys.path.append(dir_root + '/protocol/gen-py.tornado')
#sys.path.append(dir_root + '/protocol/gen-py.twisted')

from ExchangeData import ExchangeData
from ExchangeData.ttypes import *

import conf.conf
import util.util
from util.exchange_base import exchange_base
from util.exchange_data import exchange_data




class ExchangeDataHandler(ExchangeData.Iface):
    def getTicker(self, ex_id, symbol):
        """
        Parameters:
         - ex_id
         - symbol
        """
        pass

    def getTickerByTime(self, ex_id, symbol, timestamp):
        """
        Parameters:
         - ex_id
         - symbol
         - timestamp
        """
        pass

    def getTickerFromExchanges(self, symbol, timestamp, ex_ids):
        """
        Parameters:
         - symbol
         - timestamp
         - ex_ids
        """
        pass


if __name__ == '__main__':
    handler = ExchangeDataHandler()
    processor = ExchangeData.Processor(handler)

    transport = TSocket.TServerSocket(host = '127.0.0.1', port = 9090)
    #tfactory = TTransport.TFramedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    server = TNonblockingServer.TNonblockingServer(processor, transport, pfactory)

    print('Starting the server...')
    server.serve()
    print('done.')

