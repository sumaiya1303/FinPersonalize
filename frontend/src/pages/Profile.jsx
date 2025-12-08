import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { User, Shield, TrendingUp, RefreshCw, DollarSign, Calendar } from 'lucide-react';

const API_BASE = 'http://localhost:5000/api';

const Profile = ({ user }) => {
    const navigate = useNavigate();
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [isEditing, setIsEditing] = useState(false);
    const [editData, setEditData] = useState({ age: '', income: '' });

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const token = await user.getIdToken();
                const response = await axios.get(`${API_BASE}/profile`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setProfile(response.data);
                setEditData({
                    age: response.data.age || '',
                    income: response.data.income || ''
                });
            } catch (error) {
                console.error("Error fetching profile:", error);
            } finally {
                setLoading(false);
            }
        };

        if (user) {
            fetchProfile();
        }
    }, [user]);

    const handleSave = async () => {
        try {
            const token = await user.getIdToken();
            await axios.put(`${API_BASE}/profile`, {
                age: editData.age,
                income: editData.income
            }, {
                headers: { Authorization: `Bearer ${token}` }
            });

            // Refresh local data
            setProfile(prev => ({
                ...prev,
                age: editData.age,
                income: editData.income,
                // Optimistically update income level (or refetch)
            }));
            setIsEditing(false);
            alert("Profile updated successfully!");
        } catch (error) {
            console.error("Error updating profile:", error);
            alert("Failed to update profile.");
        }
    };

    if (loading) return <div className="p-8 text-center">Loading profile...</div>;
    if (!profile) return <div className="p-8 text-center">Failed to load profile.</div>;

    return (
        <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
            {/* Header */}
            <div className="flex items-center space-x-4 mb-8">
                <div className="h-16 w-16 rounded-full bg-gradient-to-tr from-blue-500 to-purple-600 flex items-center justify-center shadow-lg">
                    <span className="text-2xl font-bold text-white">{profile.email[0].toUpperCase()}</span>
                </div>
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Your Financial Profile</h1>
                    <p className="text-gray-500">{profile.email}</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Persona Card */}
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 col-span-1 md:col-span-2">
                    <div className="flex justify-between items-start mb-4">
                        <div className="flex items-center space-x-3">
                            <div className="p-2 bg-blue-50 rounded-lg">
                                <Shield className="h-6 w-6 text-blue-600" />
                            </div>
                            <h2 className="text-xl font-bold text-gray-800">Financial Persona</h2>
                        </div>
                        <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
                            {profile.persona}
                        </span>
                    </div>

                    <div className="mt-6">
                        <div className="flex justify-between items-end mb-2">
                            <span className="text-gray-600 font-medium">Risk Score</span>
                            <span className="text-2xl font-bold text-gray-900">{profile.risk_score}<span className="text-sm text-gray-400 font-normal">/100</span></span>
                        </div>
                        <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
                            <div
                                className={`h-full rounded-full transition-all duration-1000 ${profile.risk_score < 40 ? 'bg-green-500' :
                                        profile.risk_score < 70 ? 'bg-yellow-500' : 'bg-red-500'
                                    }`}
                                style={{ width: `${profile.risk_score}%` }}
                            ></div>
                        </div>
                        <p className="text-sm text-gray-500 mt-3">
                            Your risk score indicates a <strong>{profile.risk_score < 40 ? 'Conservative' : profile.risk_score < 70 ? 'Balanced' : 'Aggressive'}</strong> investment style.
                        </p>
                    </div>
                </div>

                {/* Demographics Card */}
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                    <div className="flex justify-between items-center mb-6">
                        <div className="flex items-center space-x-3">
                            <div className="p-2 bg-green-50 rounded-lg">
                                <User className="h-6 w-6 text-green-600" />
                            </div>
                            <h2 className="text-xl font-bold text-gray-800">Demographics</h2>
                        </div>
                        {!isEditing ? (
                            <button
                                onClick={() => setIsEditing(true)}
                                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                            >
                                Edit
                            </button>
                        ) : (
                            <div className="flex space-x-2">
                                <button
                                    onClick={handleSave}
                                    className="text-sm text-green-600 hover:text-green-700 font-medium"
                                >
                                    Save
                                </button>
                                <button
                                    onClick={() => setIsEditing(false)}
                                    className="text-sm text-gray-500 hover:text-gray-600 font-medium"
                                >
                                    Cancel
                                </button>
                            </div>
                        )}
                    </div>

                    <div className="space-y-4">
                        <div className="flex justify-between items-center p-3 bg-gray-50 rounded-xl">
                            <div className="flex items-center space-x-3">
                                <Calendar className="h-5 w-5 text-gray-400" />
                                <span className="text-gray-600">Age</span>
                            </div>
                            {isEditing ? (
                                <input
                                    type="number"
                                    value={editData.age}
                                    onChange={(e) => setEditData({ ...editData, age: e.target.value })}
                                    className="w-20 p-1 border rounded text-right"
                                />
                            ) : (
                                <span className="font-semibold text-gray-900">{profile.age || 'N/A'}</span>
                            )}
                        </div>
                        <div className="flex justify-between items-center p-3 bg-gray-50 rounded-xl">
                            <div className="flex items-center space-x-3">
                                <DollarSign className="h-5 w-5 text-gray-400" />
                                <span className="text-gray-600">Annual Income</span>
                            </div>
                            {isEditing ? (
                                <input
                                    type="number"
                                    value={editData.income}
                                    onChange={(e) => setEditData({ ...editData, income: e.target.value })}
                                    className="w-32 p-1 border rounded text-right"
                                />
                            ) : (
                                <span className="font-semibold text-gray-900">
                                    {profile.income ? `$${Number(profile.income).toLocaleString()}` : 'N/A'}
                                </span>
                            )}
                        </div>
                        <div className="flex justify-between items-center p-3 bg-gray-50 rounded-xl">
                            <div className="flex items-center space-x-3">
                                <TrendingUp className="h-5 w-5 text-gray-400" />
                                <span className="text-gray-600">Income Level</span>
                            </div>
                            <span className="font-semibold text-gray-900">{profile.income_level || 'N/A'}</span>
                        </div>
                    </div>
                </div>

                {/* Quiz Data Card */}
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                    <div className="flex items-center space-x-3 mb-6">
                        <div className="p-2 bg-purple-50 rounded-lg">
                            <RefreshCw className="h-6 w-6 text-purple-600" />
                        </div>
                        <h2 className="text-xl font-bold text-gray-800">Quiz Data</h2>
                    </div>

                    <div className="space-y-3">
                        {Object.entries(profile.quiz_data || {}).map(([key, value]) => (
                            <div key={key} className="flex justify-between items-center text-sm border-b border-gray-100 pb-2 last:border-0">
                                <span className="text-gray-500 capitalize">{key.replace('_', ' ')}</span>
                                <span className="font-medium text-gray-900">{value} pts</span>
                            </div>
                        ))}
                        {(!profile.quiz_data || Object.keys(profile.quiz_data).length === 0) && (
                            <p className="text-gray-400 italic text-sm">No quiz data available.</p>
                        )}
                    </div>

                    <button
                        onClick={() => navigate('/onboarding')}
                        className="w-full mt-6 flex items-center justify-center px-4 py-2 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition"
                    >
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Retake Assessment
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Profile;
