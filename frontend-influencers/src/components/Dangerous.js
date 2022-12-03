const Dangerous = ({ body }) => {
  return (
    <div
      dangerouslySetInnerHTML={{
        __html: body,
      }}
    ></div>
  );
};

export default Dangerous;
