import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

const Bills = ({ user }) => {
    const [bills, setBills] = useState([]);
    const [loading, setLoading] = useState(true);

    const [showModal, setShowModal] = useState(false);
    const [editingBill, setEditingBill] = useState(null);
    const [formData, setFormData] = useState({ name: '', amount: '', day_of_month: '' });

    useEffect(() => {
        if (user) {
            fetchBills();
        }
    }, [user]);

    const fetchBills = async () => {
        try {
            const token = await user.getIdToken();
            const res = await axios.get(`${API_BASE}/bills`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setBills(res.data);
            setLoading(false);
        } catch (error) {
            console.error("Error fetching bills:", error);
            setLoading(false);
        }
    };

    const handleMarkPaid = async (billId) => {
        try {
            const token = await user.getIdToken();
            await axios.post(`${API_BASE}/bills/${billId}/pay`, {}, {
                headers: { Authorization: `Bearer ${token}` }
            });
            // Refresh bills
            fetchBills();
        } catch (error) {
            console.error("Error marking bill as paid:", error);
            alert("Failed to mark as paid.");
        }
    };

    const handleDelete = async (billId) => {
        if (!window.confirm("Are you sure you want to delete this bill?")) return;
        try {
            const token = await user.getIdToken();
            await axios.delete(`${API_BASE}/bills/${billId}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            fetchBills();
        } catch (error) {
            console.error("Error deleting bill:", error);
            alert("Failed to delete bill.");
        }
    };

    const handleOpenAdd = () => {
        setEditingBill(null);
        setFormData({ name: '', amount: '', day_of_month: '' });
        setShowModal(true);
    };

    const handleOpenEdit = (bill) => {
        setEditingBill(bill);
        // Extract day from dueDate string or calculate it? 
        // Ideally backend returns day_of_month, but our current GET returns computed dueDate.
        // We can infer day from dueDate for now, or just ask user to re-enter if not available.
        // Actually, let's just parse the day from dueDate for pre-filling.
        const day = new Date(bill.dueDate).getDate();

        setFormData({
            name: bill.name,
            amount: bill.amount,
            day_of_month: day
        });
        setShowModal(true);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const token = await user.getIdToken();
            if (editingBill) {
                // Update
                await axios.put(`${API_BASE}/bills/${editingBill.id}`, formData, {
                    headers: { Authorization: `Bearer ${token}` }
                });
            } else {
                // Create
                await axios.post(`${API_BASE}/bills`, formData, {
                    headers: { Authorization: `Bearer ${token}` }
                });
            }
            setShowModal(false);
            setFormData({ name: '', amount: '', day_of_month: '' });
            fetchBills();
        } catch (error) {
            console.error("Error saving bill:", error);
            alert("Failed to save bill.");
        }
    };

    if (loading) return <div className="text-center py-10">Loading Bills...</div>;

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-gray-800">Recurring Bills</h1>
                <div className="space-x-4">
                    <button
                        onClick={handleOpenAdd}
                        className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition shadow-md"
                    >
                        + Add Bill
                    </button>
                    <button onClick={fetchBills} className="text-sm text-blue-600 hover:text-blue-800">
                        Refresh
                    </button>
                </div>
            </div>

            {/* Modal */}
            {showModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white p-6 rounded-xl shadow-xl w-full max-w-md">
                        <h2 className="text-xl font-bold mb-4">{editingBill ? 'Edit Bill' : 'Add Recurring Bill'}</h2>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Bill Name</label>
                                <input
                                    type="text"
                                    required
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border"
                                    value={formData.name}
                                    onChange={e => setFormData({ ...formData, name: e.target.value })}
                                    placeholder="e.g. Gym Membership"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Amount ($)</label>
                                <input
                                    type="number"
                                    required
                                    step="0.01"
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border"
                                    value={formData.amount}
                                    onChange={e => setFormData({ ...formData, amount: e.target.value })}
                                    placeholder="0.00"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Day of Month Due (1-31)</label>
                                <input
                                    type="number"
                                    required
                                    min="1"
                                    max="31"
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border"
                                    value={formData.day_of_month}
                                    onChange={e => setFormData({ ...formData, day_of_month: e.target.value })}
                                    placeholder="15"
                                />
                            </div>
                            <div className="flex justify-end space-x-3 mt-6">
                                <button
                                    type="button"
                                    onClick={() => setShowModal(false)}
                                    className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                                >
                                    {editingBill ? 'Update Bill' : 'Save Bill'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {bills.length === 0 ? (
                <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100 text-center">
                    <p className="text-gray-500">No recurring bills detected yet.</p>
                    <p className="text-sm text-gray-400 mt-2">We scan your transactions to find monthly patterns.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {bills.map(bill => (
                        <div key={bill.id} className={`bg-white p-6 rounded-xl shadow-sm border-l-4 transition-all hover:shadow-md ${bill.status === 'Overdue' ? 'border-red-500' :
                            bill.status === 'Due Soon' ? 'border-yellow-500' :
                                bill.status === 'Paid' ? 'border-green-500' :
                                    'border-blue-500'
                            }`}>
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <h3 className="text-lg font-bold text-gray-900">{bill.name}</h3>
                                    <p className="text-sm text-gray-500">Due: {bill.dueDate}</p>
                                </div>
                                <div className="flex flex-col items-end space-y-2">
                                    <span className={`px-2 py-1 rounded-full text-xs font-bold ${bill.status === 'Overdue' ? 'bg-red-100 text-red-700' :
                                        bill.status === 'Due Soon' ? 'bg-yellow-100 text-yellow-700' :
                                            bill.status === 'Paid' ? 'bg-green-100 text-green-700' :
                                                'bg-blue-100 text-blue-700'
                                        }`}>
                                        {bill.status}
                                    </span>
                                    <button
                                        onClick={() => handleOpenEdit(bill)}
                                        className="text-xs text-gray-400 hover:text-blue-600 underline"
                                    >
                                        Edit
                                    </button>
                                    <button
                                        onClick={() => handleDelete(bill.id)}
                                        className="text-xs text-gray-400 hover:text-red-600 underline"
                                    >
                                        Delete
                                    </button>
                                </div>
                            </div>

                            <div className="flex justify-between items-end">
                                <div>
                                    <p className="text-2xl font-bold text-gray-900">${bill.amount.toFixed(2)}</p>
                                    <p className="text-xs text-gray-400 mt-1">Average Amount</p>
                                </div>

                                {!bill.isPaid && (
                                    <button
                                        onClick={() => handleMarkPaid(bill.id)}
                                        className="px-4 py-2 bg-gray-900 text-white text-sm rounded-lg hover:bg-black transition"
                                    >
                                        Mark Paid
                                    </button>
                                )}
                            </div>

                            {/* Alert Message */}
                            {(bill.status === 'Due Soon' || bill.status === 'Overdue') && !bill.isPaid && (
                                <div className={`mt-4 p-3 rounded-lg text-sm flex items-center ${bill.status === 'Overdue' ? 'bg-red-50 text-red-700' : 'bg-yellow-50 text-yellow-700'
                                    }`}>
                                    <span className="mr-2">⚠️</span>
                                    {bill.status === 'Overdue'
                                        ? `Overdue by ${Math.abs(bill.daysRemaining)} days!`
                                        : `Due in ${bill.daysRemaining} days!`}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Bills;
