import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Plus, Target, TrendingUp, Calendar } from 'lucide-react';

const API_BASE = 'http://localhost:5000/api';

const Goals = ({ user }) => {
    const [goals, setGoals] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        target_amount: '',
        current_amount: '',
        monthly_contribution: '',
        target_date: ''
    });
    const [analysisResult, setAnalysisResult] = useState(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [editingGoal, setEditingGoal] = useState(null);

    useEffect(() => {
        if (user) {
            fetchGoals();
        }
    }, [user]);

    const fetchGoals = async () => {
        try {
            const token = await user.getIdToken();
            const res = await axios.get(`${API_BASE}/goals`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setGoals(res.data);
            setLoading(false);
        } catch (error) {
            console.error("Error fetching goals:", error);
            setLoading(false);
        }
    };

    const handleInputChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const analyzePlan = async () => {
        if (!formData.target_amount) return;
        setIsAnalyzing(true);
        try {
            const token = await user.getIdToken();
            // Use the new endpoint
            const res = await axios.post(`${API_BASE}/savings-plan`,
                {
                    goal_amount: formData.target_amount,
                    target_date: formData.target_date
                },
                { headers: { Authorization: `Bearer ${token}` } }
            );
            setAnalysisResult(res.data);
        } catch (error) {
            console.error("Analysis failed:", error);
        } finally {
            setIsAnalyzing(false);
        }
    };

    const applyStrategy = () => {
        if (analysisResult && analysisResult.optimized_monthly_save) {
            setFormData(prev => ({
                ...prev,
                monthly_contribution: analysisResult.optimized_monthly_save.toString()
            }));
        }
    };

    const handleEdit = (goal) => {
        setEditingGoal(goal);
        setFormData({
            name: goal.name,
            target_amount: goal.target_amount,
            current_amount: goal.current_amount,
            monthly_contribution: '', // Not stored in DB currently, so leave empty
            target_date: goal.target_date || ''
        });
        setShowForm(true);
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleDelete = async (goalId) => {
        if (!window.confirm("Are you sure you want to delete this goal?")) return;
        try {
            const token = await user.getIdToken();
            await axios.delete(`${API_BASE}/goals/${goalId}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            fetchGoals();
        } catch (error) {
            console.error("Error deleting goal:", error);
            alert("Failed to delete goal.");
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const token = await user.getIdToken();
            if (editingGoal) {
                // Update
                await axios.put(`${API_BASE}/goals/${editingGoal.id}`, formData, {
                    headers: { Authorization: `Bearer ${token}` }
                });
            } else {
                // Create
                await axios.post(`${API_BASE}/goals`, formData, {
                    headers: { Authorization: `Bearer ${token}` }
                });
            }
            setShowForm(false);
            setEditingGoal(null);
            setFormData({ name: '', target_amount: '', current_amount: '', monthly_contribution: '', target_date: '' });
            setAnalysisResult(null);
            fetchGoals(); // Refresh list
        } catch (error) {
            console.error("Error saving goal:", error);
            alert("Failed to save goal. Please check your inputs.");
        }
    };

    const calculateProgress = (current, target) => {
        if (!target) return 0;
        return Math.min((current / target) * 100, 100);
    };

    const isOnTrack = (goal) => {
        if (!goal.target_date) return true; // Assume on track if no date

        const today = new Date();
        const targetDate = new Date(goal.target_date);
        // const totalDays = (targetDate - today) / (1000 * 60 * 60 * 24);

        // Simple logic: if you have > 50% saved and > 50% time left, you're good.
        // Or just check if current amount is reasonable for time elapsed.
        // For now, let's just say if you are > 80% to target, you are on track.
        return calculateProgress(goal.current_amount, goal.target_amount) > 20;
    };

    const totalSaved = goals.reduce((acc, goal) => acc + goal.current_amount, 0);

    if (loading) return <div className="text-center py-10">Loading Goals...</div>;

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-gray-800">Financial Goals</h1>
                <button
                    onClick={() => {
                        setShowForm(!showForm);
                        setEditingGoal(null);
                        setFormData({ name: '', target_amount: '', current_amount: '', monthly_contribution: '', target_date: '' });
                    }}
                    className="flex items-center bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                >
                    <Plus className="h-5 w-5 mr-2" />
                    {showForm ? 'Cancel' : 'Add Goal'}
                </button>
            </div>

            {/* Summary Card */}
            <div className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl p-6 text-white shadow-lg">
                <div className="flex items-center space-x-3 mb-2">
                    <Target className="h-6 w-6 text-green-100" />
                    <span className="text-green-50 font-medium">Total Saved</span>
                </div>
                <h1 className="text-4xl font-bold">${totalSaved.toFixed(2)}</h1>
                <p className="text-green-100 text-sm mt-2">Across {goals.length} active goals</p>
            </div>

            {/* Add/Edit Goal Form */}
            {showForm && (
                <div className="card animate-fade-in-down">
                    <h3 className="text-lg font-bold text-gray-800 mb-4">{editingGoal ? 'Edit Goal' : 'Create New Goal'}</h3>
                    <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Goal Name</label>
                            <input
                                type="text" name="name" required
                                value={formData.name} onChange={handleInputChange}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border"
                                placeholder="e.g. New Car"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Target Amount ($)</label>
                            <div className="relative">
                                <input
                                    type="number" name="target_amount" required step="0.01"
                                    value={formData.target_amount}
                                    onChange={handleInputChange}
                                    onBlur={analyzePlan}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border"
                                    placeholder="5000.00"
                                />
                                {isAnalyzing && (
                                    <div className="absolute right-3 top-3">
                                        <div className="animate-spin h-4 w-4 border-2 border-blue-500 rounded-full border-t-transparent"></div>
                                    </div>
                                )}
                            </div>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Current Savings ($)</label>
                            <input
                                type="number" name="current_amount" step="0.01"
                                value={formData.current_amount} onChange={handleInputChange}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border"
                                placeholder="0.00"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Monthly Contribution ($)</label>
                            <input
                                type="number" name="monthly_contribution" step="0.01"
                                value={formData.monthly_contribution} onChange={handleInputChange}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border"
                                placeholder="Optional"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Target Date</label>
                            <input
                                type="date" name="target_date"
                                value={formData.target_date} onChange={handleInputChange}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border"
                            />
                        </div>

                        {/* Smart Advisor Card */}
                        {analysisResult && (
                            <div className="md:col-span-2 bg-yellow-50 border border-yellow-200 rounded-lg p-4 mt-2">
                                <div className="flex items-start space-x-3">
                                    <div className="bg-yellow-100 p-2 rounded-full">
                                        <TrendingUp className="h-5 w-5 text-yellow-700" />
                                    </div>
                                    <div className="flex-1">
                                        <h4 className="font-bold text-gray-800">🚀 Speed up your goal!</h4>
                                        <p className="text-sm text-gray-600 mt-1">{analysisResult.insight_text}</p>

                                        <div className="flex flex-wrap gap-4 mt-3 text-sm">
                                            <div className="bg-red-50 text-red-700 px-3 py-1 rounded border border-red-100">
                                                <span className="font-semibold">Current Pace:</span> Finish by {analysisResult.scenarios.current.completion_date}
                                            </div>
                                            <div className="bg-green-50 text-green-700 px-3 py-1 rounded border border-green-100">
                                                <span className="font-semibold">Smart Pace:</span> Finish by {analysisResult.scenarios.optimized.completion_date}
                                            </div>
                                        </div>

                                        <button
                                            type="button"
                                            onClick={applyStrategy}
                                            className="mt-3 text-sm bg-yellow-500 text-white px-4 py-1.5 rounded hover:bg-yellow-600 font-medium transition"
                                        >
                                            Apply Smart Plan
                                        </button>
                                    </div>
                                </div>
                            </div>
                        )}

                        <div className="md:col-span-2 flex justify-end mt-2 space-x-3">
                            <button
                                type="button"
                                onClick={() => {
                                    setShowForm(false);
                                    setEditingGoal(null);
                                }}
                                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                            >
                                Cancel
                            </button>
                            <button type="submit" className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 font-medium">
                                {editingGoal ? 'Update Goal' : 'Save Goal'}
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Goals Grid */}
            <div className="card">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {goals.map((goal) => {
                        const progress = calculateProgress(goal.current_amount, goal.target_amount);
                        const onTrack = isOnTrack(goal);

                        return (
                            <div key={goal.id} className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 hover:shadow-md transition relative group">
                                <div className="flex justify-between items-start mb-4">
                                    <div>
                                        <h3 className="text-lg font-bold text-gray-800">{goal.name}</h3>
                                        <div className="flex items-center text-xs text-gray-500 mt-1">
                                            <Calendar className="h-3 w-3 mr-1" />
                                            {goal.target_date || 'No deadline'}
                                        </div>
                                    </div>
                                    <span className={`px-2 py-1 text-xs font-bold rounded-full ${onTrack ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                                        {onTrack ? 'On Track' : 'Behind'}
                                    </span>
                                </div>

                                <div className="flex justify-between items-end mb-2">
                                    <span className="text-2xl font-bold text-gray-900">${goal.current_amount.toFixed(0)}</span>
                                    <span className="text-sm text-gray-500">of ${goal.target_amount.toFixed(0)}</span>
                                </div>

                                {/* Progress Bar */}
                                <div className="w-full bg-gray-200 rounded-full h-3 mb-2">
                                    <div
                                        className={`h-3 rounded-full transition-all duration-500 ${progress >= 100 ? 'bg-green-500' : 'bg-blue-500'}`}
                                        style={{ width: `${progress}%` }}
                                    ></div>
                                </div>

                                <div className="text-right text-xs text-blue-600 font-medium mb-4">
                                    {progress.toFixed(0)}% Completed
                                </div>

                                {/* Action Buttons */}
                                <div className="flex justify-end space-x-2 pt-2 border-t border-gray-50">
                                    <button
                                        onClick={() => handleEdit(goal)}
                                        className="text-xs text-blue-600 hover:text-blue-800 font-medium px-2 py-1 rounded hover:bg-blue-50"
                                    >
                                        Edit
                                    </button>
                                    <button
                                        onClick={() => handleDelete(goal.id)}
                                        className="text-xs text-red-600 hover:text-red-800 font-medium px-2 py-1 rounded hover:bg-red-50"
                                    >
                                        Delete
                                    </button>
                                </div>
                            </div>
                        );
                    })}

                    {goals.length === 0 && !showForm && (
                        <div className="col-span-full text-center py-10 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                            <Target className="h-10 w-10 text-gray-400 mx-auto mb-2" />
                            <p className="text-gray-500">No goals yet. Click "Add Goal" to get started!</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Goals;
