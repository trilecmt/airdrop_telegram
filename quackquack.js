const ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjQzMTkwNSwidGltZXN0YW1wIjoxNzE2NjE5NzI4ODIyLCJ0eXBlIjoxLCJpYXQiOjE3MTY2MTk3MjgsImV4cCI6MTcxNzIyNDUyOH0.xBS8dH51VdbYII6xK6sQGhiia9JuYea6yYEZ09NASxU"
let listColect = [];
let listDuck = [];
// "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjQzNDAxNywidGltZXN0YW1wIjoxNzE2NjIyNjIxMzU4LCJ0eXBlIjoxLCJpYXQiOjE3MTY2MjI2MjEsImV4cCI6MTcxNzIyNzQyMX0.fbLXxYgtn53HEFQXO2sSmXHw5Wop7A2s4rtUVvHNShI"
Array.prototype.random = function () {
  return this[Math.floor(Math.random() * this.length)];
};

function getTotalEgg() {
  fetch("https://api.quackquack.games/balance/get", {
    headers: {
      accept: "*/*",
      "accept-language": "en-US,en;q=0.9,vi;q=0.8",
      authorization: "Bearer " + ACCESS_TOKEN,
      "if-none-match": 'W/"1a9-I7Onn3jBU9AHo0MlzSY8mMECNvQ"',
      priority: "u=1, i",
      "sec-ch-ua":
        '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
      "sec-ch-ua-mobile": "?0",
      "sec-ch-ua-platform": '"Windows"',
      "sec-fetch-dest": "empty",
      "sec-fetch-mode": "cors",
      "sec-fetch-site": "cross-site",
      Referer: "https://dd42189ft3pck.cloudfront.net/",
      "Referrer-Policy": "strict-origin-when-cross-origin",
    },
    body: null,
    method: "GET",
  })
    .then((response) => response.json())
    .then((res) => {
      // console.log(res);
      res.data.data.map((item) => {
        if (item.symbol === "EGG") {
          console.log("");
          console.log("Da thu thap", Number(item.balance), "trung");
          console.log("");
        }
      });
    })
    .catch((error) => {
      console.log("ERROR", error);
    });
}

function getListReload() {
  fetch("https://api.quackquack.games/nest/list-reload", {
    headers: {
      accept: "*/*",
      "accept-language": "en-US,en;q=0.9,vi;q=0.8",
      authorization: "Bearer " + ACCESS_TOKEN,
      "if-none-match": 'W/"1218-LZvWPzXbQkzjfWJ5mauEo0z3f9c"',
      priority: "u=1, i",
      "sec-ch-ua":
        '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
      "sec-ch-ua-mobile": "?0",
      "sec-ch-ua-platform": '"Windows"',
      "sec-fetch-dest": "empty",
      "sec-fetch-mode": "cors",
      "sec-fetch-site": "cross-site",
      Referer: "https://dd42189ft3pck.cloudfront.net/",
      "Referrer-Policy": "strict-origin-when-cross-origin",
    },
    body: null,
    method: "GET",
  })
    .then((response) => response.json())
    .then((res) => {
      // console.log(res);

      if (listDuck.length === 0) {
        res.data.duck.map((item) => {
          listDuck.push(item.id);
        });
      }

      res.data.nest.map((item) => {
        // console.log(item);
        if (item.type_egg) listColect.push(item.id);
      });

      console.log("So trung co the thu thap:", listColect.length);
      console.log(listColect);
      console.log("");
    })
    .catch((error) => {
      console.log("ERROR", error);
    });
}

function collect() {
  if (listColect.length === 0) return setTimeout(collect, 3e3);

  const egg = listColect[0];

  fetch("https://api.quackquack.games/nest/collect", {
    headers: {
      accept: "*/*",
      "accept-language": "en-US,en;q=0.9,vi;q=0.8",
      authorization: "Bearer " + ACCESS_TOKEN,
      "content-type": "application/x-www-form-urlencoded",
      priority: "u=1, i",
      "sec-ch-ua":
        '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
      "sec-ch-ua-mobile": "?0",
      "sec-ch-ua-platform": '"Windows"',
      "sec-fetch-dest": "empty",
      "sec-fetch-mode": "cors",
      "sec-fetch-site": "cross-site",
      Referer: "https://dd42189ft3pck.cloudfront.net/",
      "Referrer-Policy": "strict-origin-when-cross-origin",
    },
    body: "nest_id=" + egg,
    method: "POST",
  })
    .then((response) => response.json())
    .then((res) => {
      //   console.log(res);
      console.log("Thu thap thanh cong trung", egg);
      layEgg(egg);
    })
    .catch((error) => {
      console.log("ERROR", error);
      setTimeout(() => {
        collect(egg);
      }, 3e3);
    });
}

function layEgg(egg) {
  const duck = listDuck.random();
  //   console.log(duck);
  fetch("https://api.quackquack.games/nest/lay-egg", {
    headers: {
      accept: "*/*",
      "accept-language": "en-US,en;q=0.9,vi;q=0.8",
      authorization: "Bearer " + ACCESS_TOKEN,
      "content-type": "application/x-www-form-urlencoded",
      priority: "u=1, i",
      "sec-ch-ua":
        '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
      "sec-ch-ua-mobile": "?0",
      "sec-ch-ua-platform": '"Windows"',
      "sec-fetch-dest": "empty",
      "sec-fetch-mode": "cors",
      "sec-fetch-site": "cross-site",
      Referer: "https://dd42189ft3pck.cloudfront.net/",
      "Referrer-Policy": "strict-origin-when-cross-origin",
    },
    body: "nest_id=" + egg + "&duck_id=" + duck,
    method: "POST",
  })
    .then((response) => response.json())
    .then((res) => {
      //   console.log(res);
      getTotalEgg();
      listColect.shift();
      setTimeout(collect, 3e3);
    })
    .catch((error) => {
      console.log("ERROR", error);
      setTimeout(() => {
        layEgg(egg);
      }, 3e3);
    });
}

getTotalEgg();
getListReload();

setInterval(() => {
  getListReload();
}, 10e3);

collect();