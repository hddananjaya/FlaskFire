class BBParser {
  constructor () {}
  
  static parse(text) {
    const imgRe = /^\[img\](?<imgData>[/;,=+A-Za-z0-9:]*)\[\/img\]$/;
    const urlRe = /https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)/;
    const exceptEmojisRe = /[A-Za-z0-9!@#$%^&*()_+=,./<?>{}{\]\[`~;:]/;
    const image = text.match(imgRe);
    const url = text.match(urlRe);
    const exceptEmojis = text.match(exceptEmojisRe);
    if (image) {
      const imageTag = `<img class="img-msg" src="${image.groups.imgData}">`;
      return imageTag;
    } else if (url) {
      const link = url["0"];
      const youtubeUrlIdentifier = "https://www.youtube.com/watch?v=";
      if (link.includes(youtubeUrlIdentifier)) {
        const youtubeId = link.split(youtubeUrlIdentifier)["1"];
        if (youtubeId !== "") {
          return `
            <iframe width="420" height="345" src="https://www.youtube.com/embed/${youtubeId}">
            </iframe>
          `;
        } 
      }
      return `<a target="_blank" href="${ url["0"] }">${ url["0"] }</a>`;
    } else if (!exceptEmojis) {
      return `<span style="font-size:30px"> ${ text } </span>`;
    } else {
      return text;
    }
  }
}

export default BBParser;