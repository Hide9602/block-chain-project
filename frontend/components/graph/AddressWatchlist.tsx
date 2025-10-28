'use client';

import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

interface WatchlistAddress {
  id: string;
  address: string;
  label: string;
  riskLevel: 'critical' | 'high' | 'medium' | 'low' | 'none';
  riskScore: number;
  addedAt: string;
  lastChecked?: string;
  notes?: string;
  alertsCount: number;
  tags: string[];
}

interface AddressWatchlistProps {
  addresses: WatchlistAddress[];
  onAddAddress?: (address: string, label: string) => void;
  onRemoveAddress?: (id: string) => void;
  onAddressClick?: (address: WatchlistAddress) => void;
  onRefresh?: (id: string) => void;
  className?: string;
}

export const AddressWatchlist: React.FC<AddressWatchlistProps> = ({
  addresses,
  onAddAddress,
  onRemoveAddress,
  onAddressClick,
  onRefresh,
  className = '',
}) => {
  const { t } = useTranslation('glossary');
  const [showAddForm, setShowAddForm] = useState(false);
  const [newAddress, setNewAddress] = useState('');
  const [newLabel, setNewLabel] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  const getRiskColor = (riskLevel: string): string => {
    switch (riskLevel) {
      case 'critical':
        return 'bg-red-600 text-white';
      case 'high':
        return 'bg-orange-500 text-white';
      case 'medium':
        return 'bg-yellow-500 text-white';
      case 'low':
        return 'bg-green-500 text-white';
      default:
        return 'bg-gray-400 text-white';
    }
  };

  const handleAddAddress = () => {
    if (newAddress && newLabel && onAddAddress) {
      onAddAddress(newAddress, newLabel);
      setNewAddress('');
      setNewLabel('');
      setShowAddForm(false);
    }
  };

  // Filter addresses by search term
  const filteredAddresses = addresses.filter(addr =>
    addr.address.toLowerCase().includes(searchTerm.toLowerCase()) ||
    addr.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
    addr.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  // Sort by risk level (critical first)
  const sortedAddresses = [...filteredAddresses].sort((a, b) => {
    const riskOrder = { critical: 4, high: 3, medium: 2, low: 1, none: 0 };
    return (riskOrder[b.riskLevel as keyof typeof riskOrder] || 0) - 
           (riskOrder[a.riskLevel as keyof typeof riskOrder] || 0);
  });

  return (
    <div className={`rounded-lg bg-white shadow-lg ${className}`}>
      {/* Header */}
      <div className="border-b border-gray-200 p-4">
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-lg font-bold">
            {t('watchlist.title', 'Watchlist')}
          </h3>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">
              {addresses.length} {addresses.length === 1 ? 'address' : 'addresses'}
            </span>
            {onAddAddress && (
              <button
                onClick={() => setShowAddForm(!showAddForm)}
                className="rounded bg-blue-600 px-3 py-1 text-sm font-bold text-white hover:bg-blue-700"
              >
                + Add
              </button>
            )}
          </div>
        </div>

        {/* Search bar */}
        <input
          type="text"
          placeholder="Search addresses, labels, or tags..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full rounded border px-3 py-2 text-sm"
        />
      </div>

      {/* Add address form */}
      {showAddForm && (
        <div className="border-b border-gray-200 bg-gray-50 p-4">
          <div className="mb-2">
            <label className="mb-1 block text-xs font-semibold">Address</label>
            <input
              type="text"
              placeholder="0x..."
              value={newAddress}
              onChange={(e) => setNewAddress(e.target.value)}
              className="w-full rounded border px-3 py-2 text-sm"
            />
          </div>
          <div className="mb-3">
            <label className="mb-1 block text-xs font-semibold">Label</label>
            <input
              type="text"
              placeholder="e.g., Suspected mixer"
              value={newLabel}
              onChange={(e) => setNewLabel(e.target.value)}
              className="w-full rounded border px-3 py-2 text-sm"
            />
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleAddAddress}
              disabled={!newAddress || !newLabel}
              className="flex-1 rounded bg-blue-600 px-3 py-2 text-sm font-bold text-white hover:bg-blue-700 disabled:bg-gray-300"
            >
              Add to Watchlist
            </button>
            <button
              onClick={() => {
                setShowAddForm(false);
                setNewAddress('');
                setNewLabel('');
              }}
              className="flex-1 rounded border border-gray-300 px-3 py-2 text-sm font-bold text-gray-700 hover:bg-gray-100"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Address list */}
      <div className="max-h-96 overflow-y-auto p-4">
        {sortedAddresses.length === 0 ? (
          <div className="py-8 text-center text-gray-500">
            {searchTerm ? (
              <>
                <div className="mb-2 text-4xl">🔍</div>
                <p>No addresses match your search</p>
              </>
            ) : (
              <>
                <div className="mb-2 text-4xl">👁️</div>
                <p>No addresses in watchlist</p>
                <p className="mt-1 text-sm">Add addresses to monitor their activity</p>
              </>
            )}
          </div>
        ) : (
          <div className="space-y-2">
            {sortedAddresses.map((addr) => (
              <div
                key={addr.id}
                className="group cursor-pointer rounded-lg border border-gray-200 p-3 transition-all hover:border-blue-500 hover:shadow-md"
                onClick={() => onAddressClick && onAddressClick(addr)}
              >
                <div className="mb-2 flex items-start justify-between">
                  <div className="flex-1">
                    <div className="mb-1 flex items-center gap-2">
                      <h4 className="font-bold text-gray-900">{addr.label}</h4>
                      {addr.alertsCount > 0 && (
                        <span className="flex items-center gap-1 rounded-full bg-red-100 px-2 py-0.5 text-xs font-bold text-red-800">
                          🚨 {addr.alertsCount}
                        </span>
                      )}
                    </div>
                    <p className="font-mono text-xs text-gray-600">
                      {addr.address.substring(0, 12)}...{addr.address.substring(addr.address.length - 8)}
                    </p>
                  </div>
                  <div className="flex gap-1">
                    {onRefresh && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onRefresh(addr.id);
                        }}
                        className="rounded p-1 text-gray-400 opacity-0 hover:bg-gray-100 hover:text-gray-600 group-hover:opacity-100"
                        title="Refresh"
                      >
                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                      </button>
                    )}
                    {onRemoveAddress && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onRemoveAddress(addr.id);
                        }}
                        className="rounded p-1 text-gray-400 opacity-0 hover:bg-red-100 hover:text-red-600 group-hover:opacity-100"
                        title="Remove"
                      >
                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    )}
                  </div>
                </div>

                <div className="mb-2 flex items-center gap-2">
                  <span className={`rounded px-2 py-1 text-xs font-bold uppercase ${getRiskColor(addr.riskLevel)}`}>
                    {addr.riskLevel}
                  </span>
                  <span className="text-xs font-bold text-gray-700">
                    Score: {addr.riskScore.toFixed(1)}/100
                  </span>
                </div>

                {addr.tags.length > 0 && (
                  <div className="mb-2 flex flex-wrap gap-1">
                    {addr.tags.map((tag, idx) => (
                      <span key={idx} className="rounded bg-blue-100 px-2 py-1 text-xs text-blue-800">
                        {tag}
                      </span>
                    ))}
                  </div>
                )}

                {addr.notes && (
                  <p className="mb-2 text-xs text-gray-600">{addr.notes}</p>
                )}

                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>Added: {new Date(addr.addedAt).toLocaleDateString()}</span>
                  {addr.lastChecked && (
                    <span>Last checked: {new Date(addr.lastChecked).toLocaleString()}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer stats */}
      {sortedAddresses.length > 0 && (
        <div className="border-t border-gray-200 p-4">
          <div className="grid grid-cols-4 gap-2 text-center text-xs">
            <div>
              <div className="font-bold text-red-600">
                {addresses.filter(a => a.riskLevel === 'critical').length}
              </div>
              <div className="text-gray-600">Critical</div>
            </div>
            <div>
              <div className="font-bold text-orange-600">
                {addresses.filter(a => a.riskLevel === 'high').length}
              </div>
              <div className="text-gray-600">High</div>
            </div>
            <div>
              <div className="font-bold text-yellow-600">
                {addresses.filter(a => a.riskLevel === 'medium').length}
              </div>
              <div className="text-gray-600">Medium</div>
            </div>
            <div>
              <div className="font-bold text-blue-600">
                {addresses.reduce((sum, a) => sum + a.alertsCount, 0)}
              </div>
              <div className="text-gray-600">Total Alerts</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AddressWatchlist;
