import React, { useState, useEffect } from 'react';
import { Bell, Send, CheckCircle } from 'lucide-react';

const NotificationSettings = () => {
    const [webhookUrl, setWebhookUrl] = useState('');
    const [saved, setSaved] = useState(false);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        // Fetch current webhook on mount
        fetch('/api/webhook')
            .then(res => res.json())
            .then(data => setWebhookUrl(data.url || ''))
            .catch(err => console.error("Could not fetch webhook:", err));
    }, []);

    const saveWebhook = async () => {
        setLoading(true);
        try {
            const res = await fetch('/api/webhook', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: webhookUrl })
            });
            if (res.ok) {
                setSaved(true);
                setTimeout(() => setSaved(false), 3000);
            }
        } catch (e) {
            alert("Erreur lors de la sauvegarde du webhook");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
            <h3 className="text-lg font-black text-gray-900 flex items-center mb-4">
                <Bell className="w-5 h-5 mr-3 text-purple-600" />
                Alertes Discord Webhook (Spot)
            </h3>
            
            <div className="space-y-4">
                <p className="text-xs text-gray-500 font-medium">
                    Entre ton Discord Webhook URL pour recevoir une notification dès que le signal (BUY / SELL / HOLD) change pour BTC ou ETH.
                </p>
                
                <div className="flex space-x-2">
                    <input
                        type="password"
                        placeholder="https://discord.com/api/webhooks/..."
                        className="flex-1 bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm font-mono focus:ring-2 focus:ring-purple-500 outline-none transition-all"
                        value={webhookUrl}
                        onChange={(e) => setWebhookUrl(e.target.value)}
                    />
                    <button
                        onClick={saveWebhook}
                        disabled={loading}
                        className={`px-5 py-3 rounded-xl font-black text-sm uppercase tracking-widest flex items-center transition-all ${saved ? 'bg-green-500 text-white' : 'bg-purple-600 hover:bg-purple-700 text-white shadow-lg'}`}
                    >
                        {saved ? <CheckCircle className="w-4 h-4 mr-2" /> : <Send className="w-4 h-4 mr-2" />}
                        {saved ? 'Sauvegardé' : 'Save'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default NotificationSettings;
