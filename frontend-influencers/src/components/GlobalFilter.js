import { useState } from 'react';
// import { useAsyncDebounce } from 'react-table';

const GlobalFilter = ({ filter, setFilter }) => {
  // const [value, setValue] = useState(filter);

  // const onChange = useAsyncDebounce((value) => {
  //   setFilter(value || undefined);
  // }, 400);

  return (
    <div className='mb-5'>
      <label
        htmlFor='search'
        className='block text-sm font-medium text-gray-700'
      >
        Search
      </label>
      <div className='mt-1'>
        <input
          type='text'
          name='search'
          id='search'
          className='shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-4/12 sm:text-sm border-gray-300 rounded-md'
          placeholder=''
          value={filter || ''}
          onChange={(e) => setFilter(e.target.value)}
          // value={value || ''}
          // onChange={(e) => {
          //   setValue(e.target.value);
          //   onChange(e.target.value);
          // }}
        />
      </div>
      {/* <p className='mt-2 text-sm text-gray-500'>
        La ricerca riguarda tutte le colonne
      </p> */}
    </div>
  );
};

export default GlobalFilter;
