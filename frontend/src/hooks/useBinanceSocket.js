import { useState, useEffect, useRef } from 'react';

const useBinanceSocket = (url) => {
  const [data, setData] = useState({});
  const [status, setStatus] = useState('disconnected');
  const ws = useRef(null);
  const reconnectTimeout = useRef(null);

  const connect = () => {
    
    setStatus('connecting');
    const socket = new WebSocket(url);
    ws.current = socket;

    socket.onopen = () => {
      
      setStatus('connected');
    };

    socket.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        setData(msg);
      } catch (e) {
        console.error('WebSocket parse error:', e);
      }
    };

    socket.onclose = (e) => {
      
      setStatus('reconnecting');
      reconnectTimeout.current = setTimeout(connect, 5000);
    };

    socket.onerror = (error) => {
      console.error('WebSocket Error:', error);
      socket.close();
    };
  };

  useEffect(() => {
    connect();
    return () => {
      if (ws.current) ws.current.close();
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
    };
  }, [url]);

  return { data, status };
};

export default useBinanceSocket;
