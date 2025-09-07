import { useState  , useEffect} from "react";
import { TrendingUp, TrendingDown, Wallet, BellRing ,BarChart3, PieChart, Settings, Bell, Search, Filter, Star, ArrowUpRight, ArrowDownRight, Eye, EyeOff, RefreshCw, Zap, Shield, Globe, Sidebar } from 'lucide-react';
import '../../App.css'
const SummaryCards = ({setIsgetnotify})=>{

  const [isBalanceVisible, setIsBalanceVisible] = useState(true);
  const portfolioChange = 500;
   const [currentSuggestion, setCurrentSuggestion] = useState(0);
  
  const suggestions = [
    "I'm worried about my AAVE position, tell me if it falls 25%",
    "Alert me when Bitcoin reaches $100,000", 
    "Notify me if Ethereum drops below $3,000"
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSuggestion((prev) => (prev + 1) % suggestions.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);
return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="col-span-1 md:col-span-1 bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl rounded-2xl p-6 border border-white/10 hover:border-white/20 transition-all duration-500 group">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-gray-400 text-sm">Total Portfolio Value</p>
                <div className="flex items-center space-x-2 mt-1">
                  <h2 className="text-3xl font-bold">
                    {isBalanceVisible ? "$" + portfolioChange  : '••••••••'}   {/* wallet value */}
                  </h2>
                  <button 
                    onClick={() => setIsBalanceVisible(!isBalanceVisible)}
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    {isBalanceVisible ? <Eye className="w-5 h-5" /> : <EyeOff className="w-5 h-5" />}
                  </button>
                </div>
              </div>
              <Wallet className="w-8 h-8 text-purple-400 group-hover:scale-110 transition-transform duration-300" />
            </div>
            <div className="flex items-center space-x-2">
              {portfolioChange >= 0 ? (
                <TrendingUp className="w-4 h-4 text-green-400" />
              ) : (
                <TrendingDown className="w-4 h-4 text-red-400" />
              )}
              <span className={`text-sm font-medium ${portfolioChange >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {portfolioChange >= 0 ? '+' : ''}{portfolioChange.toFixed(2)}% (24h)
              </span>
            </div>
          </div>
           <div onClick={() => setIsgetnotify(prev => !prev)} className="bg-gradient-to-br px-10 col-span-1 md:col-span-3 from-white/10 to-white/5 backdrop-blur-xl rounded-2xl p-6 border border-white/10  transition-all duration-500 group">
            <div className="flex items-center justify-between mb-4">
               <div>
                <p className="text-gray-400 text-sm">Get Notify</p>
                <h3 className="text-xl font-bold">TRACK COINS</h3>
              </div>
                 <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                <BellRing className="w-5 h-5" />
              </div>
         
            </div>
                <input 
                value={suggestions[currentSuggestion]} 
                type="text"
                 readOnly
                key={currentSuggestion}
                 style={{animation: 'fadeInUp 0.5s ease-out'}}
                className="w-full focus:outline-none text-gray-400 bg-white/10 px-4 py-3 rounded-2xl" />
          </div>
        </div>
);
            }
export default SummaryCards;