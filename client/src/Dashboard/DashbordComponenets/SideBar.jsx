import { TrendingUp, TrendingDown, Wallet, BarChart3, PieChart, Settings, Bell, Search, Filter, Star, ArrowUpRight, ArrowDownRight, Eye, EyeOff, RefreshCw, Zap, Shield, Globe, Sidebar } from 'lucide-react';
import {Link} from 'react-router-dom'
   const SideBar = ({activeTab , setActiveTab})=>{
   return(
   <div className="fixed left-0 top-0 h-full w-20 bg-black/20 backdrop-blur-xl border-r border-white/10 z-40 flex flex-col items-center py-6">
        <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-cyan-500 rounded-xl mb-8 flex items-center justify-center">
          <Zap className="w-6 h-6" />
        </div>
        
        <nav className="flex flex-col space-y-4 flex-1">
          {[
            { icon: BarChart3, id: 'overview', active: true },
            { icon: Wallet, id: 'wallet' },
            { icon: PieChart, id: 'analytics' },
            { icon: Shield, id: 'security' },
            { icon: Globe, id: 'defi' },
            { icon: Settings, id: 'settings' }
          ].map(({ icon: Icon, id, active }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className={`w-12 h-12 rounded-xl flex items-center justify-center transition-all duration-300 ${
                activeTab === id
                  ? 'bg-gradient-to-br from-purple-500 to-cyan-500 shadow-lg shadow-purple-500/25'
                  : 'hover:bg-white/10 text-gray-400 hover:text-white'
              }`}
            >
             <Link to="/"> <Icon className="w-5 h-5" />  </Link>
            </button>
          ))}
        </nav>
      </div>
   );
   }
   export default SideBar;