// src/components/SearchPage.tsx
'use client';

import React, { useState } from 'react';
import { Search, Loader2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';

type SearchType = 'player' | 'guild';

const SearchPage = () => {
  const [searchType, setSearchType] = useState<SearchType>('player');
  const [characterName, setCharacterName] = useState('');
  const [serverName, setServerName] = useState('');
  const [region, setRegion] = useState('us');
  const [version, setVersion] = useState('SoD');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchResults, setSearchResults] = useState<any>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSearchResults(null);

    if (!characterName || !serverName) {
      setError('Please enter both name and server');
      return;
    }

    setLoading(true);
    try {
      const url = searchType === 'player' 
        ? `/api/v1/player/${region}/${serverName.toLowerCase()}/${characterName.toLowerCase()}?version=${version}`
        : `/api/v1/guild/${region}/${serverName.toLowerCase()}/${characterName.toLowerCase()}`;

      console.log('Fetching:', url);
      
      const response = await fetch(url);
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch data');
      }

      const data = await response.json();
      setSearchResults(data);
    } catch (err) {
      console.error('Search error:', err);
      setError(err instanceof Error ? err.message : 'Error fetching data');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 p-4">
      <div className="max-w-4xl mx-auto">
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader>
            <CardTitle className="text-2xl font-bold text-white">
              WoW Performance Odds Calculator
            </CardTitle>
          </CardHeader>
          <CardContent>
            {/* Search Type Toggle */}
            <div className="flex gap-4 mb-6">
              <button
                onClick={() => setSearchType('player')}
                className={`px-4 py-2 rounded ${
                  searchType === 'player'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300'
                }`}
              >
                Player Search
              </button>
              <button
                onClick={() => setSearchType('guild')}
                className={`px-4 py-2 rounded ${
                  searchType === 'guild'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300'
                }`}
              >
                Guild Search
              </button>
            </div>

            {/* Search Form */}
            <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-4 mb-6">
              <input
                type="text"
                placeholder={searchType === 'player' ? "Character Name" : "Guild Name"}
                value={characterName}
                onChange={(e) => setCharacterName(e.target.value)}
                className="flex-1 p-2 rounded bg-gray-700 border border-gray-600 text-white placeholder-gray-400 focus:border-blue-500 focus:outline-none"
              />
              <input
                type="text"
                placeholder="Server"
                value={serverName}
                onChange={(e) => setServerName(e.target.value)}
                className="flex-1 p-2 rounded bg-gray-700 border border-gray-600 text-white placeholder-gray-400 focus:border-blue-500 focus:outline-none"
              />
              <select
                value={region}
                onChange={(e) => setRegion(e.target.value)}
                className="p-2 rounded bg-gray-700 border border-gray-600 text-white focus:border-blue-500 focus:outline-none"
              >
                <option value="us">US</option>
                <option value="eu">EU</option>
                <option value="kr">KR</option>
                <option value="tw">TW</option>
              </select>
              {searchType === 'player' && (
                <select
                  value={version}
                  onChange={(e) => setVersion(e.target.value)}
                  className="p-2 rounded bg-gray-700 border border-gray-600 text-white focus:border-blue-500 focus:outline-none"
                >
                  <option value="Retail">The War Within (Retail)</option>
                  <option value="Cata">Cataclysm</option>
                  <option value="ClassicFresh">Classic Fresh</option>
                  <option value="SoD">Season of Discovery</option>
                  <option value="Classic">Vanilla</option>
                </select>
              )}
              <button
                type="submit"
                disabled={loading}
                className="bg-blue-600 text-white px-6 py-2 rounded flex items-center justify-center gap-2 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? (
                  <>
                    <Loader2 size={20} className="animate-spin" />
                    Loading...
                  </>
                ) : (
                  <>
                    <Search size={20} />
                    Search
                  </>
                )}
              </button>
            </form>

            {/* Error Display */}
            {error && (
              <Alert variant="destructive" className="mb-6 bg-red-900 border-red-800">
                <AlertDescription className="text-red-200">{error}</AlertDescription>
              </Alert>
            )}

            {/* Results Display */}
            {searchResults && (
              <div className="text-white">
                {/* We'll add the results components here */}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default SearchPage;
