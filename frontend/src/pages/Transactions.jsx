import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Filter, Search, ArrowDown, ArrowUp, Upload } from 'lucide-react';

const API_BASE = 'http://localhost:5000/api';

const Transactions = ({ user }) => {
    const [transactions, setTransactions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filters, setFilters] = useState({
        category: 'All',
        startDate: '',
        endDate: ''
    });

    useEffect(() => {
        if (user) {
            fetchTransactions();
        }
    }, [user, filters]);

    const fetchTransactions = async () => {
        try {
            const token = await user.getIdToken(true);
            const params = {};
            if (filters.category !== 'All') params.category = filters.category;
            if (filters.startDate) params.start_date = filters.startDate;
            if (filters.endDate) params.end_date = filters.endDate;

            const response = await axios.get(`${API_BASE}/transactions`, {
                headers: { Authorization: `Bearer ${token}` },
                params: params
            });
            setTransactions(response.data);
            setLoading(false);
        } catch (error) {
            console.error("Error fetching transactions:", error);
            setLoading(false);
        }
    };

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
            // Refresh transactions after upload
            fetchTransactions();
            alert("Statements uploaded successfully!");
        } catch (error) {
            console.error("Upload failed:", error);
            alert("Failed to upload statements. Please try again.");
        }
    };

    const handleFilterChange = (e) => {
        const { name, value } = e.target;
        setFilters(prev => ({ ...prev, [name]: value }));
    };

    const categories = ['All', 'Food', 'Transport', 'Utilities', 'Entertainment', 'Shopping', 'Health', 'Income', 'Savings', 'Investment'];

    return (
        <div className="max-w-7xl mx-auto">
            <div className="card space-y-6">
                <header className="flex justify-between items-center">
                    <div>
                        <h1 className="text-3xl font-bold text-[#111827]">Transactions</h1>
                        <p className="text-gray-500">View and filter your financial history.</p>
                    </div>
                    <div>
                        <input
                            type="file"
                            id="tx-upload"
                            multiple
                            accept=".pdf"
                            className="hidden"
                            onChange={handleFileUpload}
                        />
                        <button
                            onClick={() => document.getElementById('tx-upload').click()}
                            className="flex items-center bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition shadow-sm"
                        >
                            <Upload className="h-5 w-5 mr-2" />
                            Upload Statements
                        </button>
                    </div>
                </header>

                {/* Filters */}
                <div className="flex flex-wrap gap-4 items-end border-b border-gray-100 pb-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                        <div className="relative">
                            <select
                                name="category"
                                value={filters.category}
                                onChange={handleFilterChange}
                                className="pl-3 pr-10 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 appearance-none bg-white"
                            >
                                {categories.map(cat => (
                                    <option key={cat} value={cat}>{cat}</option>
                                ))}
                            </select>
                            <Filter className="absolute right-3 top-2.5 h-4 w-4 text-gray-400 pointer-events-none" />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                        <input
                            type="date"
                            name="startDate"
                            value={filters.startDate}
                            onChange={handleFilterChange}
                            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                        <input
                            type="date"
                            name="endDate"
                            value={filters.endDate}
                            onChange={handleFilterChange}
                            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                        />
                    </div>

                    <button
                        onClick={() => setFilters({ category: 'All', startDate: '', endDate: '' })}
                        className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 font-medium"
                    >
                        Clear Filters
                    </button>
                </div>

                {/* Table */}
                <div className="overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Merchant</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {loading ? (
                                    <tr>
                                        <td colSpan="4" className="px-6 py-10 text-center text-gray-500">Loading transactions...</td>
                                    </tr>
                                ) : transactions.length === 0 ? (
                                    <tr>
                                        <td colSpan="4" className="px-6 py-10 text-center text-gray-500">No transactions found.</td>
                                    </tr>
                                ) : (
                                    transactions.map((tx) => (
                                        <tr key={tx.id} className="hover:bg-gray-50 transition">
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{tx.date}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                                {tx.merchant_clean || tx.description}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm">
                                                <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                                                    {tx.category}
                                                </span>
                                            </td>
                                            <td className={`px-6 py-4 whitespace-nowrap text-sm text-right font-medium ${tx.amount > 0 ? 'text-green-600' : 'text-gray-900'}`}>
                                                {tx.amount > 0 ? '+' : ''}{tx.amount.toFixed(2)}
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Transactions;
