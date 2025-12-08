import React from 'react';
import { AlertTriangle, TrendingUp, AlertCircle } from 'lucide-react';

const InsightCard = ({ data }) => {
    if (!data) return null;

    const { type, title, message, action } = data;

    const styles = {
        critical: {
            border: 'border-red-500',
            icon: <AlertCircle className="text-red-500" />,
            bg: 'bg-red-50',
            text: 'text-red-700',
            button: 'text-red-600 hover:text-red-700'
        },
        warning: {
            border: 'border-amber-400',
            icon: <AlertTriangle className="text-amber-500" />,
            bg: 'bg-amber-50',
            text: 'text-amber-700',
            button: 'text-amber-600 hover:text-amber-700'
        },
        opportunity: {
            border: 'border-emerald-500',
            icon: <TrendingUp className="text-emerald-500" />,
            bg: 'bg-emerald-50',
            text: 'text-emerald-700',
            button: 'text-emerald-600 hover:text-emerald-700'
        }
    };

    const style = styles[type] || styles.opportunity;

    return (
        <div className={`card relative border-l-4 p-4 ${style.border} ${style.bg} hover:shadow-md transition-shadow`}>
            <div className="flex items-center mb-2">
                <div className="mr-2">
                    {style.icon}
                </div>
                <h3 className={`font-bold ${style.text}`}>{title}</h3>
            </div>

            <p className="text-sm text-slate-600 mb-3">
                {message}
            </p>

            {action && (
                <div className="flex justify-end">
                    <button
                        onClick={() => console.log(`Action clicked: ${action}`)}
                        className={`text-xs font-medium ${style.button} hover:underline`}
                    >
                        {action} →
                    </button>
                </div>
            )}
        </div>
    );
};

export default InsightCard;
