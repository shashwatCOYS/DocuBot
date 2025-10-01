'use client';

import { useState } from 'react';
import Link from 'next/link';
import ThemeToggle from '../components/ThemeToggle';

export default function Settings() {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    setIsLoading(true);
    setMessage(null);

    try {
      // Simulate API call to process URL
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setMessage({
        type: 'success',
        text: `Successfully added "${url}" to the knowledge base. The documentation is being indexed and will be available for chat shortly.`
      });
      setUrl('');
    } catch (error) {
      setMessage({
        type: 'error',
        text: 'Failed to process the URL. Please check if the URL is accessible and try again.'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const isValidUrl = (string: string) => {
    try {
      new URL(string);
      return true;
    } catch (_) {
      return false;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-900">
      {/* Header */}
      <header className="bg-white dark:bg-slate-800 border-b border-gray-200 dark:border-slate-700">
        <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Settings</h1>
          <div className="flex items-center space-x-4">
            <Link 
              href="/"
              className="text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100 transition-colors"
            >
              Back to Chat
            </Link>
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-2xl mx-auto py-8 px-4">
        <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-gray-200 dark:border-slate-700 p-6">
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
              Add Documentation Source
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Enter a URL to crawl and index documentation. This will be used as context for the chatbot.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="url" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Documentation URL
              </label>
              <input
                type="url"
                id="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://docs.example.com"
                className="w-full border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-gray-100 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
              {url && !isValidUrl(url) && (
                <p className="text-sm text-red-600 dark:text-red-400 mt-1">Please enter a valid URL</p>
              )}
            </div>

            <div className="flex space-x-3">
              <button
                type="submit"
                disabled={!url.trim() || !isValidUrl(url) || isLoading}
                className="bg-blue-500 dark:bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-600 dark:hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? 'Processing...' : 'Add Documentation'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setUrl('');
                  setMessage(null);
                }}
                className="bg-gray-200 dark:bg-slate-700 dark:text-gray-300 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-300 dark:hover:bg-slate-600 transition-colors"
              >
                Clear
              </button>
            </div>
          </form>

          {/* Status Message */}
          {message && (
            <div className={`mt-4 p-4 rounded-lg ${
              message.type === 'success' 
                ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-800 dark:text-green-300' 
                : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-300'
            }`}>
              <p className="text-sm">{message.text}</p>
            </div>
          )}

          {/* Loading State */}
          {isLoading && (
            <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                <p className="text-sm text-blue-800 dark:text-blue-300">
                  Crawling and indexing documentation... This may take a few minutes.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Additional Information */}
        <div className="mt-8 bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-gray-200 dark:border-slate-700 p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            How it works
          </h3>
          <div className="space-y-3 text-sm text-gray-600 dark:text-gray-400">
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-300 rounded-full flex items-center justify-center text-xs font-semibold">1</div>
              <p>Enter a URL pointing to technical documentation, API docs, or code repositories</p>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-300 rounded-full flex items-center justify-center text-xs font-semibold">2</div>
              <p>Our system crawls and extracts content from the documentation</p>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-300 rounded-full flex items-center justify-center text-xs font-semibold">3</div>
              <p>The content is processed and stored in a vector database for semantic search</p>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-300 rounded-full flex items-center justify-center text-xs font-semibold">4</div>
              <p>You can now chat with the documentation using natural language queries</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
