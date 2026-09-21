export interface AssetManifestItem {
  id: string;
  name: string;
  folder: string;
  glbUrl: string;
  renderUrl: string | null;
  scriptName: string | null;
  sizeBytes: number;
  updatedAt: string | null;
}

export interface ModelStats {
  vertices: number;
  triangles: number;
  materials: number;
  bones: number;
  animations: string[];
}

export interface WeaponOption {
  id: string;
  name: string;
  glbUrl: string;
}

export interface WeaponTransform {
  rotX: number;
  rotY: number;
  rotZ: number;
  posX: number;
  posY: number;
  posZ: number;
}


