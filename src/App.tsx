import React, { useState, useEffect, useCallback, useRef } from 'react';
import { AssetManifestItem, ModelStats, WeaponTransform } from './types';
import { AssetSidebar } from './components/AssetSidebar';
import { HeaderBar } from './components/HeaderBar';
import { ModelViewer } from './components/ModelViewer';
import { AnimationControls } from './components/AnimationControls';
import { WeaponTuningPanel } from './components/WeaponTuningPanel';

export const App: React.FC = () => {
  const isInitializedRef = useRef<boolean>(false);
  const [assets, setAssets] = useState<AssetManifestItem[]>([]);
  const [selectedAsset, setSelectedAsset] = useState<AssetManifestItem | null>(null);
  const [stats, setStats] = useState<ModelStats | null>(null);
  const [clips, setClips] = useState<string[]>([]);
  const [activeClip, setActiveClip] = useState<string | null>(null);

  // Modular Weapon Equip & Fine-Tuning State
  const [equippedWeaponId, setEquippedWeaponId] = useState<string | null>(null);
  const [weaponTransform, setWeaponTransform] = useState<WeaponTransform>({
    rotX: 0,
    rotY: 0,
    rotZ: 0,
    posX: 0,
    posY: 0,
    posZ: 0,
  });
  const [isTuningOpen, setIsTuningOpen] = useState<boolean>(false);

  const handleSelectWeapon = (weaponId: string | null) => {
    setEquippedWeaponId(weaponId);
    if (weaponId) {
      setWeaponTransform({
        rotX: 0,
        rotY: 0,
        rotZ: 0,
        posX: 0,
        posY: 0,
        posZ: 0,
      });
      setIsTuningOpen(true);
    } else {
      setIsTuningOpen(false);
    }
  };

  // Playback state
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [duration, setDuration] = useState<number>(0);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1.0);
  const [isSeeking, setIsSeeking] = useState<boolean>(false);

  // Viewport toggles
  const [showGrid, setShowGrid] = useState<boolean>(true);
  const [showSkeleton, setShowSkeleton] = useState<boolean>(false);
  const [wireframe, setWireframe] = useState<boolean>(false);
  const [resetCameraTrigger, setResetCameraTrigger] = useState<number>(0);

  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Fetch asset manifest from dynamic backend API
  const fetchAssets = useCallback(async () => {
    try {
      setIsLoading(true);
      const res = await fetch('/api/assets');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: AssetManifestItem[] = await res.json();
      setAssets(data);

      // Auto-select asset based on URL param (search or hash)
      const rawQuery = (window.location.search || window.location.hash.replace(/^#\??/, '?')).replace(/%26/g, '&');
      const searchParams = new URLSearchParams(rawQuery);
      const urlModelId = searchParams.get('model');
      const urlWeaponId = searchParams.get('weapon');

      if (urlWeaponId) {
        setEquippedWeaponId(urlWeaponId);
        setIsTuningOpen(true);
      }

      setSelectedAsset(prev => {
        if (urlModelId) {
          const match = data.find(a => a.id === urlModelId);
          if (match) return match;
        }
        if (prev) {
          const match = data.find(a => a.id === prev.id);
          return match || (data.length > 0 ? data[0] : null);
        }
        return data.length > 0 ? data[0] : null;
      });

      // Mark initialized after React schedules state updates
      setTimeout(() => {
        isInitializedRef.current = true;
      }, 0);
    } catch (err) {
      console.error('Failed to fetch assets:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAssets();
  }, [fetchAssets]);

  const handleSelectAsset = (asset: AssetManifestItem) => {
    setSelectedAsset(asset);
    setStats(null);
    setClips([]);
    setActiveClip(null);
    setCurrentTime(0);
    setDuration(0);
    setIsPlaying(true);
  };

  const handleModelLoaded = (
    loadedStats: ModelStats,
    loadedClips: string[],
    initialDuration: number
  ) => {
    setStats(loadedStats);
    setClips(loadedClips);
    setDuration(initialDuration);
    const rawQuery = (window.location.search || window.location.hash.replace(/^#\??/, '?')).replace(/%26/g, '&');
    const searchParams = new URLSearchParams(rawQuery);
    const urlClip = searchParams.get('clip');
    if (urlClip && loadedClips.includes(urlClip)) {
      setActiveClip(urlClip);
    } else if (loadedClips.includes('Attack_Round')) {
      setActiveClip('Attack_Round');
    } else if (loadedClips.length > 0) {
      setActiveClip(loadedClips[0]);
    } else {
      setActiveClip(null);
    }
  };

  // Sync state to URL search parameters without page reloads
  useEffect(() => {
    if (!isInitializedRef.current || !selectedAsset) return;

    const params = new URLSearchParams(window.location.search);
    params.set('model', selectedAsset.id);
    if (equippedWeaponId) {
      params.set('weapon', equippedWeaponId);
    } else {
      params.delete('weapon');
    }
    if (activeClip) {
      params.set('clip', activeClip);
    } else {
      params.delete('clip');
    }
    const newSearch = params.toString();
    const newUrl = newSearch ? `${window.location.pathname}?${newSearch}` : window.location.pathname;
    window.history.replaceState(null, '', newUrl);
  }, [selectedAsset, equippedWeaponId, activeClip]);

  const handleTimeUpdate = (time: number, clipDuration: number) => {
    if (!isSeeking) {
      setCurrentTime(time);
      setDuration(clipDuration);
    }
  };

  const handleSeek = (time: number) => {
    setIsSeeking(true);
    setCurrentTime(time);
    // After short delay release seeking
    setTimeout(() => {
      setIsSeeking(false);
    }, 50);
  };

  const handleTogglePlay = () => {
    setIsPlaying(prev => !prev);
  };

  const handleResetCamera = () => {
    setResetCameraTrigger(prev => prev + 1);
  };

  return (
    <div className="app-container">
      {/* Sidebar with auto-scanned models */}
      <AssetSidebar
        assets={assets}
        activeId={selectedAsset?.id || null}
        onSelect={handleSelectAsset}
        onRefresh={fetchAssets}
        isLoading={isLoading}
      />

      {/* Main Viewport & Inspection Stage */}
      <main className="main-content">
        <HeaderBar
          modelName={selectedAsset ? selectedAsset.name : ''}
          stats={stats}
          showGrid={showGrid}
          onToggleGrid={() => setShowGrid(v => !v)}
          showSkeleton={showSkeleton}
          onToggleSkeleton={() => setShowSkeleton(v => !v)}
          wireframe={wireframe}
          onToggleWireframe={() => setWireframe(v => !v)}
          onResetCamera={handleResetCamera}
          availableWeapons={assets
            .filter(a => {
              const id = a.id.toLowerCase();
              return id.includes('sword') || id.includes('katana') || id.includes('bow') || id.includes('scythe');
            })
            .map(a => ({ id: a.id, name: a.name, glbUrl: a.glbUrl }))}
          equippedWeaponId={equippedWeaponId}
          onSelectWeapon={handleSelectWeapon}
          isTuningOpen={isTuningOpen}
          onToggleTuning={() => setIsTuningOpen(v => !v)}
        />

        <div className="viewport-container">
          <ModelViewer
            glbUrl={selectedAsset?.glbUrl || null}
            activeClip={activeClip}
            isPlaying={isPlaying}
            playbackSpeed={playbackSpeed}
            seekTime={currentTime}
            isSeeking={isSeeking}
            showGrid={showGrid}
            showSkeleton={showSkeleton}
            wireframe={wireframe}
            resetCameraTrigger={resetCameraTrigger}
            equippedWeaponUrl={
              equippedWeaponId
                ? assets.find(a => a.id === equippedWeaponId)?.glbUrl || null
                : null
            }
            weaponTransform={weaponTransform}
            onModelLoaded={handleModelLoaded}
            onTimeUpdate={handleTimeUpdate}
          />

          {equippedWeaponId && isTuningOpen && (
            <WeaponTuningPanel
              transform={weaponTransform}
              onChange={setWeaponTransform}
              onClose={() => setIsTuningOpen(false)}
            />
          )}
        </div>

        {/* Dynamic Animation Track Controls */}
        <AnimationControls
          clips={clips}
          activeClip={activeClip}
          onSelectClip={clip => {
            setActiveClip(clip);
            setCurrentTime(0);
          }}
          isPlaying={isPlaying}
          onTogglePlay={handleTogglePlay}
          currentTime={currentTime}
          duration={duration}
          onSeek={handleSeek}
          playbackSpeed={playbackSpeed}
          onChangeSpeed={setPlaybackSpeed}
        />
      </main>
    </div>
  );
};

export default App;
