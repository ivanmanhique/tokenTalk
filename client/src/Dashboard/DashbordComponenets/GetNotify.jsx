import { useState } from "react";
import { BellRing, X, Send, Sparkles, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';

const GetNotify = ({ setIsgetnotify }) => {
  const [userDescription, setUserDescription] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [responseState, setResponseState] = useState({
    loading: false,
    error: null,
    success: false
  });

  const sendMessage = async () => {
    if (!userDescription.trim() || userDescription.trim().length <= 3) return;
    
    setIsSubmitting(true);
    setResponseState({ loading: true, error: null, success: false });

    try {
      const response = await fetch(
        "https://fa2592faf19e.ngrok-free.app/api/chat/message",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: userDescription,
            user_id: "ivan",
            user_email: "viriatomanhique@gmail.com",
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      await response.json();
      setResponseState({ loading: false, error: null, success: true });
      
      // Auto close modal after 2 seconds on success
      setTimeout(() => {
        setIsgetnotify(false);
      }, 2000);

    } catch (err) {
      setResponseState({ loading: false, error: err.message, success: false });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSubmit = () => {
    sendMessage();
  };

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
            onClick={() => setIsgetnotify(false)}
            disabled={isSubmitting}
            className="w-10 h-10 bg-white/10 hover:bg-white/20 rounded-full flex items-center justify-center transition-all duration-200 group disabled:opacity-50 disabled:cursor-not-allowed"
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
              disabled={isSubmitting}
              className="w-full h-32 bg-white/10 backdrop-blur-sm rounded-2xl px-4 py-3 text-white placeholder-gray-400 border border-white/10 focus:border-blue-400 focus:outline-none resize-none transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
            />
            <div className="absolute top-3 right-3">
              <Sparkles className="w-5 h-5 text-blue-400 opacity-50" />
            </div>
          </div>
        </div>

        {/* Response Status with Animations */}
        <div className="min-h-[60px] flex items-center justify-center">
          {responseState.loading && (
            <div className="flex items-center space-x-3 text-blue-400 animate-pulse">
              <Loader2 className="w-5 h-5 animate-spin" />
              <span className="text-sm font-medium">Sending your alert request...</span>
            </div>
          )}
          
          {responseState.error && (
            <div className="flex items-center space-x-2 text-red-400 animate-bounce">
              <AlertCircle className="w-5 h-5" />
              <span className="text-sm">{responseState.error}</span>
            </div>
          )}
          
          {responseState.success && (
            <div className="flex items-center space-x-2 text-green-400 animate-pulse">
              <CheckCircle className="w-5 h-5" />
              <span className="text-sm font-medium">Alert set successfully! 🎉</span>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-3 mt-6">
          <button
            onClick={() => setIsgetnotify(false)}
            disabled={isSubmitting}
            className="flex-1 bg-white/10 hover:bg-white/20 text-gray-300 hover:text-white py-3 rounded-xl font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancel
          </button>
          
          <button
            onClick={handleSubmit}
            disabled={!userDescription.trim() || isSubmitting || userDescription.trim().length <= 3}
            className="flex-1 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 disabled:from-gray-600 disabled:to-gray-700 text-white py-3 rounded-xl font-medium flex items-center justify-center space-x-2 transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Sending...</span>
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span>Notify Me</span>
              </>
            )}
          </button>
        </div>

        {/* Quick Examples - Hidden during submission */}
        {!isSubmitting && !responseState.success && (
          <div className="mt-6 pt-4 border-t border-white/10 transition-all duration-300">
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
                  className="text-left w-full bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white px-3 py-2 rounded-lg text-sm transition-all duration-200 transform hover:scale-[1.02]"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Success Message Animation */}
        {responseState.success && (
          <div className="mt-4 text-center">
            <div className="inline-block animate-bounce">
              <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-green-600 rounded-full flex items-center justify-center mx-auto mb-2 shadow-lg">
                <CheckCircle className="w-8 h-8 text-white" />
              </div>
            </div>
            <p className="text-gray-300 text-sm animate-fade-in">
              Closing automatically in 2 seconds...
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default GetNotify;