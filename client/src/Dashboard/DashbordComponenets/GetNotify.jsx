import { useState } from "react";
import { BellRing, X, Send, Sparkles } from 'lucide-react';

const GetNotify = ({ setIsgetnotify }) => {
  const [userDescription, setUserDescription] = useState("");

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-gradient-to-br from-white/20 to-white/10 backdrop-blur-xl rounded-3xl p-8 border border-white/20 shadow-2xl w-full max-w-md transform transition-all duration-300 animate-in">
        
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg">
              <BellRing className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Set Alert</h2>
              <p className="text-gray-300 text-sm">Get notified about your coins</p>
            </div>
          </div>
          
          <button 
            onClick={()=>setIsgetnotify(false)}
            className="w-10 h-10 bg-white/10 hover:bg-white/20 rounded-full flex items-center justify-center transition-all duration-200 group"
          >
            <X className="w-5 h-5 text-gray-300 group-hover:text-white" />
          </button>
        </div>

        {/* Input Section */}
        <div className="space-y-4">
          <div className="relative">
            <textarea
              placeholder="e.g., Alert me when Bitcoin drops below $40,000 or rises above $50,000"
              value={userDescription}
              onChange={(e) => setUserDescription(e.target.value)}
              className="w-full h-32 bg-white/10 backdrop-blur-sm rounded-2xl px-4 py-3 text-white placeholder-gray-400 border border-white/10 focus:border-blue-400 focus:outline-none resize-none transition-all duration-300"
            />
            <div className="absolute top-3 right-3">
              <Sparkles className="w-5 h-5 text-blue-400 opacity-50" />
            </div>
          </div>

          {/* Preview */}
          {userDescription && (
            <div className="bg-white/5 rounded-xl p-4 border border-white/10">
              <p className="text-gray-300 text-sm mb-2">Preview:</p>
              <p className="text-white">{userDescription}</p>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-3 mt-6">
          <button
            onClick={()=>setIsgetnotify(false)}
            className="flex-1 bg-white/10 hover:bg-white/20 text-gray-300 hover:text-white py-3 rounded-xl font-medium transition-all duration-200"
          >
            Cancel
          </button>
          
          <button
            disabled={!userDescription.trim()}
            className="flex-1 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 disabled:from-gray-600 disabled:to-gray-700 text-white py-3 rounded-xl font-medium flex items-center justify-center space-x-2 transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
            <span>Notify Me</span>
          </button>
        </div>

        {/* Quick Examples */}
        <div className="mt-6 pt-4 border-t border-white/10">
          <p className="text-gray-400 text-xs mb-3">Quick examples:</p>
          <div className="space-y-2">
            {[
              "Watch Bitcoin for me",
              "Alert when ETH hits $3,000",
              "Tell me if DOGE pumps 20%"
            ].map((example, index) => (
              <button
                key={index}
                onClick={() => setUserDescription(example)}
                className="text-left w-full bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white px-3 py-2 rounded-lg text-sm transition-all duration-200"
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default GetNotify;