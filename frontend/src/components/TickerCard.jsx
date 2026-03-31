import React from 'react';
import { TrendingUp, TrendingDown, Info, ShieldCheck, Zap } from 'lucide-react';

const TickerCard = ({ symbol, data }) => {
  const { price, change, signal, rsi, macd, confidence, winrate, states, sma_20, sma_50, market, timeframe } = data || {};
  
  const getSignalColor = (s) => {
    if (s === 'BUY') return 'text-green-600 bg-green-100 border-green-200';
    if (s === 'SELL') return 'text-red-600 bg-red-100 border-red-200';
    return 'text-gray-600 bg-gray-100 border-gray-200';
  };

  const isUp = change >= 0;

  return (
    <div className="bg-white p-6 rounded-2xl shadow-xl border border-gray-100 transition-all hover:shadow-2xl">
      {/* Header Symbol & Signal */}
      <div className="flex justify-between items-center mb-6">
        <div>
           <div className="flex items-center space-x-2">
               <h3 className="text-2xl font-black text-gray-900 tracking-tight">{symbol}</h3>
               <span className="px-2 py-0.5 rounded-full bg-blue-100 text-blue-600 text-[10px] font-black uppercase tracking-widest">{market || 'Spot'}</span>
           </div>
           <div className="flex items-center mt-1">
              <span className={`flex items-center text-sm font-bold ${isUp ? 'text-green-500' : 'text-red-500'}`}>
                {isUp ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />}
                {change?.toFixed(2)}% <span className="text-gray-400 font-normal ml-1">({timeframe || '1h'})</span>
              </span>
           </div>
        </div>
        <div className="flex flex-col items-end">
            <span className={`px-4 py-2 rounded-xl text-sm font-black border-2 ${getSignalColor(signal)} shadow-sm`}>
              {signal || 'WAITING'}
            </span>
            <span className="text-[10px] text-gray-400 font-bold uppercase mt-1">Status: Active</span>
        </div>
      </div>
      
      {/* Price Section */}
      <div className="mb-6">
        <span className="text-4xl font-mono font-bold text-gray-900 tabular-nums">
          ${price?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
        </span>
      </div>

      {/* Probability & Winrate */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-xl border border-blue-100 relative overflow-hidden">
            <div className="relative z-10">
                <p className="text-[10px] text-blue-500 font-black uppercase mb-1 flex items-center">
                    <Zap className="w-3 h-3 mr-1" /> Confluence
                </p>
                <p className="text-2xl font-black text-blue-900">{confidence || 0}%</p>
            </div>
            <div className="absolute right-0 bottom-0 h-1 bg-blue-400" style={{ width: `${confidence}%` }}></div>
        </div>
        <div className="bg-purple-50 p-4 rounded-xl border border-purple-100 relative overflow-hidden">
            <div className="relative z-10">
                <p className="text-[10px] text-purple-500 font-black uppercase mb-1 flex items-center">
                    <ShieldCheck className="w-3 h-3 mr-1" /> Winrate ({timeframe || '1h'})
                </p>
                <p className="text-2xl font-black text-purple-900">{winrate || 0}%</p>
            </div>
            <div className="absolute right-0 bottom-0 h-1 bg-purple-400" style={{ width: `${winrate}%` }}></div>
        </div>
      </div>

      {/* Detailed Indicators States */}
      <div className="space-y-3 bg-gray-50 p-4 rounded-2xl border border-gray-100">
        <p className="text-xs font-black text-gray-400 uppercase tracking-widest flex items-center mb-1">
            <Info className="w-3 h-3 mr-1" /> Oscillators & MA ({timeframe || '1h'})
        </p>
        
        <div className="flex justify-between items-center text-sm">
            <span className="text-gray-500 font-bold">RSI (14)</span>
            <div className="flex items-center">
                <span className={`mr-2 px-1.5 py-0.5 rounded text-[10px] font-black ${states?.rsi === 'OVERBOUGHT' ? 'bg-red-100 text-red-600' : (states?.rsi === 'OVERSOLD' ? 'bg-green-100 text-green-600' : 'bg-gray-200 text-gray-500')}`}>
                    {states?.rsi}
                </span>
                <span className="font-mono font-bold text-gray-700">{rsi?.toFixed(2)}</span>
            </div>
        </div>

        <div className="flex justify-between items-center text-sm">
            <span className="text-gray-500 font-bold">MACD (12,26,9)</span>
            <div className="flex items-center">
                <span className={`mr-2 px-1.5 py-0.5 rounded text-[10px] font-black ${states?.macd === 'BULLISH' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}`}>
                    {states?.macd}
                </span>
                <span className="font-mono font-bold text-gray-700">{macd?.toFixed(2)}</span>
            </div>
        </div>

        <div className="border-t border-gray-200 pt-2 flex justify-between items-center text-sm">
            <span className="text-gray-500 font-bold">SMA 20/50</span>
            <div className="flex flex-col items-end">
                <span className="font-mono text-[11px] font-bold text-gray-700">20: ${sma_20?.toFixed(1)}</span>
                <span className="font-mono text-[11px] font-bold text-gray-700">50: ${sma_50?.toFixed(1)}</span>
            </div>
        </div>
      </div>
    </div>
  );
};

export default TickerCard;
