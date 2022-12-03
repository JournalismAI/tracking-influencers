/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    loader: "default",
    domains: ["", "", "localhost", "imgp.sptds.icu"],
  },
};

module.exports = nextConfig;
