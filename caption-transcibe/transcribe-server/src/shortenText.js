const WHITE_SPACE = " ";
const NEW_LINE = "\n";
const CN_CODES = ["zh-CN", "zh", "zh-TW"]

const shortenText = (text, language_code) => {
  const ONE_ROW_CHAR_COUNT = CN_CODES.indexOf(language_code) > -1 ? 20 : 40;
  let blocks = [];
  let blockIndex = 0;

  while (blockIndex < text.length) {
    let block = text.substr(blockIndex);

    if (ONE_ROW_CHAR_COUNT < block.length) {
      block = text.substr(blockIndex, ONE_ROW_CHAR_COUNT);
      
      if (CN_CODES.indexOf(language_code) > -1){
        blockIndex += ONE_ROW_CHAR_COUNT;
      } else {
        if (text.substr(blockIndex + ONE_ROW_CHAR_COUNT, 1) === WHITE_SPACE || block.lastIndexOf(WHITE_SPACE) == -1) {
          blockIndex += ONE_ROW_CHAR_COUNT;
        } else {
          const blockLength = block.lastIndexOf(WHITE_SPACE) + 1;
          block = text.substr(blockIndex, blockLength);
          blockIndex += blockLength;
        }        
      }
    } else {
      blockIndex = text.length;
    }
    block = block.trim();
    // if(block.substr(0,1).indexOf(",.?!，。？！") > -1){
    //   block = block.substr(1)
    // }
    blocks.push(block);

    if (blocks.length > 2) {
      blocks.shift();
    }
  }

  switch (blocks.length) {
    case 1:
      return blocks[0];
    case 2:
      return CN_CODES.indexOf(language_code) > -1 ? (blocks[0] + blocks[1]) : (blocks[0] + " " + blocks[1]);
      // return blocks[0] + NEW_LINE + blocks[1];
    default:
      return;
  }
};

module.exports = shortenText;
