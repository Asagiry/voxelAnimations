import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import fs from 'fs';
import path from 'path';

function formatAssetName(folder: string): string {
  const customNames: Record<string, string> = {
    bloody_zombie: 'Bloody Zombie',
    zombie: 'Undead Zombie',
    zombie_giant: 'Zombie Giant',
    flame_sword: 'Infernal Flame Greatsword',
    guts_sword_flash: 'Dragon Slayer (Guts)',
    katana_flash: 'Iaido Crescent Katana',
    katana_38_flash: 'Iaido Razor Katana',
    katana_pro: 'Tamahagane Katana',
    magic_bow: 'Celestial Recurve Bow',
  };

  if (customNames[folder]) return customNames[folder];
  return folder
    .split('_')
    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}

export default defineConfig({
  plugins: [
    react(),
    {
      name: 'voxel-asset-scanner',
      configureServer(server) {
        server.middlewares.use('/api/assets', (_req: any, res: any) => {
          const assetsDir = path.resolve(__dirname, 'assets');
          if (!fs.existsSync(assetsDir)) {
            res.setHeader('Content-Type', 'application/json');
            res.end(JSON.stringify([]));
            return;
          }

          const entries = fs.readdirSync(assetsDir, { withFileTypes: true });
          const list = entries
            .filter((d: fs.Dirent) => d.isDirectory())
            .map((d: fs.Dirent) => {
              const folder = d.name;
              const dirPath = path.join(assetsDir, folder);
              const files = fs.existsSync(dirPath) ? fs.readdirSync(dirPath) : [];
              const glbFile = files.find((f: string) => f.endsWith('.glb'));
              const renderFile =
                files.find((f: string) => f.endsWith('_render.png')) ||
                files.find((f: string) => f.endsWith('.png') && !f.includes('filmstrip') && !f.includes('preview')) ||
                files.find((f: string) => f.endsWith('.png'));
              const scriptFile = files.find((f: string) => f.startsWith('build') && f.endsWith('.py'));
              const stat = glbFile ? fs.statSync(path.join(dirPath, glbFile)) : null;

              return {
                id: folder,
                name: formatAssetName(folder),
                folder,
                glbUrl: glbFile ? `/assets/${folder}/${glbFile}` : null,
                renderUrl: renderFile ? `/assets/${folder}/${renderFile}` : null,
                scriptName: scriptFile || null,
                sizeBytes: stat ? stat.size : 0,
                updatedAt: stat ? stat.mtime.toISOString() : null,
              };
            })
            .filter((item: any) => item.glbUrl !== null);

          res.setHeader('Content-Type', 'application/json');
          res.end(JSON.stringify(list));
        });

        server.middlewares.use('/assets', (req: any, res: any, next: any) => {
          const rawUrl: string = req.url ? req.url.split('?')[0] : '';
          const filePath = path.join(__dirname, 'assets', decodeURIComponent(rawUrl));

          if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
            res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0');
            res.setHeader('Pragma', 'no-cache');
            res.setHeader('Expires', '0');
            if (filePath.endsWith('.glb')) res.setHeader('Content-Type', 'model/gltf-binary');
            else if (filePath.endsWith('.png')) res.setHeader('Content-Type', 'image/png');
            else if (filePath.endsWith('.js')) res.setHeader('Content-Type', 'application/javascript');
            else if (filePath.endsWith('.json')) res.setHeader('Content-Type', 'application/json');
            fs.createReadStream(filePath).pipe(res);
            return;
          }
          next();
        });
      },
    },
  ],
  server: {
    port: 8080,
    host: true,
  },
});
