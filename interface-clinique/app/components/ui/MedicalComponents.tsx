'use client';

import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MedicalCardProps {
    children: React.ReactNode;
    className?: string;
    hover?: boolean;
    gradient?: boolean;
}

export function MedicalCard({ children, className = '', hover = false, gradient = false }: MedicalCardProps) {
    const baseClasses = gradient
        ? 'gradient-teal-light'
        : 'medical-card';
    const hoverClasses = hover ? 'medical-card-hover' : '';

    return (
        <div className={`${baseClasses} ${hoverClasses} ${className}`}>
            {children}
        </div>
    );
}

interface ProgressModuleProps {
    icon: LucideIcon;
    value: string | number;
    label: string;
    subtitle?: string;
    color?: 'teal' | 'orange' | 'green' | 'blue';
    percentage?: number;
}

export function ProgressModule({
    icon: Icon,
    value,
    label,
    subtitle,
    color = 'teal',
    percentage
}: ProgressModuleProps) {
    const colorClasses = {
        teal: 'bg-teal-500 text-white',
        orange: 'bg-orange-400 text-white',
        green: 'bg-green-500 text-white',
        blue: 'bg-blue-500 text-white'
    };

    const bgColorClasses = {
        teal: 'bg-teal-50',
        orange: 'bg-orange-50',
        green: 'bg-green-50',
        blue: 'bg-blue-50'
    };

    return (
        <div className={`progress-module ${bgColorClasses[color]} animate-scale-in`}>
            <div className="relative z-10">
                {/* Icon */}
                <div className={`w-14 h-14 ${colorClasses[color]} rounded-2xl flex items-center justify-center mb-4 shadow-sm`}>
                    <Icon className="h-7 w-7" />
                </div>

                {/* Value */}
                <div className="text-4xl font-bold text-gray-900 mb-2">
                    {value}
                </div>

                {/* Label */}
                <div className="text-sm font-medium text-gray-700 mb-1">
                    {label}
                </div>

                {/* Subtitle */}
                {subtitle && (
                    <div className="text-xs text-gray-500">
                        {subtitle}
                    </div>
                )}

                {/* Percentage Indicator */}
                {percentage !== undefined && (
                    <div className="mt-3">
                        <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                            <span>{percentage}% Done</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-1.5">
                            <div
                                className={`h-1.5 rounded-full ${colorClasses[color].split(' ')[0]}`}
                                style={{ width: `${percentage}%` }}
                            />
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

interface IconButtonProps {
    icon: LucideIcon;
    label: string;
    description?: string;
    onClick?: () => void;
    color?: 'teal' | 'orange' | 'green' | 'blue';
    size?: 'sm' | 'md' | 'lg';
}

export function IconButton({
    icon: Icon,
    label,
    description,
    onClick,
    color = 'teal',
    size = 'md'
}: IconButtonProps) {
    const colorClasses = {
        teal: 'bg-teal-500 text-white hover:bg-teal-600',
        orange: 'bg-orange-400 text-white hover:bg-orange-500',
        green: 'bg-green-500 text-white hover:bg-green-600',
        blue: 'bg-blue-500 text-white hover:bg-blue-600'
    };

    const sizeClasses = {
        sm: 'w-12 h-12',
        md: 'w-16 h-16',
        lg: 'w-20 h-20'
    };

    const iconSizes = {
        sm: 'h-5 w-5',
        md: 'h-7 w-7',
        lg: 'h-9 w-9'
    };

    return (
        <button
            onClick={onClick}
            className="medical-card-hover p-4 text-center smooth-transition group"
        >
            <div className={`${sizeClasses[size]} ${colorClasses[color]} rounded-2xl flex items-center justify-center mx-auto mb-3 shadow-sm group-hover:shadow-md smooth-transition`}>
                <Icon className={iconSizes[size]} />
            </div>
            <div className="text-sm font-semibold text-gray-900 mb-1">
                {label}
            </div>
            {description && (
                <div className="text-xs text-gray-500">
                    {description}
                </div>
            )}
        </button>
    );
}

interface AppointmentCardProps {
    doctorName: string;
    specialty: string;
    date: string;
    time: string;
    icon: LucideIcon;
    color?: 'teal' | 'orange' | 'green' | 'blue';
}

export function AppointmentCard({
    doctorName,
    specialty,
    date,
    time,
    icon: Icon,
    color = 'teal'
}: AppointmentCardProps) {
    const colorClasses = {
        teal: 'bg-teal-500 text-white',
        orange: 'bg-orange-400 text-white',
        green: 'bg-green-500 text-white',
        blue: 'bg-blue-500 text-white'
    };

    return (
        <div className="medical-card-hover p-4 gradient-teal">
            <div className="flex items-start space-x-3">
                <div className={`w-12 h-12 ${colorClasses[color]} rounded-xl flex items-center justify-center flex-shrink-0`}>
                    <Icon className="h-6 w-6" />
                </div>
                <div className="flex-1 min-w-0">
                    <h3 className="text-base font-bold text-gray-900 mb-0.5">
                        {doctorName}
                    </h3>
                    <p className="text-sm text-gray-600 mb-2">
                        {specialty}
                    </p>
                    <div className="flex items-center space-x-3 text-xs text-gray-700">
                        <span className="flex items-center">
                            📅 {date}
                        </span>
                        <span className="flex items-center">
                            🕐 {time}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    );
}
