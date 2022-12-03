import Moment from 'react-moment';

const Reference = ({ reference }) => {
  return (
    <>
      {reference.link && reference.link.text ? (
        <li className='ml-4 px-1'>
          {reference.author ? <span>{reference.author}</span> : ''}
          {reference.author && reference.source ? (
            <span>
              {', '}
              {reference.source}
            </span>
          ) : (
            <>{reference.source ? <span>{reference.source}</span> : ''}</>
          )}
          <span>
            {(reference.source && reference.title) ||
            (reference.author && reference.title) ? (
              <span>
                , <i>{reference.title}</i>{' '}
              </span>
            ) : (
              <>{reference.title ? <i>{reference.title} </i> : ''}</>
            )}
          </span>

          {reference.date ? <span> ({reference.date}) </span> : ''}

          <a
            className='cursor-pointer underline'
            href={reference.link ? reference.link.url : ''}
          >
            {reference.link.text}
          </a>
        </li>
      ) : (
        <li className='ml-4 px-1'>
          <a
            className='cursor-pointer underline'
            href={reference.link ? reference.link.url : ''}
          >
            {reference.author ? <span>{reference.author}</span> : ''}

            {reference.author && reference.source ? (
              <span>
                {', '}
                {reference.source}
              </span>
            ) : (
              <>{reference.source ? <span>{reference.source}</span> : ''}</>
            )}

            <span>
              {(reference.source && reference.title) ||
              (reference.author && reference.title) ? (
                <span>
                  , <i>{reference.title}</i>{' '}
                </span>
              ) : (
                <>{reference.title ? <i>{reference.title} </i> : ''}</>
              )}
            </span>
          </a>
          {reference.date ? <span> ({reference.date}) </span> : ''}
        </li>
      )}
    </>
  );
};

export default Reference;
