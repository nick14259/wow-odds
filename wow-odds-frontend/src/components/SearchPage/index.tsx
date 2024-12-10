// src/components/SearchPage/index.tsx
'use client';

import React from 'react';
import { Search, Loader2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface SearchPageProps {
 onSearchComplete: (data: any) => void;
 setLoading: (loading: boolean) => void;
 setError: (error: string) => void;
}

const SearchPage: React.FC<SearchPageProps> = ({
 onSearchComplete,
 setLoading,
 setError
}) => {
 const [searchType, setSearchType] = React.useState<'player' | 'guild'>('player');
 const [characterName, setCharacterName] = React.useState('');
 const [serverName, setServerName] = React.useState('');
 const [region, setRegion] = React.useState('us');
 const [version, setVersion] = React.useState('SoD');
 const [localLoading, setLocalLoading] = React.useState(false);
 const [localError, setLocalError] = React.useState('');

 const handleSearch = async (e: React.FormEvent) => {
   e.preventDefault();
   
   if (!characterName || !serverName) {
     setLocalError('Please fill in all required fields');
     return;
   }

   setLocalError('');
   setError('');
   setLoading(true);
   setLocalLoading(true);

   try {
     const url = searchType === 'player'
       ? `/api/v1/player/${region}/${encodeURIComponent(serverName.toLowerCase())}/${encodeURIComponent(characterName.toLowerCase())}?version=${version}`
       : `/api/v1/guild/${region}/${encodeURIComponent(serverName.toLowerCase())}/${encodeURIComponent(characterName.toLowerCase())}`;

     console.log('Fetching:', url);

     const response = await fetch(url);
     console.log('Response received:', response.status);
     const data = await response.json();
     console.log('Data parsed:', data);

     if (!response.ok) {
       throw new Error(data.detail || 'Failed to fetch data');
     }

     console.log('Calling onSearchComplete with:', data);
     onSearchComplete(data);

   } catch (err) {
     console.error('Search error:', err);
     setError(err instanceof Error ? err.message : 'Unknown error occurred');
     onSearchComplete(null);
   } finally {
     setLoading(false);
     setLocalLoading(false);
   }
 };

 return (
   <Card className="bg-gray-800 border-gray-700">
     <CardHeader>
       <CardTitle className="text-2xl font-bold text-white">
         WoW Performance Odds Calculator
       </CardTitle>
     </CardHeader>
     <CardContent>
       {localError && (
         <Alert className="mb-4 bg-red-900/50 border-red-900 text-red-300">
           <AlertDescription>{localError}</AlertDescription>
         </Alert>
       )}

       <div className="flex gap-4 mb-6">
         <button
           type="button"
           onClick={() => setSearchType('player')}
           className={`px-4 py-2 rounded transition-colors ${
             searchType === 'player'
               ? 'bg-blue-600 text-white'
               : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
           }`}
         >
           Player Search
         </button>
         <button
           type="button"
           onClick={() => setSearchType('guild')}
           className={`px-4 py-2 rounded transition-colors ${
             searchType === 'guild'
               ? 'bg-blue-600 text-white'
               : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
           }`}
         >
           Guild Search
         </button>
       </div>

       <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-4">
         <input
           type="text"
           placeholder={searchType === 'player' ? "Character Name" : "Guild Name"}
           value={characterName}
           onChange={(e) => setCharacterName(e.target.value)}
           className="flex-1 p-2 rounded bg-gray-700 border border-gray-600 text-white placeholder-gray-400 focus:border-blue-500 focus:outline-none"
           required
         />
         <input
           type="text"
           placeholder="Server"
           value={serverName}
           onChange={(e) => setServerName(e.target.value)}
           className="flex-1 p-2 rounded bg-gray-700 border border-gray-600 text-white placeholder-gray-400 focus:border-blue-500 focus:outline-none"
           required
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
           disabled={localLoading}
           className="bg-blue-600 text-white px-6 py-2 rounded flex items-center justify-center gap-2 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed transition-colors"
         >
           {localLoading ? (
             <>
               <Loader2 className="animate-spin" size={20} />
               <span>Searching...</span>
             </>
           ) : (
             <>
               <Search size={20} />
               <span>Search</span>
             </>
           )}
         </button>
       </form>
     </CardContent>
   </Card>
 );
};

export default SearchPage;
