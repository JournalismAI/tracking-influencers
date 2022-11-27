const useragents = require('./useragents');
const randomInt = require('random-int');
const puppeteer = require('puppeteer');

function timeout(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function get(target, storeCookie, headers = {}, hashes = [], feed = [], count = []) {

    const ua = (await useragents.init)();

    const headless = (storeCookie.length) ? true : false;

    const browser = await puppeteer.launch({
        headless,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    const page = await browser.newPage();

    page.setViewport({
        width: 1080,
        height: 640,
        deviceScaleFactor: 2
    });

    await page.setUserAgent(ua);

    process.env.USER_AGENT = ua;

    if (storeCookie.length) {

        await page.setCookie(...storeCookie);

        await page.setRequestInterception(true);

        await page.on('request', (request) => {
            const current = request.headers();
            const url = request.url();
            if (Object.keys(current).includes('x-ig-app-id')) {
                Object.assign(headers, current);
            }
            if (url.includes('query_hash')) {
                hashes.push(decodeURIComponent(url));
            }
            if (url.includes('?count=') && !url.includes('max_id')) {
                count.push(decodeURIComponent(url));
            }
            if (url.includes('max_id')) {
                feed.push(decodeURIComponent(url));
            }
            request.continue();
        });

        await page.goto(`https://www.${process.env.INSTAGRAM_HOST}/${target}/`, {
            waitUntil: 'networkidle2'
        });

        await timeout(randomInt(4000, 6000));

        await browser.close();

        return {
            cookies: storeCookie,
            count: [...new Set(count)],
            feed: [...new Set(feed)],
            hashes,
            headers
        };
    }

    await page.goto(`https://www.${process.env.INSTAGRAM_HOST}/accounts/login/`, {
        waitUntil: 'networkidle2'
    });

    await timeout(randomInt(2000, 3000));

    if (!headless) {
        const [button] = await page.$x("//button[contains(., 'Only allow essential cookies')]");
        await button.click();
    }

    await page.click('[role="dialog"] button');

    await timeout(randomInt(2000, 3000));

    await page.type('input[name=username]', process.env.INSTAGRAM_USER, {
        delay: 5
    });

    await timeout(randomInt(3000, 4000));

    await page.type('input[name=password]', process.env.INSTAGRAM_PASSWORD, {
        delay: 8
    });

    await timeout(randomInt(2000, 3000));

    await page.click('[type="submit"]');

    if (!headless) {
        await page.waitForXPath('//button[contains(text(), "Not now")]');
        const [button] = await page.$x('//button[contains(text(), "Not now")]')
        await button.click();
    }

    await timeout(randomInt(4000, 5000));

    await page.setRequestInterception(true);

    await page.on('request', (request) => {
        const current = request.headers();
        const url = request.url();
        if (Object.keys(current).includes('x-ig-app-id')) {
            Object.assign(headers, current);
        }
        if (url.includes('query_hash')) {
            hashes.push(decodeURIComponent(url));
        }
        if (url.includes('?count=') && !url.includes('max_id')) {
            count.push(decodeURIComponent(url));
        }
        if (url.includes('max_id')) {
            feed.push(decodeURIComponent(url));
        }
        request.continue();
    });

    await page.goto(`https://www.${process.env.INSTAGRAM_HOST}/${target}/`, {
        waitUntil: 'networkidle2'
    });

    await timeout(randomInt(4000, 6000));

    const cookies = await page.cookies();

    if (!cookies.length) {
        await browser.close();
        return {
            error: true,
            msg: 'Unable to retrieve cookies'
        };
    }

    await browser.close();

    return {
        cookies,
        count: [...new Set(count)],
        feed: [...new Set(feed)],
        hashes,
        headers
    };

}

module.exports = {
    get
};