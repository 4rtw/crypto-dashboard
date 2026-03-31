import React, { useState, useEffect } from 'react';
import { History, CheckCircle, XCircle, Clock } from 'lucide-react';

const TradeHistory = () => {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchHistory = async () => {
        try {
            const res = await fetch('http://localhost:8000/api/history');
            const data = await res.json();
            setHistory(data);
        } catch (e) {
            console.error("Failed to fetch history:", e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchHistory();
        const interval = setInterval(fetchHistory, 5000); // Poll history every 5s
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 mt-8">
            <h2 className="text-xl font-black text-gray-900 flex items-center mb-6">
                <History className="w-6 h-6 mr-3 text-blue-600" />
                Derniers Trades Execution (Spot)
            </h2>

            {loading ? (
                <div className="text-center py-6">Chargement...</div>
            ) : history.length === 0 ? (
                <div className="text-center py-10 bg-gray-50 rounded-xl border border-dashed border-gray-200">
                    <Clock className="w-10 h-10 text-gray-300 mx-auto mb-3" />
                    <p className="text-gray-400 font-bold uppercase tracking-widest text-sm">Aucun historique de trade sur cette session</p>
                </div>
            ) : (
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="text-[10px] text-gray-400 font-black uppercase tracking-widest border-b border-gray-100">
                                <th className="pb-3 px-2">Date (S)</th>
                                <th className="pb-3 px-2">Symbole</th>
                                <th className="pb-3 px-2">Side</th>
                                <th className="pb-3 px-2">Qté</th>
                                <th className="pb-3 px-2">Prix</th>
                                <th className="pb-3 px-2">Statut</th>
                            </tr>
                        </thead>
                        <tbody className="text-sm">
                            {history.map((t, idx) => (
                                <tr key={idx} className="border-b border-gray-50 last:border-0 hover:bg-gray-50 transition-colors">
                                    <td className="py-4 px-2 whitespace-nowrap text-gray-500 font-mono">
                                        {new Date(t.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                                    </td>
                                    <td className="py-4 px-2 font-black text-gray-900">{t.symbol}</td>
                                    <td className="py-4 px-2">
                                        <span className={`px-2 py-1 rounded text-[10px] font-black ${t.side === 'BUY' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}`}>
                                            {t.side}
                                        </span>
                                    </td>
                                    <td className="py-4 px-2 font-mono">{t.quantity}</td>
                                    <td className="py-4 px-2 font-mono text-gray-700 font-bold">
                                        {t.price > 0 ? `$${t.price.toLocaleString(undefined, { minimumFractionDigits: 2 })}` : "-"}
                                    </td>
                                    <td className="py-4 px-2">
                                        {t.status === 'FILLED' ? (
                                            <span className="flex items-center text-green-600 font-bold">
                                                <CheckCircle className="w-4 h-4 mr-1" /> OK
                                            </span>
                                        ) : (
                                            <span className="flex items-center text-red-600 font-bold" title={t.error}>
                                                <XCircle className="w-4 h-4 mr-1" /> FAIL
                                            </span>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default TradeHistory;
