/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  skipTrailingSlashRedirect: true,
  rewrites: async () => {
    if (process.env.NODE_ENV !== "development") return [];
    return [
      {
        source: "/api/users",
        destination: "http://127.0.0.1:8000/api/users/",
      },
      {
        source: "/api/:path*",
        destination: "http://127.0.0.1:8000/api/:path*",
      },
      {
        source: "/bank/:path*",
        destination: "http://127.0.0.1:8000/bank/:path*",
      },
      {
        source: "/docs",
        destination: "http://127.0.0.1:8000/docs",
      },
      {
        source: "/openapi.json",
        destination: "http://127.0.0.1:8000/openapi.json",
      },
    ];
  },
};

module.exports = nextConfig;
