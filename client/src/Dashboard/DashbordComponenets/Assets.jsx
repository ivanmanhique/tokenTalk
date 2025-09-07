import { useEffect, useState } from "react";
import { TrendingUp, TrendingDown, Wallet, BarChart3, PieChart, Settings, Bell, Search, Filter, Star, ArrowUpRight, ArrowDownRight, Eye, EyeOff, RefreshCw, Zap, Shield, Globe, Sidebar, ChevronLeft, ChevronRight, X } from 'lucide-react';
import useFetch from '../../hook/useFetch'


const Assets = () => {
  const { data, error, loading, callData } = useFetch("https://api.redstone.finance/prices?provider=redstone");
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [showFilter, setShowFilter] = useState(false);
  const [sortBy, setSortBy] = useState('price');
  const [sortOrder, setSortOrder] = useState('desc');
  const [priceRange, setPriceRange] = useState({ min: '', max: '' });

  async function getCurrenciesValues() {
    const cvalues = await callData();
    if (!cvalues) return;
  }

  useEffect(() => {
    getCurrenciesValues();
  }, []);

  // Filter and sort data
  const getFilteredAndSortedData = () => {
    if (!data) return [];
    
    let filtered = Object.keys(data).filter(key => {
      const crypto = data[key];
      const matchesSearch = crypto.symbol?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           key.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesPrice = (!priceRange.min || crypto.value >= parseFloat(priceRange.min)) &&
                          (!priceRange.max || crypto.value <= parseFloat(priceRange.max));
      
      return matchesSearch && matchesPrice;
    });

    // Sort data
    filtered.sort((a, b) => {
      let valueA, valueB;
      
      switch (sortBy) {
        case 'symbol':
          valueA = data[a].symbol || a;
          valueB = data[b].symbol || b;
          break;
        case 'price':
          valueA = parseFloat(data[a].value) || 0;
          valueB = parseFloat(data[b].value) || 0;
          break;
        default:
          valueA = data[a].symbol || a;
          valueB = data[b].symbol || b;
      }
      
      if (typeof valueA === 'string') {
        return sortOrder === 'asc' 
          ? valueA.localeCompare(valueB)
          : valueB.localeCompare(valueA);
      }
      
      return sortOrder === 'asc' ? valueA - valueB : valueB - valueA;
    });

    return filtered;
  };

  // Pagination logic
  const filteredData = getFilteredAndSortedData();
  const totalPages = Math.ceil(filteredData.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentData = filteredData.slice(startIndex, endIndex);

  // Reset to first page when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, priceRange, sortBy, sortOrder]);

  const clearFilters = () => {
    setSearchTerm('');
    setPriceRange({ min: '', max: '' });
    setSortBy('symbol');
    setSortOrder('asc');
  };

  const cryptochange24h = 3.12; // You can modify this to use real data

  // Enhanced Loading component
  if (loading) {
    return (
      <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl rounded-2xl border border-white/10 overflow-hidden">
        <div className="flex items-center justify-between p-6 border-b border-white/10">
          <h3 className="text-xl font-bold">Your Assets</h3>
          <div className="flex items-center space-x-2">
            <div className="w-20 h-10 bg-white/5 rounded-xl animate-pulse"></div>
            <div className="w-24 h-10 bg-white/5 rounded-xl animate-pulse"></div>
          </div>
        </div>
        
        <div className="p-8 flex flex-col items-center justify-center space-y-4">
          <RefreshCw className="w-12 h-12 text-purple-400 animate-spin" />
          <div className="text-center">
            <h4 className="text-lg font-medium text-white mb-2">Loading Assets</h4>
            <p className="text-gray-400">Fetching the latest crypto data...</p>
          </div>
          
          {/* Loading skeleton */}
          <div className="w-full max-w-4xl space-y-3 mt-8">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="flex items-center space-x-4 p-4 bg-white/5 rounded-xl animate-pulse">
                <div className="w-10 h-10 bg-white/10 rounded-xl"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-white/10 rounded w-1/4"></div>
                  <div className="h-3 bg-white/5 rounded w-1/6"></div>
                </div>
                <div className="space-y-2">
                  <div className="h-4 bg-white/10 rounded w-20"></div>
                  <div className="h-3 bg-white/5 rounded w-16"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-8 text-center">
        <div className="text-red-400 mb-4 text-lg font-medium">Error loading data</div>
        <p className="text-gray-400 mb-4">Failed to fetch cryptocurrency data</p>
        <button 
          onClick={getCurrenciesValues}
          className="px-6 py-3 bg-gradient-to-r from-purple-500 to-cyan-500 rounded-xl hover:shadow-lg hover:shadow-purple-500/25 transition-all duration-300 font-medium"
        >
          <RefreshCw className="w-4 h-4 inline mr-2" />
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl rounded-2xl border border-white/10 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-white/10">
        <h3 className="text-xl font-bold">Your Assets</h3>
        <div className="flex items-center space-x-2">
          <button 
            onClick={() => setShowFilter(!showFilter)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-xl transition-all duration-300 ${
              showFilter ? 'bg-purple-500/20 text-purple-400' : 'bg-white/5 hover:bg-white/10'
            }`}
          >
            <Filter className="w-4 h-4" />
            <span className="text-sm">Filter</span>
          </button>
         
        </div>
      </div>

      {/* Filter Panel */}
      {showFilter && (
        <div className="p-6 border-b border-white/10 bg-white/5">
          <div className="flex flex-wrap items-center gap-4">
            {/* Search */}
            <div className="relative flex-1 min-w-64">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search assets..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-400"
              />
            </div>

            {/* Price Range */}
            <div className="flex items-center space-x-2">
              <input
                type="number"
                placeholder="Min $"
                value={priceRange.min}
                onChange={(e) => setPriceRange(prev => ({ ...prev, min: e.target.value }))}
                className="w-24 px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-400"
              />
              <span className="text-gray-400">-</span>
              <input
                type="number"
                placeholder="Max $"
                value={priceRange.max}
                onChange={(e) => setPriceRange(prev => ({ ...prev, max: e.target.value }))}
                className="w-24 px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-400"
              />
            </div>

            {/* Sort */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-purple-400"
            >
            <option value="price" className="bg-gray-800">Price</option>
              <option value="symbol" className="bg-gray-800">Name</option>
             
            </select>

            <button
              onClick={() => setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc')}
              className="px-3 py-2 bg-white/10 border border-white/20 rounded-lg hover:bg-white/20 transition-colors"
            >
              {sortOrder === 'asc' ? '↑' : '↓'}
            </button>

            {/* Clear Filters */}
            {(searchTerm || priceRange.min || priceRange.max) && (
              <button
                onClick={clearFilters}
                className="flex items-center space-x-1 px-3 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors"
              >
                <X className="w-4 h-4" />
                <span className="text-sm">Clear</span>
              </button>
            )}
          </div>
        </div>
      )}

      {/* Results Info */}
      <div className="px-6 py-3 bg-white/5 border-b border-white/10 text-sm text-gray-400">
        Showing {currentData.length} of {filteredData.length} assets
      </div>

      {/* Table */}
      
      <div className="overflow-x-auto">
        <div className="overflow-x-auto">
  <table className="w-full">
    <thead>
      <tr className="border-b border-white/10">
        <th className="text-left py-4 px-6 text-gray-400 font-medium">Asset</th>
        <th className="text-left py-4 px-6 text-gray-400 font-medium">Price</th>
        <th className="text-left py-4 px-6 text-gray-400 font-medium">Provider</th>
        <th className="text-left py-4 px-6 text-gray-400 font-medium">Chart</th>
      </tr>
    </thead>
    <tbody>
      {currentData.map((key, index) => {
        // Generate fake chart data for each crypto
        const generateChartPath = (isPositive) => {
            const points = [];
            const width = 64;
            const height = 32;
            let currentY = height / 2;

            for (let i = 0; i <= 12; i++) {
                const x = (i / 12) * width;

                // bias the variance: up if positive, down if negative
                const bias = isPositive ? -1 : 1; // SVG y-axis: smaller = higher
                const variance = (Math.random() - 0.5) * 6 + bias * 1.5;

                currentY = Math.max(4, Math.min(height - 4, currentY + variance));
                points.push(`${x},${currentY}`);
            }

            return `M${points.join(" L")}`;
            };

        // Get 3-letter symbol
        const getSymbol = (key) => {
          const symbolMap = {
            'bitcoin': 'BTC',
            'ethereum': 'ETH',
            'cardano': 'ADA',
            'polkadot': 'DOT',
            'chainlink': 'LNK',
            'litecoin': 'LTC',
            'stellar': 'XLM',
            'uniswap': 'UNI',
            'solana': 'SOL',
            'avalanche': 'AVA'
          };
          return symbolMap[key] || key.substring(0, 3).toUpperCase();
        };

        const isPositive = cryptochange24h >= 0;
        
        return (
          <tr
            key={key}
            className="border-b border-white/5 hover:bg-white/5 transition-all duration-300 group cursor-pointer"
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <td className="py-4 px-6">
              <div className="flex items-center space-x-4">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                  <span className="text-white font-bold text-xs">
                    {getSymbol(key)}
                  </span>
                </div>
                <div>
                  <h4 className="font-medium">{data[key].symbol || key}</h4>
                  <p className="text-gray-400 text-sm">{key}</p>
                </div>
                <button className="opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <Star className="w-4 h-4 text-gray-400 hover:text-yellow-400" />
                </button>
              </div>
            </td>
            <td className="py-4 px-6 ">
              <span className="font-medium">${parseFloat(data[key].value).toFixed(2)}</span>
            </td>
           
            <td className="py-4 px-6 ">
              <div>
                <p className="text-gray-400 text-xs">${data[key].provider}</p>
              </div>
            </td>
           
            <td className="py-4 px-6  ">
              <div className="w-16 h-8 relative justify-right">
                <svg 
                  className="w-full h-full" 
                  viewBox="0 0 64 32" 
                  preserveAspectRatio="none"
                >
                  <defs>
                    <linearGradient id={`gradient-${index}`} x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop 
                        offset="0%" 
                        stopColor={isPositive ? '#10b981' : '#ef4444'} 
                        stopOpacity="0.3"
                      />
                      <stop 
                        offset="100%" 
                        stopColor={isPositive ? '#10b981' : '#ef4444'} 
                        stopOpacity="0"
                      />
                    </linearGradient>
                  </defs>
                  <path
                    d={`${generateChartPath()} L64,32 L0,32 Z`}
                    fill={`url(#gradient-${index})`}
                  />
                  <path
                    d={generateChartPath()}
                    fill="none"
                    stroke={isPositive ? '#10b981' : '#ef4444'}
                    strokeWidth="1.5"
                    className="opacity-80"
                  />
                </svg>
                {/* Hover overlay */}
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </div>
            </td>
          </tr>
        );
      })}
    </tbody>
  </table>
</div>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between p-6 border-t border-white/10">
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-400">Show</span>
            <select
              value={itemsPerPage}
              onChange={(e) => setItemsPerPage(Number(e.target.value))}
              className="px-2 py-1 bg-white/10 border border-white/20 rounded text-white text-sm focus:outline-none focus:border-purple-400"
            >
              <option value={5} className="bg-gray-800">5</option>
              <option value={10} className="bg-gray-800">10</option>
              <option value={20} className="bg-gray-800">20</option>
              <option value={50} className="bg-gray-800">50</option>
            </select>
            <span className="text-sm text-gray-400">per page</span>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
              className="flex items-center px-3 py-2 bg-white/10 rounded-lg hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>

            <div className="flex items-center space-x-1">
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                let pageNum;
                if (totalPages <= 5) {
                  pageNum = i + 1;
                } else if (currentPage <= 3) {
                  pageNum = i + 1;
                } else if (currentPage >= totalPages - 2) {
                  pageNum = totalPages - 4 + i;
                } else {
                  pageNum = currentPage - 2 + i;
                }

                return (
                  <button
                    key={pageNum}
                    onClick={() => setCurrentPage(pageNum)}
                    className={`px-3 py-2 rounded-lg transition-colors ${
                      currentPage === pageNum
                        ? 'bg-purple-500 text-white'
                        : 'bg-white/10 hover:bg-white/20'
                    }`}
                  >
                    {pageNum}
                  </button>
                );
              })}
            </div>

            <button
              onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
              disabled={currentPage === totalPages}
              className="flex items-center px-3 py-2 bg-white/10 rounded-lg hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>

          <div className="text-sm text-gray-400">
            Page {currentPage} of {totalPages}
          </div>
        </div>
      )}
    </div>
  );
};

export default Assets;