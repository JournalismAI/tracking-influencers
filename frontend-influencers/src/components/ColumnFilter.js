const ColumnFilter = ({ column }) => {
  const { filterValue, setFilter } = column;

  return (
    <div className='mb-5'>
      <div className='mt-1'>
        <input
          type='text'
          name='search'
          id='search'
          className='shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full text-xs border-gray-300 rounded-md'
          placeholder='Search'
          value={filterValue || ''}
          onChange={(e) => setFilter(e.target.value)}
        />
      </div>
    </div>
  );
};

export default ColumnFilter;
