import React, { useState } from 'react';
import axios from 'axios';
import { ShoppingCart, LogOut } from 'lucide-react';

const TradeForm = () => {
    const [apiKey, setApiKey] = useState('');
    const [apiSecret, setApiSecret] = useState('');
    const [symbol, setSymbol] = useState('BTCUSDT');
    const [side, setSide] = useState('BUY');
    const [quantity, setQuantity] = useState(0.001);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setResult(null);
        try {
            const resp = await axios.post('/api/trade', {
                api_key: apiKey,
                api_secret: apiSecret,
                symbol,
                side,
                quantity
            });
            setResult(resp.data);
        } catch (err) {
            setResult({ status: 'error', message: err.message });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-white p-6 rounded-xl shadow-md border border-gray-100">
            <h2 className="text-xl font-bold mb-6 flex items-center">
                <ShoppingCart className="w-5 h-5 mr-1" /> Execute Order
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700">API Key</label>
                        <input
                            type="password"
                            value={apiKey}
                            onChange={(e) => setApiKey(e.target.value)}
                            className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">API Secret</label>
                        <input
                            type="password"
                            value={apiSecret}
                            onChange={(e) => setApiSecret(e.target.value)}
                            className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            required
                        />
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Symbol</label>
                        <select
                            value={symbol}
                            onChange={(e) => setSymbol(e.target.value)}
                            className="mt-1 block w-full px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm sm:text-sm"
                        >
                            <option value="BTCUSDT">BTC/USDT</option>
                            <option value="ETHUSDT">ETH/USDT</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Side</label>
                        <select
                            value={side}
                            onChange={(e) => setSide(e.target.value)}
                            className="mt-1 block w-full px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm sm:text-sm"
                        >
                            <option value="BUY">BUY</option>
                            <option value="SELL">SELL</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Quantity</label>
                        <input
                            type="number"
                            step="0.0001"
                            value={quantity}
                            onChange={(e) => setQuantity(Number(e.target.value))}
                            className="mt-1 block w-full px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm sm:text-sm"
                            required
                        />
                    </div>
                </div>

                <button
                    type="submit"
                    disabled={loading}
                    className={`w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white transition-colors
                        ${side === 'BUY' ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700'}
                        ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                    {loading ? 'Processing...' : `Place ${side} Order`}
                </button>
            </form>

            {result && (
                <div className={`mt-6 p-4 rounded-lg text-sm border ${result.status === 'success' ? 'bg-green-50 text-green-700 border-green-200' : 'bg-red-50 text-red-700 border-red-200'}`}>
                    <pre className="overflow-x-auto">{JSON.stringify(result, null, 2)}</pre>
                </div>
            )}
        </div>
    );
};

export default TradeForm;
