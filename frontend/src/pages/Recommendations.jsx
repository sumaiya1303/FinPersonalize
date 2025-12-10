import React, { useState, useEffect } from 'react';
import axios from 'axios';
import InsightCard from '../components/InsightCard';
import RecommendationCard from '../components/RecommendationCard';
import { Shield, TrendingUp, AlertTriangle } from 'lucide-react';

const API_BASE = 'http://localhost:5000/api';

const Recommendations = ({ user }) => {
    const [insights, setInsights] = useState([]);
    const [products, setProducts] = useState([]);
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

            const [insightsRes, productsRes] = await Promise.all([
                axios.get(`${API_BASE}/insights`, { headers }),
                axios.get(`${API_BASE}/recommend`, { headers })
            ]);

            setInsights(insightsRes.data);
            setProducts(productsRes.data);
            setLoading(false);
        } catch (error) {
            console.error("Error fetching data:", error);
            setLoading(false);
        }
    };

    if (loading) return <div className="text-center py-10">Loading AI Recommendations...</div>;

    return (
        <div className="space-y-12 animate-fade-in max-w-5xl mx-auto pb-10">
            {/* Header */}
            <div className="border-b pb-6">
                <h1 className="text-3xl font-bold text-gray-900">AI Financial Advisor</h1>
                <p className="text-gray-600 mt-2 text-lg">Personalized strategies to optimize your financial health.</p>
            </div>

            {/* Section 1: Financial Health Insights */}
            <section>
                <div className="flex items-center space-x-2 mb-6">
                    <div className="p-2 bg-indigo-100 rounded-lg">
                        <Shield className="h-6 w-6 text-indigo-600" />
                    </div>
                    <h2 className="text-2xl font-bold text-gray-800">Health Insights</h2>
                </div>

                <div className="grid grid-cols-1 gap-6">
                    {insights.length > 0 ? (
                        insights.map((insight, index) => (
                            <InsightCard key={index} data={insight} />
                        ))
                    ) : (
                        <div className="bg-gray-50 rounded-xl p-8 text-center border border-gray-100">
                            <p className="text-gray-500">No specific insights at the moment. You're doing great!</p>
                        </div>
                    )}
                </div>
            </section>

            {/* Section 2: Product Recommendations (SVD) */}
            <section>
                <div className="flex items-center space-x-2 mb-6">
                    <div className="p-2 bg-blue-100 rounded-lg">
                        <TrendingUp className="h-6 w-6 text-blue-600" />
                    </div>
                    <h2 className="text-2xl font-bold text-gray-800">Recommended Products</h2>
                </div>
                <p className="text-gray-500 mb-6 -mt-4 ml-12">Curated financial tools matching your risk profile and spending habits.</p>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {products.length > 0 ? (
                        products.map((product, index) => (
                            <div key={index} className="h-full">
                                {/* Import RecommendationCard if not already imported at top, assuming it is or I need to check imports */}
                                <RecommendationCard product={product} />
                            </div>
                        ))
                    ) : (
                        <div className="col-span-full bg-gray-50 rounded-xl p-8 text-center border border-gray-100">
                            <p className="text-gray-500">No product recommendations available yet.</p>
                        </div>
                    )}
                </div>
            </section>
        </div>
    );
};

export default Recommendations;
