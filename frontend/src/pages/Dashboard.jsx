import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, AreaChart, Area, XAxis, YAxis, CartesianGrid, BarChart, Bar, Legend } from 'recharts';
import Chatbox from '../components/Chatbox';
import InsightCard from '../components/InsightCard';
import { ArrowRight, Wallet, TrendingUp, Shield, Activity } from 'lucide-react';

const API_BASE = 'http://localhost:5000/api';
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#a855f7'];

const Dashboard = ({ user }) => {
    const navigate = useNavigate();
    const [dashboardData, setDashboardData] = useState({
        transactions: [],
        analysis: {},
        profile: null,
        nextBill: null,
        loading: true
    });
    const [insights, setInsights] = useState([]);
    const [chatLoading, setChatLoading] = useState(false);

    useEffect(() => {
        if (user) {
            fetchDashboardData();
        }
    }, [user]);

    const fetchDashboardData = async () => {
        try {
            const token = await user.getIdToken(true);
            const headers = { Authorization: `Bearer ${token}` };

            const [txRes, analysisRes, recRes, goalsRes, billsRes, profileRes] = await Promise.all([
                axios.get(`${API_BASE}/transactions`, { headers }),
                axios.get(`${API_BASE}/analysis`, { headers }),
                axios.get(`${API_BASE}/insights`, { headers }),
                axios.get(`${API_BASE}/goals`, { headers }),
                axios.get(`${API_BASE}/bills`, { headers }),
                axios.get(`${API_BASE}/profile`, { headers })
            ]);

            // Find the soonest upcoming bill
            const bills = billsRes.data;
            // Only show if due in <= 10 days
            const upcomingBills = bills.filter(b => !b.isPaid && (b.status === 'Due Soon' || b.status === 'Overdue' || (b.status === 'Upcoming' && b.daysRemaining <= 10)));
            upcomingBills.sort((a, b) => a.daysRemaining - b.daysRemaining);
            const nextBill = upcomingBills.length > 0 ? upcomingBills[0] : null;
            const activeGoal = goalsRes.data.length > 0 ? goalsRes.data[0] : null;

            setInsights(recRes.data);

            setDashboardData({
                transactions: txRes.data,
                analysis: analysisRes.data,
                profile: profileRes.data,
                nextBill: nextBill,
                activeGoal: activeGoal,
                loading: false
            });
        } catch (error) {
            console.error("Error fetching data:", error);
            setDashboardData(prev => ({ ...prev, loading: false }));
        }
    };



    const handleSendMessage = async (message) => {
        setChatLoading(true);
        try {
            const token = await user.getIdToken(true);
            const res = await axios.post(`${API_BASE}/chat`, { message }, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setChatLoading(false);
            return res.data.response;
        } catch (error) {
            console.error("Chat Error:", error);
            setChatLoading(false);
            if (error.response && error.response.status === 429) {
                return "You are chatting too fast. Please wait a moment.";
            }
            return "Sorry, I encountered an error processing your request.";
        }
    };

    // Prepare Pie Data
    const pieData = dashboardData.analysis.spending
        ? Object.keys(dashboardData.analysis.spending).map(key => ({
            name: key,
            value: Math.abs(dashboardData.analysis.spending[key])
        })).sort((a, b) => b.value - a.value).slice(0, 5)
        : [];

    if (dashboardData.loading) {
        return <div className="text-center py-10">Loading Dashboard...</div>;
    }

    // Empty State: Onboarding Card
    if (dashboardData.transactions.length === 0) {
        const handleFileUpload = async (event) => {
            const files = event.target.files;
            if (!files || files.length === 0) return;

            const formData = new FormData();
            for (let i = 0; i < files.length; i++) {
                formData.append('files', files[i]);
            }

            try {
                const token = await user.getIdToken(true);
                await axios.post(`${API_BASE}/upload-statements`, formData, {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'multipart/form-data'
                    }
                });
                window.location.reload();
            } catch (error) {
                console.error("Upload failed:", error);
                alert("Failed to upload statements. Please try again.");
            }
        };

        return (
            <div className="max-w-2xl mx-auto mt-10 p-8 bg-white rounded-2xl shadow-lg text-center">
                <div className="bg-blue-50 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
                    <Wallet className="h-10 w-10 text-blue-600" />
                </div>
                <h1 className="text-3xl font-bold text-gray-900 mb-4">Welcome to FinPersonalize!</h1>
                <p className="text-gray-600 text-lg mb-8">
                    We don't see any data yet. Please wait for your bank statements to sync or upload them manually to get started.
                </p>

                <input
                    type="file"
                    id="statement-upload"
                    multiple
                    accept=".pdf"
                    className="hidden"
                    onChange={handleFileUpload}
                />
                <button
                    onClick={() => document.getElementById('statement-upload').click()}
                    className="bg-blue-600 text-white px-8 py-3 rounded-xl font-semibold hover:bg-blue-700 transition-colors shadow-md hover:shadow-lg"
                >
                    Upload your statements
                </button>
            </div>
        );
    }

    const riskScore = dashboardData.profile?.risk_score || 50;
    const riskData = [
        { name: 'Score', value: riskScore },
        { name: 'Remaining', value: 100 - riskScore }
    ];
    const RISK_COLORS = ['#3B82F6', '#E5E7EB']; // Blue and Gray

    const cashflowData = dashboardData.analysis.cashflow || [
        { month: 'Jan', income: 3000, expense: 2500 },
        { month: 'Feb', income: 3200, expense: 2300 },
        { month: 'Mar', income: 2800, expense: 2600 },
        { month: 'Apr', income: 3500, expense: 2900 },
        { month: 'May', income: 3100, expense: 2400 },
        { month: 'Jun', income: 3800, expense: 3000 },
    ];

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="card flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-800">Welcome back, {dashboardData.profile?.email?.split('@')[0] || 'User'}</h1>
                    <div className="flex items-center mt-2 space-x-2">
                        <span className="bg-indigo-100 text-indigo-700 px-3 py-1 rounded-full text-sm font-semibold flex items-center">
                            <Shield className="w-4 h-4 mr-1" />
                            {dashboardData.profile?.persona || 'Financial Explorer'}
                        </span>
                        <span className="text-gray-500 text-sm">Financial DNA</span>
                    </div>
                </div>
                <div className="text-right hidden md:block">
                    <p className="text-sm text-gray-500">Current Risk Score</p>
                    <p className="text-3xl font-bold text-blue-600">{riskScore}/100</p>
                </div>
            </div>

            {/* New Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Spending by Category */}
                <div
                    className="card cursor-pointer hover:shadow-lg transition group"
                    onClick={() => navigate('/spending')}
                >
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="text-lg font-bold text-gray-800 group-hover:text-blue-600 transition-colors">Spending by Category</h3>
                        <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-blue-500" />
                    </div>
                    <div className="h-64">
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
                                <Legend layout="vertical" verticalAlign="middle" align="right" />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Income vs. Expense */}
                <div className="card">
                    <h3 className="text-lg font-bold text-gray-800 mb-4">Income vs. Expense</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={cashflowData}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                <XAxis dataKey="month" />
                                <YAxis />
                                <Tooltip />
                                <Legend />
                                <Bar dataKey="income" fill="#10b981" name="Income" />
                                <Bar dataKey="expense" fill="#3b82f6" name="Expense" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* AI Financial Insights Widget */}
                <div className="card h-full flex flex-col">
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-lg font-bold text-slate-800">✨ AI Insights</h2>
                        <button
                            onClick={() => navigate('/analysis')}
                            className="text-xs text-blue-600 font-medium hover:underline"
                        >
                            View Report →
                        </button>
                    </div>
                    <div className="flex-1 space-y-3">
                        {insights.length > 0 ? (
                            insights.map((insight, index) => (
                                <InsightCard key={index} data={insight} />
                            ))
                        ) : (
                            <div className="bg-gray-50 rounded-lg p-4 border border-gray-100">
                                <p className="text-gray-500 text-sm">No insights available yet.</p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Cashflow Trend */}
                <div className="card hover:border-blue-100 transition lg:col-span-2">
                    <h3 className="font-bold text-gray-800 mb-4 flex items-center">
                        <TrendingUp className="w-5 h-5 mr-2 text-green-500" />
                        Cashflow Trend (6 Months)
                    </h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={dashboardData.analysis.cashflow || []}>
                                <defs>
                                    <linearGradient id="colorIncome" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#10B981" stopOpacity={0.1} />
                                        <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                                    </linearGradient>
                                    <linearGradient id="colorExpense" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#EF4444" stopOpacity={0.1} />
                                        <stop offset="95%" stopColor="#EF4444" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                                <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: '#9CA3AF', fontSize: 12 }} />
                                <YAxis axisLine={false} tickLine={false} tick={{ fill: '#9CA3AF', fontSize: 12 }} />
                                <Tooltip
                                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                                />
                                <Area type="monotone" dataKey="income" stroke="#10B981" strokeWidth={2} fillOpacity={1} fill="url(#colorIncome)" name="Income" />
                                <Area type="monotone" dataKey="expense" stroke="#EF4444" strokeWidth={2} fillOpacity={1} fill="url(#colorExpense)" name="Expenses" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
            {/* Bill Alert */}
            {dashboardData.nextBill && dashboardData.nextBill.daysRemaining <= 7 && (
                <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4 rounded shadow-sm flex justify-between items-center" role="alert">
                    <div>
                        <p className="font-bold">Upcoming Bill Alert</p>
                        <p>{dashboardData.nextBill.name} is due in {dashboardData.nextBill.daysRemaining} days (${dashboardData.nextBill.amount.toFixed(2)})</p>
                    </div>
                    <button onClick={() => navigate('/bills')} className="text-sm font-semibold underline hover:text-red-800">Pay Now</button>
                </div>
            )}

            {/* Balance Card */}
            <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-xl p-6 text-white shadow-lg">
                <div className="flex items-center space-x-3 mb-2">
                    <Wallet className="h-6 w-6 text-blue-200" />
                    <span className="text-blue-100 font-medium">Total Balance</span>
                </div>
                <h1 className="text-4xl font-bold">
                    ${dashboardData.transactions.reduce((acc, t) => acc + t.amount, 0).toFixed(2)}
                </h1>
                <p className="text-blue-200 text-sm mt-2">Available for spending</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Spending Widget */}
                <div
                    onClick={() => navigate('/spending')}
                    className="card cursor-pointer hover:shadow-lg transition group"
                >
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="font-bold text-gray-800">Spending</h3>
                        <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-blue-500" />
                    </div>
                    <div className="h-40 relative">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={pieData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={40}
                                    outerRadius={60}
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
                        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                            <span className="text-xs text-gray-500 font-medium">Top Categories</span>
                        </div>
                    </div>
                    <button className="w-full mt-4 text-sm text-blue-600 font-medium hover:underline">
                        View Details
                    </button>
                </div>

                {/* Goals Widget */}
                <div
                    onClick={() => navigate('/goals')}
                    className="card cursor-pointer hover:shadow-lg transition group"
                >
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="font-bold text-gray-800">Active Goal</h3>
                        <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-blue-500" />
                    </div>
                    {dashboardData.activeGoal ? (
                        <div className="space-y-4">
                            <div>
                                <div className="flex justify-between text-sm mb-1">
                                    <span className="font-medium">{dashboardData.activeGoal.name}</span>
                                    <span className="text-gray-500">${dashboardData.activeGoal.current_amount} / ${dashboardData.activeGoal.target_amount}</span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2.5">
                                    <div
                                        className="bg-green-500 h-2.5 rounded-full"
                                        style={{ width: `${Math.min((dashboardData.activeGoal.current_amount / dashboardData.activeGoal.target_amount) * 100, 100)}%` }}
                                    ></div>
                                </div>
                            </div>
                            <p className="text-sm text-gray-500">
                                {dashboardData.activeGoal.target_date
                                    ? `Target Date: ${dashboardData.activeGoal.target_date}`
                                    : 'Keep saving!'}
                            </p>
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center h-40 text-gray-500">
                            <p>No active goals.</p>
                            <span className="text-sm text-blue-500 mt-2">Click to add one</span>
                        </div>
                    )}
                </div>

                {/* Bills Widget */}
                <div
                    onClick={() => navigate('/bills')}
                    className="card cursor-pointer hover:shadow-lg transition group"
                >
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="font-bold text-gray-800">Upcoming Bill</h3>
                        <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-blue-500" />
                    </div>
                    {dashboardData.nextBill ? (
                        <div className="bg-red-50 rounded-lg p-4 border border-red-100">
                            <p className="text-sm text-red-800 font-medium">Next Bill Due</p>
                            <h4 className="text-lg font-bold text-red-900 mt-1">{dashboardData.nextBill.name}</h4>
                            <p className="text-red-700 font-medium">${dashboardData.nextBill.amount.toFixed(2)}</p>
                            <p className="text-xs text-red-600 mt-2">
                                {dashboardData.nextBill.daysRemaining < 0
                                    ? `Overdue by ${Math.abs(dashboardData.nextBill.daysRemaining)} days`
                                    : `Due in ${dashboardData.nextBill.daysRemaining} days`}
                            </p>
                        </div>
                    ) : (
                        <div className="bg-gray-50 rounded-lg p-4 border border-gray-100">
                            <p className="text-gray-500 text-sm">No upcoming bills found.</p>
                        </div>
                    )}
                </div>

            </div>

            {/* Chatbox */}
            <div className="card overflow-hidden p-0">
                <div className="p-4 border-b">
                    <h3 className="font-bold text-gray-800">AI Financial Assistant</h3>
                </div>
                <div className="p-4">
                    <Chatbox onSendMessage={handleSendMessage} isLoading={chatLoading} />
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
