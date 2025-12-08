import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const Chatbox = ({ onSendMessage, isLoading }) => {
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState([
        { sender: 'ai', text: 'Hello! I am your AI financial assistant. Ask me about your spending, budget, or financial advice.' }
    ]);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isLoading]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMsg = { sender: 'user', text: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');

        const responseText = await onSendMessage(userMsg.text);

        setMessages(prev => [...prev, { sender: 'ai', text: responseText }]);
    };

    return (
        <div className="flex flex-col h-[500px] bg-gray-50 rounded-xl overflow-hidden">
            <div className="flex-1 overflow-y-auto p-4 space-y-6">
                {messages.map((msg, index) => (
                    <div
                        key={index}
                        className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div className={`flex max-w-[85%] ${msg.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                            <div className={`flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center shadow-sm ${msg.sender === 'user' ? 'bg-blue-600 ml-3' : 'bg-white border border-gray-200 mr-3'}`}>
                                {msg.sender === 'user' ? <User className="h-5 w-5 text-white" /> : <Bot className="h-5 w-5 text-blue-600" />}
                            </div>

                            <div
                                className={`p-4 rounded-2xl text-sm shadow-sm leading-relaxed ${msg.sender === 'user'
                                    ? 'bg-blue-600 text-white rounded-tr-none'
                                    : 'bg-white text-gray-800 border border-gray-200 rounded-tl-none'
                                    }`}
                            >
                                {msg.sender === 'user' ? (
                                    msg.text
                                ) : (
                                    <div className="markdown-content">
                                        {typeof msg.text === 'object' ? (
                                            <div>
                                                <ReactMarkdown
                                                    components={{
                                                        ul: ({ node, ...props }) => <ul className="list-disc list-inside space-y-1 my-2" {...props} />,
                                                        li: ({ node, ...props }) => <li className="ml-2" {...props} />,
                                                        strong: ({ node, ...props }) => <span className="font-bold text-gray-900" {...props} />
                                                    }}
                                                >
                                                    {msg.text.answer}
                                                </ReactMarkdown>
                                                {msg.text.sources && msg.text.sources.length > 0 && (
                                                    <div className="mt-3 pt-3 border-t border-gray-100">
                                                        <p className="text-xs font-semibold text-gray-500 mb-1">Sources:</p>
                                                        <ul className="list-disc list-inside text-xs text-gray-500 space-y-0.5">
                                                            {msg.text.sources.map((source, idx) => (
                                                                <li key={idx}>{source}</li>
                                                            ))}
                                                        </ul>
                                                    </div>
                                                )}
                                            </div>
                                        ) : (
                                            <ReactMarkdown
                                                components={{
                                                    ul: ({ node, ...props }) => <ul className="list-disc list-inside space-y-1 my-2" {...props} />,
                                                    li: ({ node, ...props }) => <li className="ml-2" {...props} />,
                                                    strong: ({ node, ...props }) => <span className="font-bold text-gray-900" {...props} />
                                                }}
                                            >
                                                {msg.text}
                                            </ReactMarkdown>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div className="flex justify-start animate-fade-in">
                        <div className="flex items-center space-x-2 bg-white p-4 rounded-2xl rounded-tl-none border border-gray-200 ml-11 shadow-sm">
                            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <form onSubmit={handleSubmit} className="p-4 bg-white border-t border-gray-200">
                <div className="flex items-center space-x-2 relative">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask about your finances..."
                        className="flex-1 p-4 pr-12 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-50 text-gray-800 placeholder-gray-400 transition-all"
                        disabled={isLoading}
                    />
                    <button
                        type="submit"
                        disabled={isLoading || !input.trim()}
                        className="absolute right-2 p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:hover:bg-blue-600 transition-colors"
                    >
                        <Send className="h-5 w-5" />
                    </button>
                </div>
            </form>
        </div>
    );
};

export default Chatbox;
