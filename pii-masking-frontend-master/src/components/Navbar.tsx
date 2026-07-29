import React from 'react';
import { useLocation } from 'react-router-dom';

const Navbar: React.FC = () => {
  let locationPath = '/';
  try {
    const loc = useLocation();
    locationPath = loc.pathname;
  } catch (e) {
    locationPath = window.location.pathname;
  }

  const navItems = [
    { label: 'Interactive Workbench', path: '/' },
    { label: 'Batch Processing', path: '/batch' },
    { label: 'HITL Review', path: '/preview' },
    { label: 'Audit Ledger', path: '/audit' },
    { label: 'Analytics & Compliance', path: '/analytics' },
  ];

  return (
    <nav className="flex items-center justify-center sticky top-0 z-20 bg-slate-950/80 backdrop-blur-md border-b border-slate-800/80 md:h-[80px]">
      <div className="max-w-[1440px] w-full px-6 py-3 flex flex-col md:flex-row justify-between items-center gap-4">
        <a href="/" className="flex items-center gap-3 outline-none">
          <div className="flex items-center gap-2">
            <span className="bg-indigo-600 text-white p-2 rounded-xl text-base shadow-lg shadow-indigo-500/30">🔒</span>
            <span className="text-xl font-black tracking-tight text-white">PII<span className="text-indigo-400">Shield</span></span>
          </div>
          <span className="bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-xs font-semibold px-2.5 py-0.5 rounded-full uppercase tracking-wider">
            Enterprise Local
          </span>
        </a>

        <div className="flex items-center gap-1 bg-slate-900/90 p-1.5 rounded-xl border border-slate-800 text-xs font-medium">
          {navItems.map((item) => {
            const isActive = locationPath === item.path;
            return (
              <a
                key={item.path}
                href={item.path}
                className={`px-3.5 py-2 rounded-lg transition-all ${
                  isActive
                    ? 'bg-indigo-600 text-white font-semibold shadow-md shadow-indigo-500/20'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                {item.label}
              </a>
            );
          })}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;