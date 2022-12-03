import Head from 'next/head';
import { useContext } from 'react';
import { GlobalContext } from '@/pages/_app';
import { getStrapiMedia } from '@/lib/media';

const Seo = ({ seo }) => {
  const { defaultSeo, site_name } = useContext(GlobalContext);
  const seoWithDefaults = {
    ...defaultSeo,
    ...seo,
  };
  const fullSeo = {
    ...seoWithDefaults,
    // Add title suffix
    title: `${seoWithDefaults.title} | ${site_name}`,
    // Get full image URL
    image: getStrapiMedia(seoWithDefaults.image),
  };

  return (
    <Head>
      {fullSeo.title && (
        <>
          <title>{fullSeo.title}</title>
          <meta property='og:title' content={fullSeo.title} />
          <meta name='twitter:title' content={fullSeo.title} />
        </>
      )}
      {fullSeo.description && (
        <>
          <meta name='description' content={fullSeo.description} />
          <meta property='og:description' content={fullSeo.description} />
          <meta name='twitter:description' content={fullSeo.description} />
        </>
      )}
      {fullSeo.image && (
        <>
          <meta property='og:image' content={fullSeo.image} />
          <meta name='twitter:image' content={fullSeo.image} />
          <meta name='image' content={fullSeo.image} />
        </>
      )}
      {fullSeo.article && <meta property='og:type' content='article' />}
      <meta name='twitter:card' content='summary_large_image' />
    </Head>
  );
};

export default Seo;
