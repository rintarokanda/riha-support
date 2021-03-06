var request = require('request');
var Bleacon = require("bleacon");
var sleep = require('sleep');
var DETECTION_LEVEL = 0.2;
var MIN_STAY_TIME = 3;
var POST_URL = 'http://rehabili.mitotte.me/api/reception';

var active_users = [];

var is_detected = false;

Bleacon.startScanning();
Bleacon.on("discover", function(bleacon) {
  if (bleacon.accuracy < DETECTION_LEVEL && is_detected == false) {
    post(bleacon.major);
    is_detected = true;
  }
});

setInterval(function() {
  is_detected = false;
}, (MIN_STAY_TIME * 1000));

var post = function(uuid) {
    var url = POST_URL;
    console.log(JSON.stringify({uuid: uuid}));
    request.post(
        url,
        {
            json: false,
            form: {
                uuid: uuid,
            }
        },
        function (err, res, body) {
            if (!err && res.statusCode == 200) {
                console.log(body);
            } else {
                console.log(body);
            }
        }
    );
}
