import { getStrapiURL } from '@/lib/api';

export function getStrapiMedia(media) {
  const { url } = media.data ? media.data.attributes : '';
  const imageUrl = url
    ? url.startsWith('/')
      ? getStrapiURL(url)
      : url
    : '/img/missing.svg';
  return imageUrl;
}
