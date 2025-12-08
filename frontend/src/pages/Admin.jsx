import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ShieldCheck, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

const API_BASE = 'http://localhost:5000/api';

const Admin = () => {
    const [auditData, setAuditData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        runAudit();
    }, []);

    const runAudit = async () => {
        setLoading(true);
        try {
            const res = await axios.get(`${API_BASE}/audit`);
            setAuditData(res.data);
            setLoading(false);
        } catch (error) {
            console.error("Audit failed:", error);
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center h-full space-y-4">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                <p className="text-gray-600 font-medium">Running Red Team Audit...</p>
                <p className="text-sm text-gray-400">Testing Safety, PII, and Accuracy</p>
            </div>
        );
    }

    if (!auditData) return <div>Error loading audit data.</div>;

    const scoreColor = auditData.safety_score === 100 ? '#10B981' : '#F59E0B';
    const pieData = [
        { name: 'Safe', value: auditData.safety_score },
        { name: 'Risk', value: 100 - auditData.safety_score }
    ];

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-gray-800 flex items-center">
                    <ShieldCheck className="mr-2 text-blue-600" />
                    System Security Audit
                </h1>
                <button
                    onClick={runAudit}
                    className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
                >
                    Re-Run Audit
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Safety Score Card */}
                <div className="bg-white p-6 rounded-lg shadow-md flex flex-col items-center justify-center">
                    <h3 className="text-lg font-semibold text-gray-700 mb-4">Safety Score</h3>
                    <div className="h-40 w-full relative">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={pieData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={80}
                                    startAngle={90}
                                    endAngle={-270}
                                    dataKey="value"
                                >
                                    <Cell fill={scoreColor} />
                                    <Cell fill="#E5E7EB" />
                                </Pie>
                            </PieChart>
                        </ResponsiveContainer>
                        <div className="absolute inset-0 flex items-center justify-center">
                            <span className="text-3xl font-bold" style={{ color: scoreColor }}>
                                {auditData.safety_score}%
                            </span>
                        </div>
                    </div>
                </div>

                {/* Metrics Cards */}
                <div className="bg-white p-6 rounded-lg shadow-md flex flex-col justify-center space-y-4">
                    <div className="flex justify-between items-center p-3 bg-green-50 rounded">
                        <div>
                            <p className="text-sm text-green-800 font-medium">Tests Passed</p>
                            <p className="text-2xl font-bold text-green-900">{auditData.passed}/{auditData.total_tests}</p>
                        </div>
                        <CheckCircle className="text-green-500 h-8 w-8" />
                    </div>
                    <div className="flex justify-between items-center p-3 bg-red-50 rounded">
                        <div>
                            <p className="text-sm text-red-800 font-medium">Tests Failed</p>
                            <p className="text-2xl font-bold text-red-900">{auditData.failed}</p>
                        </div>
                        <XCircle className="text-red-500 h-8 w-8" />
                    </div>
                </div>

                {/* Summary Text */}
                <div className="bg-white p-6 rounded-lg shadow-md">
                    <h3 className="text-lg font-semibold text-gray-700 mb-2">Audit Summary</h3>
                    <p className="text-gray-600 text-sm">
                        The Red Team Audit tests the AI against adversarial attacks, PII injection attempts, and hallucination triggers.
                    </p>
                    <div className="mt-4 space-y-2">
                        <div className="flex items-center text-sm text-gray-600">
                            <ShieldCheck className="h-4 w-4 mr-2 text-green-500" />
                            <span>PII Scrubbing Active</span>
                        </div>
                        <div className="flex items-center text-sm text-gray-600">
                            <ShieldCheck className="h-4 w-4 mr-2 text-green-500" />
                            <span>Refusal Logic Active</span>
                        </div>
                        <div className="flex items-center text-sm text-gray-600">
                            <ShieldCheck className="h-4 w-4 mr-2 text-green-500" />
                            <span>Fact Checking Active</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Audit Log Table */}
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200">
                    <h3 className="text-lg font-bold text-gray-800">Red Team Audit Log</h3>
                </div>
                <div className="overflow-x-auto">
                    <table className="min-w-full text-left">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Question</th>
                                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">AI Response</th>
                                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {auditData.audit_log.map((log, idx) => (
                                <tr key={idx} className="hover:bg-gray-50">
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                        {log.type}
                                    </td>
                                    <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate" title={log.question}>
                                        {log.question}
                                    </td>
                                    <td className="px-6 py-4 text-sm text-gray-500 max-w-md truncate" title={log.response}>
                                        {log.response}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${log.status === 'PASS' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                            }`}>
                                            {log.status}
                                        </span>
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

export default Admin;
