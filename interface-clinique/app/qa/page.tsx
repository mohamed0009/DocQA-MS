'use client';

import { useState } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { Send, Sparkles, FileText, Clock, Target } from 'lucide-react';
import { api } from '../utils/api';
import { Button } from '../components/ui';

interface Message {
    role: 'user' | 'assistant';
    content: string;
    sources?: any[];
    timestamp: Date;
}

export default function QAPage() {
    const [messages, setMessages] = useState<Message[]>([
        {
            role: 'assistant',
            content: 'Hello! I\'m your AI medical assistant. Ask me anything about your patients\' medical records, and I\'ll provide answers with citations from the documents.',
            timestamp: new Date(),
        },
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSend = async () => {
        if (!input.trim() || loading) return;

        const userMessage: Message = {
            role: 'user',
            content: input,
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const response = await api.askQuestion(input);

            const assistantMessage: Message = {
                role: 'assistant',
                content: response.answer,
                sources: response.sources,
                timestamp: new Date(),
            };

            setMessages((prev) => [...prev, assistantMessage]);
        } catch (error) {
            console.error('Error asking question:', error);
            const errorMessage: Message = {
                role: 'assistant',
                content: 'Sorry, I encountered an error processing your question. Please try again.',
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <DashboardLayout>
            <div className="max-w-5xl mx-auto">
                {/* Header - UPGRADED */}
                <div className="relative bg-gradient-to-br from-teal-500 via-teal-600 to-teal-700 rounded-3xl p-8 text-white shadow-2xl overflow-hidden border border-teal-500/20 mb-6">
                    {/* Animated Background */}
                    <div className="absolute top-0 right-0 -mr-16 -mt-16 w-80 h-80 bg-white/10 rounded-full blur-3xl animate-pulse"></div>
                    <div className="absolute bottom-0 left-0 -ml-16 -mb-16 w-80 h-80 bg-teal-400/20 rounded-full blur-3xl"></div>

                    <div className="relative z-10">
                        <div className="flex items-center space-x-4">
                            <div className="w-16 h-16 bg-white/20 backdrop-blur-lg rounded-2xl flex items-center justify-center border border-white/30">
                                <Sparkles className="h-8 w-8 text-white" />
                            </div>
                            <div>
                                <h1 className="text-4xl font-bold mb-1">AI Medical Assistant</h1>
                                <p className="text-purple-100 text-lg">Ask questions about patient records and get AI-powered answers with citations</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Chat Container */}
                <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
                    {/* Messages */}
                    <div className="h-[600px] overflow-y-auto p-6 space-y-6">
                        {messages.map((message, index) => (
                            <div
                                key={index}
                                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                <div
                                    className={`max-w-3xl rounded-2xl p-4 ${message.role === 'user'
                                        ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white'
                                        : 'bg-gray-100 text-gray-900'
                                        }`}
                                >
                                    <div className="flex items-start space-x-3">
                                        {message.role === 'assistant' && (
                                            <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-teal-500 to-teal-600 rounded-lg flex items-center justify-center">
                                                <Sparkles className="h-4 w-4 text-white" />
                                            </div>
                                        )}
                                        <div className="flex-1">
                                            <p className="text-sm whitespace-pre-wrap">{message.content}</p>

                                            {/* Sources */}
                                            {message.sources && message.sources.length > 0 && (
                                                <div className="mt-4 space-y-2">
                                                    <div className="flex items-center space-x-2 text-xs text-gray-600">
                                                        <FileText className="h-3 w-3" />
                                                        <span className="font-semibold">Sources ({message.sources.length})</span>
                                                    </div>
                                                    <div className="space-y-1">
                                                        {message.sources.map((source, idx) => (
                                                            <div
                                                                key={idx}
                                                                className="text-xs bg-white rounded-lg p-2 border border-gray-200"
                                                            >
                                                                <p className="font-medium text-gray-700">
                                                                    {source.source_id}
                                                                </p>
                                                                <p className="text-gray-500 mt-1 line-clamp-2">
                                                                    {source.chunk_text.substring(0, 100)}...
                                                                </p>
                                                            </div>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}

                                            {/* Metadata */}
                                            <div className="mt-2 flex items-center space-x-4 text-xs opacity-70">
                                                <span className="flex items-center space-x-1">
                                                    <Clock className="h-3 w-3" />
                                                    <span>{message.timestamp.toLocaleTimeString()}</span>
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}

                        {loading && (
                            <div className="flex justify-start">
                                <div className="bg-gray-100 rounded-2xl p-4 max-w-3xl">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-8 h-8 bg-gradient-to-br from-teal-500 to-teal-600 rounded-lg flex items-center justify-center">
                                            <Sparkles className="h-4 w-4 text-white animate-pulse" />
                                        </div>
                                        <div className="flex space-x-2">
                                            <div className="w-2 h-2 bg-teal-600 rounded-full animate-bounce"></div>
                                            <div className="w-2 h-2 bg-teal-600 rounded-full animate-bounce [animation-delay:0.2s]"></div>
                                            <div className="w-2 h-2 bg-teal-600 rounded-full animate-bounce [animation-delay:0.4s]"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Input Area */}
                    <div className="border-t bg-gray-50 p-4">
                        <div className="flex items-center space-x-3">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                                placeholder="Ask a question about your patient records..."
                                className="flex-1 px-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                                disabled={loading}
                            />
                            <Button
                                onClick={handleSend}
                                disabled={loading || !input.trim()}
                                variant="primary"
                                size="lg"
                            >
                                Send
                                <Send className="h-4 w-4 ml-2" />
                            </Button>
                        </div>
                    </div>
                </div>

                {/* Tips */}
                <div className="mt-6 bg-gradient-to-r from-teal-50 to-teal-100 rounded-xl p-6 border border-teal-100">
                    <div className="flex items-start space-x-3">
                        <Target className="h-5 w-5 text-teal-600 mt-0.5" />
                        <div>
                            <h3 className="font-semibold text-gray-900 mb-2">Example Questions:</h3>
                            <ul className="space-y-1 text-sm text-gray-600">
                                <li>• "What medications is patient PAT001 currently taking?"</li>
                                <li>• "Summarize the lab results for patient PAT002"</li>
                                <li>• "What were the diagnoses in the last visit for PAT003?"</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
}
