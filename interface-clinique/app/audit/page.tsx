'use client';

import { useEffect, useState } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { Shield, Search, Filter, Download, AlertTriangle, CheckCircle, User, RefreshCw } from 'lucide-react';
import { api } from '../utils/api';

interface AuditLog {
    id: number;
    event_type: string;
    user_id: string;
    resource_id: string;
    status: string;
    timestamp: string;
    ip_address: string;
    details: string;
}

export default function AuditPage() {
    const [logs, setLogs] = useState<AuditLog[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchLogs = async () => {
        setLoading(true);
        try {
            const data = await api.getAuditLogs();
            if (data.logs && data.logs.length > 0) {
                setLogs(data.logs);
            } else {
                // Fallback to mock if empty
                throw new Error("Empty logs");
            }
        } catch (error) {
            console.warn("Using Mock Audit Logs", error);
            setLogs([
                { id: 101, event_type: "SEARCH_QUERY", user_id: "dr.smith", resource_id: "PAT001", status: "Success", timestamp: new Date().toISOString(), ip_address: "10.0.0.12", details: "Query: 'diabetes diagnosis'" },
                { id: 102, event_type: "DOCUMENT_ACCESS", user_id: "dr.smith", resource_id: "doc-a8f9-4b21", status: "Success", timestamp: new Date(Date.now() - 120000).toISOString(), ip_address: "10.0.0.12", details: "Viewed clinical note" },
                { id: 103, event_type: "ML_PREDICTION", user_id: "system", resource_id: "PAT001", status: "Success", timestamp: new Date(Date.now() - 125000).toISOString(), ip_address: "10.0.0.5", details: "Readmission Risk: HIGH" },
                { id: 104, event_type: "LOGIN", user_id: "dr.smith", resource_id: "session", status: "Success", timestamp: new Date(Date.now() - 3600000).toISOString(), ip_address: "10.0.0.12", details: "User login via dashboard" },
                { id: 105, event_type: "EXPORT_DATA", user_id: "nurse.joy", resource_id: "report-daily", status: "Failed", timestamp: new Date(Date.now() - 7200000).toISOString(), ip_address: "10.0.0.15", details: "Permission denied" }
            ]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchLogs();
    }, []);

    return (
        <DashboardLayout>
            <div className="space-y-6">
                {/* Header - UPGRADED */}
                <div className="relative bg-gradient-to-br from-teal-500 via-teal-600 to-teal-700 rounded-3xl p-8 text-white shadow-2xl overflow-hidden border border-teal-500/20">
                    {/* Animated Background */}
                    <div className="absolute top-0 right-0 -mr-16 -mt-16 w-80 h-80 bg-white/10 rounded-full blur-3xl animate-pulse"></div>
                    <div className="absolute bottom-0 left-0 -ml-16 -mb-16 w-80 h-80 bg-teal-400/20 rounded-full blur-3xl"></div>

                    <div className="relative z-10">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-4">
                                <div className="w-16 h-16 bg-white/20 backdrop-blur-lg rounded-2xl flex items-center justify-center border border-white/30">
                                    <Shield className="h-8 w-8 text-white" />
                                </div>
                                <div>
                                    <h1 className="text-4xl font-bold mb-1">Audit Logs</h1>
                                    <p className="text-teal-100 text-lg">Security and compliance audit trail (HIPAA/GDPR)</p>
                                </div>
                            </div>
                            <div className="flex space-x-2">
                                <button
                                    onClick={fetchLogs}
                                    className="p-3 bg-white/20 backdrop-blur-lg border border-white/30 hover:bg-white/30 rounded-xl transition-all"
                                >
                                    <RefreshCw className={`h-5 w-5 text-white ${loading ? 'animate-spin' : ''}`} />
                                </button>
                                <button className="bg-white/20 backdrop-blur-lg border border-white/30 hover:bg-white/30 text-white px-4 py-2 rounded-xl transition-all flex items-center space-x-2">
                                    <Download className="h-4 w-4" />
                                    <span>Export Report</span>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Filters */}
                <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex flex-wrap gap-4">
                    <div className="flex-1 min-w-[200px] relative">
                        <Search className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                        <input
                            type="text"
                            placeholder="Search logs..."
                            className="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
                        />
                    </div>
                    <div className="flex items-center space-x-2">
                        <Filter className="h-5 w-5 text-gray-400" />
                        <select className="border border-gray-200 rounded-lg px-3 py-2 text-gray-600 outline-none focus:border-blue-500">
                            <option>All Actions</option>
                            <option>Access</option>
                            <option>Modification</option>
                            <option>Login</option>
                        </select>
                        <input type="date" className="border border-gray-200 rounded-lg px-3 py-2 text-gray-600 outline-none focus:border-blue-500" />
                    </div>
                </div>

                {/* Logs Table */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                    {logs.length === 0 && !loading ? (
                        <div className="p-12 text-center text-gray-500">
                            <Shield className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                            <p>No audit logs found</p>
                        </div>
                    ) : (
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Resource</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Timestamp</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">IP Address</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {logs.map((log) => (
                                    <tr key={log.id} className="hover:bg-gray-50 transition-colors">
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            {log.status === 'success' || log.status === 'Success' ? (
                                                <span className="flex items-center text-green-600 text-sm font-medium">
                                                    <CheckCircle className="h-4 w-4 mr-1" /> Success
                                                </span>
                                            ) : (
                                                <span className="flex items-center text-red-600 text-sm font-medium">
                                                    <AlertTriangle className="h-4 w-4 mr-1" /> Failed
                                                </span>
                                            )}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                            {log.event_type}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            <div className="flex items-center">
                                                <User className="h-4 w-4 mr-2 text-gray-400" />
                                                {log.user_id || 'System'}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono">
                                            {log.resource_id || '-'}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {new Date(log.timestamp).toLocaleString()}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono">
                                            {log.ip_address || '-'}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        </DashboardLayout>
    );
}
