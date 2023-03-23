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
#include <JAson.mqh>


// Global variables
CTrade Trade;
CSymbolInfo SymbolInfo;
string API_URL = "http://127.0.0.1:5000/infer";
string SymbolName;
datetime lastCheckTime;
input double UserLotSize = 0.01; // User-defined lot size
input double TakeProfit = 15.0; // User-defined take profit in points
input double MaxOrders = 6; // User-Defined Max orders


//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
   SymbolName = Symbol();
   Print(SymbolName);
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
  string headers = "Content-Type: application/json";

  string url = API_URL;
  char result[];
  string result_headers;
  char placeholder[];
   if(TimeCurrent() - lastCheckTime < 40)
     {
      
      int res = WebRequest("GET", url, headers, 5000, placeholder, result, result_headers);
      if (res > 0)
        {
        CJAVal jv;
        jv.Deserialize(result);
         string orderType = jv["command"].ToStr();
         string prediction = jv["prediction"].ToStr();
         Print(orderType + " " + prediction);
        }
      int totalOrders = PositionsTotal();
      for (int i = 0; i < totalOrders; i++)
         {
             ulong ticket = PositionGetTicket(i);
             if (ticket > 0)
             {
                 
                 ENUM_POSITION_TYPE positionType = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
                 double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
                 double currentPrice = PositionGetDouble(POSITION_PRICE_CURRENT);
                 double profitPoints = (positionType == POSITION_TYPE_BUY ? currentPrice - openPrice : openPrice - currentPrice) * _Point;
                 //Print(profitPoints);        
                 if (profitPoints >= TakeProfit)
                 {
                     Trade.PositionClose(ticket, currentPrice);
                 }
             }
         }
     
      return;
     }
   lastCheckTime = TimeCurrent();
   
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   int totalOrders = PositionsTotal();
   if(totalOrders < MaxOrders){

      int res = WebRequest("GET", url, headers, 5000, placeholder, result, result_headers);
      if (res > 0)
        {
        CJAVal jv;
        jv.Deserialize(result);
         string orderType = jv["command"].ToStr();
         string prediction = jv["prediction"].ToStr();
            if (orderType == "SELL" || orderType == "BUY")
            {
            Print(orderType);
            ENUM_ORDER_TYPE ot = orderType == "SELL" ? ORDER_TYPE_SELL : ORDER_TYPE_BUY;
            Print(ot);
            double requiredMargin;
            OrderCalcMargin(ot, SymbolName, UserLotSize, SymbolInfo.Ask(), requiredMargin);
            if (equity >= requiredMargin)
              {
               double price = ot == 0 ? SymbolInfo.Ask() : SymbolInfo.Bid();
               //Print("asking price" + price);
               double sl = 0.0;
               double tp = 0.0;
               MqlTradeRequest tradeRequest;
               MqlTradeResult tradeResult;
               
               tradeRequest.action = TRADE_ACTION_DEAL;
               tradeRequest.symbol = SymbolName;
               tradeRequest.volume = UserLotSize;
               tradeRequest.price = price;
               tradeRequest.sl = sl;
               tradeRequest.tp = tp;
               tradeRequest.type = ot == 1 ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
               tradeRequest.type_filling = ORDER_FILLING_IOC;
               tradeRequest.type_time = ORDER_TIME_GTC;
               
               
               MqlTradeCheckResult check;
               bool checkResult = OrderCheck(tradeRequest, check);
               //Print(checkResult);
               //Print(check.comment);
               bool orderResult = OrderSend(tradeRequest, tradeResult);
               if (orderResult)
                {
                    // Order placed successfully, you can print the trade result or perform other actions here
                    Print("Order placed successfully, Order ticket: ", tradeResult.order);
                }
                else
                {
                    // Order placement failed, print the error information
                    Print("Order placement failed, Error code: ", GetLastError());
                }
               
                
              }
            else
              {
               Print("Insufficient balance for trade");
              }
           }
        }
      else
        {
         Print("Error in WebRequest. Error code =", GetLastError());
        }
     }
  }
//+------------------------------------------------------------------+
