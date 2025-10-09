import React, { useState } from 'react';
import './App.css'; 
function App() {
  const [paragraph, setParagraph] = useState('');
  const [summary, setSummary] = useState('');
  const [questions, setQuestions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [copiedSummary, setCopiedSummary] = useState(false);
  const [copiedQuestions, setCopiedQuestions] = useState(false);
  const [wordCount, setWordCount] = useState(0);

  const handleInputChange = (e) => {
    const text = e.target.value;
    setParagraph(text);
    setWordCount(text.trim().split(/\s+/).filter(word => word.length > 0).length);
  };

  const handleSubmit = async () => {
    if (!paragraph.trim()) return;
    
    setIsLoading(true);
    try {
      // Replace this with your actual fetch API call:
      const response = await fetch('http://localhost:8000/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ paragraph }),
      });
      
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      
      const data = await response.json();
      setSummary(data.summary);
      setQuestions(data.questions);
    } catch (error) {
      console.error('Error generating summary and questions:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = async (text, type) => {
    try {
      await navigator.clipboard.writeText(text);
      if (type === 'summary') {
        setCopiedSummary(true);
        setTimeout(() => setCopiedSummary(false), 2000);
      } else {
        setCopiedQuestions(true);
        setTimeout(() => setCopiedQuestions(false), 2000);
      }
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const clearAll = () => {
    setParagraph('');
    setSummary('');
    setQuestions([]);
    setWordCount(0);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-800 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <div className="w-12 h-12 text-4xl mr-3">🧠</div>
            <h1 className="text-5xl font-bold bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
              LearnMaster AI
            </h1>
            <div className="w-8 h-8 text-2xl ml-3 animate-pulse">✨</div>
          </div>
          <p className="text-gray-300 text-lg">
            Transform any paragraph into concise summaries and insightful questions
          </p>
        </div>

        {/* Main Container */}
        <div className="bg-white/10 backdrop-blur-lg rounded-3xl p-8 border border-white/20 shadow-2xl">
          {/* Input Section */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <div className="w-6 h-6 text-xl mr-2">📄</div>
                <label className="text-white font-semibold text-lg">Your Paragraph</label>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-300">
                  {wordCount} words
                </span>
                {paragraph && (
                  <button
                    onClick={clearAll}
                    className="text-red-400 hover:text-red-300 transition-colors text-sm font-medium"
                  >
                    Clear All
                  </button>
                )}
              </div>
            </div>
            
            <div className="relative">
              <textarea
                rows="8"
                placeholder="Paste your paragraph here..."
                value={paragraph}
                onChange={handleInputChange}
                className="w-full p-6 bg-black/20 border-2 border-white/20 rounded-2xl text-white placeholder-gray-400 focus:border-cyan-400 focus:ring-4 focus:ring-cyan-400/20 transition-all duration-300 resize-none text-lg leading-relaxed"
              />
              <div className="absolute bottom-4 right-4">
                {/* <div className="w-5 h-5 text-lg opacity-50">⚡</div> */}
              </div>
            </div>
          </div>

          {/* Generate Button */}
          <button
            onClick={handleSubmit}
            disabled={!paragraph.trim() || isLoading}
            className="w-full py-4 px-8 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 disabled:from-gray-600 disabled:to-gray-700 text-white font-bold text-lg rounded-2xl transition-all duration-300 transform hover:scale-[1.02] disabled:scale-100 disabled:cursor-not-allowed shadow-lg hover:shadow-xl flex items-center justify-center space-x-3"
          >
            {isLoading ? (
              <>
                <div className="w-6 h-6 animate-spin border-2 border-white border-t-transparent rounded-full"></div>
                <span>Generating Magic...</span>
              </>
            ) : (
              <>
                <div className="w-6 h-6 text-xl">🧠</div>
                <span>Generate Summary & Questions</span>
                <div className="w-5 h-5 text-lg">✨</div>
              </>
            )}
          </button>

          {/* Results Section */}
          <div className="mt-8 space-y-6">
            {/* Summary */}
            {summary && (
              <div className="bg-gradient-to-br from-green-500/20 to-emerald-600/20 rounded-2xl p-6 border border-green-400/30 backdrop-blur-sm animate-fadeIn">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <div className="w-6 h-6 text-xl mr-2">📄</div>
                    <h2 className="text-2xl font-bold text-white">Summary</h2>
                  </div>
                  <button
                    onClick={() => copyToClipboard(summary, 'summary')}
                    className="flex items-center space-x-2 px-4 py-2 bg-green-500/20 hover:bg-green-500/30 rounded-lg transition-colors border border-green-400/30"
                  >
                    {copiedSummary ? (
                      <div className="w-4 h-4 text-sm">✓</div>
                    ) : (
                      <div className="w-4 h-4 text-sm">📋</div>
                    )}
                    <span className="text-green-400 text-sm font-medium">
                      {copiedSummary ? 'Copied!' : 'Copy'}
                    </span>
                  </button>
                </div>
                <div className="bg-black/20 rounded-xl p-5 border border-white/10">
                  <p className="text-gray-100 text-lg leading-relaxed">{summary}</p>
                </div>
              </div>
            )}

            {/* Questions */}
            {questions.length > 0 && (
              <div className="bg-gradient-to-br from-purple-500/20 to-pink-600/20 rounded-2xl p-6 border border-purple-400/30 backdrop-blur-sm animate-fadeIn">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <div className="w-6 h-6 text-xl mr-2">❓</div>
                    <h2 className="text-2xl font-bold text-white">Questions</h2>
                  </div>
                  <button
                    onClick={() => copyToClipboard(questions.join('\n'), 'questions')}
                    className="flex items-center space-x-2 px-4 py-2 bg-purple-500/20 hover:bg-purple-500/30 rounded-lg transition-colors border border-purple-400/30"
                  >
                    {copiedQuestions ? (
                      <div className="w-4 h-4 text-sm">✓</div>
                    ) : (
                      <div className="w-4 h-4 text-sm">📋</div>
                    )}
                    <span className="text-purple-400 text-sm font-medium">
                      {copiedQuestions ? 'Copied!' : 'Copy'}
                    </span>
                  </button>
                </div>
                <div className="space-y-3">
                  {questions.map((question, index) => (
                    <div
                      key={index}
                      className="bg-black/20 rounded-xl p-4 border border-white/10 hover:bg-black/30 transition-colors group"
                    >
                      <div className="flex items-start space-x-4">
                        <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
                          {index + 1}
                        </div>
                        <p className="text-gray-100 text-lg leading-relaxed flex-1 group-hover:text-white transition-colors">
                          {question}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8">
          <p className="text-gray-400">
            Powered by AI • Made for better learning.
          </p>
        </div>
      </div>

      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        .animate-fadeIn {
          animation: fadeIn 0.6s ease-out;
        }
      `}</style>
    </div>
  );
}

export default App;
