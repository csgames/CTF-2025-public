const puppeteer = require("puppeteer");

class Bot {
    constructor(siteURL) {
        this.siteURL = siteURL
    }

    async generateBrowser() {
        this.browser =  await puppeteer.launch({
            ignoreHTTPSErrors: true,
            args: [
                "--headless",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-gpu",
                "--no-gpu",
                "--disable-default-apps",
                "--disable-translate",
                "--disable-device-discovery-notifications",
                "--disable-software-rasterizer",
                "--disable-xss-auditor",
                "--disable-site-isolation-trials",
                "--disable-web-security",
            ],    
        });
    }

    async visitPage() {
        if (this.browser === undefined) {
            await this.generateBrowser();
        }

        const page = await this.browser.newPage();

        // Set cookie to use to the secret key
        await page.goto(`${this.siteURL}/pages/data.html`);
        await page.setCookie({
            name: "token",
            domain: process.env.HOST,
            path: "/", 
            value: process.env.SECRET,
            httpOnly: false,
            secure: false,
        });
        await page.goto(`${this.siteURL}/pages/data.html`);

        // Wait for the button to be available and click it
        await page.waitForSelector("button#btn");
        await page.click("button#btn");

        console.log("Visited page");
    }
}

module.exports.Bot = Bot;
