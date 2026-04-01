import React, { useState, useEffect } from 'react';
import { History, TrendingUp, TrendingDown, Minus, Clock } from 'lucide-react';

const SignalHistory = () => {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchHistory = async () => {
        try {
            const res = await fetch('/api/signals');
            const data = await res.json();
            if (Array.isArray(data)) {
                setHistory(data);
            } else {
                console.error("Signal history data is not an array:", data);
                setHistory([]);
            }
        } catch (e) {
            console.error("Failed to fetch signal history:", e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchHistory();
        const interval = setInterval(fetchHistory, 5000); // Poll signals every 5s
        return () => clearInterval(interval);
    }, []);

    const getSignalIcon = (signal) => {
        if (signal === 'BUY') return <TrendingUp className="w-3 h-3 mr-1" />;
        if (signal === 'SELL') return <TrendingDown className="w-3 h-3 mr-1" />;
        return <Minus className="w-3 h-3 mr-1" />;
    };

    const getSignalColor = (signal) => {
        if (signal === 'BUY') return 'bg-green-100 text-green-700 border-green-200';
        if (signal === 'SELL') return 'bg-red-100 text-red-700 border-red-200';
        return 'bg-gray-100 text-gray-700 border-gray-200';
    };

    return (
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
            <h2 className="text-xl font-black text-gray-900 flex items-center mb-6">
                <History className="w-6 h-6 mr-3 text-indigo-600" />
                Historique des Signaux
            </h2>

            {loading ? (
                <div className="text-center py-6">Chargement...</div>
            ) : history.length === 0 ? (
                <div className="text-center py-10 bg-gray-50 rounded-xl border border-dashed border-gray-200">
                    <Clock className="w-10 h-10 text-gray-300 mx-auto mb-3" />
                    <p className="text-gray-400 font-bold uppercase tracking-widest text-sm text-center px-4">
                        Aucun changement de signal détecté pour le moment
                    </p>
                </div>
            ) : (
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="text-[10px] text-gray-400 font-black uppercase tracking-widest border-b border-gray-100">
                                <th className="pb-3 px-2">Heure</th>
                                <th className="pb-3 px-2">Symbole</th>
                                <th className="pb-3 px-2">Transition</th>
                                <th className="pb-3 px-2">Prix</th>
                            </tr>
                        </thead>
                        <tbody className="text-sm">
                            {history.map((s, idx) => (
                                <tr key={idx} className="border-b border-gray-50 last:border-0 hover:bg-gray-50 transition-colors">
                                    <td className="py-4 px-2 whitespace-nowrap text-gray-500 font-mono">
                                        {s.timestamp ? new Date(s.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : 'N/A'}
                                    </td>
                                    <td className="py-4 px-2 font-black text-gray-900">{s.symbol}</td>
                                    <td className="py-4 px-2">
                                        <div className="flex items-center space-x-2">
                                            <span className={`px-2 py-0.5 rounded text-[10px] font-black border ${getSignalColor(s.old_signal)}`}>
                                                {s.old_signal}
                                            </span>
                                            <span className="text-gray-400">→</span>
                                            <span className={`px-2 py-0.5 rounded text-[10px] font-black border flex items-center ${getSignalColor(s.new_signal)}`}>
                                                {getSignalIcon(s.new_signal)}
                                                {s.new_signal}
                                            </span>
                                        </div>
                                    </td>
                                    <td className="py-4 px-2 font-mono text-gray-700 font-bold">
                                        ${s.price?.toLocaleString(undefined, { minimumFractionDigits: 2 }) || '0.00'}
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

export default SignalHistory;
