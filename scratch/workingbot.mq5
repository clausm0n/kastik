//+------------------------------------------------------------------+
//|                                                      FlaskTest.mq5 |
//|                        Copyright 2023, MetaQuotes Software Corp. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2023, MetaQuotes Software Corp."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict

#include <Trade\Trade.mqh>
#include <Trade\SymbolInfo.mqh>

// Global variables
CTrade Trade;
CSymbolInfo SymbolInfo;
string API_URL = "http://127.0.0.1:5000/infer";
string SymbolName;
datetime lastCheckTime;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
   SymbolName = _Symbol;
   lastCheckTime = TimeCurrent();
   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
  }

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
  {
   if(TimeCurrent() - lastCheckTime < 30)
     {
      return;
     }
   lastCheckTime = TimeCurrent();
   
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);

   if (balance != equity)
     {
      int totalOrders = PositionsTotal();
      for (int i = 0; i < totalOrders; i++)
        {
         ulong ticket = PositionGetTicket(i);
         if (ticket > 0)
           {
            double closePrice;
            SymbolInfoDouble(SymbolName, SYMBOL_BID, closePrice);
            Trade.PositionClose(ticket, closePrice);
           }
        }
     }
   else
     {
      string headers = "Content-Type: application/json";

      string url = API_URL;
      char result[];
      string result_headers;
      char placeholder[];

      int res = WebRequest("GET", url, headers, 5000, placeholder, result, result_headers);

      if (res > 0)
        {
         string response = CharArrayToString(result);

         // Parse the response and execute trade operations.
        }
      else
        {
         Print("Error in WebRequest. Error code =", GetLastError());
        }
     }
  }
//+------------------------------------------------------------------+