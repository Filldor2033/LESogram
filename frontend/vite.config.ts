import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import path from 'node:path';

export default defineConfig({
    plugins: [
        svelte()
    ],

    resolve: {
        alias: {
            $lib: path.resolve(
                import.meta.dirname,
                'src/lib'
            ),

            $components: path.resolve(
                import.meta.dirname,
                'src/components'
            )
        }
    },

    server: {
        port: 5173,

        proxy: {
            '/api': {
                target: 'http://localhost:8000',
                changeOrigin: true,

                rewrite: path =>
                    path.replace(/^\/api/, '')
            },

            '/ws': {
                target: 'ws://localhost:8000',
                ws: true
            }
        }
    }
});
