import React, { useState } from 'react';
import { Github, Loader, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { processGitHubRepo } from '../api/client';

const GitHubUpload = ({ onUploadSuccess }) => {
  const [repoUrl, setRepoUrl] = useState('');
  const [processing, setProcessing] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!repoUrl.trim()) {
      setError('Please enter a GitHub repository URL');
      return;
    }

    // Basic validation
    if (!repoUrl.includes('github.com')) {
      setError('Please enter a valid GitHub repository URL');
      return;
    }

    setProcessing(true);
    setError(null);
    setUploadStatus(null);

    try {
      const result = await processGitHubRepo(repoUrl);
      setUploadStatus(result);
      setRepoUrl(''); // Clear input on success
      if (onUploadSuccess) {
        onUploadSuccess(result);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to process repository');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="w-full space-y-4">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
          <div className="flex flex-col items-center space-y-4">
            <Github className="w-12 h-12 text-gray-400" />
            <div>
              <p className="text-lg font-medium text-gray-700">
                Process GitHub Repository
              </p>
              <p className="text-sm text-gray-500 mt-1">
                Enter a GitHub repository URL to analyze the code
              </p>
            </div>
          </div>
        </div>

        <div className="flex space-x-3">
          <input
            type="text"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder="https://github.com/username/repository"
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            disabled={processing}
          />
          <button
            type="submit"
            disabled={processing || !repoUrl.trim()}
            className="px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
          >
            {processing ? (
              <>
                <Loader className="w-5 h-5 animate-spin" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <Github className="w-5 h-5" />
                <span>Process Repo</span>
              </>
            )}
          </button>
        </div>

        <div className="flex items-start space-x-2 text-sm text-gray-600 bg-blue-50 p-3 rounded-lg">
          <AlertCircle className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-blue-800">Supported repositories:</p>
            <ul className="list-disc list-inside mt-1 text-blue-700">
              <li>Public GitHub repositories</li>
              <li>Processes all code files (Python, JavaScript, Java, etc.)</li>
              <li>May take a few minutes for large repositories</li>
            </ul>
          </div>
        </div>
      </form>

      {uploadStatus && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg flex items-start space-x-3">
          <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="font-medium text-green-800">Repository processed successfully!</p>
            <p className="text-sm text-green-700 mt-1">
              {uploadStatus.repo_name || uploadStatus.filename}
            </p>
            <div className="text-xs text-green-600 mt-2 space-y-1">
              <p>• {uploadStatus.file_count} files processed</p>
              <p>• {uploadStatus.chunks_created} code chunks created</p>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-3">
          <XCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="font-medium text-red-800">Processing failed</p>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default GitHubUpload;
