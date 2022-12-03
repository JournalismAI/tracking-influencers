import Link from 'next/link';
import { useState } from 'react';
import { fetcher } from '../lib/api';
import { setToken, unsetToken } from '../lib/auth';
import { useUser } from '../lib/authContext';

import { Prose } from '@/components/Prose';
import { LockClosedIcon } from '@heroicons/react/20/solid';

const Login = () => {
  const [data, setData] = useState({
    identifier: '',
    password: '',
  });

  const { user, loading } = useUser();

  const handleSubmit = async (e) => {
    e.preventDefault();

    const responseData = await fetcher(
      `${process.env.NEXT_PUBLIC_STRAPI_URL}/auth/local`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          identifier: data.identifier,
          password: data.password,
        }),
      }
    );
    setToken(responseData);
  };

  const logout = () => {
    unsetToken();
  };

  const handleChange = (e) => {
    setData({ ...data, [e.target.name]: e.target.value });
  };

  return (
    <div className='flex min-h-full flex-col justify-center pb-4 sm:pb-8 pr-2 sm:pr-12'>
      <Prose>
        {/* {!loading && (user ? '' : '')} */}

        {/* {user ? (
          <button
            className='block prose-a:font-normal dark:prose-a:text-sky-400'
            onClick={logout}
            style={{ cursor: 'pointer' }}
          >
            Logout
          </button>
        ) : (
          ''
        )} */}
        {!user ? (
          <div className='max-w-full space-y-8'>
            {/* <div>
              <h2 className='prose-headings:scroll-mt-28 prose-headings:font-display prose-headings:font-normal lg:prose-headings:scroll-mt-[8.5rem]'>
                Sign in to view
              </h2>
            </div> */}
            <form
              onSubmit={handleSubmit}
              className='mt-8 space-y-6'
              action='#'
              method='POST'
            >
              <input type='hidden' name='remember' defaultValue='true' />
              <div className='-space-y-px rounded-md shadow-sm'>
                <div>
                  <label htmlFor='username' className='sr-only'>
                    Username
                  </label>
                  <input
                    id='username'
                    name='identifier'
                    type='text'
                    onChange={handleChange}
                    autoComplete='username'
                    required
                    className='relative block w-full appearance-none rounded-none rounded-t-md border border-sky-100 px-3 py-2 text-gray-900 placeholder-gray-500 focus:z-10 focus:border-sky-500 focus:outline-none focus:ring-sky-500 sm:text-md'
                    placeholder='Username'
                  />
                </div>
                <div>
                  <label htmlFor='password' className='sr-only'>
                    Password
                  </label>
                  <input
                    id='password'
                    name='password'
                    type='password'
                    onChange={handleChange}
                    autoComplete='current-password'
                    required
                    className='relative block w-full appearance-none rounded-none rounded-b-md border border-sky-100 px-3 py-2 text-gray-900 placeholder-gray-500 focus:z-10 focus:border-sky-500 focus:outline-none focus:ring-sky-500 sm:text-md'
                    placeholder='Password'
                  />
                </div>
              </div>

              <div>
                <button
                  type='submit'
                  className='group relative flex w-full justify-center rounded-md border border-transparent bg-sky-500 dark:bg-slate-700 py-2 px-4 text-sm font-medium text-white hover:bg-sky-600 dark:hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-2'
                >
                  <span className='absolute inset-y-0 left-0 flex items-center pl-3'>
                    <LockClosedIcon
                      className='h-5 w-5 text-sky-400 dark:text-slate-500 group-hover:text-sky-400 dark:group-hover:text-slate-500'
                      aria-hidden='true'
                    />
                  </span>
                  Sign in
                </button>
              </div>
            </form>
          </div>
        ) : (
          <button
            className='block prose-a:font-normal dark:prose-a:text-sky-400'
            onClick={logout}
            style={{ cursor: 'pointer' }}
          >
            Logout
          </button>
        )}
      </Prose>
    </div>
  );
};

export default Login;
