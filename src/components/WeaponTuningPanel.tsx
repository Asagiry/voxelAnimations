import React from 'react';
import { WeaponTransform } from '../types';

interface WeaponTuningPanelProps {
  transform: WeaponTransform;
  onChange: (t: WeaponTransform) => void;
  onClose: () => void;
}

export const WeaponTuningPanel: React.FC<WeaponTuningPanelProps> = ({
  transform,
  onChange,
  onClose,
}) => {
  const updateVal = (key: keyof WeaponTransform, val: number) => {
    onChange({ ...transform, [key]: val });
  };

  const stepRot = (axis: 'rotX' | 'rotY' | 'rotZ', delta: number) => {
    let next = (transform[axis] + delta) % 360;
    if (next > 180) next -= 360;
    if (next < -180) next += 360;
    updateVal(axis, next);
  };

  const applyPreset = (preset: Partial<WeaponTransform>) => {
    onChange({
      rotX: 0,
      rotY: 0,
      rotZ: 0,
      posX: 0,
      posY: 0,
      posZ: 0,
      ...preset,
    });
  };

  return (
    <div className="weapon-tuning-panel">
      <div className="tuning-header">
        <div className="tuning-title">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="3" />
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
          </svg>
          <span>WEAPON FIT & ROTATION (SOCKET_HAND_R)</span>
        </div>
        <button type="button" className="tuning-close" onClick={onClose} title="Close Panel">
          ✕
        </button>
      </div>

      {/* Quick Presets */}
      <div className="tuning-presets">
        <button
          type="button"
          className="preset-btn"
          onClick={() => applyPreset({ rotX: 0, rotY: 0, rotZ: 0 })}
        >
          Upright (0° X)
        </button>
        <button
          type="button"
          className="preset-btn"
          onClick={() => applyPreset({ rotX: 90, rotY: 0, rotZ: 0 })}
        >
          Forward Slash (90° X)
        </button>
        <button
          type="button"
          className="preset-btn"
          onClick={() => applyPreset({ rotX: 180, rotY: 0, rotZ: 0 })}
        >
          Inverted (180° X)
        </button>
        <button
          type="button"
          className="preset-btn"
          onClick={() => applyPreset({ rotX: 0, rotY: 0, rotZ: 180 })}
        >
          Reverse Grip (180° Z)
        </button>
        <button
          type="button"
          className="preset-btn preset-reset"
          onClick={() => applyPreset({ rotX: 0, rotY: 0, rotZ: 0, posX: 0, posY: 0, posZ: 0 })}
        >
          Reset (0,0,0)
        </button>
      </div>

      {/* Rotation Sliders */}
      <div className="tuning-section">
        <div className="tuning-section-title">ROTATION (DEGREES)</div>
        
        {/* Rot X */}
        <div className="tuning-row">
          <span className="tuning-label">ROT X</span>
          <input
            type="range"
            min="-180"
            max="180"
            step="5"
            value={transform.rotX}
            onChange={e => updateVal('rotX', parseFloat(e.target.value))}
            className="tuning-slider"
          />
          <span className="tuning-val">{Math.round(transform.rotX)}°</span>
          <div className="step-btns">
            <button type="button" onClick={() => stepRot('rotX', -90)}>-90°</button>
            <button type="button" onClick={() => stepRot('rotX', 90)}>+90°</button>
          </div>
        </div>

        {/* Rot Y */}
        <div className="tuning-row">
          <span className="tuning-label">ROT Y</span>
          <input
            type="range"
            min="-180"
            max="180"
            step="5"
            value={transform.rotY}
            onChange={e => updateVal('rotY', parseFloat(e.target.value))}
            className="tuning-slider"
          />
          <span className="tuning-val">{Math.round(transform.rotY)}°</span>
          <div className="step-btns">
            <button type="button" onClick={() => stepRot('rotY', -90)}>-90°</button>
            <button type="button" onClick={() => stepRot('rotY', 90)}>+90°</button>
          </div>
        </div>

        {/* Rot Z */}
        <div className="tuning-row">
          <span className="tuning-label">ROT Z</span>
          <input
            type="range"
            min="-180"
            max="180"
            step="5"
            value={transform.rotZ}
            onChange={e => updateVal('rotZ', parseFloat(e.target.value))}
            className="tuning-slider"
          />
          <span className="tuning-val">{Math.round(transform.rotZ)}°</span>
          <div className="step-btns">
            <button type="button" onClick={() => stepRot('rotZ', -90)}>-90°</button>
            <button type="button" onClick={() => stepRot('rotZ', 90)}>+90°</button>
          </div>
        </div>
      </div>

      {/* Position Offset */}
      <div className="tuning-section">
        <div className="tuning-section-title">HILT POSITION OFFSET (METERS)</div>

        <div className="tuning-row">
          <span className="tuning-label">POS X</span>
          <input
            type="range"
            min="-0.15"
            max="0.15"
            step="0.005"
            value={transform.posX}
            onChange={e => updateVal('posX', parseFloat(e.target.value))}
            className="tuning-slider"
          />
          <span className="tuning-val">{transform.posX.toFixed(3)}m</span>
        </div>

        <div className="tuning-row">
          <span className="tuning-label">POS Y</span>
          <input
            type="range"
            min="-0.15"
            max="0.15"
            step="0.005"
            value={transform.posY}
            onChange={e => updateVal('posY', parseFloat(e.target.value))}
            className="tuning-slider"
          />
          <span className="tuning-val">{transform.posY.toFixed(3)}m</span>
        </div>

        <div className="tuning-row">
          <span className="tuning-label">POS Z</span>
          <input
            type="range"
            min="-0.15"
            max="0.15"
            step="0.005"
            value={transform.posZ}
            onChange={e => updateVal('posZ', parseFloat(e.target.value))}
            className="tuning-slider"
          />
          <span className="tuning-val">{transform.posZ.toFixed(3)}m</span>
        </div>
      </div>
    </div>
  );
};
