import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, Apple, FileText, Settings, Upload, RefreshCw } from 'lucide-react';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [query, setQuery] = useState('');
  const [searchMode, setSearchMode] = useState('single');
  const [selectedYear, setSelectedYear] = useState(null);
  const [availableYears, setAvailableYears] = useState([]);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  const [exampleQueries, setExampleQueries] = useState([]);
  const [showUpload, setShowUpload] = useState(false);

  // Fetch initial data
  useEffect(() => {
    fetchInitialData();
  }, []);

  // Clear error when search mode changes
  useEffect(() => {
    setError(null);
  }, [searchMode]);

  const fetchInitialData = async () => {
    try {
      const [yearsRes, statsRes, examplesRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/years`),
        axios.get(`${API_BASE_URL}/api/stats`),
        axios.get(`${API_BASE_URL}/api/example-queries`)
      ]);

      setAvailableYears(yearsRes.data.years);
      setStats(statsRes.data);
      setExampleQueries(examplesRes.data.examples);
      
      if (yearsRes.data.years.length > 0) {
        setSelectedYear(yearsRes.data.years[yearsRes.data.years.length - 1]);
      }
    } catch (err) {
      console.error('Error fetching initial data:', err);
      setError('Failed to load system data');
    }
  };

  const handleQuery = async () => {
    if (!query.trim()) return;

    // Validate year selection for single year mode
    if (searchMode === 'single' && !selectedYear) {
      setError('Please select a year when searching in single year mode');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const requestData = {
        query: query.trim(),
        search_all_years: searchMode === 'all'
      };

      if (searchMode === 'single') {
        requestData.year = selectedYear;
      }

      const response = await axios.post(`${API_BASE_URL}/api/query`, requestData);
      
      if (response.data.success) {
        setResults(response.data.data);
      } else {
        setError(response.data.error || 'Query failed');
      }
    } catch (err) {
      console.error('Query error:', err);
      setError(err.response?.data?.detail || 'Failed to process query');
    } finally {
      setLoading(false);
    }
  };

  const handleExampleQuery = (exampleQuery) => {
    setQuery(exampleQuery);
  };

  const handleInitializeData = async () => {
    try {
      setLoading(true);
      await axios.post(`${API_BASE_URL}/api/init-data`);
      await fetchInitialData();
      alert('Data initialization complete!');
    } catch (err) {
      console.error('Data initialization error:', err);
      alert('Failed to initialize data');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.pdf')) {
      alert('Please upload a PDF file');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      setLoading(true);
      await axios.post(`${API_BASE_URL}/api/upload-pdf`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      await fetchInitialData();
      alert('File uploaded successfully!');
      setShowUpload(false);
    } catch (err) {
      console.error('Upload error:', err);
      alert('Failed to upload file');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Apple className="h-8 w-8 text-apple-blue mr-3" />
              <h1 className="text-2xl font-bold text-gray-900">
                Apple Annual Reports QA System
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowUpload(!showUpload)}
                className="flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                <Upload className="h-4 w-4 mr-2" />
                Upload PDF
              </button>
              <button
                onClick={handleInitializeData}
                disabled={loading}
                className="flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-apple-blue hover:bg-blue-700 disabled:opacity-50"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Initialize Data
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* File Upload Modal */}
      {showUpload && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3 text-center">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Upload PDF File</h3>
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileUpload}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-apple-blue file:text-white hover:file:bg-blue-700"
              />
              <button
                onClick={() => setShowUpload(false)}
                className="mt-4 px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Settings className="h-5 w-5 mr-2" />
                Settings
              </h2>

              {/* Search Mode */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Search Mode
                </label>
                <div className="space-y-2">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="single"
                      checked={searchMode === 'single'}
                      onChange={(e) => setSearchMode(e.target.value)}
                      className="mr-2"
                    />
                    Single Year
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="all"
                      checked={searchMode === 'all'}
                      onChange={(e) => setSearchMode(e.target.value)}
                      className="mr-2"
                    />
                    All Years
                  </label>
                </div>
              </div>

              {/* Year Selection */}
              {searchMode === 'single' && (
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Year <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={selectedYear || ''}
                    onChange={(e) => setSelectedYear(parseInt(e.target.value))}
                    className={`w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-apple-blue ${
                      searchMode === 'single' && !selectedYear 
                        ? 'border-red-300 focus:ring-red-500' 
                        : 'border-gray-300 focus:ring-apple-blue'
                    }`}
                  >
                    <option value="">Select a year</option>
                    {availableYears.map(year => (
                      <option key={year} value={year}>{year}</option>
                    ))}
                  </select>
                  {searchMode === 'single' && !selectedYear && (
                    <p className="mt-1 text-sm text-red-600">Please select a year to continue</p>
                  )}
                </div>
              )}

              {/* System Stats */}
              {stats && (
                <div className="border-t pt-4">
                  <h3 className="text-sm font-medium text-gray-700 mb-2">System Information</h3>
                  <div className="text-sm text-gray-600 space-y-1">
                    <p>Available Years: {stats.total_years}</p>
                    <p>Processed Years: {stats.processed_years.length}</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {/* Query Input */}
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Ask a Question</h2>
              
              <div className="flex space-x-4">
                <div className="flex-1">
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="e.g., What was Apple's total revenue in 2023?"
                    className="w-full border border-gray-300 rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-apple-blue"
                    onKeyPress={(e) => e.key === 'Enter' && handleQuery()}
                  />
                </div>
                <button
                  onClick={handleQuery}
                  disabled={loading || !query.trim() || (searchMode === 'single' && !selectedYear)}
                  className="px-6 py-2 bg-apple-blue text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center"
                >
                  <Search className="h-4 w-4 mr-2" />
                  Search
                </button>
              </div>

              {/* Example Queries */}
              <div className="mt-4">
                <h3 className="text-sm font-medium text-gray-700 mb-2">Example Questions:</h3>
                <div className="flex flex-wrap gap-2">
                  {exampleQueries.slice(0, 5).map((example, index) => (
                    <button
                      key={index}
                      onClick={() => handleExampleQuery(example)}
                      className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200"
                    >
                      {example}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Loading State */}
            {loading && (
              <div className="bg-white rounded-lg shadow p-6 text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-apple-blue mx-auto"></div>
                <p className="mt-4 text-gray-600">Processing your query...</p>
              </div>
            )}

            {/* Error State */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                <p className="text-red-800">{error}</p>
              </div>
            )}

            {/* Results */}
            {results && (
              <div className="space-y-6">
                {results.search_mode === 'single_year' ? (
                  <SingleYearResult result={results.result} />
                ) : (
                  <AllYearsResult results={results.results} />
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// Single Year Result Component
function SingleYearResult({ result }) {
  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.7) return 'bg-green-100 text-green-800';
    if (confidence >= 0.4) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Results for {result.year}
        </h3>

        {/* Answer */}
        <div className="bg-apple-gray rounded-lg p-4 mb-4 border-l-4 border-apple-blue">
          <h4 className="font-medium text-gray-900 mb-2">Answer</h4>
          <p className="text-gray-700 mb-3">{result.answer}</p>
          <span className={`inline-block px-2 py-1 text-xs font-medium rounded-full ${getConfidenceColor(result.confidence)}`}>
            Confidence: {(result.confidence * 100).toFixed(0)}%
          </span>
        </div>

                {/* Citations */}
        {result.citations && result.citations.length > 0 && (
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Citations</h4>
            <div className="space-y-2">
              {result.citations.map((citation, index) => (
                <div key={index} className="bg-apple-yellow rounded-lg p-3 border-l-4 border-yellow-400">
                  <p className="text-sm text-gray-700">
                    <strong>Citation {index + 1}:</strong> {citation.text}
                  </p>
                  {citation.source && (
                    <p className="text-xs text-gray-500 mt-1">
                      Source: {citation.source}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// All Years Result Component
function AllYearsResult({ results }) {
  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.7) return 'bg-green-100 text-green-800';
    if (confidence >= 0.4) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">Results Across All Years</h3>
      {Object.entries(results).map(([year, result]) => (
        <div key={year} className="bg-white rounded-lg shadow">
          <div className="p-6">
            <h4 className="text-md font-semibold text-gray-900 mb-3 flex items-center">
              <FileText className="h-4 w-4 mr-2" />
              {year} Results
            </h4>

            <div className="bg-apple-gray rounded-lg p-4 mb-3 border-l-4 border-apple-blue">
              <p className="text-gray-700 mb-2">{result.answer}</p>
              <span className={`inline-block px-2 py-1 text-xs font-medium rounded-full ${getConfidenceColor(result.confidence)}`}>
                Confidence: {(result.confidence * 100).toFixed(0)}%
              </span>
            </div>

            {result.citations && result.citations.length > 0 && (
              <div className="space-y-2">
                {result.citations.slice(0, 2).map((citation, index) => (
                  <div key={index} className="bg-apple-yellow rounded-lg p-2 border-l-4 border-yellow-400">
                    <p className="text-xs text-gray-700">
                      <strong>Citation {index + 1}:</strong> {citation.text}
                    </p>
                    {citation.source && (
                      <p className="text-xs text-gray-500 mt-1">
                        Source: {citation.source}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

export default App;
