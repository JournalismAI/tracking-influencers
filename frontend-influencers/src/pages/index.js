// import { fetchAPI } from '@/lib/api';

import { gql } from '@apollo/client';
import client from '@/lib/api';

import Hero from '@/components/Hero';
import Layout from '@/components/Layout';
import Seo from '@/components/Seo';

import { useFetchUser } from '@/lib/authContext';
import Callout from '@/components/Callout';
import Article_2 from '@/components/Article_2';

const Home = ({ categories, homepage }) => {
  const { user, loading } = useFetchUser();

  return (
    <Layout user={user} categories={categories}>
      <Seo seo={homepage.attributes.seo} />
      <div>
        {/* {!loading &&
          (user ? (
            <blockquote className='py-2 text-red-500'>
              Huzzah! You are authorized to see this page, but alas there is
              nothing to see
            </blockquote>
          ) : (
            ''
          ))} */}
        {/* {!loading && (user ? '' : <Callout />)} */}
        <Hero hero={homepage.attributes.hero} />
        <Article_2 article={homepage.attributes} />
      </div>
    </Layout>
  );
};

export async function getStaticProps() {
  // const [homepage] = await Promise.all([
  //   fetchAPI('/home', {
  //     populate: {
  //       hero: '*',
  //       seo: { populate: '*' },
  //     },
  //   }),
  // ]);

  const { data } = await client.query({
    query: gql`
      query {
        home {
          data {
            id
            attributes {
              title
              slug
              summary
              body
              image {
                data {
                  id
                  attributes {
                    name
                    alternativeText
                    caption
                    url
                    width
                    height
                    formats
                  }
                }
              }
              image2 {
                data {
                  id
                  attributes {
                    name
                    alternativeText
                    caption
                    url
                    width
                    height
                    formats
                  }
                }
              }
              addenda {
                id
                title
                slug
                body
              }
              people {
                title
                people {
                  name
                  url
                  affiliation
                  role
                }
              }
              references {
                id
                author
                title
                source
                date
                link {
                  text
                  url
                  class
                  type
                }
              }
              hero {
                id
                slug
                title
                label
                summary
                body
                image {
                  data {
                    id
                    attributes {
                      name
                      alternativeText
                      caption
                      url
                      width
                      height
                      formats
                    }
                  }
                }
              }
            }
          }
        }
        categories(sort: "id:asc") {
          data {
            id
            attributes {
              name
              slug
              articles(sort: "priority:asc") {
                data {
                  id
                  attributes {
                    slug
                    title
                    summary
                    body
                    priority
                  }
                }
              }
            }
          }
        }
      }
    `,
  });

  const homepage = data.home;
  const categories = data.categories;
  return {
    props: {
      categories: categories.data,
      homepage: homepage.data,
    },
    revalidate: 1,
  };
}

export default Home;
