import {  Bell, Search, RefreshCw ,User} from 'lucide-react';


const HeaderDashbord = ({searchTerm, setSearchTerm})=>{
    return(
       <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
              TokenTalk
            </h1>
            <p className="text-gray-400 mt-1">Track your crypto investments in real-time</p>
          </div>
          
          <div className="flex items-center space-x-4">
           
            
            {/* Notifications */}
            <button className="relative w-10 h-10 bg-white/5 backdrop-blur-xl rounded-xl border border-white/10 flex items-center justify-center hover:bg-white/10 transition-all duration-300">
              <Bell className="w-5 h-5" />
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
            </button>
            
            {/* Refresh */}
            <button className="w-10 h-10 bg-white/5 backdrop-blur-xl rounded-xl border border-white/10 flex items-center justify-center hover:bg-white/10 transition-all duration-300 hover:rotate-180">
              <RefreshCw className="w-5 h-5" />
            </button>
            <button className="w-10 h-10 bg-white/5 backdrop-blur-xl rounded-xl border border-white/10 flex items-center justify-center hover:bg-white/10 transition-all duration-300 ">
              <User className="w-5 h-5" />
            </button>
          </div>
        </div>
    );
}
export default HeaderDashbord