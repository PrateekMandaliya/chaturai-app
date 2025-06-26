import { useState, useRef, useEffect } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import chaturImage from "./assets/chatur.png"; // Place your Chatur image here

function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const chatContainerRef = useRef(null);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTo({
        top: chatContainerRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messages]);

  const askQuestion = async () => {
    if (!question.trim()) return;
    const userMessage = { role: "user", text: question };
    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");
    setLoading(true);

    try {
      const res = await axios.post("http://localhost:8000/ask", { question });
      const answer =
        res.data.answer || res.data.error || "Something went wrong";
      const botMessage = { role: "bot", text: answer };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "⚠️ Failed to fetch answer." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") askQuestion();
  };

  return (
    <div className={`${darkMode ? "dark" : ""}`}>
      <div className="min-h-screen flex flex-col bg-gradient-to-br from-slate-100 to-blue-50 dark:from-gray-900 dark:to-gray-800">
        <header className="bg-white dark:bg-gray-900 shadow px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <div className="max-w-6xl mx-auto flex items-center justify-between relative">
            {/* Left: Chatur Image */}
            <div className="absolute left-0 flex items-center">
              <img
                src={chaturImage}
                alt="Chatur"
                className="w-12 h-12 rounded-full"
              />
            </div>

            {/* Center: Title */}
            <div className="flex flex-col items-center mx-auto">
              <h1 className="text-4xl font-bold text-gray-800 dark:text-white">
                ChaturAI
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400 font-medium mt-1">
                Smarter with Context. Powered by RAG.
              </p>
            </div>

            {/* Right: Toggle Button */}
            <div className="absolute right-0">
              <button
                className="text-xs bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 px-3 py-1.5 rounded hover:bg-gray-300 dark:hover:bg-gray-600"
                onClick={() => setDarkMode((prev) => !prev)}
              >
                Toggle {darkMode ? "Light" : "Dark"} Mode
              </button>
            </div>
          </div>
        </header>

        <main
          ref={chatContainerRef}
          className="flex-1 overflow-y-auto w-full flex flex-col items-center px-4 py-6"
        >
          <div className="w-full max-w-3xl space-y-4">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${
                  msg.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`px-5 py-3 rounded-2xl text-base whitespace-pre-wrap max-w-[75%] shadow-md ${
                    msg.role === "user"
                      ? "bg-blue-600 text-white self-end"
                      : "bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-800 dark:text-gray-100"
                  }`}
                >
                  {msg.role === "user" ? (
                    msg.text
                  ) : (
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        a: ({ node, ...props }) => (
                          <a
                            {...props}
                            className="text-blue-600 underline hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                            target="_blank"
                            rel="noopener noreferrer"
                          />
                        ),
                        li: ({ children }) => (
                          <li className="list-disc ml-6">{children}</li>
                        ),
                        ul: ({ children }) => (
                          <ul className="mb-2">{children}</ul>
                        ),
                        strong: ({ children }) => (
                          <strong className="font-semibold">{children}</strong>
                        ),
                      }}
                    >
                      {msg.text}
                    </ReactMarkdown>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="text-sm text-gray-500 dark:text-gray-400">
                ChaturAI is thinking...
              </div>
            )}
          </div>
        </main>

        <footer className="bg-white dark:bg-gray-900 border-t border-gray-300 dark:border-gray-700 p-4 sticky bottom-0">
          <div className="max-w-3xl mx-auto flex flex-col gap-3">
            <div className="flex items-center gap-3">
              <input
                type="text"
                className="flex-1 p-3 border border-gray-300 dark:border-gray-600 rounded-full shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
                placeholder="Ask about today’s tech, biz, or world news..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={handleKeyPress}
              />
              <button
                onClick={askQuestion}
                className="bg-blue-600 text-white px-6 py-3 rounded-full hover:bg-blue-700 transition"
              >
                Send
              </button>
            </div>
            <p className="text-center text-sm text-gray-500 dark:text-gray-400">
              — Powered by <strong>ChaturAI 🧠</strong>, crafted with ❤️ by
              Prateek Mandaliya
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
}

export default App;
