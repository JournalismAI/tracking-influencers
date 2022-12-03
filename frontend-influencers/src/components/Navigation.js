import Link from 'next/link';
import clsx from 'clsx';

const Navigation = ({ router, categories, className }) => {
  return (
    <nav className={clsx('text-base lg:text-sm', className)}>
      <ul role='list' className='space-y-9'>
        <li>
          <Link href={`/`}>
            <h2 className='font-display font-medium text-slate-900 dark:text-white'>
              The Project (in 10 Minutes)
            </h2>
          </Link>
          <ul
            role='list'
            className='mt-2 space-y-2 border-l-2 border-slate-100 dark:border-slate-800 lg:mt-4 lg:space-y-4 lg:border-slate-200'
          >
            <li className='relative'>
              <Link href={`/`}>
                <a
                  className={`block w-full pl-3.5 before:pointer-events-none before:absolute before:-left-1 before:top-1/2
                        before:h-1.5 before:w-1.5 before:-translate-y-1/2 before:rounded-full ${
                          router.asPath === `/`
                            ? 'font-semibold text-sky-500 before:bg-sky-500'
                            : 'text-slate-500 before:hidden before:bg-slate-300 hover:text-slate-600 hover:before:block dark:text-slate-400 dark:before:bg-slate-700 dark:hover:text-slate-300'
                        }`}
                >
                  Tracking Influencers: four lessons when dealing with Instagram
                </a>
              </Link>
            </li>
          </ul>
        </li>
        {categories
          .slice()
          .sort((a, b) => a.id - b.id)
          // .sort((a, b) => (a.name > id.name ? 1 : -1))
          .map((category, i) => (
            <li key={i}>
              <h2 className='font-display font-medium text-slate-900 dark:text-white'>
                <Link href={`/docs/${category.attributes.slug}`}>
                  {category.attributes.name}
                </Link>
              </h2>

              <ul
                role='list'
                className='mt-2 space-y-2 border-l-2 border-slate-100 dark:border-slate-800 lg:mt-4 lg:space-y-4 lg:border-slate-200'
              >
                {category.attributes.articles.data
                  .slice()
                  .sort((a, b) =>
                    a.attributes.priority > b.attributes.priority ? 1 : -1
                  )
                  .map((article, i) => (
                    <li key={i} className='relative'>
                      <Link
                        href={`/docs/${category.attributes.slug}#${article.attributes.slug}`}
                      >
                        {/* <a
                          className={clsx(
                            'block w-full pl-3.5 before:pointer-events-none before:absolute before:-left-1 before:top-1/2 before:h-1.5 before:w-1.5 before:-translate-y-1/2 before:rounded-full',
                            article.attributes.slug === router.pathname
                              ? 'font-semibold text-sky-500 before:bg-sky-500'
                              : 'text-slate-500 before:hidden before:bg-slate-300 hover:text-slate-600 hover:before:block dark:text-slate-400 dark:before:bg-slate-700 dark:hover:text-slate-300'
                          )}
                        >
                          {article.attributes.title}
                        </a> */}
                        <a
                          className={`block w-full pl-3.5 before:pointer-events-none before:absolute before:-left-1 before:top-1/2
                        before:h-1.5 before:w-1.5 before:-translate-y-1/2 before:rounded-full ${
                          router.asPath ===
                          `/docs/${category.attributes.slug}#${article.attributes.slug}`
                            ? 'font-semibold text-sky-500 before:bg-sky-500'
                            : 'text-slate-500 before:hidden before:bg-slate-300 hover:text-slate-600 hover:before:block dark:text-slate-400 dark:before:bg-slate-700 dark:hover:text-slate-300'
                        }`}
                        >
                          {article.attributes.title}
                        </a>
                      </Link>
                    </li>
                  ))}
              </ul>
            </li>
          ))}
      </ul>
    </nav>
  );
};

export default Navigation;
