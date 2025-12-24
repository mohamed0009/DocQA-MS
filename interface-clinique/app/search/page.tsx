'use client';

import { useState } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { Search as SearchIcon, Filter, FileText, ChevronRight, Calendar, Tag, RefreshCw } from 'lucide-react';
import { api } from '../utils/api';

interface SearchResult {
    document_id: string;
    filename: string;
    chunk_text: string;
    score: number;
    metadata: any;
}

export default function SearchPage() {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<SearchResult[]>([]);
    const [loading, setLoading] = useState(false);
    const [searched, setSearched] = useState(false);

    const handleSearch = async () => {
        if (!query.trim()) return;

        setLoading(true);
        setSearched(true);
        try {
            const data = await api.search(query);
            setResults(data.results || []);
        } catch (error) {
            console.error("Search failed", error);
            setResults([]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    };

    return (
        <DashboardLayout>
            <div className="space-y-6">
                {/* Header - UPGRADED */}
                <div className="relative bg-gradient-to-br from-teal-500 via-teal-600 to-teal-700 rounded-3xl p-8 text-white shadow-2xl overflow-hidden border border-teal-500/20">
                    {/* Animated Background */}
                    <div className="absolute top-0 right-0 -mr-16 -mt-16 w-80 h-80 bg-white/10 rounded-full blur-3xl animate-pulse"></div>
                    <div className="absolute bottom-0 left-0 -ml-16 -mb-16 w-80 h-80 bg-teal-400/20 rounded-full blur-3xl"></div>

                    <div className="relative z-10">
                        <div className="flex items-center space-x-4">
                            <div className="w-16 h-16 bg-white/20 backdrop-blur-lg rounded-2xl flex items-center justify-center border border-white/30">
                                <SearchIcon className="h-8 w-8 text-white" />
                            </div>
                            <div>
                                <h1 className="text-4xl font-bold mb-1">Semantic Search</h1>
                                <p className="text-teal-100 text-lg">Search through medical records using natural language</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Search Bar */}
                <div className="bg-white p-6 rounded-xl shadow-lg">
                    <div className="relative">
                        <SearchIcon className="absolute left-4 top-3.5 h-5 w-5 text-gray-400" />
                        <input
                            type="text"
                            placeholder="e.g., 'Patients with hypertension prescribed beta-blockers'"
                            className="w-full pl-12 pr-4 py-3 rounded-lg border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all outline-none text-gray-700"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            onKeyDown={handleKeyPress}
                        />
                        <button
                            onClick={handleSearch}
                            disabled={loading}
                            className="absolute right-2 top-2 bg-blue-600 text-white px-4 py-1.5 rounded-md hover:bg-blue-700 transition-colors font-medium text-sm disabled:bg-blue-400 flex items-center"
                        >
                            {loading ? <RefreshCw className="h-4 w-4 animate-spin mr-2" /> : null}
                            {loading ? 'Searching...' : 'Search'}
                        </button>
                    </div>

                    <div className="mt-4 flex items-center space-x-4 text-sm text-gray-600">
                        <div className="flex items-center space-x-2 cursor-pointer hover:text-blue-600">
                            <Filter className="h-4 w-4" />
                            <span>Filters</span>
                        </div>
                        <div className="flex space-x-2">
                            <span className="px-3 py-1 bg-gray-100 rounded-full text-xs font-medium hover:bg-gray-200 cursor-pointer">Last 30 days</span>
                            <span className="px-3 py-1 bg-gray-100 rounded-full text-xs font-medium hover:bg-gray-200 cursor-pointer">PDF only</span>
                            <span className="px-3 py-1 bg-gray-100 rounded-full text-xs font-medium hover:bg-gray-200 cursor-pointer">High confidence</span>
                        </div>
                    </div>
                </div>

                {/* Results */}
                <div className="space-y-4">
                    {searched && (
                        <h2 className="text-lg font-semibold text-gray-900">
                            {results.length > 0 ? `Found ${results.length} relevant results` : 'No results found'}
                        </h2>
                    )}

                    {results.map((result, index) => (
                        <div key={`${result.document_id}-${index}`} className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-all border border-gray-100 group cursor-pointer">
                            <div className="flex justify-between items-start">
                                <div className="flex items-start space-x-4">
                                    <div className="p-3 bg-blue-50 rounded-lg group-hover:bg-blue-100 transition-colors">
                                        <FileText className="h-6 w-6 text-blue-600" />
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                                            {result.filename || 'Unknown Document'}
                                        </h3>
                                        <p className="text-gray-600 mt-1 text-sm leading-relaxed line-clamp-3">
                                            {result.chunk_text}
                                        </p>
                                        <div className="mt-3 flex items-center space-x-4 text-xs text-gray-500">
                                            <div className="flex items-center space-x-1">
                                                <Tag className="h-3 w-3" />
                                                <span>Chunk {index + 1}</span>
                                            </div>
                                            {result.metadata && Object.keys(result.metadata).map(key => (
                                                <span key={key} className="px-2 py-0.5 bg-gray-100 rounded text-gray-600 truncate max-w-[150px]">
                                                    {key}: {String(result.metadata[key])}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                                <div className="flex flex-col items-end space-y-2">
                                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${result.score > 0.8 ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                                        }`}>
                                        {(result.score * 100).toFixed(0)}% Match
                                    </span>
                                    <ChevronRight className="h-5 w-5 text-gray-300 group-hover:text-gray-500" />
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </DashboardLayout>
    );
}
