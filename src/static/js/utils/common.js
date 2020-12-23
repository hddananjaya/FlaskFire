const getProtocol = () => {
  return location.hostname.includes('localhost') ?
    'http://' : 'https://';
}

export {
  getProtocol,
}