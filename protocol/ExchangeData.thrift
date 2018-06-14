/**
 *  bool        Boolean, one byte
 *  i8 (byte)   Signed 8-bit integer
 *  i16         Signed 16-bit integer
 *  i32         Signed 32-bit integer
 *  i64         Signed 64-bit integer
 *  double      64-bit floating point value
 *  string      String
 *  binary      Blob (byte array)
 *  map<t1,t2>  Map from one type to another
 *  list<t1>    Ordered list of one type
 *  set<t1>     Set of unique elements of one type
 */

/*
{
  'symbol': symbol,
  'timestamp': timestamp,
  'datetime': iso8601,
  'high': self.safe_float(ticker, 'highPrice'),
  'low': self.safe_float(ticker, 'lowPrice'),
  'bid': self.safe_float(ticker, 'bidPrice'),
  'bidVolume': self.safe_float(ticker, 'bidQty'),
  'ask': self.safe_float(ticker, 'askPrice'),
  'askVolume': self.safe_float(ticker, 'askQty'),
  'vwap': self.safe_float(ticker, 'weightedAvgPrice'),
  'open': self.safe_float(ticker, 'openPrice'),
  'close': self.safe_float(ticker, 'prevClosePrice'),
  'first': None,
  'last': self.safe_float(ticker, 'lastPrice'),
  'change': self.safe_float(ticker, 'priceChange'),
  'percentage': self.safe_float(ticker, 'priceChangePercent'),
  'average': None,
  'baseVolume': self.safe_float(ticker, 'volume'),
  'quoteVolume': self.safe_float(ticker, 'quoteVolume'),
  'info': ticker,
}
*/
struct TickerInfo {
  1: string ex_id
  2: string symbol
  3: i64 timestamp
  4: double bid
  5: double ask
}

service ExchangeData {
  TickerInfo getTicker(1: string ex_id, 2:string symbol),
  TickerInfo getTickerByTime(1: string ex_id, 2:string symbol, 3:i64 timestamp),
  // 同 1 种 symbol， 多个交易所
  map<string, TickerInfo> getTickerFromExchanges(1:string symbol, 2:i64 timestamp, 3:list<string> ex_ids),

}



