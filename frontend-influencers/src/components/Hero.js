import Dangerous from '@/components/Dangerous';
import Image from 'next/image';

const Article = ({ hero }) => {
  return (
    <div id={hero.slug}>
      {hero.label ? (
        <p className='font-display text-sm font-medium text-sky-500'>
          {hero.label}
        </p>
      ) : (
        ''
      )}
      {hero.image.data ? (
        <figure className='flex max-w-3xl'>
          <Image
            // src={nutshell.image.data.attributes.url}
            // width={nutshell.image.data.attributes.width}
            // height={nutshell.image.data.attributes.height}
            src={`${process.env.NEXT_PUBLIC_STRAPI_API_URL}${hero.image.data.attributes.formats.medium.url}`}
            width={hero.image.data.attributes.formats.medium.width}
            height={hero.image.data.attributes.formats.medium.height}
          />
          {/* <figcaption>{article.image.data.attributes.caption}</figcaption> */}
        </figure>
      ) : (
        ''
      )}

      {hero.title ? <h1>{hero.title}</h1> : ''}

      {hero.summary || hero.body ? (
        <div className='scroll-mt-32'>
          {hero.summary ? <h3>{hero.summary}</h3> : ''}
          <Dangerous body={hero.body} />
        </div>
      ) : (
        ''
      )}
      {hero.addenda ? (
        <>
          {hero.addenda.map((addendum, i) => {
            return (
              <div key={i} id={addendum.slug}>
                <h3>{addendum.title}</h3>
                <div dangerouslySetInnerHTML={{ __html: addendum.body }}></div>
              </div>
            );
          })}
        </>
      ) : (
        ''
      )}
    </div>
  );
};

export default Article;
