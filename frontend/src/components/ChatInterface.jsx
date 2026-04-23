import React, { useState } from 'react';
import { Send, Upload } from 'lucide-react';

const ChatInterface = ({ onQuery, onUpload, onSourceClick, messages, isLoading }) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onQuery(input);
    setInput('');
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      onUpload(e.target.files[0]);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white border-l">
      {/* Header */}
      <div className="p-4 border-b flex justify-between items-center bg-sensei-50">
        <h2 className="text-lg font-semibold text-sensei-900">Sensei Chat</h2>
        <div>
          <label className="cursor-pointer bg-sensei-500 hover:bg-sensei-600 text-white px-3 py-1.5 rounded-md text-sm flex items-center transition-colors">
            <Upload className="w-4 h-4 mr-2" /> Upload PDF
            <input type="file" className="hidden" accept=".pdf" onChange={handleFileChange} />
          </label>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-400 mt-10">
            Ask me anything about the uploaded Japanese document!
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
              <div className={`max-w-[85%] rounded-lg p-3 ${msg.role === 'user' ? 'bg-sensei-500 text-white' : 'bg-gray-100 text-gray-800'}`}>
                <div className="whitespace-pre-wrap">{msg.content}</div>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {msg.sources.map((src, sIdx) => (
                      <button
                        key={sIdx}
                        onClick={() => onSourceClick(src)}
                        className="text-xs bg-white text-sensei-600 border border-sensei-200 px-2 py-1 rounded hover:bg-sensei-50 transition-colors"
                      >
                        {src.type === 'image' ? '🖼️ Diagram' : '📄 Text'} (Pg {src.page_number})
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="flex items-start">
            <div className="bg-gray-100 rounded-lg p-3 text-gray-500 animate-pulse">
              Sensei is thinking...
            </div>
          </div>
        )}
      </div>

      {/* Input Form */}
      <div className="p-4 border-t bg-gray-50">
        <form onSubmit={handleSubmit} className="flex relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your question..."
            className="flex-1 border rounded-full px-4 py-2 pr-12 focus:outline-none focus:border-sensei-500 focus:ring-1 focus:ring-sensei-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="absolute right-1 top-1 bottom-1 bg-sensei-500 text-white p-2 rounded-full hover:bg-sensei-600 disabled:opacity-50 transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;
