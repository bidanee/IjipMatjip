export const getPhotoUrl = (urlsString) => {
  if(!urlsString || typeof urlsString !== 'string'){
    return 'https://placehold.co/200x130/fbcfe8/4a044e?text=No+Image';
  }
  const urls = urlsString.replace(/[{}]/g,'').split(',')
  return urls
}