'use client';

import { useState, useEffect, useCallback } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { Upload, FileText, CheckCircle, Clock, AlertCircle, Trash2, Download, Eye, RefreshCw } from 'lucide-react';
import { api } from '../utils/api';
import { StatusBadge, SkeletonTable } from '../components/ui';

interface Document {
    id: string;
    filename: string;
    content_type: string;
    size: number;
    status: string;
    created_at: string;
    metadata?: any;
}

export default function DocumentsPage() {
    const [documents, setDocuments] = useState<Document[]>([]);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [dragActive, setDragActive] = useState(false);

    const fetchDocuments = async () => {
        try {
            setLoading(true);
            const data = await api.getDocuments();
            // Handle different response structures (list or object with items)
            const docs = Array.isArray(data) ? data : (data.items || []);
            setDocuments(docs);
        } catch (error) {
            console.error("Failed to fetch documents", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDocuments();
    }, []);

    const handleDrag = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setDragActive(true);
        } else if (e.type === 'dragleave') {
            setDragActive(false);
        }
    }, []);

    const handleDrop = useCallback(async (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            await handleUpload(e.dataTransfer.files[0]);
        }
    }, []);

    const handleFileInput = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            await handleUpload(e.target.files[0]);
        }
    }, []);

    const handleUpload = async (file: File) => {
        setUploading(true);
        try {
            await api.uploadDocument(file);
            await fetchDocuments(); // Refresh list
        } catch (error) {
            console.error('Upload error:', error);
            alert('Failed to upload document');
        } finally {
            setUploading(false);
        }
    };

    const handleDelete = async (id: string) => {
        if (confirm('Are you sure you want to delete this document?')) {
            try {
                await api.deleteDocument(id);
                setDocuments(prev => prev.filter(d => d.id !== id));
            } catch (error) {
                console.error('Delete error:', error);
                alert('Failed to delete document');
            }
        }
    };

    const formatSize = (bytes: number) => {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    return (
        <DashboardLayout>
            <div className="space-y-6">
                {/* Header Section - UPGRADED */}
                <div className="relative bg-gradient-to-br from-teal-500 via-teal-600 to-teal-700 rounded-3xl p-8 text-white shadow-2xl overflow-hidden border border-teal-500/20">
                    {/* Animated Background */}
                    <div className="absolute top-0 right-0 -mr-16 -mt-16 w-80 h-80 bg-white/10 rounded-full blur-3xl animate-pulse"></div>
                    <div className="absolute bottom-0 left-0 -ml-16 -mb-16 w-80 h-80 bg-teal-400/20 rounded-full blur-3xl"></div>

                    <div className="relative z-10">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-4">
                                <div className="w-16 h-16 bg-white/20 backdrop-blur-lg rounded-2xl flex items-center justify-center border border-white/30">
                                    <FileText className="h-8 w-8 text-white" />
                                </div>
                                <div>
                                    <h1 className="text-4xl font-bold mb-1">Documents</h1>
                                    <p className="text-teal-100 text-lg">Manage and process medical documents</p>
                                </div>
                            </div>
                            <button
                                onClick={fetchDocuments}
                                className="p-3 bg-white/20 backdrop-blur-lg border border-white/30 hover:bg-white/30 rounded-xl transition-all"
                                title="Refresh list"
                            >
                                <RefreshCw className={`h-5 w-5 text-white ${loading ? 'animate-spin' : ''}`} />
                            </button>
                        </div>

                        {/* Stats Badges */}
                        <div className="flex flex-wrap gap-3 mt-6">
                            <div className="bg-white/20 backdrop-blur-lg border border-white/30 rounded-xl px-4 py-2 flex items-center space-x-2">
                                <FileText className="h-4 w-4" />
                                <span className="text-sm font-medium">{documents.length} Documents</span>
                            </div>
                            <div className="bg-white/20 backdrop-blur-lg border border-white/30 rounded-xl px-4 py-2 flex items-center space-x-2">
                                <CheckCircle className="h-4 w-4" />
                                <span className="text-sm font-medium">{documents.filter(d => d.status === 'completed').length} Processed</span>
                            </div>
                            <div className="bg-white/20 backdrop-blur-lg border border-white/30 rounded-xl px-4 py-2 flex items-center space-x-2">
                                <Clock className="h-4 w-4" />
                                <span className="text-sm font-medium">{documents.filter(d => d.status === 'processing').length} Processing</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Upload Area - UPGRADED */}
                <div
                    className={`relative border-2 border-dashed rounded-3xl p-12 text-center transition-all group ${dragActive
                        ? 'border-teal-600 bg-gradient-to-br from-teal-50 to-teal-100 shadow-xl'
                        : 'border-gray-300 bg-white hover:border-teal-400 hover:shadow-lg'
                        }`}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                >
                    <input
                        type="file"
                        id="file-upload"
                        className="sr-only"
                        onChange={handleFileInput}
                        accept=".pdf,.docx,.hl7,.json,.txt"
                    />
                    <label htmlFor="file-upload" className="cursor-pointer">
                        <div className="space-y-6">
                            <div className="mx-auto w-20 h-20 bg-gradient-to-br from-teal-500 to-teal-600 rounded-2xl flex items-center justify-center shadow-2xl group-hover:scale-110 transition-transform">
                                <Upload className="h-10 w-10 text-white" />
                            </div>
                            <div>
                                <p className="text-2xl font-bold text-gray-900 mb-2">
                                    {dragActive ? '✨ Drop files here' : 'Upload Medical Documents'}
                                </p>
                                <p className="text-base text-gray-600">Drag & drop files or <span className="text-teal-600 font-semibold">browse</span> to upload</p>
                            </div>
                            <div className="flex items-center justify-center space-x-8 text-sm">
                                <div className="flex items-center space-x-2 bg-gray-50 px-4 py-2 rounded-xl">
                                    <FileText className="h-5 w-5 text-teal-600" />
                                    <span className="font-medium text-gray-700">PDF, DOCX, HL7, FHIR</span>
                                </div>
                                <div className="flex items-center space-x-2 bg-gray-50 px-4 py-2 rounded-xl">
                                    <span className="font-medium text-gray-700">Max 100MB</span>
                                </div>
                            </div>
                        </div>
                    </label>
                    {uploading && (
                        <div className="absolute inset-0 bg-white/95 backdrop-blur-md flex items-center justify-center rounded-3xl">
                            <div className="text-center">
                                <div className="w-20 h-20 border-4 border-teal-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                                <p className="text-lg font-semibold text-gray-900">Uploading & Processing...</p>
                                <p className="text-sm text-gray-600 mt-2">Please wait while we analyze your document</p>
                            </div>
                        </div>
                    )}
                </div>

                {/* Documents List */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                    {loading ? (
                        <SkeletonTable rows={5} />
                    ) : documents.length === 0 ? (
                        <div className="p-12 text-center text-gray-500">
                            <FileText className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                            <p>No documents found</p>
                        </div>
                    ) : (
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Size</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {documents.map((doc) => (
                                    <tr key={doc.id} className="hover:bg-gray-50 transition-colors">
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex items-center">
                                                <FileText className="h-5 w-5 text-gray-400 mr-3" />
                                                <div className="text-sm font-medium text-gray-900">{doc.filename}</div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            {doc.status === 'completed' ? (
                                                <StatusBadge status="success">Completed</StatusBadge>
                                            ) : doc.status === 'processing' ? (
                                                <StatusBadge status="processing">Processing</StatusBadge>
                                            ) : (
                                                <StatusBadge status="error">Failed</StatusBadge>
                                            )}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {formatSize(doc.size)}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {new Date(doc.created_at).toLocaleDateString()}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                            <div className="flex justify-end space-x-2">
                                                <button
                                                    className="text-gray-400 hover:text-blue-600 p-1 transition-colors"
                                                    aria-label="View document"
                                                >
                                                    <Eye className="h-4 w-4" />
                                                </button>
                                                <button
                                                    className="text-gray-400 hover:text-green-600 p-1 transition-colors"
                                                    aria-label="Download document"
                                                >
                                                    <Download className="h-4 w-4" />
                                                </button>
                                                <button
                                                    onClick={() => handleDelete(doc.id)}
                                                    className="text-gray-400 hover:text-red-600 p-1 transition-colors"
                                                    aria-label="Delete document"
                                                >
                                                    <Trash2 className="h-4 w-4" />
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
