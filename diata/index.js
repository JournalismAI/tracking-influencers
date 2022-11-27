if (process.env.NODE_ENV !== 'production') {
    require('dotenv-yaml').config({
        path: __dirname + '/env.yaml'
    });
}

const fs = require('fs').promises;
const csvtojson = require('csvtojson');
const percent = require('percent-value');
const prettyHrtime = require('pretty-hrtime');
const instagram = require('./lib/instagram');

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

async function processUsers(source, total = null) {

    if (!total) {
        total = source.length;
    }

    const current = source.shift();

    const state = (source.length === 0) ? ' - last one: ' : ' - so far: ';

    console.log('Extracting: ' + current + state + percent(total - source.length).of(total).toFixed(1) + '%');

    const data = await instagram.getUserData(current);

    if (data.error) {
        return console.log(data.msg);
    }

    await fs.writeFile(`${data.output.data}/profile.json`, JSON.stringify(data.profile));
    await fs.writeFile(`${data.output.data}/posts.json`, JSON.stringify(data.posts));
    await fs.writeFile(`${data.output.data}/tagged.json`, JSON.stringify(data.tagged));

    if (source.length) {
        return processUsers(source, total);
    }
}

(async () => {

    const file = 'list.csv';
    const start = process.hrtime();
    const source = await outcome(csvtojson().fromFile(file));

    if (!source.success) {
        return console.log(source.error.message);
    }

    if (process.env.INSTAGRAM_PROFILES === 'true' && (!process.env.INSTAGRAM_POSTS || process.env.INSTAGRAM_POSTS === 'false')) {
        console.log('Collecting: profiles only');
        const data = await instagram.profiles(source.result);
        await fs.writeFile(`${data.output.data}/profiles.json`, JSON.stringify(data.profiles));
    }

    if (process.env.INSTAGRAM_PROFILES === 'true' && process.env.INSTAGRAM_POSTS === 'true') {
        console.log(`Collecting: profiles and posts ${(process.env.INSTAGRAM_IMAGES === 'true') ? 'and images' : ''}`);
        const users = source.result.map(item => item.username);
        await processUsers(users);
    }

    const end = process.hrtime(start);
    console.log('All done in ' + prettyHrtime(end));

})();