'use client';

import { useState, useEffect } from 'react';
import { Save, Globe, AlertCircle, CheckCircle, Info, ExternalLink, Settings as SettingsIcon } from 'lucide-react';
import { Settings } from '@/types';

export default function SettingsPage() {
  const [settings, setSettings] = useState<Settings>({
    documentationUrl: '',
    isConfigured: false,
  });
  
  const [isValidUrl, setIsValidUrl] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle');

  // Load settings from localStorage on mount
  useEffect(() => {
    const savedSettings = localStorage.getItem('docubot-settings');
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings);
        setSettings(parsed);
      } catch (error) {
        console.error('Failed to parse saved settings:', error);
      }
    }
  }, []);

  const validateUrl = (url: string): boolean => {
    if (!url.trim()) return true; // Empty URL is valid (just not configured)
    
    try {
      const urlObj = new URL(url);
      return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
    } catch {
      return false;
    }
  };

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newUrl = e.target.value;
    setSettings(prev => ({ ...prev, documentationUrl: newUrl }));
    setIsValidUrl(validateUrl(newUrl));
    setSaveStatus('idle');
  };

  const handleSave = async () => {
    if (!isValidUrl || isSaving) return;
    
    setIsSaving(true);
    setSaveStatus('idle');

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const updatedSettings: Settings = {
        ...settings,
        isConfigured: settings.documentationUrl.trim() !== '',
        lastUpdated: new Date(),
      };

      // Save to localStorage
      localStorage.setItem('docubot-settings', JSON.stringify(updatedSettings));
      setSettings(updatedSettings);
      setSaveStatus('success');
    } catch (error) {
      console.error('Failed to save settings:', error);
      setSaveStatus('error');
    } finally {
      setIsSaving(false);
    }
  };

  const handleReset = () => {
    setSettings({
      documentationUrl: '',
      isConfigured: false,
    });
    localStorage.removeItem('docubot-settings');
    setSaveStatus('idle');
    setIsValidUrl(true);
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center">
            <SettingsIcon className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">
              Settings
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Configure your documentation source
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="space-y-8">
        {/* Documentation URL Section */}
        <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
          <div className="space-y-6">
            <div>
              <div className="flex items-center space-x-2 mb-3">
                <Globe className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                <h2 className="text-lg font-medium text-gray-900 dark:text-white">
                  Documentation Source
                </h2>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                Enter the URL of the documentation website you want DocuBot to learn from.
              </p>
            </div>

            {/* URL Input */}
            <div>
              <label htmlFor="documentation-url" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Documentation URL
              </label>
              <div className="relative">
                <input
                  id="documentation-url"
                  type="url"
                  value={settings.documentationUrl}
                  onChange={handleUrlChange}
                  placeholder="https://docs.example.com"
                  className={`w-full px-4 py-3 border rounded-xl bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200 ${
                    !isValidUrl 
                      ? 'border-red-300 dark:border-red-600 bg-red-50 dark:bg-red-900/10' 
                      : 'border-gray-300 dark:border-gray-600'
                  }`}
                />
                {!isValidUrl && (
                  <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                    <AlertCircle className="h-5 w-5 text-red-500" />
                  </div>
                )}
              </div>
              {!isValidUrl && (
                <p className="mt-2 text-sm text-red-600 dark:text-red-400 flex items-center">
                  <AlertCircle className="w-4 h-4 mr-1" />
                  Please enter a valid URL starting with http:// or https://
                </p>
              )}
            </div>

            {/* Status Indicator */}
            <div className={`p-4 rounded-xl border ${
              settings.isConfigured 
                ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800' 
                : 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800'
            }`}>
              <div className="flex items-center">
                {settings.isConfigured ? (
                  <>
                    <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 mr-3" />
                    <div>
                      <span className="text-sm font-medium text-green-800 dark:text-green-300">
                        Documentation configured
                      </span>
                      {settings.lastUpdated && (
                        <p className="text-xs text-green-600 dark:text-green-400 mt-1">
                          Last updated: {settings.lastUpdated.toLocaleString()}
                        </p>
                      )}
                    </div>
                  </>
                ) : (
                  <>
                    <AlertCircle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 mr-3" />
                    <span className="text-sm font-medium text-yellow-800 dark:text-yellow-300">
                      No documentation source configured
                    </span>
                  </>
                )}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-3">
              <button
                onClick={handleSave}
                disabled={!isValidUrl || isSaving || !settings.documentationUrl.trim()}
                className="flex-1 flex items-center justify-center px-4 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-medium"
              >
                <Save className="w-4 h-4 mr-2" />
                {isSaving ? 'Saving...' : 'Save Configuration'}
              </button>
              
              <button
                onClick={handleReset}
                className="px-4 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-all duration-200 font-medium"
              >
                Reset
              </button>
            </div>
          </div>
        </div>

        {/* Save Status */}
        {saveStatus === 'success' && (
          <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl p-4">
            <div className="flex items-center">
              <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 mr-3" />
              <span className="text-sm font-medium text-green-800 dark:text-green-300">
                Configuration saved successfully!
              </span>
            </div>
          </div>
        )}

        {saveStatus === 'error' && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4">
            <div className="flex items-center">
              <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 mr-3" />
              <span className="text-sm font-medium text-red-800 dark:text-red-300">
                Failed to save configuration. Please try again.
              </span>
            </div>
          </div>
        )}

        {/* How it Works Section */}
        <div className="bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-800 rounded-xl p-6">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <Info className="w-5 h-5 text-indigo-600 dark:text-indigo-400 mt-0.5" />
            </div>
            <div>
              <h3 className="text-sm font-medium text-indigo-900 dark:text-indigo-300 mb-3">
                How DocuBot Works
              </h3>
              <div className="space-y-2 text-sm text-indigo-800 dark:text-indigo-200">
                <div className="flex items-start space-x-2">
                  <span className="text-indigo-600 dark:text-indigo-400 font-medium">1.</span>
                  <span>Enter your documentation website URL above</span>
                </div>
                <div className="flex items-start space-x-2">
                  <span className="text-indigo-600 dark:text-indigo-400 font-medium">2.</span>
                  <span>DocuBot crawls and indexes the content using advanced AI</span>
                </div>
                <div className="flex items-start space-x-2">
                  <span className="text-indigo-600 dark:text-indigo-400 font-medium">3.</span>
                  <span>Ask questions in natural language and get instant, accurate answers</span>
                </div>
                <div className="flex items-start space-x-2">
                  <span className="text-indigo-600 dark:text-indigo-400 font-medium">4.</span>
                  <span>Powered by RAG (Retrieval-Augmented Generation) for context-aware responses</span>
                </div>
              </div>
              
              <div className="mt-4 pt-4 border-t border-indigo-200 dark:border-indigo-800">
                <p className="text-xs text-indigo-700 dark:text-indigo-300 flex items-center">
                  <ExternalLink className="w-3 h-3 mr-1" />
                  Supported formats: HTML documentation, API docs, guides, and tutorials
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}