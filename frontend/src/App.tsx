import React, { useState } from 'react';
import SessionSidebar from '@/components/SessionSidebar';
import DocumentUploader from '@/components/DocumentUploader';
import ChatWindow from '@/components/ChatWindow';

const App: React.FC = () => {
  const [activeSessionId, setActiveSessionId] = useState<string | undefined>(undefined);

  const handleSelectSession = (id: string) => {
    setActiveSessionId(id);
  };

  return (
    <div className="flex flex-col h-screen">
      <header className="flex items-center justify-between px-4 py-2 bg-gray-800 text-white">
        <h1 className="text-lg font-bold">Aakaar AI Chat</h1>
        <button
          onClick={() => setActiveSessionId(undefined)}
          className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded"
        >
          New Chat
        </button>
      </header>
      <div className="flex flex-1">
        <aside className="w-64 bg-gray-100 border-r border-gray-300">
          <SessionSidebar
            onSelectSession={handleSelectSession}
            activeSessionId={activeSessionId}
          />
          <div className="mt-4">
            <DocumentUploader sessionId={activeSessionId} />
          </div>
        </aside>
        <main className="flex-1 bg-white">
          <ChatWindow activeSessionId={activeSessionId} />
        </main>
      </div>
    </div>
  );
};

export default App;