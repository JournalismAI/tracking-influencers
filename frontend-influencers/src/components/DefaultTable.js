import { ArrowDownIcon, ArrowUpIcon } from '@heroicons/react/outline';
import { useTable, useGlobalFilter, usePagination } from 'react-table';
import GlobalFilter from './GlobalFilter';

function DefaultTable({ columns, data, defaultColumn }) {
  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    page,
    nextPage,
    previousPage,
    canNextPage,
    canPreviousPage,
    pageOptions,
    state,
    setGlobalFilter,

    gotoPage,
    pageCount,
    setPageSize,
    prepareRow,
  } = useTable(
    {
      columns,
      data,
      defaultColumn,
      // initialState: { pageSize: '20' },
    },
    useGlobalFilter,
    usePagination
  );

  const { globalFilter, pageIndex, pageSize } = state;

  return (
    <div className='px-0'>
      <div className='sm:flex sm:items-center'>
        <div className='sm:flex-auto'>
          {/* <GlobalFilter filter={globalFilter} setFilter={setGlobalFilter} /> */}
          <div className='shadow-sm ring-1 ring-black ring-opacity-5'>
            <table
              className='min-w-full divide-y divide-gray-200'
              style={{ borderSpacing: 0 }}
              {...getTableProps()}
            >
              <thead className='bg-gray-50'>
                {headerGroups.map((headerGroup, i) => (
                  <tr key={i} {...headerGroup.getHeaderGroupProps()}>
                    {headerGroup.headers.map((column, i) => (
                      <th
                        key={i}
                        scope='col'
                        className='uppercase sticky top-20 z-10 border-b border-gray-300 bg-gray-50 bg-opacity-75 py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 backdrop-blur backdrop-filter sm:pl-6 lg:pl-8'
                        {...column.getHeaderProps()}
                      >
                        {column.render('Header')}
                      </th>
                    ))}
                  </tr>
                ))}
              </thead>
              <tbody {...getTableBodyProps()}>
                {page.map((row, i) => {
                  prepareRow(row);
                  return (
                    <tr
                      key={i}
                      {...row.getRowProps()}
                      className={i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
                    >
                      {row.cells.map((cell, i) => {
                        return (
                          <td
                            key={i}
                            className='px-6 py-4 text-sm font-medium text-gray-900 '
                            {...cell.getCellProps()}
                          >
                            {cell.render('Cell')}
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}
              </tbody>
            </table>
            <nav
              className='bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6'
              aria-label='Pagination'
            >
              <div className='hidden sm:block'>
                <p className='text-sm text-gray-700'>
                  {pageOptions.length > 1 ? (
                    <>
                      Page <span className='font-medium'>{pageIndex + 1}</span>{' '}
                      of{' '}
                      <span className='font-medium'>{pageOptions.length}</span>
                    </>
                  ) : (
                    <span className='font-medium'>&nbsp;</span>
                  )}
                </p>
              </div>
              <div className='flex-1 flex justify-between sm:justify-end'>
                {pageOptions.length > 1 ? (
                  <>
                    <button
                      className='relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50'
                      onClick={() => previousPage()}
                      disabled={!canPreviousPage}
                    >
                      Previous
                    </button>
                    <button
                      className='ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50'
                      onClick={() => nextPage()}
                      disabled={!canNextPage}
                    >
                      Next
                    </button>
                  </>
                ) : (
                  ''
                )}
              </div>
            </nav>
          </div>
        </div>
      </div>
    </div>
  );
}
export default DefaultTable;
