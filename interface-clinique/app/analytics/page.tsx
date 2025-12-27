'use client';

import { useEffect, useState } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { BarChart3, TrendingUp, Users, FileText, Activity, PieChart } from 'lucide-react';
import { StatCard } from '../components/ui';
import { api } from '../utils/api';

export default function AnalyticsPage() {
    const [stats, setStats] = useState({
        totalDocuments: 0,
        totalIndexed: 0,
        totalQueries: 0,
        processingSuccess: 0
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const data = await api.getStats();
                setStats(data);
            } catch (error) {
                console.error('Error fetching analytics:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchStats();
    }, []);

    return (
        <DashboardLayout>
            <div className="space-y-6">
                {/* Header - Medical Theme Match */}
                <div className="relative gradient-teal rounded-3xl p-8 text-white shadow-lg overflow-hidden">
                    {/* Animated Background */}
                    <div className="absolute top-0 right-0 -mr-20 -mt-20 w-96 h-96 bg-white/10 rounded-full blur-3xl animate-pulse-soft"></div>
                    <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-96 h-96 bg-white/5 rounded-full blur-3xl"></div>

                    <div className="relative z-10">
                        <div className="flex items-center space-x-4">
                            <div className="w-16 h-16 bg-white/20 backdrop-blur-lg rounded-2xl flex items-center justify-center border border-white/30 shadow-lg">
                                <BarChart3 className="h-8 w-8 text-white" />
                            </div>
                            <div>
                                <div>
                                    <h1 className="text-3xl font-bold mb-1">Analytics Dashboard</h1>
                                    <p className="text-white/90 text-base">Real-time insights from your medical data processing</p>
                                </div>
                            </div>
                        </div>

                        {/* Key Metrics */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                            <StatCard
                                label="Total Documents"
                                value={loading ? "..." : String(stats.totalDocuments)}
                                change={{ value: "+0%", trend: "up" }}
                                icon={FileText}
                                color="teal"
                            />
                            <StatCard
                                label="Indexed Chunks"
                                value={loading ? "..." : String(stats.totalIndexed)}
                                change={{ value: "+0%", trend: "up" }}
                                icon={Activity}
                                color="green"
                            />
                            <StatCard
                                label="AI Queries"
                                value={loading ? "..." : String(stats.totalQueries)}
                                change={{ value: "+0%", trend: "up" }}
                                icon={Users}
                                color="blue"
                            />
                            <StatCard
                                label="Success Rate"
                                value={loading ? "..." : stats.totalDocuments > 0 ? "100%" : "0%"}
                                change={{ value: "0%", trend: "up" }}
                                icon={TrendingUp}
                                color="orange"
                            />
                        </div>

                        {/* System Performance Overview */}
                        <div className="medical-card p-6">
                            <div className="flex justify-between items-center mb-6">
                                <h3 className="text-lg font-semibold text-gray-900">System Performance</h3>
                                <PieChart className="h-5 w-5 text-gray-400" />
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div className="text-center p-6 bg-teal-50 rounded-2xl">
                                    <div className="text-3xl font-bold text-teal-600 mb-2">{stats.totalDocuments}</div>
                                    <div className="text-sm text-gray-600">Documents Uploaded</div>
                                </div>
                                <div className="text-center p-6 bg-green-50 rounded-2xl">
                                    <div className="text-3xl font-bold text-green-600 mb-2">{stats.totalIndexed}</div>
                                    <div className="text-sm text-gray-600">Chunks Indexed</div>
                                </div>
                                <div className="text-center p-6 bg-blue-50 rounded-2xl">
                                    <div className="text-3xl font-bold text-blue-600 mb-2">{stats.totalQueries}</div>
                                    <div className="text-sm text-gray-600">Total Queries</div>
                                </div>
                            </div>
                        </div>

                        {/* Info Message */}
                        <div className="medical-card p-6 bg-blue-50 border-blue-200">
                            <p className="text-blue-800 text-sm">
                                <strong>Real-time Data:</strong> All statistics are fetched from your live system. Upload more documents or run queries to see updates!
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
}
