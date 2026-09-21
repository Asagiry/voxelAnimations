import React, { useState } from 'react';
import { AssetManifestItem } from '../types';

interface AssetSidebarProps {
  assets: AssetManifestItem[];
  activeId: string | null;
  onSelect: (asset: AssetManifestItem) => void;
  onRefresh: () => void;
  isLoading: boolean;
}

export const AssetSidebar: React.FC<AssetSidebarProps> = ({
  assets,
  activeId,
  onSelect,
  onRefresh,
  isLoading,
}) => {
  const [filter, setFilter] = useState('');

  const filteredAssets = assets.filter(
    a =>
      a.name.toLowerCase().includes(filter.toLowerCase()) ||
      a.folder.toLowerCase().includes(filter.toLowerCase())
  );

  const formatSize = (bytes: number) => {
    if (!bytes) return '';
    if (bytes > 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    return `${Math.round(bytes / 1024)} KB`;
  };

  return (
    <aside
      style={{
        width: 320,
        height: '100%',
        backgroundColor: 'var(--bg-panel)',
        borderRight: '1px solid var(--border)',
        display: 'flex',
        flexDirection: 'column',
        flexShrink: 0,
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: '16px',
          borderBottom: '1px solid var(--border)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <div>
          <h2 style={{ fontSize: 14, fontWeight: 700, letterSpacing: '0.02em' }}>
            Voxel Assets
          </h2>
          <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
            {assets.length} models detected
          </span>
        </div>
        <button
          onClick={onRefresh}
          disabled={isLoading}
          style={{
            padding: '6px 10px',
            background: 'var(--bg-surface)',
            border: '1px solid var(--border)',
            borderRadius: 4,
            fontSize: 11,
            fontWeight: 500,
            opacity: isLoading ? 0.5 : 1,
          }}
        >
          {isLoading ? 'Scanning...' : 'Scan Assets'}
        </button>
      </div>

      {/* Filter Input */}
      <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border)' }}>
        <input
          type="text"
          placeholder="Filter models..."
          value={filter}
          onChange={e => setFilter(e.target.value)}
          style={{
            width: '100%',
            padding: '7px 10px',
            backgroundColor: 'var(--bg-surface)',
            border: '1px solid var(--border)',
            borderRadius: 4,
            color: 'var(--text-primary)',
            fontSize: 12,
            outline: 'none',
          }}
        />
      </div>

      {/* Asset List */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '8px' }}>
        {filteredAssets.length === 0 ? (
          <div style={{ padding: '24px 16px', textAlign: 'center', color: 'var(--text-muted)' }}>
            No models found
          </div>
        ) : (
          filteredAssets.map(asset => {
            const isActive = asset.id === activeId;
            return (
              <button
                key={asset.id}
                type="button"
                data-asset-id={asset.id}
                onClick={() => onSelect(asset)}
                style={{
                  width: '100%',
                  textAlign: 'left',
                  padding: '8px 10px',
                  borderRadius: 6,
                  marginBottom: 4,
                  cursor: 'pointer',
                  backgroundColor: isActive ? 'var(--bg-active)' : 'transparent',
                  border: `1px solid ${isActive ? 'var(--border-focus)' : 'transparent'}`,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                  transition: 'background-color 0.15s',
                }}
              >
                {/* Thumbnail */}
                <div
                  style={{
                    width: 44,
                    height: 44,
                    borderRadius: 4,
                    backgroundColor: 'var(--bg-surface)',
                    border: '1px solid var(--border)',
                    overflow: 'hidden',
                    flexShrink: 0,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  {asset.renderUrl ? (
                    <img
                      src={asset.renderUrl}
                      alt={asset.name}
                      style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                    />
                  ) : (
                    <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>3D</div>
                  )}
                </div>

                {/* Details */}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div
                    style={{
                      fontSize: 12,
                      fontWeight: 600,
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      color: isActive ? '#38bdf8' : 'var(--text-primary)',
                    }}
                  >
                    {asset.name}
                  </div>
                  <div
                    style={{
                      fontSize: 11,
                      color: 'var(--text-muted)',
                      display: 'flex',
                      justifyContent: 'space-between',
                      marginTop: 2,
                      fontFamily: 'var(--font-mono)',
                    }}
                  >
                    <span>{asset.folder}</span>
                    <span>{formatSize(asset.sizeBytes)}</span>
                  </div>
                </div>
              </button>
            );
          })
        )}
      </div>
    </aside>
  );
};
