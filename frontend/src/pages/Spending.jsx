import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';

const API_BASE = 'http://localhost:5000/api';
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d', '#ffc658'];

const Spending = ({ user }) => {
    const [data, setData] = useState({
        transactions: [],
        analysis: { spending: {}, cashflow: [] },
        loading: true
    });
    const [duration, setDuration] = useState('30'); // Default 1 Month (30 days)

    useEffect(() => {
        if (user) {
            fetchData();
        }
    }, [user, duration]);

    const fetchData = async () => {
        try {
            console.log("Fetching spending data with duration:", duration);
            const token = await user.getIdToken();
            const headers = { Authorization: `Bearer ${token}` };

            const [txRes, analysisRes] = await Promise.all([
                axios.get(`${API_BASE}/transactions?duration=${duration}`, { headers }),
                axios.get(`${API_BASE}/analysis?duration=${duration}`, { headers })
            ]);

            setData({
                transactions: txRes.data,
                analysis: analysisRes.data,
                loading: false
            });
        } catch (error) {
            console.error("Error fetching spending data:", error);
            setData(prev => ({ ...prev, loading: false }));
        }
    };

    if (data.loading) return <div className="text-center py-10">Loading Spending Data...</div>;

    // Prepare Pie Chart Data
    const spendingData = data.analysis.spending || {};
    const pieChartData = Object.keys(spendingData).map(key => ({
        name: key,
        value: Math.abs(spendingData[key])
    })).filter(item => item.value > 0);

    const totalSpending = pieChartData.reduce((acc, curr) => acc + curr.value, 0);

    // Prepare Bar Chart Data
    const barChartData = data.analysis.cashflow || [];

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-gray-800">Spending Analysis</h1>

                {/* Duration Filter */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-1 flex space-x-1">
                    {['30', '90', '180', '365', 'ALL'].map((d) => (
                        <button
                            key={d}
                            onClick={() => setDuration(d)}
                            className={`px-3 py-1 text-sm rounded-md transition-colors ${duration === d
                                    ? 'bg-blue-100 text-blue-700 font-medium'
                                    : 'text-gray-500 hover:bg-gray-50'
                                }`}
                        >
                            {d === '30' ? '1M' :
                                d === '90' ? '3M' :
                                    d === '180' ? '6M' :
                                        d === '365' ? '1Y' : 'ALL'}
                        </button>
                    ))}
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Pie Chart */}
                <div className="card p-6">
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-lg font-bold text-gray-800">Spending by Category</h2>
                        <span className="text-lg font-bold text-blue-600">
                            ${totalSpending.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </span>
                    </div>
                    <div className="h-80">
                        {pieChartData.length > 0 ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={pieChartData}
                                        cx="50%"
                                        cy="50%"
                                        labelLine={false}
                                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                                        outerRadius={100}
                                        fill="#8884d8"
                                        dataKey="value"
                                    >
                                        {pieChartData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
                                    <Legend />
                                </PieChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="flex items-center justify-center h-full text-gray-400">
                                No spending data for this period
                            </div>
                        )}
                    </div>
                </div>

                {/* Bar Chart */}
                <div className="card p-6">
                    <h2 className="text-lg font-bold text-gray-800 mb-4">Monthly Cashflow</h2>
                    <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={barChartData}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                <XAxis dataKey="month" />
                                <YAxis />
                                <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
                                <Legend />
                                <Bar dataKey="income" name="Income" fill="#10B981" radius={[4, 4, 0, 0]} />
                                <Bar dataKey="expense" name="Expenses" fill="#EF4444" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Transactions Table */}
            <div className="card overflow-hidden">
                <div className="p-6 border-b border-gray-100">
                    <h2 className="text-lg font-bold text-gray-800">Recent Transactions</h2>
                </div>
                <div className="overflow-x-auto">
                    <table className="min-w-full text-left">
                        <thead>
                            <tr className="bg-gray-50 border-b border-gray-200">
                                <th className="px-6 py-3 font-semibold text-xs text-gray-500 uppercase tracking-wider">Date</th>
                                <th className="px-6 py-3 font-semibold text-xs text-gray-500 uppercase tracking-wider">Description</th>
                                <th className="px-6 py-3 font-semibold text-xs text-gray-500 uppercase tracking-wider">Category</th>
                                <th className="px-6 py-3 font-semibold text-xs text-gray-500 uppercase tracking-wider text-right">Amount</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {data.transactions.slice(0, 10).map((t, index) => (
                                <tr key={t.id} className={`hover:bg-blue-50 transition-colors ${index % 2 === 0 ? 'bg-white' : 'bg-gray-50/50'}`}>
                                    <td className="px-6 py-4 text-sm text-gray-600 whitespace-nowrap">{t.date}</td>
                                    <td className="px-6 py-4 text-sm text-gray-800 font-medium">
                                        {t.merchant_clean || t.vendor || t.description}
                                        {t.merchant_clean && t.merchant_clean !== t.description && (
                                            <span className="block text-xs text-gray-400 font-normal">{t.description}</span>
                                        )}
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className="px-2.5 py-0.5 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
                                            {t.category}
                                        </span>
                                    </td>
                                    <td className={`px-6 py-4 text-right text-sm font-bold ${t.amount < 0 ? 'text-red-500' : 'text-emerald-600'}`}>
                                        ${Math.abs(t.amount).toFixed(2)}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default Spending;
