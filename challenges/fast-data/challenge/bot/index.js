const { Bot } = require("./bot.js");

var bot = new Bot(`http://${process.env.HOST}:1337`);

console.log(`Running at ${bot.siteURL}`);

setInterval(async () => {
    try {
        await bot.visitPage();
    } catch(e) {
        console.error(e);
    }
}, 30_000);
