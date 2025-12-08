import React, { useState, useEffect } from 'react';
import axios from 'axios';
import InsightCard from '../components/InsightCard';
import { Shield, TrendingUp, AlertTriangle } from 'lucide-react';

const API_BASE = 'http://localhost:5000/api';

const Recommendations = ({ user }) => {
    const [insights, setInsights] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (user) {
            fetchData();
        }
    }, [user]);

    const fetchData = async () => {
        try {
            const token = await user.getIdToken();
            const headers = { Authorization: `Bearer ${token}` };

            const res = await axios.get(`${API_BASE}/insights`, { headers });
            setInsights(res.data);
            setLoading(false);
        } catch (error) {
            console.error("Error fetching insights:", error);
            setLoading(false);
        }
    };

    if (loading) return <div className="text-center py-10">Loading Insights...</div>;

    return (
        <div className="space-y-8 animate-fade-in max-w-4xl mx-auto">
            <div className="flex justify-between items-end border-b pb-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-800">AI Financial Insights</h1>
                    <p className="text-gray-500 mt-1">Actionable advice to optimize your financial health.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 gap-6">
                {insights.length > 0 ? (
                    insights.map((insight, index) => (
                        <InsightCard key={index} data={insight} />
                    ))
                ) : (
                    <div className="text-center py-10 bg-gray-50 rounded-lg border border-gray-100">
                        <Shield className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                        <p className="text-gray-500 font-medium">No insights available at the moment.</p>
                        <p className="text-sm text-gray-400">Check back later as your transaction history grows.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Recommendations;
