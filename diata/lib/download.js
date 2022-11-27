const fs = require('fs');
const util = require('util');
const stream = require('stream');
const once = require('events').once;
const ndjson = require('iterable-ndjson');
const randomInt = require('random-int');
const jsonToCsv = require('json-to-csv-stream');
const Readable = require('stream').Readable;
const pool = require('@supercharge/promise-pool').PromisePool;
const image = require('./image');

const finished = util.promisify(stream.finished);
const pipeline = util.promisify(stream.pipeline);

function timeout(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function assets(data, output) {
    await pool.withConcurrency(5).for(data).process(async (target, index, pool) => {
        const out = `${output}/${target.file}`;
        await timeout(randomInt(100, 500));
        const res = await image.request({
            url: target.profilePicHD || target.imageUrl,
            headers: {}
        });
        await fs.promises.writeFile(out, Buffer.from(res.body, 'utf-8'));
        return {
            id: target.id,
            file: out
        };
    });
}

async function toCSV(data, target, headers = true) {

    const readable = new Readable();
    data.forEach(item => readable.push(JSON.stringify(item)));
    readable.push(null);

    const csv = {
        sendHeaders: headers
    };

    await pipeline(
        readable,
        jsonToCsv({
            csv
        }),
        fs.createWriteStream(target, {
            flags: 'a'
        })
    );
}

async function toNdJson(data, target) {
    const writable = fs.createWriteStream(target, {
        flags: 'a'
    });

    for await (const chunk of ndjson.stringify(data)) {
        if (!writable.write(chunk)) {
            await once(writable, 'drain');
        }
    }

    writable.end();

    await finished(writable);
}

module.exports = {
    assets,
    toCSV,
    toNdJson
};