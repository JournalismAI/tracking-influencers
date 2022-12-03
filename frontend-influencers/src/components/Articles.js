import Article from '@/components/Article';

const Articles = ({ articles }) => {
  return (
    <>
      {articles.map((article, i) => (
        <Article article={article.attributes} key={i} />
      ))}
    </>
  );
};

export default Articles;
