// src/app/page.tsx
'use client';

import { useState, useEffect } from 'react';
import SearchPage from '@/components/SearchPage';
import { MetricsLayout } from '@/components/layout';

export default function Home() {
  const [searchResults, setSearchResults] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Add effect to monitor state changes
  useEffect(() => {
    console.log('State changed:', { searchResults, isLoading, error });
  }, [searchResults, isLoading, error]);

  const handleSearchComplete = (data: any) => {
    console.log('handleSearchComplete called with:', data);
    setSearchResults(data);
  };

  return (
    <main className="min-h-screen bg-gray-900 p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        <SearchPage 
          onSearchComplete={handleSearchComplete}
          setLoading={setIsLoading}
          setError={setError}
        />
        
        <div className="text-white">
          {isLoading && <p>Loading...</p>}
          {error && <p>Error: {error}</p>}
          {searchResults && <p>Results found for: {searchResults.character?.name}</p>}
        </div>

        {searchResults && (
          <MetricsLayout
            data={searchResults}
            isLoading={isLoading}
            error={error}
          />
        )}
      </div>
    </main>
  );
}
