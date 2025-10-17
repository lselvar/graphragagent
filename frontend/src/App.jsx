import React, { useState } from 'react';
import { MessageSquare, Upload as UploadIcon, Database, Github } from 'lucide-react';
import DocumentUpload from './components/DocumentUpload';
import GitHubUpload from './components/GitHubUpload';
import ChatInterface from './components/ChatInterface';
import DocumentList from './components/DocumentList';

function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [uploadRefresh, setUploadRefresh] = useState(0);

  const handleUploadSuccess = () => {
    setUploadRefresh((prev) => prev + 1);
  };

  const tabs = [
    { id: 'chat', label: 'Chat', icon: MessageSquare },
    { id: 'upload', label: 'Upload', icon: UploadIcon },
    { id: 'github', label: 'GitHub', icon: Github },
    { id: 'documents', label: 'Documents', icon: Database },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
                <Database className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">GraphRAG Agent</h1>
                <p className="text-sm text-gray-500">Powered by Gemini LLM</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          {/* Tabs */}
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`
                      flex items-center space-x-2 px-6 py-4 border-b-2 font-medium text-sm
                      transition-colors duration-200
                      ${
                        activeTab === tab.id
                          ? 'border-primary-500 text-primary-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }
                    `}
                  >
                    <Icon className="w-5 h-5" />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'chat' && (
              <div className="h-[600px]">
                <ChatInterface />
              </div>
            )}

            {activeTab === 'upload' && (
              <div className="max-w-2xl mx-auto">
                <div className="mb-6">
                  <h2 className="text-xl font-semibold text-gray-800 mb-2">
                    Upload Documents
                  </h2>
                  <p className="text-gray-600">
                    Upload documents to create embeddings and store them in the GraphRAG database.
                    Supported formats: PDF, DOCX, TXT.
                  </p>
                </div>
                <DocumentUpload onUploadSuccess={handleUploadSuccess} />
              </div>
            )}

            {activeTab === 'github' && (
              <div className="max-w-2xl mx-auto">
                <div className="mb-6">
                  <h2 className="text-xl font-semibold text-gray-800 mb-2">
                    Process GitHub Repository
                  </h2>
                  <p className="text-gray-600">
                    Analyze code from any public GitHub repository. The system will clone the repo,
                    extract all code files, and create embeddings for intelligent code querying.
                  </p>
                </div>
                <GitHubUpload onUploadSuccess={handleUploadSuccess} />
              </div>
            )}

            {activeTab === 'documents' && (
              <div className="max-w-4xl mx-auto">
                <DocumentList refreshTrigger={uploadRefresh} />
              </div>
            )}
          </div>
        </div>

        {/* Footer Info */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>
            GraphRAG combines knowledge graphs with retrieval-augmented generation
            for enhanced document understanding and question answering.
          </p>
        </div>
      </main>
    </div>
  );
}

export default App;
