import React from 'react';
import useBinanceSocket from './hooks/useBinanceSocket';
import TickerCard from './components/TickerCard';
import TradeForm from './components/TradeForm';
import TradeHistory from './components/TradeHistory';
import NotificationSettings from './components/NotificationSettings';

// Using lucide-react for icons
import { Activity as ActivityIcon, ShieldCheck as ShieldIcon, Globe as GlobeIcon } from 'lucide-react';

function App() {
  const { data: tickers, status } = useBinanceSocket('ws://localhost:8000/ws/tickers');

  return (
    <div className="min-h-screen bg-gray-100 py-6 px-4 sm:px-6 lg:px-8 font-sans">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Header */}
        <header className="flex flex-col md:flex-row md:items-center md:justify-between bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
          <div>
            <h1 className="text-3xl font-black text-gray-900 flex items-center">
              <ActivityIcon className="w-8 h-8 mr-3 text-blue-600" />
              Crypto Dashboard <span className="ml-3 text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded-lg uppercase tracking-widest font-black">Spot V1</span>
            </h1>
            <p className="text-sm text-gray-400 mt-1 uppercase font-black tracking-widest flex items-center">
              <GlobeIcon className="w-3 h-3 mr-2" /> Real-time Binance Surveillance
            </p>
          </div>
          <div className="mt-4 md:mt-0 flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${status === 'connected' ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
            <span className="text-sm font-black text-gray-600 uppercase tracking-widest">{status === 'connected' ? 'Live' : 'Offline'}</span>
          </div>
        </header>

        {/* Ticker Cards */}
        <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <TickerCard symbol="BTC/USDT" data={tickers.BTCUSDT} />
          <TickerCard symbol="ETH/USDT" data={tickers.ETHUSDT} />
        </section>

        {/* Settings & Alerts Section */}
        <NotificationSettings />

        {/* Trade and History Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            <TradeForm />
            <TradeHistory />
          </div>
          <div className="space-y-6">
            <div className="bg-blue-600 p-6 rounded-3xl text-white shadow-xl overflow-hidden relative border-4 border-blue-500">
              <ShieldIcon className="absolute -right-4 -bottom-4 w-32 h-32 text-blue-400 opacity-20" />
              <h3 className="text-xl font-black mb-2 uppercase tracking-tight italic">Secure Keys</h3>
              <p className="text-blue-100 text-sm leading-relaxed relative z-10 font-bold">
                API keys are never saved. Each order is isolated. Non-persistent state for maximum security.
              </p>
            </div>
            
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
              <h3 className="text-xs font-black mb-4 text-gray-400 uppercase tracking-widest">Logic & Metrics</h3>
              <ul className="text-sm text-gray-600 space-y-3">
                <li className="flex items-start">
                  <div className="w-2 h-2 rounded-full bg-green-500 mt-1.5 mr-3 shrink-0"></div>
                  <div>
                      <b className="text-gray-900 block">BUY CONFLUENCE</b>
                      <span className="text-xs">RSI &lt; 35 + Bullish MACD + Price &gt; SMAs.</span>
                  </div>
                </li>
                <li className="flex items-start">
                  <div className="w-2 h-2 rounded-full bg-red-500 mt-1.5 mr-3 shrink-0"></div>
                  <div>
                      <b className="text-gray-900 block">SELL CONFLUENCE</b>
                      <span className="text-xs">RSI &gt; 65 + Bearish MACD.</span>
                  </div>
                </li>
                <li className="flex items-start">
                  <div className="w-2 h-2 rounded-full bg-blue-500 mt-1.5 mr-3 shrink-0"></div>
                  <div>
                      <b className="text-gray-900 block">NOTIFICATIONS</b>
                      <span className="text-xs">Alertes Discord immédiates en cas de changement de signal.</span>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
