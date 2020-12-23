class BBParser {
  constructor () {}
  
  static parse(text) {
    const imgRe = /^\[img\](?<imgData>[/;,=+A-Za-z0-9:]*)\[\/img\]$/;
    const image = text.match(imgRe);
    if (image) {
      const imageTag = `<img class="img-msg" src="${image.groups.imgData}">`;
      return imageTag;
    } else {
      return text;
    }
  }
}

export default BBParser;