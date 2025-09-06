import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Wallet, BarChart3, PieChart, Settings, Bell, Search, Filter, Star, ArrowUpRight, ArrowDownRight, Eye, EyeOff, RefreshCw, Zap, Shield, Globe, Sidebar } from 'lucide-react';
import SideBar from './DashbordComponenets/SideBar';
import HeaderDashbord from './DashbordComponenets/HeaderDashbord'
import SummaryCards from './DashbordComponenets/SummaryCards'
import Assets from './DashbordComponenets/Assets';
import GetNotify from './DashbordComponenets/GetNotify'
const Dashboard = () => {
 
  const [activeTab, setActiveTab] = useState('overview');
  const [isgetnotify  , setIsgetnotify] = useState(false);


  return (
    <div className="min-h-screen bg-black text-white overflow-hidden">
     

      {/* Sidebar */}
      <SideBar activeTab={activeTab} setActiveTab = {setActiveTab}/>

      {/* Main Content */}
      <div className="ml-20 p-6">
                {/* Header */}
              <HeaderDashbord />

                {/* Portfolio Summary Cards */}
              <SummaryCards setIsgetnotify={setIsgetnotify} />
              {isgetnotify && <GetNotify setIsgetnotify={setIsgetnotify}/>}
            

        {/* Crypto Assets Table */}
        <Assets />

      
      </div>
    </div>
  );
};

export default Dashboard;