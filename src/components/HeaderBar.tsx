import React from 'react';
import { ModelStats, WeaponOption } from '../types';

interface HeaderBarProps {
  modelName: string;
  stats: ModelStats | null;
  showGrid: boolean;
  onToggleGrid: () => void;
  showSkeleton: boolean;
  onToggleSkeleton: () => void;
  wireframe: boolean;
  onToggleWireframe: () => void;
  onResetCamera: () => void;
  availableWeapons?: WeaponOption[];
  equippedWeaponId?: string | null;
  onSelectWeapon?: (weaponId: string | null) => void;
  isTuningOpen?: boolean;
  onToggleTuning?: () => void;
}

export const HeaderBar: React.FC<HeaderBarProps> = ({
  modelName,
  stats,
  showGrid,
  onToggleGrid,
  showSkeleton,
  onToggleSkeleton,
  wireframe,
  onToggleWireframe,
  onResetCamera,
  availableWeapons = [],
  equippedWeaponId = null,
  onSelectWeapon,
  isTuningOpen = false,
  onToggleTuning,
}) => {
  return (
    <header className="viewer-header">
      {/* Brand & Current Asset Title */}
      <div className="header-left">
        <div className="header-brand">
          <span className="brand-badge">VOXEL LAB</span>
          <span className="brand-divider">/</span>
          <span className="brand-title">{modelName || 'No model selected'}</span>
        </div>

        {/* Technical Stats Strip */}
        {stats && (
          <div className="header-stats">
            <span className="stat-item">
              <span className="stat-label">VERTS</span>
              <span className="stat-value">{stats.vertices.toLocaleString()}</span>
            </span>
            <span className="stat-divider">•</span>
            <span className="stat-item">
              <span className="stat-label">TRIS</span>
              <span className="stat-value">{stats.triangles.toLocaleString()}</span>
            </span>
            <span className="stat-divider">•</span>
            <span className="stat-item">
              <span className="stat-label">BONES</span>
              <span className="stat-value">{stats.bones}</span>
            </span>
            <span className="stat-divider">•</span>
            <span className="stat-item">
              <span className="stat-label">MATS</span>
              <span className="stat-value">{stats.materials}</span>
            </span>
          </div>
        )}
      </div>

      {/* Viewport View Controls */}
      <div className="header-controls">
        {/* Modular Weapon Equip Selector */}
        {availableWeapons.length > 0 && onSelectWeapon && (
          <div className="weapon-equip-group">
            <div className="weapon-equip-selector" title="Equip modular weapon to Socket_Hand_R">
              <span className="weapon-equip-label">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="14.5 17.5 3 6 3 3 6 3 17.5 14.5" />
                  <line x1="13" y1="19" x2="19" y2="13" />
                  <line x1="16" y1="16" x2="20" y2="20" />
                  <line x1="19" y1="21" x2="21" y2="19" />
                </svg>
                <span>EQUIP</span>
              </span>
              <select
                className="weapon-select"
                value={equippedWeaponId || ''}
                onChange={e => onSelectWeapon(e.target.value ? e.target.value : null)}
              >
                <option value="">None (Empty Hands)</option>
                {availableWeapons.map(w => (
                  <option key={w.id} value={w.id}>
                    {w.name}
                  </option>
                ))}
              </select>
            </div>

            {equippedWeaponId && onToggleTuning && (
              <button
                type="button"
                className={`control-btn ${isTuningOpen ? 'active' : ''}`}
                onClick={onToggleTuning}
                title="Fine-tune Weapon Rotation and Position in Hand"
              >
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="3" />
                  <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
                </svg>
                <span>Tune Grip</span>
              </button>
            )}
          </div>
        )}

        <button
          type="button"
          className={`control-btn ${showGrid ? 'active' : ''}`}
          onClick={onToggleGrid}
          title="Toggle Ground Grid"
        >
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="3" width="18" height="18" rx="2" />
            <path d="M3 9h18M3 15h18M9 3v18M15 3v18" />
          </svg>
          <span>Grid</span>
        </button>

        <button
          type="button"
          className={`control-btn ${showSkeleton ? 'active' : ''}`}
          onClick={onToggleSkeleton}
          title="Toggle Armature Bones"
        >
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="5" r="2" />
            <path d="M12 7v10M9 11l6-2M9 17l3-3 3 3" />
          </svg>
          <span>Bones</span>
        </button>

        <button
          type="button"
          className={`control-btn ${wireframe ? 'active' : ''}`}
          onClick={onToggleWireframe}
          title="Toggle Wireframe Shading"
        >
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2l10 6-10 6-10-6z" />
            <path d="M2 8v8l10 6 10-6V8" />
            <path d="M12 14v8" />
          </svg>
          <span>Wireframe</span>
        </button>

        <button
          type="button"
          className="control-btn"
          onClick={onResetCamera}
          title="Re-frame Camera to Model"
        >
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 9V5a2 2 0 0 1 2-2h4M15 3h4a2 2 0 0 1 2 2v4M21 15v4a2 2 0 0 1-2 2h-4M9 21H5a2 2 0 0 1-2-2v-4" />
          </svg>
          <span>Reset Cam</span>
        </button>
      </div>
    </header>
  );
};
