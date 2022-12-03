import { UserProvider } from '@/lib/authContext';
import { useRouter } from 'next/router';

import { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';

import Header from '@/components/Header';

import Navigation from '@/components/Navigation';
import Navigation_data from '@/components/Navigation_data';

import { Prose } from '@/components/Prose';

import Login from '@/components/Login';

const Layout = ({ user, loading = false, children, categories, seo }) => {
  let router = useRouter();

  return (
    <UserProvider value={{ user, loading }}>
      <Header categories={categories} />

      {/* <Navigation categories={categories} /> */}

      <div className='relative mx-auto flex max-w-8xl justify-center sm:px-2 lg:px-8 xl:px-12'>
        <div className='hidden lg:relative lg:block lg:flex-none'>
          <div className='absolute inset-y-0 right-0 w-[50vw] bg-slate-50 dark:hidden' />
          {/* sidebar left */}
          <div className='sticky top-[4.5rem] -ml-0.5 h-[calc(100vh-4.5rem)] overflow-y-auto py-16 pl-0.5 no-scrollbar'>
            <div className='absolute top-16 bottom-0 right-0 hidden h-12 w-px bg-gradient-to-t from-slate-800 dark:block' />
            <div className='absolute top-28 bottom-0 right-0 hidden w-px bg-slate-800 dark:block' />
            {router.asPath.includes('/docs') || router.asPath === `/` ? (
              <Navigation
                router={router}
                categories={categories}
                className='w-64 pr-8 xl:w-72 xl:pr-16'
              />
            ) : (
              <Navigation_data
                router={router}
                className='w-64 pr-8 xl:w-72 xl:pr-16'
              />
            )}
          </div>
        </div>
        {/* main */}
        <div className='min-w-0 max-w-2xl flex-auto px-4 py-4 md:py-16 lg:max-w-none lg:pr-0 lg:pl-8 xl:px-16'>
          <article>
            {/* <header className='mb-9 space-y-1'>
            <p className='font-display text-sm font-medium text-sky-500'>
              section title
            </p>

            <h1 className='font-display text-3xl tracking-tight text-slate-900 dark:text-white'>
              title
            </h1>
          </header> */}

            <Prose>{children}</Prose>
          </article>

          {/* <dl className='mt-12 flex border-t border-slate-200 pt-6 dark:border-slate-800'>
          <div>
            <dt className='font-display text-sm font-medium text-slate-900 dark:text-white'>
              Previous
            </dt>
            <dd className='mt-1'>
              <Link
                href='#'
                className='text-base font-semibold text-slate-500 hover:text-slate-600 dark:text-slate-400 dark:hover:text-slate-300'
              >
                <>
                  <span aria-hidden='true'>&larr;</span> title 1
                </>
              </Link>
            </dd>
          </div>

          <div className='ml-auto text-right'>
            <dt className='font-display text-sm font-medium text-slate-900 dark:text-white'>
              Next
            </dt>
            <dd className='mt-1'>
              <Link
                href='#'
                className='text-base font-semibold text-slate-500 hover:text-slate-600 dark:text-slate-400 dark:hover:text-slate-300'
              >
                <>
                  title 3 <span aria-hidden='true'>&rarr;</span>
                </>
              </Link>
            </dd>
          </div>
        </dl> */}
        </div>
        {/* sidebar right */}

        {router.asPath == `/data` ? (
          <div className='hidden xl:sticky xl:top-[4.5rem] xl:-mr-6 xl:block xl:h-[calc(100vh-4.5rem)] xl:flex-none xl:overflow-y-auto xl:py-16 xl:pr-6'>
            {/* <Login user={user} /> */}
            {/* <nav aria-labelledby='on-this-page-title' className='w-56'>
          <h2
            id='on-this-page-title'
            className='font-display text-sm font-medium text-slate-900 dark:text-white'
          >
            On this page
          </h2>
          <ol role='list' className='mt-4 space-y-3 text-sm'>
            <li>
              <h3>
                <Link
                  href='#'
                  className='font-normal text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300'
                >
                  section title
                </Link>
              </h3>
              <ol
                role='list'
                className='mt-2 space-y-3 pl-5 text-slate-500 dark:text-slate-400'
              >
                <li>
                  <Link
                    href='#'
                    className='hover:text-slate-600 dark:hover:text-slate-300'
                  >
                    subsection title 1
                  </Link>
                </li>

                <li>
                  <Link href='#' className='text-sky-500'>
                    subsection title 2
                  </Link>
                </li>
              </ol>
            </li>
          </ol>
        </nav> */}
          </div>
        ) : (
          ''
        )}
      </div>
    </UserProvider>
  );
};

export default Layout;
