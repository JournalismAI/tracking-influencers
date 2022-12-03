import Image from 'next/image';

import Dangerous from '@/components/Dangerous';
import Reference from '@/components/Reference';

const Article = ({ article }) => {
  return (
    <>
      <div id={article.slug} className='scroll-mt-32'>
        <div className='max-w-3xl'>
          <h1>{article.title}</h1>
          <h4>{article.summary}</h4>
        </div>
        {article.image.data ? (
          <div className='mt-1 max-w-2xl'>
            <figure>
              <Image
                // src={nutshell.image.data.attributes.url}
                // width={nutshell.image.data.attributes.width}
                // height={nutshell.image.data.attributes.height}
                src={`${process.env.NEXT_PUBLIC_STRAPI_API_URL}${article.image.data.attributes.url}`}
                width={article.image.data.attributes.width}
                height={article.image.data.attributes.height}
              />
              {/* <figcaption>{article.image.data.attributes.caption}</figcaption> */}
            </figure>
          </div>
        ) : (
          ''
        )}
        <div className='max-w-2xl'>
          <Dangerous body={article.body} />

          {article.image2.data ? (
            <div className='mt-1'>
              <figure>
                <Image
                  // src={nutshell.image.data.attributes.url}
                  // width={nutshell.image.data.attributes.width}
                  // height={nutshell.image.data.attributes.height}
                  src={`${process.env.NEXT_PUBLIC_STRAPI_API_URL}${article.image2.data.attributes.url}`}
                  width={article.image2.data.attributes.width}
                  height={article.image2.data.attributes.height}
                />
                {/* <figcaption>{article.image.data.attributes.caption}</figcaption> */}
              </figure>
            </div>
          ) : (
            ''
          )}

          {/* {article.image.data ? (
          <>{`${process.env.NEXT_PUBLIC_STRAPI_API_URL}${article.image.data.attributes.formats.small.url}`}</>
        ) : (
          ''
        )} */}
        </div>
        <div className='addenda'>
          {article.addenda ? (
            <>
              {article.addenda.map((addendum, i) => {
                return (
                  <div key={i} id={addendum.slug} className='max-w-2xl'>
                    {addendum.title ? <h2>{addendum.title}</h2> : ''}
                    {addendum.summary ? <h4>{addendum.summary}</h4> : ''}
                    <div
                      dangerouslySetInnerHTML={{ __html: addendum.body }}
                    ></div>
                  </div>
                );
              })}
            </>
          ) : (
            ''
          )}
        </div>
        <div>
          <ul className='mt-4 text-md'>
            {article.people &&
              article.people.map((person, i) => {
                return (
                  <li key={i}>
                    {person.url ? (
                      <a href={person.url}>{person.name}</a>
                    ) : (
                      <span>{person.name}</span>
                    )}
                    {' – '}
                    {person.role}

                    {person.affiliation ? (
                      <>
                        {', '}
                        {person.affiliation}
                      </>
                    ) : (
                      ''
                    )}
                  </li>
                );
              })}
          </ul>
        </div>
        <div>
          {article.references.length ? (
            <ul className='list-[square]'>
              {article.references.map((reference, i) => (
                <Reference reference={reference} key={i} />
              ))}
            </ul>
          ) : (
            ''
          )}
        </div>
      </div>
    </>
  );
};

export default Article;
