var fs = require('fs');

function exportToFile(fileName, content) {
  var message = JSON.stringify(content, null, ' ');
  fs.writeFile(
    __dirname + '/test_results/' + fileName + '.json',
    message,
    function(err) {
      if (err) {
        return console.log(err);
      }
      return;
    }
  );
}

module.exports = { exportToFile };
