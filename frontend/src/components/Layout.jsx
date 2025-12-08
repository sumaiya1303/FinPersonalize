import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, DollarSign, Target, Receipt, LogOut, ShieldCheck, Sparkles, Activity } from 'lucide-react';

const Layout = ({ user, onLogout }) => {
    const location = useLocation();

    return (
        <div className="flex h-screen bg-[#f3f4f6]">
            {/* Sidebar */}
            <aside className="w-64 bg-[#1e293b] text-white flex flex-col shadow-xl z-10">
                <div className="p-6 flex items-center border-b border-slate-700">
                    <DollarSign className="h-8 w-8 text-blue-400 mr-2" />
                    <span className="text-xl font-bold tracking-tight">FinPersonalize</span>
                </div>

                <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
                    <Link to="/" className={`flex items-center p-3 rounded-lg transition-all duration-200 ${location.pathname === '/' ? 'bg-blue-600 shadow-md' : 'hover:bg-slate-700 text-slate-300 hover:text-white'}`}>
                        <LayoutDashboard className="h-5 w-5 mr-3" />
                        Dashboard
                    </Link>
                    <Link to="/transactions" className={`flex items-center p-3 rounded-lg transition-all duration-200 ${location.pathname === '/transactions' ? 'bg-blue-600 shadow-md' : 'hover:bg-slate-700 text-slate-300 hover:text-white'}`}>
                        <Receipt className="h-5 w-5 mr-3" />
                        Transactions
                    </Link>
                    <Link to="/analytics" className={`flex items-center p-3 rounded-lg transition-all duration-200 ${location.pathname === '/analytics' ? 'bg-blue-600 shadow-md' : 'hover:bg-slate-700 text-slate-300 hover:text-white'}`}>
                        <Activity className="h-5 w-5 mr-3" />
                        Analytics
                    </Link>
                    <Link to="/goals" className={`flex items-center p-3 rounded-lg transition-all duration-200 ${location.pathname === '/goals' ? 'bg-blue-600 shadow-md' : 'hover:bg-slate-700 text-slate-300 hover:text-white'}`}>
                        <Target className="h-5 w-5 mr-3" />
                        Goals
                    </Link>
                    <Link to="/recommendations" className={`flex items-center p-3 rounded-lg transition-all duration-200 ${location.pathname === '/recommendations' ? 'bg-blue-600 shadow-md' : 'hover:bg-slate-700 text-slate-300 hover:text-white'}`}>
                        <Sparkles className="h-5 w-5 mr-3" />
                        Insights
                    </Link>
                    <div className="border-t border-slate-700 my-2"></div>
                    <Link to="/admin" className={`flex items-center p-3 rounded-lg transition-all duration-200 ${location.pathname === '/admin' ? 'bg-blue-600 shadow-md' : 'hover:bg-slate-700 text-slate-300 hover:text-white'}`}>
                        <ShieldCheck className="h-5 w-5 mr-3" />
                        Admin Audit
                    </Link>

                </nav>

                <div className="p-4 border-t border-slate-700 bg-[#1e293b]">
                    <Link to="/profile" className="flex items-center mb-4 px-3 hover:bg-slate-700 p-2 rounded-lg transition cursor-pointer">
                        <div className="h-9 w-9 rounded-full bg-gradient-to-tr from-blue-500 to-purple-500 flex items-center justify-center mr-3 shadow-sm">
                            <span className="font-bold text-sm">{user.email[0].toUpperCase()}</span>
                        </div>
                        <div className="overflow-hidden">
                            <p className="text-sm font-medium truncate text-slate-200">{user.email}</p>
                            <p className="text-xs text-slate-400">View Profile</p>
                        </div>
                    </Link>
                    <button
                        onClick={onLogout}
                        className="w-full flex items-center justify-center p-2 text-red-400 hover:bg-red-500/10 hover:text-red-300 rounded-lg transition"
                    >
                        <LogOut className="h-4 w-4 mr-2" />
                        Sign Out
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 flex flex-col overflow-hidden">
                {/* Mobile/Top Header */}
                <header className="bg-white shadow-sm border-b border-gray-200 p-4 flex justify-between items-center lg:hidden">
                    <span className="font-bold text-gray-800">FinPersonalize</span>
                    <button onClick={onLogout} className="text-gray-600 hover:text-red-500">
                        <LogOut className="h-5 w-5" />
                    </button>
                </header>

                <div className="flex-1 overflow-y-auto p-8">
                    <Outlet />
                </div>
            </main>
        </div>
    );
};

export default Layout;
