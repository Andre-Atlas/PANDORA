import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  cacheComponents: true,
  partialPrefetching: true,
  async redirects() {
    // Por enquanto o app abre no Início. Quando a Abertura existir (#71),
    // a decisão de para onde mandar a pessoa muda aqui.
    return [{ source: "/", destination: "/inicio", permanent: false }];
  },
};

export default nextConfig;
