import React from 'react';

const RecentTransactions = ({ transactions }) => {
    return (
        <div className="bg-white p-4 rounded-lg shadow-md mt-4">
            <h2 className="text-xl font-bold mb-4">Recent Transactions</h2>
            <div className="overflow-x-auto">
                <table className="min-w-full table-auto">
                    <thead>
                        <tr className="bg-gray-100">
                            <th className="px-4 py-2 text-left">Date</th>
                            <th className="px-4 py-2 text-left">Vendor</th>
                            <th className="px-4 py-2 text-left">Category</th>
                            <th className="px-4 py-2 text-right">Amount</th>
                        </tr>
                    </thead>
                    <tbody>
                        {transactions.slice(0, 10).map((t) => (
                            <tr key={t.id} className="border-b hover:bg-gray-50">
                                <td className="px-4 py-2">{t.date}</td>
                                <td className="px-4 py-2">{t.vendor || t.description}</td>
                                <td className="px-4 py-2">
                                    <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                                        {t.category}
                                    </span>
                                </td>
                                <td className={`px-4 py-2 text-right font-medium ${t.amount < 0 ? 'text-red-600' : 'text-green-600'}`}>
                                    ${Math.abs(t.amount).toFixed(2)}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default RecentTransactions;
