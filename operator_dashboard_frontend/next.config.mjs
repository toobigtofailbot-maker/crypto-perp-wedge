/**
 * Next.js configuration for the local-first, read-only operator dashboard shell.
 *
 * Local-first posture: this config adds no rewrites/proxies to any hosted
 * service, no image domains, no auth, no telemetry, and no deployment target.
 * The shell renders committed API-shaped fixtures by default and performs no
 * runtime, paper, or live contact.
 *
 * @type {import('next').NextConfig}
 */
const nextConfig = {
  reactStrictMode: true,
};

export default nextConfig;
