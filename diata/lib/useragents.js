const path = require('path');
const zlib = require('zlib');
const fs = require('fs').promises;
const constants = require('fs').constants;
const dayjs = require('dayjs');
const uaparser = require('ua-parser-js');
const fetch = require('node-fetch');

const contentPath = path.join(__dirname, '../useragents.json');

const outcome = (promise) => {
    return promise
        .then(result => ({
            success: true,
            result
        }))
        .catch(error => ({
            success: false,
            error
        }));
};

function shuffle(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}

async function update(status = true) {
    const res = await fetch('https://raw.githubusercontent.com/intoli/user-agents/master/src/user-agents.json.gz');
    const buff = await res.buffer();
    const data = await new Promise((resolve) => {
        zlib.unzip(buff, (_, buffer) => {
            resolve(JSON.parse(buffer.toString()));
        });
    });
    const desktop = [...new Set(data.filter(item => item.deviceCategory === 'desktop').map(item => item.userAgent))];
    const mobile = [...new Set(data.filter(item => item.deviceCategory === 'mobile').map(item => item.userAgent))];
    const content = [...desktop, ...mobile].map(item => uaparser(item)).filter(item => item.browser.name && item.os.name).map(item => item.ua);
    await fs.writeFile(contentPath, JSON.stringify(content));
    if (status) {
        return content;
    }
}

async function content() {
    const available = await outcome(fs.access(contentPath, constants.R_OK | constants.W_OK));
    if (!available.success) {
        console.log('Getting user agents');
        return await update();
    }

    const stat = await fs.stat(contentPath);

    if (dayjs().diff(stat.ctime, 'day') >= 1) {
        console.log('Updating user agents');
        return await update();
    }

    const content = await fs.readFile(contentPath);
    return JSON.parse(content.toString());
}

(async () => {
    const [args] = process.argv.slice(2);
    if (args && args.includes('update')) {
        return update(false);
    }
})();

const init = (async () => {

    const userAgents = await content();

    let entries = shuffle(userAgents).entries();

    return () => {
        let item = entries.next();
        if (!item.done) {
            return item.value[1];
        }
        entries = shuffle(userAgents).entries();
        return entries.next().value[1];
    };

})();

module.exports = {
    init,
    update
}