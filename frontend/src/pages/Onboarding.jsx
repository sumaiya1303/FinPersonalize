import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { ArrowRight, ArrowLeft, CheckCircle, TrendingUp, Shield, PieChart } from 'lucide-react';

const API_BASE = 'http://localhost:5000/api';

const Onboarding = ({ user, onComplete }) => {
    const navigate = useNavigate();
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null); // { persona, risk_score }

    // Form State
    const [formData, setFormData] = useState({
        age: '',
        income: '',
        quiz_answers: {}
    });

    const handleInputChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleQuizAnswer = (questionId, value) => {
        setFormData(prev => ({
            ...prev,
            quiz_answers: { ...prev.quiz_answers, [questionId]: value }
        }));
    };

    const handleSubmit = async () => {
        setLoading(true);
        try {
            const token = await user.getIdToken();
            const response = await axios.post(`${API_BASE}/onboarding`, formData, {
                headers: { Authorization: `Bearer ${token}` }
            });

            setResult(response.data);
            setStep(3); // Move to Reveal Step
        } catch (error) {
            console.error("Onboarding Error:", error);
            alert("Failed to analyze profile. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const handleFinish = () => {
        if (onComplete) {
            onComplete();
        }
        navigate('/');
    };

    const nextStep = () => setStep(step + 1);
    const prevStep = () => setStep(step - 1);

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl overflow-hidden">

                {/* Progress Bar (Only for Steps 1 & 2) */}
                {step < 3 && (
                    <div className="bg-gray-100 h-2 w-full">
                        <div
                            className="bg-blue-600 h-full transition-all duration-500 ease-out"
                            style={{ width: `${(step / 2) * 100}%` }}
                        ></div>
                    </div>
                )}

                <div className="p-8 md:p-12">

                    {/* Step 1: The Basics */}
                    {step === 1 && (
                        <div className="space-y-8 animate-fade-in">
                            <div className="text-center">
                                <h2 className="text-3xl font-bold text-gray-900">Let's get started</h2>
                                <p className="text-gray-500 mt-2">We need a few details to build your financial twin.</p>
                            </div>

                            <div className="space-y-5">
                                <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-2">Age</label>
                                    <input
                                        type="number"
                                        name="age"
                                        value={formData.age}
                                        onChange={handleInputChange}
                                        className="w-full p-4 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition bg-gray-50 focus:bg-white"
                                        placeholder="e.g. 30"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-2">Annual Income ($)</label>
                                    <input
                                        type="number"
                                        name="income"
                                        value={formData.income}
                                        onChange={handleInputChange}
                                        className="w-full p-4 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition bg-gray-50 focus:bg-white"
                                        placeholder="e.g. 75000"
                                    />
                                </div>
                            </div>

                            <div className="flex justify-end pt-4">
                                <button
                                    onClick={nextStep}
                                    disabled={!formData.age || !formData.income}
                                    className="flex items-center bg-blue-600 text-white px-8 py-4 rounded-xl font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition transform hover:scale-[1.02] active:scale-[0.98]"
                                >
                                    Next Step <ArrowRight className="ml-2 h-5 w-5" />
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Step 2: The Money Quiz */}
                    {step === 2 && (
                        <div className="space-y-8 animate-fade-in">
                            <div className="text-center">
                                <h2 className="text-3xl font-bold text-gray-900">Risk Assessment</h2>
                                <p className="text-gray-500 mt-2">How do you handle money decisions?</p>
                            </div>

                            <div className="space-y-8">
                                {/* Q1 */}
                                <div className="space-y-4">
                                    <p className="font-semibold text-lg text-gray-800">1. What happens if the stock market drops 20%?</p>
                                    <div className="grid grid-cols-1 gap-3">
                                        {[
                                            { label: "Sell everything immediately", value: 0, icon: <Shield className="w-5 h-5 text-red-500" /> },
                                            { label: "Hold (Do nothing)", value: 15, icon: <PieChart className="w-5 h-5 text-yellow-500" /> },
                                            { label: "Buy more while it's cheap", value: 30, icon: <TrendingUp className="w-5 h-5 text-green-500" /> }
                                        ].map((opt, i) => (
                                            <button
                                                key={i}
                                                onClick={() => handleQuizAnswer('q1', opt.value)}
                                                className={`flex items-center p-4 text-left rounded-xl border-2 transition-all ${formData.quiz_answers['q1'] === opt.value
                                                    ? 'bg-blue-50 border-blue-500 text-blue-800 shadow-sm'
                                                    : 'border-gray-100 hover:border-blue-200 hover:bg-gray-50'
                                                    }`}
                                            >
                                                <div className="mr-3 p-2 bg-white rounded-full shadow-sm">{opt.icon}</div>
                                                <span className="font-medium">{opt.label}</span>
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                {/* Q2 */}
                                <div className="space-y-4">
                                    <p className="font-semibold text-lg text-gray-800">2. What is your primary goal?</p>
                                    <div className="grid grid-cols-1 gap-3">
                                        {[
                                            { label: "Safety (Preserve Capital)", value: 0 },
                                            { label: "Retirement (Long Term)", value: 15 },
                                            { label: "Aggressive Wealth (Max Growth)", value: 30 }
                                        ].map((opt, i) => (
                                            <button
                                                key={i}
                                                onClick={() => handleQuizAnswer('q2', opt.value)}
                                                className={`p-4 text-left rounded-xl border-2 transition-all ${formData.quiz_answers['q2'] === opt.value
                                                    ? 'bg-blue-50 border-blue-500 text-blue-800 shadow-sm'
                                                    : 'border-gray-100 hover:border-blue-200 hover:bg-gray-50'
                                                    }`}
                                            >
                                                <span className="font-medium">{opt.label}</span>
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                {/* Q3 */}
                                <div className="space-y-4">
                                    <p className="font-semibold text-lg text-gray-800">3. How long until you need this money?</p>
                                    <div className="grid grid-cols-1 gap-3">
                                        {[
                                            { label: "Less than 2 years", value: 0 },
                                            { label: "5-10 years", value: 15 },
                                            { label: "10+ years", value: 30 }
                                        ].map((opt, i) => (
                                            <button
                                                key={i}
                                                onClick={() => handleQuizAnswer('q3', opt.value)}
                                                className={`p-4 text-left rounded-xl border-2 transition-all ${formData.quiz_answers['q3'] === opt.value
                                                    ? 'bg-blue-50 border-blue-500 text-blue-800 shadow-sm'
                                                    : 'border-gray-100 hover:border-blue-200 hover:bg-gray-50'
                                                    }`}
                                            >
                                                <span className="font-medium">{opt.label}</span>
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            <div className="flex justify-between pt-6">
                                <button
                                    onClick={prevStep}
                                    className="flex items-center text-gray-500 hover:text-gray-900 font-medium px-4 py-2 rounded-lg hover:bg-gray-100 transition"
                                >
                                    <ArrowLeft className="mr-2 h-5 w-5" /> Back
                                </button>
                                <button
                                    onClick={handleSubmit}
                                    disabled={loading || Object.keys(formData.quiz_answers).length < 3}
                                    className="flex items-center bg-blue-600 text-white px-8 py-4 rounded-xl font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition transform hover:scale-[1.02] active:scale-[0.98] shadow-lg shadow-blue-200"
                                >
                                    {loading ? 'Analyzing...' : 'Reveal My Persona'}
                                    {!loading && <ArrowRight className="ml-2 h-5 w-5" />}
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Step 3: The Reveal */}
                    {step === 3 && result && (
                        <div className="text-center space-y-8 animate-fade-in-up">
                            <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 text-green-600 rounded-full mb-4 animate-bounce-slow">
                                <CheckCircle className="w-10 h-10" />
                            </div>

                            <div>
                                <h2 className="text-4xl font-extrabold text-gray-900 mb-2">You are a</h2>
                                <h1 className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
                                    {result.persona}
                                </h1>
                            </div>

                            <div className="bg-gray-50 rounded-2xl p-8 border border-gray-100">
                                <div className="flex justify-between items-end mb-2">
                                    <span className="text-gray-600 font-medium">Risk Score</span>
                                    <span className="text-3xl font-bold text-gray-900">{result.risk_score}<span className="text-lg text-gray-400 font-normal">/100</span></span>
                                </div>
                                <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
                                    <div
                                        className={`h-full rounded-full transition-all duration-1000 ease-out ${result.risk_score < 40 ? 'bg-green-500' :
                                            result.risk_score < 70 ? 'bg-yellow-500' : 'bg-red-500'
                                            }`}
                                        style={{ width: `${result.risk_score}%` }}
                                    ></div>
                                </div>
                                <p className="text-gray-500 text-sm mt-4 text-left">
                                    Based on your answers, we've calibrated your financial digital twin.
                                    Your dashboard is now personalized with recommendations that match your style.
                                </p>
                            </div>

                            <button
                                onClick={handleFinish}
                                className="w-full bg-gray-900 text-white px-8 py-4 rounded-xl font-bold hover:bg-black transition transform hover:scale-[1.02] active:scale-[0.98] shadow-xl"
                            >
                                Go to Dashboard
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Onboarding;
