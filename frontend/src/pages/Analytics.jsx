import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    PieChart, Pie, Cell
} from 'recharts';
import { TrendingUp, TrendingDown, Activity } from 'lucide-react';

const API_BASE = 'http://localhost:5000/api';
const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

const Analytics = ({ user }) => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (user) {
            fetchAnalytics();
        }
    }, [user]);

    const fetchAnalytics = async () => {
        try {
            const token = await user.getIdToken(true);
            const response = await axios.get(`${API_BASE}/analysis`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setData(response.data);
            setLoading(false);
        } catch (error) {
            console.error("Error fetching analytics:", error);
            setLoading(false);
        }
    };

    if (loading) return <div className="p-8 text-center text-gray-500">Loading analytics...</div>;
    if (!data) return <div className="p-8 text-center text-red-500">Failed to load data.</div>;

    // Prepare Pie Data
    const pieData = Object.keys(data.spending).map(key => ({
        name: key,
        value: Math.abs(data.spending[key])
    })).sort((a, b) => b.value - a.value);

    // Risk Gauge Color
    const getRiskColor = (score) => {
        if (score < 30) return 'text-green-600';
        if (score < 70) return 'text-yellow-600';
        return 'text-red-600';
    };

    return (
        <div className="p-8 max-w-7xl mx-auto space-y-8">
            <header>
                <h1 className="text-3xl font-bold text-gray-900">Analytics Hub</h1>
                <p className="text-gray-500">Deep dive into your financial health.</p>
            </header>

            {/* Top Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <div className="flex items-center space-x-3 mb-2">
                        <div className="p-2 bg-blue-100 rounded-lg">
                            <Activity className="h-6 w-6 text-blue-600" />
                        </div>
                        <span className="text-gray-500 font-medium">Risk Score</span>
                    </div>
                    <div className="flex items-end space-x-2">
                        <h2 className={`text-4xl font-bold ${getRiskColor(data.risk_score)}`}>{Math.round(data.risk_score)}</h2>
                        <span className="text-gray-400 mb-1">/ 100</span>
                    </div>
                    <p className="text-sm text-gray-500 mt-2">
                        {data.risk_score < 30 ? 'Conservative Profile' : data.risk_score < 70 ? 'Moderate Profile' : 'Aggressive Profile'}
                    </p>
                </div>

                {/* Placeholder for Net Worth or other stats */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 md:col-span-2 flex items-center justify-center text-gray-400">
                    More insights coming soon...
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Cashflow Chart */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <h3 className="font-bold text-gray-800 mb-6">Cashflow History (6 Months)</h3>
                    <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={data.cashflow}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                <XAxis dataKey="month" />
                                <YAxis />
                                <Tooltip />
                                <Legend />
                                <Line type="monotone" dataKey="income" stroke="#10B981" strokeWidth={2} name="Income" />
                                <Line type="monotone" dataKey="expense" stroke="#EF4444" strokeWidth={2} name="Expenses" />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Spending Donut */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <h3 className="font-bold text-gray-800 mb-6">Spending Breakdown</h3>
                    <div className="h-80 flex">
                        <div className="w-1/2">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={pieData}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={80}
                                        paddingAngle={5}
                                        dataKey="value"
                                    >
                                        {pieData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                        <div className="w-1/2 overflow-y-auto max-h-80 pl-4 space-y-3">
                            {pieData.map((entry, index) => (
                                <div key={index} className="flex items-center justify-between text-sm">
                                    <div className="flex items-center">
                                        <div className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: COLORS[index % COLORS.length] }}></div>
                                        <span className="text-gray-600 truncate max-w-[100px]">{entry.name}</span>
                                    </div>
                                    <span className="font-medium text-gray-900">${entry.value.toFixed(0)}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Analytics;
