import React from 'react';

interface AnimationControlsProps {
  clips: string[];
  activeClip: string | null;
  onSelectClip: (clip: string) => void;
  isPlaying: boolean;
  onTogglePlay: () => void;
  currentTime: number;
  duration: number;
  onSeek: (time: number) => void;
  playbackSpeed: number;
  onChangeSpeed: (speed: number) => void;
}

const SPEED_PRESETS = [0.25, 0.5, 1.0, 1.5, 2.0];

export const AnimationControls: React.FC<AnimationControlsProps> = ({
  clips,
  activeClip,
  onSelectClip,
  isPlaying,
  onTogglePlay,
  currentTime,
  duration,
  onSeek,
  playbackSpeed,
  onChangeSpeed,
}) => {
  if (clips.length === 0) {
    return (
      <div className="anim-bar empty">
        <span className="anim-empty-label">Static Model (No Skeletal Animations)</span>
      </div>
    );
  }

  const formatTime = (seconds: number) => {
    return seconds.toFixed(2) + 's';
  };

  const currentFrame = Math.round(currentTime * 30);
  const totalFrames = Math.round(duration * 30);

  return (
    <div className="anim-bar">
      {/* Clip Selector Tabs */}
      <div className="anim-clip-tabs">
        <span className="anim-group-label">CLIPS</span>
        {clips.map(clip => {
          const isActive = clip === activeClip;
          return (
            <button
              key={clip}
              type="button"
              className={`anim-clip-tab ${isActive ? 'active' : ''}`}
              onClick={() => onSelectClip(clip)}
            >
              {clip}
            </button>
          );
        })}
      </div>

      {/* Playback Controls & Scrubber */}
      <div className="anim-playback-row">
        <button
          type="button"
          className="anim-play-btn"
          onClick={onTogglePlay}
          title={isPlaying ? 'Pause' : 'Play'}
        >
          {isPlaying ? (
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
              <rect x="6" y="4" width="4" height="16" />
              <rect x="14" y="4" width="4" height="16" />
            </svg>
          ) : (
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
              <polygon points="5 3 19 12 5 21 5 3" />
            </svg>
          )}
        </button>

        <div className="anim-scrubber-wrapper">
          <input
            type="range"
            min={0}
            max={duration || 0.001}
            step={0.01}
            value={currentTime}
            onChange={e => onSeek(parseFloat(e.target.value))}
            className="anim-slider"
          />
        </div>

        <div className="anim-time-display">
          <span className="anim-time-seconds">
            {formatTime(currentTime)} / {formatTime(duration)}
          </span>
          <span className="anim-time-frames">
            F{currentFrame} / {totalFrames}
          </span>
        </div>

        {/* Speed Controls */}
        <div className="anim-speed-pills">
          {SPEED_PRESETS.map(speed => (
            <button
              key={speed}
              type="button"
              className={`anim-speed-pill ${playbackSpeed === speed ? 'active' : ''}`}
              onClick={() => onChangeSpeed(speed)}
            >
              {speed}x
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
