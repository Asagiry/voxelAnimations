import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { ModelStats, WeaponTransform } from '../types';

interface ModelViewerProps {
  glbUrl: string | null;
  activeClip: string | null;
  isPlaying: boolean;
  playbackSpeed: number;
  seekTime: number;
  isSeeking: boolean;
  showGrid: boolean;
  showSkeleton: boolean;
  wireframe: boolean;
  resetCameraTrigger?: number;
  equippedWeaponUrl?: string | null;
  weaponTransform?: WeaponTransform;
  onModelLoaded: (stats: ModelStats, clipNames: string[], duration: number) => void;
  onTimeUpdate: (currentTime: number, duration: number) => void;
}

export const ModelViewer: React.FC<ModelViewerProps> = ({
  glbUrl,
  activeClip,
  isPlaying,
  playbackSpeed,
  seekTime,
  isSeeking,
  showGrid,
  showSkeleton,
  wireframe,
  resetCameraTrigger,
  equippedWeaponUrl,
  weaponTransform,
  onModelLoaded,
  onTimeUpdate,
}) => {
  const [modelReadyEpoch, setModelReadyEpoch] = useState<number>(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const controlsRef = useRef<OrbitControls | null>(null);
  const mixerRef = useRef<THREE.AnimationMixer | null>(null);
  const actionsMapRef = useRef<Map<string, THREE.AnimationAction>>(new Map());
  const currentActionRef = useRef<THREE.AnimationAction | null>(null);
  const currentModelRef = useRef<THREE.Group | null>(null);
  const weaponModelRef = useRef<THREE.Group | null>(null);
  const gridHelperRef = useRef<THREE.GridHelper | null>(null);
  const skeletonHelperRef = useRef<THREE.SkeletonHelper | null>(null);
  const clockRef = useRef<THREE.Clock>(new THREE.Clock());
  const animationFrameId = useRef<number>(0);

  const frameModelCamera = (model: THREE.Object3D) => {
    if (!controlsRef.current || !cameraRef.current) return;
    const bbox = new THREE.Box3().setFromObject(model);
    const center = bbox.getCenter(new THREE.Vector3());
    const size = bbox.getSize(new THREE.Vector3());
    const maxDim = Math.max(size.x, size.y, size.z, 0.5);

    controlsRef.current.target.copy(center);
    cameraRef.current.position.set(
      center.x + maxDim * 1.3,
      center.y + maxDim * 0.7,
      center.z - maxDim * 1.7
    );
    controlsRef.current.update();
  };

  // Initialize Three.js Scene
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const width = container.clientWidth;
    const height = container.clientHeight;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0e0e11);
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.05, 100);
    camera.position.set(1.5, 1.2, 1.8);
    cameraRef.current = camera;

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.1;
    container.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.autoRotate = false; // Strictly disabled per user instructions
    controls.target.set(0, 0.35, 0);
    controls.maxDistance = 15;
    controls.minDistance = 0.2;
    controlsRef.current = controls;

    // Grid Floor
    const grid = new THREE.GridHelper(4, 32, 0x3f3f4e, 0x1f1f26);
    grid.position.y = 0;
    scene.add(grid);
    gridHelperRef.current = grid;

    // Studio Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 1.2);
    scene.add(ambientLight);

    const keyLight = new THREE.DirectionalLight(0xffffff, 2.5);
    keyLight.position.set(3, 5, 4);
    scene.add(keyLight);

    const rimLight = new THREE.DirectionalLight(0x38bdf8, 1.8);
    rimLight.position.set(-3, 3, -3);
    scene.add(rimLight);

    const fillLight = new THREE.DirectionalLight(0xa1a1aa, 1.2);
    fillLight.position.set(2, -1, -2);
    scene.add(fillLight);

    // Render loop
    const animate = () => {
      animationFrameId.current = requestAnimationFrame(animate);
      const delta = clockRef.current.getDelta();

      if (mixerRef.current && !isSeeking) {
        mixerRef.current.update(delta * playbackSpeed);
        if (currentActionRef.current) {
          const clipDuration = currentActionRef.current.getClip().duration;
          const time = currentActionRef.current.time % clipDuration;
          onTimeUpdate(time, clipDuration);
        }
      }

      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    const handleResize = () => {
      if (!container || !cameraRef.current || !rendererRef.current) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      cameraRef.current.aspect = w / h;
      cameraRef.current.updateProjectionMatrix();
      rendererRef.current.setSize(w, h);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animationFrameId.current);
      window.removeEventListener('resize', handleResize);
      renderer.dispose();
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
    };
  }, []);

  // Update Grid Visibility
  useEffect(() => {
    if (gridHelperRef.current) {
      gridHelperRef.current.visible = showGrid;
    }
  }, [showGrid]);

  // Update Skeleton Visibility
  useEffect(() => {
    if (skeletonHelperRef.current) {
      skeletonHelperRef.current.visible = showSkeleton;
    }
  }, [showSkeleton]);

  // Update Wireframe
  useEffect(() => {
    if (currentModelRef.current) {
      currentModelRef.current.traverse(child => {
        if ((child as THREE.Mesh).isMesh) {
          const mesh = child as THREE.Mesh;
          if (Array.isArray(mesh.material)) {
            mesh.material.forEach(m => {
              if ('wireframe' in m) {
                (m as THREE.MeshStandardMaterial).wireframe = wireframe;
              }
            });
          } else if (mesh.material && 'wireframe' in mesh.material) {
            (mesh.material as THREE.MeshStandardMaterial).wireframe = wireframe;
          }
        }
      });
    }
  }, [wireframe]);

  // Load Model when glbUrl changes
  useEffect(() => {
    if (!glbUrl || !sceneRef.current) return;

    const scene = sceneRef.current;

    // Cleanup previous model and helpers
    if (currentModelRef.current) {
      scene.remove(currentModelRef.current);
      currentModelRef.current = null;
    }
    if (skeletonHelperRef.current) {
      scene.remove(skeletonHelperRef.current);
      skeletonHelperRef.current = null;
    }
    if (mixerRef.current) {
      mixerRef.current.stopAllAction();
      mixerRef.current = null;
    }
    actionsMapRef.current.clear();
    currentActionRef.current = null;

    const loader = new GLTFLoader();
    const cacheBustUrl = glbUrl.includes('?') ? `${glbUrl}&_v=${Date.now()}` : `${glbUrl}?_v=${Date.now()}`;
    loader.load(
      cacheBustUrl,
      gltf => {
        const model = gltf.scene;
        currentModelRef.current = model;
        scene.add(model);

        // Stats calculation
        let vertices = 0;
        let triangles = 0;
        let bones = 0;
        const materialsSet = new Set<THREE.Material>();

        model.traverse(node => {
          if ((node as THREE.Mesh).isMesh) {
            const mesh = node as THREE.Mesh;
            const geom = mesh.geometry;
            if (geom.attributes.position) {
              vertices += geom.attributes.position.count;
            }
            if (geom.index) {
              triangles += geom.index.count / 3;
            } else if (geom.attributes.position) {
              triangles += geom.attributes.position.count / 3;
            }
            if (Array.isArray(mesh.material)) {
              mesh.material.forEach(m => materialsSet.add(m));
            } else if (mesh.material) {
              materialsSet.add(mesh.material);
            }
          }
          if ((node as THREE.Bone).isBone) {
            bones++;
          }
        });

        // Skeleton Helper
        const skelHelper = new THREE.SkeletonHelper(model);
        skelHelper.visible = showSkeleton;
        scene.add(skelHelper);
        skeletonHelperRef.current = skelHelper;

        // Frame camera based on model bounding box
        frameModelCamera(model);

        // Animation Mixer
        const mixer = new THREE.AnimationMixer(model);
        mixerRef.current = mixer;

        const clipNames: string[] = [];
        let firstDuration = 0;

        gltf.animations.forEach((clip, index) => {
          const action = mixer.clipAction(clip);
          actionsMapRef.current.set(clip.name, action);
          clipNames.push(clip.name);
          if (index === 0) {
            firstDuration = clip.duration;
          }
        });

        onModelLoaded(
          {
            vertices,
            triangles: Math.round(triangles),
            materials: materialsSet.size,
            bones,
            animations: clipNames,
          },
          clipNames,
          firstDuration
        );

        // Play initial clip if available
        if (clipNames.length > 0) {
          const initialClipName = activeClip && clipNames.includes(activeClip) ? activeClip : clipNames[0];
          const initialAction = actionsMapRef.current.get(initialClipName);
          if (initialAction) {
            initialAction.play();
            currentActionRef.current = initialAction;
          }
        }

        // Signal that the model and its skeleton/sockets are ready for weapon mounting
        setModelReadyEpoch(e => e + 1);
      },
      undefined,
      err => {
        console.error('Failed to load GLB:', err);
      }
    );
  }, [glbUrl]);

  // Handle Modular Weapon Equipping to Socket_Hand_R
  useEffect(() => {
    // 1. Remove previously equipped weapon if any
    if (weaponModelRef.current) {
      weaponModelRef.current.removeFromParent();
      weaponModelRef.current = null;
    }

    if (!equippedWeaponUrl || !currentModelRef.current) return;

    const currentModel = currentModelRef.current;
    const loader = new GLTFLoader();
    const cacheBustWeaponUrl = equippedWeaponUrl.includes('?')
      ? `${equippedWeaponUrl}&_v=${Date.now()}`
      : `${equippedWeaponUrl}?_v=${Date.now()}`;

    loader.load(
      cacheBustWeaponUrl,
      weaponGltf => {
        // Double check model still exists
        if (currentModelRef.current !== currentModel) return;

        const weaponScene = weaponGltf.scene;
        weaponModelRef.current = weaponScene;

        // Hide plinth / display stand / pedestal / target objects if present, and disable frustum culling
        weaponScene.traverse(child => {
          const name = child.name.toLowerCase();
          if (
            name.includes('plinth') ||
            name.includes('pedestal') ||
            name.includes('ground') ||
            name.includes('debris') ||
            name.includes('target') ||
            name.startsWith('display_')
          ) {
            child.visible = false;
          }

          if ((child as THREE.Mesh).isMesh) {
            child.frustumCulled = false;
          }
        });

        // Apply weapon rotation and position offset
        if (weaponTransform) {
          weaponScene.rotation.set(
            THREE.MathUtils.degToRad(weaponTransform.rotX),
            THREE.MathUtils.degToRad(weaponTransform.rotY),
            THREE.MathUtils.degToRad(weaponTransform.rotZ)
          );
          weaponScene.position.set(
            weaponTransform.posX,
            weaponTransform.posY,
            weaponTransform.posZ
          );
        }

        // Search for weapon socket based on activeClip (Left Hand for Attack_Round, Right Hand default)
        const isLeftHandClip = activeClip?.toLowerCase().includes('round');
        const socket = isLeftHandClip
          ? currentModel.getObjectByName('Socket_Hand_L') ||
            currentModel.getObjectByName('Hand.L') ||
            currentModel.getObjectByName('Socket_Hand_R')
          : currentModel.getObjectByName('Socket_Hand_R') ||
            currentModel.getObjectByName('Hand.R') ||
            currentModel.getObjectByName('Socket_Hand_L') ||
            currentModel.getObjectByName('Hand.L');

        console.log('[ModelViewer] Loaded equipped weapon:', equippedWeaponUrl);
        console.log('[ModelViewer] Weapon scene children:', weaponScene.children.map(c => c.name));
        console.log('[ModelViewer] Found socket:', socket ? socket.name : 'NONE');

        (window as any).__weaponScene = weaponScene;
        (window as any).__socket = socket;
        (window as any).__currentModel = currentModel;

        if (socket) {
          socket.add(weaponScene);
        } else {
          // If model has no hand socket, add to model root as fallback
          currentModel.add(weaponScene);
        }
      },
      undefined,
      err => {
        console.error('Failed to load equipped weapon GLB:', err);
      }
    );
  }, [equippedWeaponUrl, modelReadyEpoch, activeClip]);

  // Update Weapon Transform in real-time when sliders change
  useEffect(() => {
    if (weaponModelRef.current && weaponTransform) {
      weaponModelRef.current.rotation.set(
        THREE.MathUtils.degToRad(weaponTransform.rotX),
        THREE.MathUtils.degToRad(weaponTransform.rotY),
        THREE.MathUtils.degToRad(weaponTransform.rotZ)
      );
      weaponModelRef.current.position.set(
        weaponTransform.posX,
        weaponTransform.posY,
        weaponTransform.posZ
      );
    }
  }, [weaponTransform]);


  // Handle activeClip change
  useEffect(() => {
    if (!activeClip || !mixerRef.current) return;

    const newAction = actionsMapRef.current.get(activeClip);
    if (!newAction) return;

    if (currentActionRef.current && currentActionRef.current !== newAction) {
      currentActionRef.current.fadeOut(0.2);
      newAction.reset().fadeIn(0.2).play();
    } else if (!currentActionRef.current) {
      newAction.reset().play();
    }
    currentActionRef.current = newAction;
  }, [activeClip]);

  // Handle Play/Pause
  useEffect(() => {
    if (!currentActionRef.current) return;
    currentActionRef.current.paused = !isPlaying;
  }, [isPlaying]);

  // Handle Scrubbing
  useEffect(() => {
    if (isSeeking && currentActionRef.current) {
      currentActionRef.current.time = seekTime;
      if (mixerRef.current) {
        mixerRef.current.update(0);
      }
    }
  }, [seekTime, isSeeking]);

  // Handle Manual Camera Reset
  useEffect(() => {
    if (resetCameraTrigger !== undefined && resetCameraTrigger > 0 && currentModelRef.current) {
      frameModelCamera(currentModelRef.current);
    }
  }, [resetCameraTrigger]);

  return (
    <div
      ref={containerRef}
      style={{
        width: '100%',
        height: '100%',
        position: 'relative',
        overflow: 'hidden',
      }}
    />
  );
};
