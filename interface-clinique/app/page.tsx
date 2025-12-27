'use client';

import { useEffect, useState } from 'react';
import DashboardLayout from './components/DashboardLayout';
import {
  FileText,
  CheckCircle,
  MessageSquare,
  TrendingUp,
  Activity,
  Calendar,
  Stethoscope,
  Upload,
  Brain,
  FileBarChart
} from 'lucide-react';
import { api } from './utils/api';
import { StatCard, SkeletonCard } from './components/ui';
import { ProgressModule, IconButton, AppointmentCard } from './components/ui/MedicalComponents';

export default function Home() {
  const [stats, setStats] = useState({
    totalDocuments: 0,
    totalIndexed: 0,
    totalQueries: 0,
    processingSuccess: 0
  });
  const [activities, setActivities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const data = await api.getStats();
        setStats(data);

        // Fetch recent activity
        const logs = await api.getAuditLogs(5);
        setActivities(logs.events || []);

        setError(null);
      } catch (err) {
        setError('Failed to load statistics');
        console.error('Error fetching stats:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  return (
    <DashboardLayout>
      <div className="space-y-6 animate-fade-in">
        {/* Welcome Section - MEDICAL THEME */}
        <div className="relative gradient-teal rounded-3xl p-8 text-white shadow-lg overflow-hidden">
          {/* Decorative Background Pattern */}
          <div className="absolute top-0 right-0 -mr-20 -mt-20 w-96 h-96 bg-white/10 rounded-full blur-3xl animate-pulse-soft"></div>
          <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-96 h-96 bg-white/5 rounded-full blur-3xl"></div>

          <div className="relative z-10">
            <div className="flex items-start justify-between mb-6">
              <div className="flex-1">
                <div className="flex items-center space-x-4 mb-4">
                  <div className="w-16 h-16 bg-white/20 backdrop-blur-lg rounded-2xl flex items-center justify-center border border-white/30 shadow-lg">
                    <Stethoscope className="h-8 w-8 text-white" />
                  </div>
                  <div>
                    <h1 className="text-3xl font-bold mb-1">MedBot Intelligence Dashboard</h1>
                    <p className="text-white/90 text-base">
                      Advanced Medical Document Intelligence System
                    </p>
                  </div>
                </div>

                {/* Quick Stats Badges */}
                <div className="flex flex-wrap gap-3 mt-6">
                  <div className="glass-medical rounded-xl px-4 py-2 flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    <span className="text-sm font-medium text-teal-900">System Online</span>
                  </div>
                  <div className="glass-medical rounded-xl px-4 py-2 flex items-center space-x-2">
                    <TrendingUp className="h-4 w-4 text-teal-900" />
                    <span className="text-sm font-medium text-teal-900">{stats.totalDocuments} Documents</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Progress Modules Grid - Like Reference Design */}
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {loading ? (
            <>
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
            </>
          ) : (
            <>
              <ProgressModule
                icon={FileText}
                value={stats.totalDocuments}
                label="Total Documents"
                subtitle="Medical records"
                color="teal"
                percentage={75}
              />
              <ProgressModule
                icon={CheckCircle}
                value={stats.totalIndexed}
                label="Indexed Chunks"
                subtitle="Ready for AI"
                color="green"
                percentage={100}
              />
              <ProgressModule
                icon={MessageSquare}
                value={stats.totalQueries}
                label="AI Queries"
                subtitle="This month"
                color="blue"
                percentage={67}
              />
              <ProgressModule
                icon={Activity}
                value="98.5%"
                label="System Health"
                subtitle="All systems operational"
                color="orange"
                percentage={98}
              />
            </>
          )}
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Quick Actions - Medical Style */}
          <div className="medical-card p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-5 flex items-center">
              <div className="w-8 h-8 bg-teal-100 rounded-lg flex items-center justify-center mr-2">
                <Activity className="h-4 w-4 text-teal-600" />
              </div>
              Quick Actions
            </h2>
            <div className="grid grid-cols-2 gap-3">
              <IconButton
                icon={Upload}
                label="Upload"
                description="Add document"
                color="teal"
                size="md"
              />
              <IconButton
                icon={Brain}
                label="Ask AI"
                description="Get answers"
                color="blue"
                size="md"
              />
              <IconButton
                icon={Calendar}
                label="Schedule"
                description="Appointments"
                color="green"
                size="md"
              />
              <IconButton
                icon={FileBarChart}
                label="Reports"
                description="Analytics"
                color="orange"
                size="md"
              />
            </div>
          </div>

          {/* Upcoming Appointments */}
          <div className="lg:col-span-2 medical-card p-6">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-lg font-bold text-gray-900 flex items-center">
                <div className="w-8 h-8 bg-teal-100 rounded-lg flex items-center justify-center mr-2">
                  <Calendar className="h-4 w-4 text-teal-600" />
                </div>
                Recent Activity
              </h2>
              <button className="text-sm font-semibold text-teal-600 hover:text-teal-700">
                See All
              </button>
            </div>
            <div className="space-y-3">
              {activities.length > 0 ? (
                activities.slice(0, 3).map((log, i) => (
                  <AppointmentCard
                    key={i}
                    doctorName={log.event_type}
                    specialty={log.details ? String(JSON.stringify(log.details)).substring(0, 50) + "..." : "System Event"}
                    date={new Date(log.timestamp).toLocaleDateString()}
                    time={new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    icon={Activity}
                    color="teal"
                  />
                ))
              ) : (
                <div className="text-center py-4 text-gray-500 text-sm">No recent activity</div>
              )}
            </div>
          </div>
        </div>

        {/* System Statistics */}
        <div className="medical-card p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-5 flex items-center">
            <div className="w-8 h-8 bg-teal-100 rounded-lg flex items-center justify-center mr-2">
              <TrendingUp className="h-4 w-4 text-teal-600" />
            </div>
            System Performance
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-teal-50 rounded-2xl">
              <div className="text-2xl font-bold text-teal-600 mb-1">{stats.totalDocuments}</div>
              <div className="text-xs text-gray-600">Documents Processed</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-2xl">
              <div className="text-2xl font-bold text-green-600 mb-1">{stats.totalIndexed}</div>
              <div className="text-xs text-gray-600">Chunks Indexed</div>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-2xl">
              <div className="text-2xl font-bold text-blue-600 mb-1">{stats.totalQueries}</div>
              <div className="text-xs text-gray-600">AI Queries</div>
            </div>
            <div className="text-center p-4 bg-orange-50 rounded-2xl">
              <div className="text-2xl font-bold text-orange-600 mb-1">-</div>
              <div className="text-xs text-gray-600">Avg Response Time</div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
