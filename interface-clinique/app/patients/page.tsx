'use client';

import { useState, useEffect } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { Users, Search, FileText, Activity, ChevronRight, Plus, Loader2 } from 'lucide-react';
import { api } from '../utils/api';

export default function PatientsPage() {
    const [patients, setPatients] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [generatingId, setGeneratingId] = useState<string | null>(null);

    // Fetch patients on component mount
    useEffect(() => {
        const fetchPatients = async () => {
            try {
                setLoading(true);
                const response = await api.getPatients();
                setPatients(response.patients || []);
            } catch (error) {
                console.error("Error fetching patients:", error);
                setPatients([]);
            } finally {
                setLoading(false);
            }
        };

        fetchPatients();
    }, []);

    const handleGenerateSummary = async (patientId: string) => {
        setGeneratingId(patientId);
        try {
            const summary = await api.generateSummary(patientId);
            alert(`Summary generated for ${patientId}:\n\n${summary.summary || 'No summary available.'}`);
        } catch (error) {
            console.error("Error generating summary", error);
            alert("Failed to generate summary. Make sure backend is running.");
        } finally {
            setGeneratingId(null);
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
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-4">
                                <div className="w-16 h-16 bg-white/20 backdrop-blur-lg rounded-2xl flex items-center justify-center border border-white/30">
                                    <Users className="h-8 w-8 text-white" />
                                </div>
                                <div>
                                    <h1 className="text-4xl font-bold mb-1">Patients</h1>
                                    <p className="text-teal-100 text-lg">View and manage patient records</p>
                                </div>
                            </div>
                            <button className="bg-white/20 backdrop-blur-lg border border-white/30 hover:bg-white/30 text-white px-4 py-2 rounded-xl transition-all flex items-center space-x-2">
                                <Plus className="h-5 w-5" />
                                <span>Add Patient</span>
                            </button>
                        </div>
                    </div>
                </div>

                {/* Search & Filter */}
                <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex space-x-4">
                    <div className="flex-1 relative">
                        <Search className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                        <input
                            type="text"
                            placeholder="Search patients by name, ID, or condition..."
                            className="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
                        />
                    </div>
                    <select className="border border-gray-200 rounded-lg px-4 py-2 text-gray-600 outline-none focus:border-blue-500">
                        <option>All Statuses</option>
                        <option>Critical</option>
                        <option>Stable</option>
                        <option>Warning</option>
                    </select>
                </div>

                {/* Patients List */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                    {loading ? (
                        <div className="flex items-center justify-center py-20">
                            <Loader2 className="h-8 w-8 animate-spin text-teal-600" />
                            <span className="ml-3 text-gray-600">Loading patients...</span>
                        </div>
                    ) : patients.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-20 text-gray-500">
                            <Users className="h-16 w-16 text-gray-300 mb-4" />
                            <p className="text-lg font-medium">No patients found</p>
                            <p className="text-sm mt-2">Upload documents with patient metadata to see them here</p>
                        </div>
                    ) : (
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Patient</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Documents</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Age</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Gender</th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {patients.map((patient) => (
                                    <tr key={patient.id} className="hover:bg-gray-50 transition-colors cursor-pointer group">
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex items-center">
                                                <div className="flex-shrink-0 h-10 w-10 rounded-full bg-gradient-to-br from-blue-500 to-teal-500 flex items-center justify-center text-white font-medium">
                                                    {patient.name ? patient.name.charAt(0).toUpperCase() : 'U'}
                                                </div>
                                                <div className="ml-4">
                                                    <div className="text-sm font-medium text-gray-900">{patient.name || 'Unknown Patient'}</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {patient.id}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                                                {patient.document_count || 0} docs
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {patient.age || 'N/A'}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {patient.gender || 'N/A'}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                            <div className="flex justify-end space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                                <button
                                                    onClick={(e) => { e.stopPropagation(); handleGenerateSummary(patient.id); }}
                                                    className="text-teal-600 hover:text-teal-900 bg-teal-50 p-2 rounded-lg flex items-center"
                                                    title="Generate Summary"
                                                    disabled={generatingId === patient.id}
                                                >
                                                    {generatingId === patient.id ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileText className="h-4 w-4" />}
                                                </button>
                                                <button className="text-teal-600 hover:text-teal-900 bg-teal-50 p-2 rounded-lg">
                                                    <Activity className="h-4 w-4" />
                                                </button>
                                            </div>
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
