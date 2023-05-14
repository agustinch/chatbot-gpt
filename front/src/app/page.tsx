'use client';
import Image from 'next/image';
import { useEffect, useState } from 'react';

interface ChatHistoryItem {
  role: string;
  content: string;
  foods: { action: string; food_name: string; amount: number; unit?: string }[];
}

export default function Home() {
  const [inputValue, setInputValue] = useState('');
  const [chatHistory, setChatHistory] = useState<ChatHistoryItem[]>([]);
  const handleInputChange = (event: any) => {
    setInputValue(event.target.value);
  };

  const handleSendClick = async () => {
    try {
      setChatHistory((prev) => [
        ...prev,
        { role: 'user', content: inputValue, foods: [] },
      ]);
      setInputValue('');
      const response = await fetch('http://127.0.0.1:8000/chatbot', {
        method: 'POST',
        mode: 'cors', // no-cors, *cors, same-origin
        cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
        credentials: 'same-origin', // include, *same-origin, omit
        headers: {
          'Content-Type': 'application/json',
          // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: JSON.stringify({
          prompt: inputValue,
          chat_id: 2,
        }),
      });
      const chatResponse = await response.json();
      const message = chatResponse?.message || '';
      setChatHistory((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: message,
          foods: chatResponse.foods.filter((f: any) => f.action === 'read'),
        },
      ]);
    } catch (e) {
      console.log(e);
    }
  };

  return (
    <main className="flex flex-col h-screen justify-between">
      <div className="px-4 py-6 bg-gray-900 w-100 h-screen text-white">
        <h1 className="text-3xl font-bold mb-4">Chatbot</h1>
        <div className="flex justify-between items-center">
          <div className="flex-1">
            {chatHistory.map((p, i) => (
              <>
                <p key={i} className="mb-2">
                  {p.role} - {p.content}
                </p>
                {p.foods.length > 0 ? (
                  <p className="font-bold">
                    Comida:
                    <ul>
                      {p.foods.map((f) => (
                        <li>
                          {f.food_name} - {f.amount} {f?.unit}
                        </li>
                      ))}
                    </ul>
                  </p>
                ) : (
                  <div />
                )}
              </>
            ))}
          </div>
        </div>
      </div>
      <div className="px-4 py-6 bg-gray-800 text-white">
        <div className="flex items-center">
          <input
            className="border rounded px-4 py-2 w-full text-black"
            type="text"
            placeholder="Enter your message here"
            value={inputValue}
            onChange={handleInputChange}
            onKeyPress={(ev) => {
              if (ev.key === 'Enter') {
                handleSendClick();
                ev.preventDefault();
              }
            }}
          />
          <button
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-full mr-4"
            onClick={handleSendClick}
          >
            Send
          </button>
        </div>
      </div>
    </main>
  );
}
