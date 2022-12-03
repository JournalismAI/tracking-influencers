import { gql } from '@apollo/client';
import client from '../../lib/api';
import { fetchAPI } from '@/lib/api';

import Layout from '@/components/Layout';
import Seo from '@/components/Seo';
import Articles from '@/components/Articles';

const Category_Slug = ({ category, categories }) => {
  const seo = {
    title: category.attributes.name,
    description: `All ${category.attributes.name} articles`,
  };

  return (
    <Layout categories={categories.data}>
      <Seo seo={seo} />
      <div>
        <div>
          <h1>{category.attributes.name}</h1>

          <Articles articles={category.attributes.articles.data} />
        </div>
      </div>
    </Layout>
  );
};

export async function getStaticPaths() {
  const { data } = await client.query({
    query: gql`
      query {
        categories {
          data {
            attributes {
              slug
            }
          }
        }
      }
    `,
  });

  const categories = data.categories.data;

  // console.log(categories);

  const paths = categories.map((category) => ({
    params: { slug: category.attributes.slug },
  }));
  return { paths, fallback: false };
}

export async function getStaticProps({ params }) {
  const slug = params.slug;

  const { data } = await client.query({
    query: gql`
      query ($slug: String) {
        categories(filters: { slug: { eq: $slug } }) {
          data {
            id
            attributes {
              name
              articles(sort: "priority:asc") {
                data {
                  id
                  attributes {
                    title
                    summary
                    body
                    slug
                    priority
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
                    addenda {
                      id
                      title
                      slug
                      body
                      class
                    }
                    people {
                      name
                      url
                      affiliation
                      role
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
                  }
                }
              }
            }
          }
        }
      }
    `,
    variables: { slug },
  });

  // temporary fetch for navigation
  const categories_0 = await fetchAPI('/categories', { populate: '*' });
  const category = data.categories.data[0];

  return {
    props: {
      categories: categories_0,
      category: category,
    },
    revalidate: 1,
  };
}

export default Category_Slug;
