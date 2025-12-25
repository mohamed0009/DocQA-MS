'use client';

import { useState } from 'react';
import {
    LayoutDashboard,
    FileText,
    MessageSquare,
    Search,
    BarChart3,
    Users,
    Shield,
    Settings,
    Menu,
    X,
    Bell,
    User,
    LogOut,
    Activity,
    Clock
} from 'lucide-react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import Image from 'next/image';

const navigation = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Documents', href: '/docs', icon: FileText },
    { name: 'Q&A Assistant', href: '/qa', icon: MessageSquare },
    { name: 'Search', href: '/search', icon: Search },
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
    { name: 'Patients', href: '/patients', icon: Users },
    { name: 'Audit Logs', href: '/audit', icon: Shield },
    { name: 'Settings', href: '/settings', icon: Settings },
];

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [showNotifications, setShowNotifications] = useState(false);
    const [showUserMenu, setShowUserMenu] = useState(false);
    const pathname = usePathname();
    const router = useRouter();

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        if (searchQuery.trim()) {
            router.push(`/search?q=${encodeURIComponent(searchQuery)}`);
        }
    };

    const handleSearchKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            handleSearch(e as any);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Skip Navigation Link for Accessibility */}
            <a
                href="#main-content"
                className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-blue-600 text-white px-4 py-2 rounded-lg z-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
                Skip to main content
            </a>

            {/* Sidebar for mobile with animation - MEDICAL THEME */}
            <div className={`fixed inset-0 z-50 lg:hidden transition-opacity duration-300 ${sidebarOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
                }`}>
                <div
                    className="fixed inset-0 bg-gray-900 bg-opacity-50 transition-opacity backdrop-blur-sm"
                    onClick={() => setSidebarOpen(false)}
                    aria-hidden="true"
                />
                <div className={`fixed inset-y-0 left-0 flex w-72 flex-col bg-white shadow-2xl transform transition-transform duration-300 ease-in-out ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'
                    }`}>
                    {/* Logo Section */}
                    <div className="flex h-20 items-center justify-between px-6 border-b border-gray-200 bg-white">
                        <div className="flex items-center space-x-2">
                            <div className="relative w-16 h-16 rounded-2xl flex items-center justify-center p-1">
                                <Image
                                    src="/logo-v3.png"
                                    alt="DocQA-MS Logo"
                                    fill
                                    className="object-contain p-0.5"
                                />
                            </div>
                            <div className="flex flex-col justify-center">
                                <h1 className="text-xl font-extrabold text-teal-950 leading-none mb-0.5">
                                    DocQA-MS
                                </h1>
                                <p className="text-[9px] text-teal-600 font-bold tracking-[0.2em] uppercase">Clinical Intelligence</p>
                            </div>
                        </div>
                        <button
                            onClick={() => setSidebarOpen(false)}
                            className="text-gray-400 hover:text-gray-900 transition-colors p-2 hover:bg-gray-100 rounded-lg"
                            aria-label="Close sidebar"
                        >
                            <X className="h-6 w-6" />
                        </button>
                    </div>

                    {/* Navigation */}
                    <nav className="flex-1 space-y-2 px-4 py-6 bg-gray-50/50">
                        {navigation.map((item) => {
                            const isActive = pathname === item.href;
                            return (
                                <Link
                                    key={item.name}
                                    href={item.href}
                                    className={`group flex items-center px-4 py-3.5 rounded-2xl text-sm font-semibold transition-all duration-200 ${isActive
                                        ? 'bg-teal-500 text-white shadow-md shadow-teal-500/30'
                                        : 'text-gray-700 hover:bg-white hover:shadow-sm'
                                        }`}
                                    onClick={() => setSidebarOpen(false)}
                                >
                                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center mr-3 transition-all ${isActive
                                        ? 'bg-white/20'
                                        : 'bg-gray-100 group-hover:bg-teal-50'
                                        }`}>
                                        <item.icon className={`h-5 w-5 ${isActive ? 'text-white' : 'text-teal-600'
                                            }`} />
                                    </div>
                                    <span className="flex-1">{item.name}</span>
                                    {isActive && (
                                        <div className="w-2 h-2 rounded-full bg-white"></div>
                                    )}
                                </Link>
                            );
                        })}
                    </nav>
                </div>
            </div>

            {/* Static sidebar for desktop - MEDICAL THEME */}
            <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-72 lg:flex-col">
                <div className="flex flex-col flex-grow bg-white shadow-xl border-r border-gray-200">
                    {/* Logo Section - Updated Design */}
                    <div className="flex h-20 items-center px-6 border-b border-gray-200 bg-white">
                        <div className="flex items-center space-x-2">
                            <div className="relative w-16 h-16 rounded-2xl flex items-center justify-center p-1">
                                <Image
                                    src="/logo-v3.png"
                                    alt="DocQA-MS Logo"
                                    fill
                                    className="object-contain p-0.5"
                                />
                            </div>
                            <div className="flex flex-col justify-center">
                                <h1 className="text-xl font-extrabold text-teal-950 leading-none mb-0.5">
                                    DocQA-MS
                                </h1>
                                <p className="text-[9px] text-teal-600 font-bold tracking-[0.2em] uppercase">Clinical Intelligence</p>
                            </div>
                        </div>
                    </div>

                    {/* Navigation - Medical Theme */}
                    <nav className="flex-1 space-y-2 px-4 py-6 bg-gray-50/50">
                        {navigation.map((item) => {
                            const isActive = pathname === item.href;
                            return (
                                <Link
                                    key={item.name}
                                    href={item.href}
                                    className={`group flex items-center px-4 py-3.5 rounded-2xl text-sm font-semibold transition-all duration-200 ${isActive
                                        ? 'bg-teal-500 text-white shadow-md shadow-teal-500/30'
                                        : 'text-gray-700 hover:bg-white hover:shadow-sm'
                                        }`}
                                >
                                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center mr-3 transition-all ${isActive
                                        ? 'bg-white/20'
                                        : 'bg-gray-100 group-hover:bg-teal-50'
                                        }`}>
                                        <item.icon className={`h-5 w-5 ${isActive ? 'text-white' : 'text-teal-600'
                                            }`} />
                                    </div>
                                    <span className="flex-1">{item.name}</span>
                                    {isActive && (
                                        <div className="w-2 h-2 rounded-full bg-white"></div>
                                    )}
                                </Link>
                            );
                        })}
                    </nav>

                    {/* User Profile - Medical Theme */}
                    <div className="border-t border-gray-200 p-4 bg-gradient-to-r from-teal-50/50 to-white">
                        <div className="medical-card-hover p-4 cursor-pointer">
                            <div className="flex items-center space-x-3">
                                <div className="relative">
                                    <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-teal-500 to-teal-600 flex items-center justify-center text-white font-bold shadow-md text-lg">
                                        DM
                                    </div>
                                    <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white"></div>
                                </div>
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm font-bold text-gray-900 truncate">Dr. Martinez</p>
                                    <p className="text-xs text-gray-500">Cardiologist</p>
                                </div>
                                <button
                                    className="text-gray-400 hover:text-red-500 transition-colors p-1.5 hover:bg-red-50 rounded-lg"
                                    aria-label="Logout"
                                >
                                    <LogOut className="h-4 w-4" />
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main content */}
            <div className="lg:pl-72">
                {/* Top navigation - UPGRADED */}
                <div className="sticky top-0 z-40 flex h-16 border-b bg-white/70 backdrop-blur-xl shadow-sm border-gray-200/50">
                    <button
                        type="button"
                        className="px-4 focus:outline-none lg:hidden hover:opacity-80 transition-opacity flex items-center"
                        onClick={() => setSidebarOpen(true)}
                        aria-label="Open sidebar"
                    >
                        <div className="relative w-8 h-8 rounded-lg flex items-center justify-center p-1">
                            <Image
                                src="/logo.png"
                                alt="DocQA-MS Logo"
                                fill
                                className="object-contain p-0.5"
                            />
                        </div>
                    </button>

                    <div className="flex flex-1 justify-between px-4 sm:px-6 lg:px-8">
                        {/* Search Bar - FUNCTIONAL */}
                        <div className="flex flex-1 items-center max-w-2xl">
                            <form onSubmit={handleSearch} className="relative w-full">
                                <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                                    <Search className="h-5 w-5 text-gray-400" />
                                </div>
                                <input
                                    type="text"
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    onKeyPress={handleSearchKeyPress}
                                    placeholder="Search patients, documents, or ask AI..."
                                    className="block w-full pl-10 pr-3 py-2 border border-gray-200 rounded-xl text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-50/50 hover:bg-white transition-colors"
                                />
                            </form>
                        </div>

                        {/* Right Actions - FUNCTIONAL */}
                        <div className="ml-4 flex items-center space-x-3">
                            {/* Notifications - UPGRADED */}
                            <div className="relative">
                                <button
                                    onClick={() => setShowNotifications(!showNotifications)}
                                    className="relative p-2.5 text-gray-500 hover:text-teal-600 transition-all rounded-xl hover:bg-teal-50 group"
                                    aria-label="View notifications"
                                >
                                    <Bell className="h-5 w-5 transition-transform group-hover:scale-110" />
                                    <span className="absolute top-1.5 right-1.5 flex h-4 w-4">
                                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-teal-400 opacity-75"></span>
                                        <span className="relative inline-flex rounded-full h-4 w-4 bg-gradient-to-br from-teal-500 to-teal-600 items-center justify-center text-[10px] font-bold text-white shadow-sm">3</span>
                                    </span>
                                </button>

                                {/* Notifications Dropdown - UPGRADED */}
                                {showNotifications && (
                                    <>
                                        <div
                                            className="fixed inset-0 z-40"
                                            onClick={() => setShowNotifications(false)}
                                        ></div>
                                        <div className="absolute right-0 mt-3 w-96 bg-white rounded-2xl shadow-2xl border border-gray-200 z-50 overflow-hidden animate-scale-in">
                                            {/* Header */}
                                            <div className="p-5 border-b border-gray-100 bg-gradient-to-r from-teal-50 to-teal-100">
                                                <div className="flex items-center justify-between">
                                                    <div className="flex items-center space-x-2">
                                                        <div className="w-8 h-8 bg-gradient-to-br from-teal-500 to-teal-600 rounded-xl flex items-center justify-center shadow-md">
                                                            <Bell className="h-4 w-4 text-white" />
                                                        </div>
                                                        <div>
                                                            <h3 className="text-base font-bold text-gray-900">Notifications</h3>
                                                            <p className="text-xs text-teal-600 font-medium">3 unread messages</p>
                                                        </div>
                                                    </div>
                                                    <button
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            alert('Mark all as read');
                                                        }}
                                                        className="text-xs text-teal-600 hover:text-teal-700 font-semibold px-3 py-1.5 rounded-lg hover:bg-teal-200/50 transition-colors"
                                                    >
                                                        Mark all read
                                                    </button>
                                                </div>
                                            </div>

                                            {/* Notifications List */}
                                            <div className="max-h-[450px] overflow-y-auto">
                                                {[
                                                    {
                                                        id: 1,
                                                        title: 'New Patient Record Uploaded',
                                                        message: 'Patient Sarah Connor\'s medical history has been successfully added to the system',
                                                        time: '5 min ago',
                                                        type: 'success',
                                                        icon: Users,
                                                        link: '/patients',
                                                        unread: true
                                                    },
                                                    {
                                                        id: 2,
                                                        title: 'Document Processing Complete',
                                                        message: 'Lab_Results_2024.pdf has been indexed and is ready for AI queries',
                                                        time: '1 hour ago',
                                                        type: 'info',
                                                        icon: FileText,
                                                        link: '/docs',
                                                        unread: true
                                                    },
                                                    {
                                                        id: 3,
                                                        title: 'AI Analysis Ready',
                                                        message: 'Comprehensive medical summary generated for Patient ID: PAT001',
                                                        time: '2 hours ago',
                                                        type: 'warning',
                                                        icon: Activity,
                                                        link: '/qa',
                                                        unread: true
                                                    },
                                                    {
                                                        id: 4,
                                                        title: 'System Backup Complete',
                                                        message: 'All medical records backed up successfully at 3:00 AM',
                                                        time: '5 hours ago',
                                                        type: 'success',
                                                        icon: Shield,
                                                        link: '/audit',
                                                        unread: false
                                                    },
                                                ].map((notif) => {
                                                    const IconComponent = notif.icon;
                                                    const typeColors = {
                                                        success: 'bg-green-100 text-green-600',
                                                        info: 'bg-blue-100 text-blue-600',
                                                        warning: 'bg-orange-100 text-orange-600',
                                                        error: 'bg-red-100 text-red-600'
                                                    };

                                                    return (
                                                        <div
                                                            key={notif.id}
                                                            onClick={() => {
                                                                router.push(notif.link);
                                                                setShowNotifications(false);
                                                            }}
                                                            className={`p-4 hover:bg-teal-50/50 border-b border-gray-100 cursor-pointer transition-all group ${notif.unread ? 'bg-teal-50/30' : ''
                                                                }`}
                                                        >
                                                            <div className="flex items-start space-x-3">
                                                                <div className={`flex-shrink-0 w-10 h-10 rounded-xl ${typeColors[notif.type as keyof typeof typeColors]} flex items-center justify-center shadow-sm group-hover:scale-110 transition-transform`}>
                                                                    <IconComponent className="h-5 w-5" />
                                                                </div>
                                                                <div className="flex-1 min-w-0">
                                                                    <div className="flex items-start justify-between">
                                                                        <p className="text-sm font-semibold text-gray-900 group-hover:text-teal-600 transition-colors">
                                                                            {notif.title}
                                                                        </p>
                                                                        {notif.unread && (
                                                                            <div className="flex-shrink-0 w-2 h-2 bg-teal-500 rounded-full ml-2 mt-1.5"></div>
                                                                        )}
                                                                    </div>
                                                                    <p className="text-xs text-gray-600 mt-1 line-clamp-2">{notif.message}</p>
                                                                    <div className="flex items-center mt-2">
                                                                        <Clock className="h-3 w-3 text-gray-400 mr-1" />
                                                                        <p className="text-xs text-gray-500">{notif.time}</p>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    );
                                                })}
                                            </div>

                                            {/* Footer */}
                                            <div className="p-3 bg-gradient-to-r from-gray-50 to-teal-50 border-t border-gray-100">
                                                <button
                                                    onClick={() => {
                                                        router.push('/audit');
                                                        setShowNotifications(false);
                                                    }}
                                                    className="w-full text-sm text-teal-600 hover:text-teal-700 font-semibold py-2 rounded-lg hover:bg-teal-100/50 transition-colors"
                                                >
                                                    View All Activity →
                                                </button>
                                            </div>
                                        </div>
                                    </>
                                )}
                            </div>

                            {/* User Menu - UPGRADED */}
                            <div className="relative">
                                <button
                                    onClick={() => setShowUserMenu(!showUserMenu)}
                                    className="group flex items-center space-x-2 p-1.5 pr-3 text-gray-600 hover:text-teal-600 transition-all rounded-xl hover:bg-teal-50 border border-transparent hover:border-teal-200"
                                    aria-label="User menu"
                                >
                                    <div className="relative">
                                        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-teal-500 to-teal-600 flex items-center justify-center text-white font-bold shadow-md text-sm group-hover:scale-105 transition-transform">
                                            DM
                                        </div>
                                        <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></div>
                                    </div>
                                </button>

                                {/* User Menu Dropdown - UPGRADED */}
                                {showUserMenu && (
                                    <>
                                        <div
                                            className="fixed inset-0 z-40"
                                            onClick={() => setShowUserMenu(false)}
                                        ></div>
                                        <div className="absolute right-0 mt-3 w-72 bg-white rounded-2xl shadow-2xl border border-gray-200 z-50 overflow-hidden animate-scale-in">
                                            {/* Profile Header */}
                                            <div className="p-5 border-b border-gray-100 bg-gradient-to-br from-teal-50 to-teal-100">
                                                <div className="flex items-center space-x-3">
                                                    <div className="relative">
                                                        <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-teal-500 to-teal-600 flex items-center justify-center text-white font-bold shadow-lg text-xl">
                                                            DM
                                                        </div>
                                                        <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white shadow-sm"></div>
                                                    </div>
                                                    <div className="flex-1 min-w-0">
                                                        <p className="text-base font-bold text-gray-900 truncate">Dr. Alejandro Martinez</p>
                                                        <p className="text-xs text-teal-700 font-medium truncate">Cardiologist • Admin</p>
                                                        <p className="text-xs text-gray-600 truncate mt-0.5">dr.martinez@medbot.hospital</p>
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Menu Items */}
                                            <div className="py-2">
                                                <Link
                                                    href="/settings"
                                                    onClick={() => setShowUserMenu(false)}
                                                    className="flex items-center px-4 py-3 text-sm text-gray-700 hover:bg-teal-50 hover:text-teal-700 transition-all group"
                                                >
                                                    <div className="w-9 h-9 rounded-xl bg-gray-100 group-hover:bg-teal-100 flex items-center justify-center mr-3 transition-colors">
                                                        <Settings className="h-4 w-4 text-gray-600 group-hover:text-teal-600 transition-colors" />
                                                    </div>
                                                    <div className="flex-1">
                                                        <p className="font-semibold">Account Settings</p>
                                                        <p className="text-xs text-gray-500">Manage your profile</p>
                                                    </div>
                                                </Link>

                                                <Link
                                                    href="/patients"
                                                    onClick={() => setShowUserMenu(false)}
                                                    className="flex items-center px-4 py-3 text-sm text-gray-700 hover:bg-teal-50 hover:text-teal-700 transition-all group"
                                                >
                                                    <div className="w-9 h-9 rounded-xl bg-gray-100 group-hover:bg-teal-100 flex items-center justify-center mr-3 transition-colors">
                                                        <Users className="h-4 w-4 text-gray-600 group-hover:text-teal-600 transition-colors" />
                                                    </div>
                                                    <div className="flex-1">
                                                        <p className="font-semibold">My Patients</p>
                                                        <p className="text-xs text-gray-500">View patient records</p>
                                                    </div>
                                                    <span className="bg-teal-100 text-teal-700 text-xs font-bold px-2 py-1 rounded-lg">24</span>
                                                </Link>

                                                <Link
                                                    href="/audit"
                                                    onClick={() => setShowUserMenu(false)}
                                                    className="flex items-center px-4 py-3 text-sm text-gray-700 hover:bg-teal-50 hover:text-teal-700 transition-all group"
                                                >
                                                    <div className="w-9 h-9 rounded-xl bg-gray-100 group-hover:bg-teal-100 flex items-center justify-center mr-3 transition-colors">
                                                        <Shield className="h-4 w-4 text-gray-600 group-hover:text-teal-600 transition-colors" />
                                                    </div>
                                                    <div className="flex-1">
                                                        <p className="font-semibold">Activity Log</p>
                                                        <p className="text-xs text-gray-500">View audit trail</p>
                                                    </div>
                                                </Link>
                                            </div>

                                            {/* Divider */}
                                            <div className="border-t border-gray-100"></div>

                                            {/* Logout */}
                                            <div className="p-2">
                                                <button
                                                    onClick={() => {
                                                        setShowUserMenu(false);
                                                        alert('Logout functionality - Ready for backend integration');
                                                    }}
                                                    className="w-full flex items-center px-4 py-3 text-sm text-red-600 hover:bg-red-50 transition-all rounded-xl group"
                                                >
                                                    <div className="w-9 h-9 rounded-xl bg-red-50 group-hover:bg-red-100 flex items-center justify-center mr-3 transition-colors">
                                                        <LogOut className="h-4 w-4 text-red-600" />
                                                    </div>
                                                    <div className="flex-1 text-left">
                                                        <p className="font-semibold">Sign Out</p>
                                                        <p className="text-xs text-gray-500">End your session</p>
                                                    </div>
                                                </button>
                                            </div>
                                        </div>
                                    </>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Page content */}
                <main className="flex-1" id="main-content" role="main">
                    <div className="py-6">
                        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                            {children}
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
}
