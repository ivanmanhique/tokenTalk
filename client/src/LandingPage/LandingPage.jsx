import React, { useState, useEffect } from 'react';
import {Link} from 'react-router-dom'
import { 
  ChevronRight, 
  Star, 
  Bell, 
  Shield, 
  Eye, 
  Globe, 
  TrendingUp, 
  ArrowRight,
  Play,
  Check,
  Menu,
  X,
  Github,
  Twitter,
  Linkedin,
  Mail,
  Phone,
  MapPin,
  Users,
  Award,
  Rocket,
  AlertTriangle,
  Heart,
  MessageCircle,
  Activity,
  Target,
  Smartphone,
  Zap
} from 'lucide-react';

const LandingPage = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [scrollY, setScrollY] = useState(0);
  const [currentTestimonial, setCurrentTestimonial] = useState(0);
  const [stats, setStats] = useState({
    currencies: 0,
    alerts: 0,
    users: 0,
    uptime: 0
  });

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Animate stats counter
  useEffect(() => {
    const animateStats = () => {
      const targets = { currencies: 5000, alerts: 150000, users: 25000, uptime: 99 };
      const duration = 2000;
      const steps = 60;
      
      let step = 0;
      const interval = setInterval(() => {
        step++;
        const progress = step / steps;
        const easeOut = 1 - Math.pow(1 - progress, 3);
        
        setStats({
          currencies: Math.floor(targets.currencies * easeOut),
          alerts: Math.floor(targets.alerts * easeOut),
          users: Math.floor(targets.users * easeOut),
          uptime: Math.floor(targets.uptime * easeOut)
        });
        
        if (step >= steps) clearInterval(interval);
      }, duration / steps);
    };

    const timer = setTimeout(animateStats, 1000);
    return () => clearTimeout(timer);
  }, []);

  // Auto-rotate testimonials
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTestimonial((prev) => (prev + 1) % testimonials.length);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const features = [
    {
      icon: Bell,
      title: "Smart Notifications",
      description: "Get instant alerts when your cryptocurrencies hit your target prices or percentage changes",
      gradient: "from-blue-400 to-indigo-500"
    },
    {
      icon: Eye,
      title: "Real-Time Tracking",
      description: "Monitor 5000+ cryptocurrencies with live price updates and comprehensive market data",
      gradient: "from-green-400 to-emerald-500"
    },
    {
      icon: Target,
      title: "Custom Parameters",
      description: "Set personalized alerts based on price, volume, market cap, or percentage changes",
      gradient: "from-purple-400 to-violet-500"
    },
    {
      icon: Smartphone,
      title: "Multi-Platform",
      description: "Receive notifications via email, SMS, push notifications, or in-app alerts",
      gradient: "from-orange-400 to-red-500"
    }
  ];

  const testimonials = [
    {
      name: "Alex Thompson",
      role: "Crypto Investor",
      image: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
      quote: "Never miss a market opportunity again. The alert system is incredibly precise and reliable.",
      rating: 5
    },
    {
      name: "Maria Santos",
      role: "Portfolio Manager",
      image: "https://images.unsplash.com/photo-1494790108755-2616b332c433?w=150&h=150&fit=crop&crop=face",
      quote: "The best crypto monitoring tool I've used. Clean interface and powerful notification system.",
      rating: 5
    },
    {
      name: "David Kim",
      role: "Day Trader",
      image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face",
      quote: "Real-time alerts have completely transformed how I track the crypto market. Essential tool!",
      rating: 5
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900  to-black text-white overflow-x-hidden">
      {/* Dark Geometric Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl"></div>
        <div className="absolute top-40 right-20 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 left-1/3 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl"></div>
        
        {/* Subtle grid pattern */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(99,102,241,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(99,102,241,0.05)_1px,transparent_1px)] bg-[size:50px_50px]"></div>
      </div>

      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 bg-gray-900/80 backdrop-blur-xl border-b border-gray-800/50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center">
                <Activity className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
                TokenTalk
              </span>
            </div>

            {/* Desktop Menu */}
            <div className="hidden md:flex items-center space-x-8">
              {['Features', 'Pricing', 'About', 'Contact'].map((item) => (
                <a
                  key={item}
                  href={`#${item.toLowerCase()}`}
                  className="text-gray-300 hover:text-white transition-colors duration-300 relative group font-medium"
                >
                  {item}
                  <div className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-blue-500 to-indigo-600 group-hover:w-full transition-all duration-300" />
                </a>
              ))}
              <button className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-6 py-2 rounded-full font-semibold hover:shadow-lg hover:shadow-blue-500/25 transition-all duration-300 transform hover:scale-105">
               <Link to="/Dashboard">Start Tracking</Link> 
              </button>
            </div>

            {/* Mobile Menu Button */}
            <button
              className="md:hidden text-white"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              {isMenuOpen ? <X /> : <Menu />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden bg-gray-900/95 backdrop-blur-xl border-t border-gray-800/50">
            <div className="px-6 py-4 space-y-4">
              {['Features', 'Pricing', 'About', 'Contact'].map((item) => (
                <a
                  key={item}
                  href={`#${item.toLowerCase()}`}
                  className="block text-gray-300 hover:text-white transition-colors"
                  onClick={() => setIsMenuOpen(false)}
                >
                  {item}
                </a>
              ))}
              <button className="w-full bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-6 py-2 rounded-full font-semibold">
                  <Link to="/Dashboard">Start Tracking</Link> 
              </button>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center pt-20">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <div 
            className="transform transition-all duration-1000"
            style={{ transform: `translateY(${scrollY * -0.05}px)` }}
          >
            <div className="inline-flex items-center space-x-2 bg-blue-500/10 backdrop-blur-xl rounded-full px-4 py-2 mb-8 border border-blue-500/20">
              <Bell className="w-4 h-4 text-blue-400" />
              <span className="text-sm text-blue-300 font-medium">Never miss a price movement again</span>
            </div>

            <h1 className="text-6xl md:text-8xl font-bold mb-6 leading-tight">
              <span className="bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
                Stay Ahead of
              </span>
              <br />
              <span className="bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">
                Crypto Markets
              </span>
            </h1>

            <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto leading-relaxed">
              Track 5000+ cryptocurrencies in real-time and get instant notifications when prices 
              hit your targets. Never miss an opportunity again.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6 mb-12">
              <button className="group bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-8 py-4 rounded-full font-semibold text-lg hover:shadow-2xl hover:shadow-blue-500/25 transition-all duration-300 transform hover:scale-105 flex items-center space-x-2">
                <span>  <Link to="/Dashboard">Start Monitoring Free</Link> </span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>
              <button className="group flex items-center space-x-3 px-8 py-4 rounded-full border border-gray-700 hover:border-gray-600 hover:bg-gray-800/50 transition-all duration-300">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-500/20 to-indigo-500/20 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform">
                  <Play className="w-6 h-6 ml-1 text-blue-400" />
                </div>
                <span className="text-lg text-gray-300">Watch Demo</span>
              </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mt-16">
              {[
                { label: 'Cryptocurrencies', value: stats.currencies, suffix: '+' },
                { label: 'Alerts Sent', value: stats.alerts, suffix: '+' },
                { label: 'Active Users', value: stats.users, suffix: '+' },
                { label: 'Uptime', value: stats.uptime, suffix: '%' }
              ].map((stat, index) => (
                <div key={index} className="text-center">
                  <div className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
                    {stat.value.toLocaleString()}{stat.suffix}
                  </div>
                  <div className="text-gray-400 mt-1">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
          <div className="w-6 h-10 border-2 border-gray-500 rounded-full flex justify-center">
            <div className="w-1 h-3 bg-gray-500 rounded-full mt-2 animate-pulse" />
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 relative">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-5xl font-bold mb-6 bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
              Powerful Monitoring Features
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Everything you need to stay on top of cryptocurrency markets with intelligent alerts and real-time tracking
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="group relative bg-gray-800/50 backdrop-blur-xl rounded-2xl p-8 border border-gray-700/50 hover:border-gray-600 hover:shadow-2xl hover:shadow-blue-500/10 transition-all duration-500 hover:transform hover:scale-105"
              >
                <div className={`w-16 h-16 bg-gradient-to-r ${feature.gradient} rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}>
                  <feature.icon className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold mb-4 text-white">{feature.title}</h3>
                <p className="text-gray-300 leading-relaxed">{feature.description}</p>
                
                {/* Hover Effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-indigo-500/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 relative bg-gray-800/30 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-5xl font-bold mb-6 bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
              How It Works
            </h2>
            <p className="text-xl text-gray-300">Get started in minutes with our simple three-step process</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            {[
              {
                step: "01",
                title: "Choose Your Coins",
                description: "Select from 5000+ cryptocurrencies to monitor, from Bitcoin to the newest DeFi tokens",
                icon: Eye
              },
              {
                step: "02",
                title: "Set Alert Parameters",
                description: "Define your price targets, percentage changes, volume thresholds, or market cap alerts",
                icon: Target
              },
              {
                step: "03",
                title: "Receive Notifications",
                description: "Get instant alerts via email, SMS, push notifications whenever your conditions are met",
                icon: Bell
              }
            ].map((step, index) => (
              <div key={index} className="text-center relative">
                <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mb-6 mx-auto">
                  <step.icon className="w-10 h-10 text-white" />
                </div>
                <div className="text-4xl font-bold text-blue-400 mb-4">{step.step}</div>
                <h3 className="text-2xl font-bold mb-4 text-white">{step.title}</h3>
                <p className="text-gray-300 leading-relaxed">{step.description}</p>
                
                {/* Connector Line */}
                {index < 2 && (
                  <div className="hidden md:block absolute top-10 left-full w-12 h-0.5 bg-gradient-to-r from-blue-400 to-indigo-400 transform -translate-x-6" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 relative">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-5xl font-bold mb-6 bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
              Trusted by Crypto Enthusiasts
            </h2>
            <p className="text-xl text-gray-300">See what our community is saying about CryptoWatch</p>
          </div>

          <div className="relative">
            <div className="flex items-center justify-center">
              <div className="max-w-4xl mx-auto">
                {testimonials.map((testimonial, index) => (
                  <div
                    key={index}
                    className={`transition-all duration-700 transform ${
                      index === currentTestimonial
                        ? 'opacity-100 scale-100'
                        : 'opacity-0 scale-95 absolute inset-0'
                    }`}
                  >
                    <div className="bg-gray-800/50 backdrop-blur-xl rounded-3xl p-12 border border-gray-700/50 text-center shadow-xl">
                      <div className="flex items-center justify-center mb-6">
                        {[...Array(5)].map((_, i) => (
                          <Star key={i} className="w-6 h-6 text-yellow-400 fill-current" />
                        ))}
                      </div>
                      <blockquote className="text-2xl font-light mb-8 text-gray-200 leading-relaxed">
                        "{testimonial.quote}"
                      </blockquote>
                      <div className="flex items-center justify-center space-x-4">
                        <img
                          src={testimonial.image}
                          alt={testimonial.name}
                          className="w-16 h-16 rounded-full border-2 border-gray-600"
                        />
                        <div>
                          <div className="font-bold text-white text-lg">{testimonial.name}</div>
                          <div className="text-gray-400">{testimonial.role}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Testimonial Dots */}
            <div className="flex items-center justify-center mt-8 space-x-3">
              {testimonials.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentTestimonial(index)}
                  className={`w-3 h-3 rounded-full transition-all duration-300 ${
                    index === currentTestimonial
                      ? 'bg-gradient-to-r from-blue-500 to-indigo-600 w-8'
                      : 'bg-gray-600 hover:bg-gray-500'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 relative">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <div className="bg-gradient-to-br from-blue-500/10 to-indigo-600/10 backdrop-blur-xl rounded-3xl p-12 border border-blue-500/20">
            <h2 className="text-5xl font-bold mb-6 bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
              Start Tracking Crypto Today
            </h2>
            <p className="text-xl text-gray-300 mb-8 leading-relaxed">
              Join thousands who never miss a market movement. Get real-time alerts, 
              comprehensive tracking, and stay ahead of the market.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
              <button className="group bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-8 py-4 rounded-full font-semibold text-lg hover:shadow-2xl hover:shadow-blue-500/25 transition-all duration-300 transform hover:scale-105 flex items-center space-x-2">
                <span>Get Started Free</span>
                <Zap className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>
              <button className="px-8 py-4 rounded-full border border-gray-600 hover:border-gray-500 hover:bg-gray-800/50 transition-all duration-300 text-lg text-gray-300">
                View Pricing
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800/50 bg-gray-900/50 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center">
                  <Activity className="w-6 h-6 text-white" />
                </div>
                <span className="text-xl font-bold text-white">CryptoWatch</span>
              </div>
              <p className="text-gray-400 mb-6 max-w-md">
                The most reliable cryptocurrency monitoring platform with intelligent alerts and real-time tracking.
              </p>
              <div className="flex space-x-4">
                {[Twitter, Github, Linkedin].map((Icon, index) => (
                  <button
                    key={index}
                    className="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-gray-700 transition-all duration-300 hover:scale-110"
                  >
                    <Icon className="w-5 h-5 text-gray-400" />
                  </button>
                ))}
              </div>
            </div>

            <div>
              <h3 className="font-semibold mb-4 text-white">Product</h3>
              <ul className="space-y-2 text-gray-400">
                {['Features', 'Pricing', 'API', 'Documentation'].map((item) => (
                  <li key={item}>
                    <a href="#" className="hover:text-white transition-colors">{item}</a>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4 text-white">Support</h3>
              <ul className="space-y-2 text-gray-400">
                {['Help Center', 'Contact', 'Status', 'Updates'].map((item) => (
                  <li key={item}>
                    <a href="#" className="hover:text-white transition-colors">{item}</a>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800/50 mt-12 pt-8 flex flex-col md:flex-row items-center justify-between text-gray-400">
            <p>&copy; 2024 CryptoWatch. All rights reserved.</p>
            <div className="flex space-x-6 mt-4 md:mt-0">
              <a href="#" className="hover:text-white transition-colors">Privacy</a>
              <a href="#" className="hover:text-white transition-colors">Terms</a>
              <a href="#" className="hover:text-white transition-colors">Cookies</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;