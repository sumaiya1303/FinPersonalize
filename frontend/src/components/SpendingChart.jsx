import React from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

const SpendingChart = ({ data }) => {
    // Convert dictionary to array for Recharts
    // data is like {'Food': 150, 'Bills': 200}
    const chartData = Object.keys(data).map((key, index) => ({
        name: key,
        value: Math.abs(data[key]) // Use absolute value as spending might be negative
    })).filter(item => item.value > 0);

    return (
        <div className="bg-white p-4 rounded-lg shadow-md">
            <h2 className="text-xl font-bold mb-4">Spending Breakdown</h2>
            <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie
                            data={chartData}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="value"
                        >
                            {chartData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                        </Pie>
                        <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
                        <Legend />
                    </PieChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default SpendingChart;
