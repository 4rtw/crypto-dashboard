import { useState, useEffect, useRef } from 'react';

const useBinanceSocket = (url) => {
  const [data, setData] = useState({});
  const [status, setStatus] = useState('disconnected');
  const ws = useRef(null);

  useEffect(() => {
    ws.current = new WebSocket(url);

    ws.current.onopen = () => {
      setStatus('connected');
    };

    ws.current.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      setData(msg);
    };

    ws.current.onclose = () => {
        setStatus('disconnected');
    };

    ws.current.onerror = (error) => {
        setStatus('error');
    };

    return () => {
      if (ws.current) ws.current.close();
    };
  }, [url]);

  return { data, status };
};

export default useBinanceSocket;
