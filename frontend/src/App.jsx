import React, { useState, useEffect, useRef } from 'react';
import PDFViewer from './components/PDFViewer';
import ChatInterface from './components/ChatInterface';

function App() {
  const [pdfUrl, setPdfUrl] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [highlightBbox, setHighlightBbox] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  
  const wsRef = useRef(null);

  useEffect(() => {
    // Initialize WebSocket connection
    wsRef.current = new WebSocket('ws://localhost:8000/api/ws/chat');
    
    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages(prev => [...prev, {
        role: 'sensei',
        content: data.answer,
        sources: data.sources
      }]);
      setIsLoading(false);
    };

    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  const handleUpload = async (file) => {
    // Create local object URL for immediate display
    const objectUrl = URL.createObjectURL(file);
    setPdfUrl(objectUrl);
    setHighlightBbox(null);
    setCurrentPage(1);

    // Send to backend
    const formData = new FormData();
    formData.append('file', file);

    try {
      setMessages(prev => [...prev, { role: 'sensei', content: `Uploading and analyzing ${file.name}... Please wait.` }]);
      const res = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'sensei', content: `Analysis complete: ${data.message}` }]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { role: 'sensei', content: 'Upload failed. Please try again.' }]);
    }
  };

  const handleQuery = (queryText) => {
    setMessages(prev => [...prev, { role: 'user', content: queryText }]);
    setIsLoading(true);
    
    // Send over WebSocket or fallback to HTTP
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(queryText);
    } else {
      // Fallback HTTP request
      fetch('http://localhost:8000/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: queryText })
      })
      .then(res => res.json())
      .then(data => {
        setMessages(prev => [...prev, { role: 'sensei', content: data.answer, sources: data.sources }]);
      })
      .finally(() => setIsLoading(false));
    }
  };

  const handleSourceClick = (source) => {
    if (source.page_number) {
      setCurrentPage(source.page_number);
    }
    if (source.bbox) {
      setHighlightBbox(source.bbox);
    } else {
      setHighlightBbox(null);
    }
  };

  return (
    <div className="h-screen w-full flex flex-col font-sans">
      <header className="bg-white border-b px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-2xl">⛩️</span>
          <h1 className="text-xl font-bold text-sensei-900 tracking-tight">Bilingual Technical Sensei</h1>
        </div>
        <div className="text-sm text-gray-500 flex items-center gap-4">
          <span className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-green-500"></div> Connected
          </span>
        </div>
      </header>
      
      <main className="flex-1 flex overflow-hidden">
        {/* Left Pane: PDF Viewer */}
        <div className="w-1/2 h-full relative">
          <PDFViewer 
            pdfUrl={pdfUrl} 
            currentPage={currentPage} 
            highlightBbox={highlightBbox} 
          />
          {pdfUrl && (
            <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-white px-4 py-2 rounded-full shadow-md flex items-center gap-4 text-sm font-medium">
              <button 
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                className="hover:text-sensei-500 disabled:opacity-50"
                disabled={currentPage <= 1}
              >
                Previous
              </button>
              <span>Page {currentPage}</span>
              <button 
                onClick={() => setCurrentPage(p => p + 1)}
                className="hover:text-sensei-500"
              >
                Next
              </button>
            </div>
          )}
        </div>

        {/* Right Pane: Chat Interface */}
        <div className="w-1/2 h-full">
          <ChatInterface 
            onQuery={handleQuery}
            onUpload={handleUpload}
            onSourceClick={handleSourceClick}
            messages={messages}
            isLoading={isLoading}
          />
        </div>
      </main>
    </div>
  );
}

export default App;
